require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { PDFDocument } = require('pdf-lib');
const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium');
const { createClient } = require('@supabase/supabase-js');
const mailchimp = require('@mailchimp/mailchimp_marketing');
const { Resend } = require('resend');
const QRCode = require('qrcode');

const app = express();
app.use(cors());
// IMPORTANT: Keep raw body for webhook verification if needed in the future
app.use('/api/shopify/webhook', express.json());
app.use(express.json());
app.use(express.static(__dirname, { extensions: ['html'] }));

// Init Supabase (Use Service Role Key to bypass RLS in the serverless environment)
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey, {
    auth: {
        persistSession: false,
        autoRefreshToken: false,
        detectSessionInUrl: false
    }
});

// Init Mailchimp
mailchimp.setConfig({
    apiKey: process.env.MAILCHIMP_API_KEY,
    server: process.env.MAILCHIMP_SERVER_PREFIX, 
});

// Use Memory Storage for Vercel Serverless Compatibility
const upload = multer({ storage: multer.memoryStorage() });
const uploadFields = [
    { name: 'logoUpload', maxCount: 1 },
    { name: 'headshotUpload', maxCount: 1 },
    { name: 'heroUpload', maxCount: 1 },
    { name: 'interiorUpload', maxCount: 1 }
];

// Helper to upload Buffer to Supabase Storage
async function uploadBufferToSupabase(buffer, originalName, mimeType) {
    if (!buffer) return null;
    const ext = path.extname(originalName) || '.png';
    const fileName = `${crypto.randomUUID()}${ext}`;
    
    const { data, error } = await supabase.storage
        .from('b2b_pdfs')
        .upload(`uploads/${fileName}`, buffer, {
            contentType: mimeType,
            upsert: false
        });

    if (error) {
        console.error("Supabase Storage Upload Error:", error);
        return null;
    }

    const { data: publicUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`uploads/${fileName}`);
    return publicUrlData.publicUrl;
}

// ---------------------------------------------------------
// Step 1 - Save data and redirect to Shopify Checkout
// ---------------------------------------------------------
app.post('/api/checkout-session', upload.fields(uploadFields), async (req, res) => {
    try {
        const data = req.body;
        console.log('Received configurator data for checkout:', data.email);

        const orderId = crypto.randomUUID();

        // Upload files to Supabase if they exist
        const logoUrl = req.files['logoUpload'] ? await uploadBufferToSupabase(req.files['logoUpload'][0].buffer, req.files['logoUpload'][0].originalname, req.files['logoUpload'][0].mimetype) : null;
        const headshotUrl = req.files['headshotUpload'] ? await uploadBufferToSupabase(req.files['headshotUpload'][0].buffer, req.files['headshotUpload'][0].originalname, req.files['headshotUpload'][0].mimetype) : null;
        const heroUrl = req.files['heroUpload'] ? await uploadBufferToSupabase(req.files['heroUpload'][0].buffer, req.files['heroUpload'][0].originalname, req.files['heroUpload'][0].mimetype) : null;
        const interiorUrl = req.files['interiorUpload'] ? await uploadBufferToSupabase(req.files['interiorUpload'][0].buffer, req.files['interiorUpload'][0].originalname, req.files['interiorUpload'][0].mimetype) : null;

        // Save to Supabase b2b_orders table
        const { error } = await supabase
            .from('b2b_orders')
            .insert([{
                order_id: orderId,
                email: data.accountEmail || data.email,
                company_name: data.companyName,
                phone: data.phone,
                website: data.website,
                headline: data.headline,
                copy: data.copy,
                logo_path: logoUrl,
                headshot_path: headshotUrl,
                hero_path: heroUrl,
                interior_path: interiorUrl,
                status: 'pending_payment'
            }]);

        if (error) throw error;

        // 1.2 Account Creation
        let authUserId = null;
        if (data.accountEmail && data.password) {
            // Register user in Supabase Auth using the Admin API
            const { data: authData, error: authError } = await supabase.auth.admin.createUser({
                email: data.accountEmail,
                password: data.password,
                email_confirm: true
            });

            if (authError) {
                console.error("Supabase Auth Error:", authError.message);
                if (authError.message.includes("already registered") || authError.message.includes("User already exists") || authError.status === 422) {
                    return res.status(400).json({ error: "An account with this email already exists. Please log in to your Resource Center." });
                }
                // We'll log other errors, but won't fail the checkout if they already exist
            } else if (authData.user) {
                authUserId = authData.user.id;
                
                // Create a unique book slug
                const baseSlug = (data.companyName || 'agent').toLowerCase().replace(/[^a-z0-9]+/g, '-');
                const uniqueSlug = `${baseSlug}-${Math.floor(1000 + Math.random() * 9000)}`;

                // Insert into public.users
                const { error: userError } = await supabase.from('users').insert([{
                    id: authUserId,
                    username: data.username,
                    email: data.accountEmail,
                    company_name: data.companyName,
                    vertical: data.industry || 'Real Estate',
                    book_slug: uniqueSlug
                }]);

                if (userError) console.error("Error creating public.users record:", userError.message);
            }
        }

        // 1.5 Mailchimp Pre-Checkout Lead Capture (Abandoned Cart protection)
        if (process.env.MAILCHIMP_API_KEY && process.env.MAILCHIMP_API_KEY !== 'missing_key' && data.email) {
            const listId = process.env.MAILCHIMP_LIST_ID;
            const subscriberHash = crypto.createHash('md5').update(data.email.toLowerCase()).digest('hex');
            try {
                await mailchimp.lists.setListMember(listId, subscriberHash, {
                    email_address: data.email,
                    status_if_new: 'subscribed',
                    merge_fields: { 
                        COMPANY: data.companyName || '',
                        PHONE: data.phone || ''
                    },
                });
                await mailchimp.lists.updateListMemberTags(listId, subscriberHash, {
                    tags: [{ name: 'b2b-configurator-lead', status: 'active' }]
                });
                console.log(`📧 Mailchimp: Captured pre-checkout lead ${data.email}.`);
            } catch (mcError) {
                console.error("Mailchimp Pre-Checkout Capture Error:", mcError.response?.body?.detail || mcError.message);
            }
        }

        // Redirect to Shopify Cart Permalink
        const shopifyVariantId = "46498770059463"; 
        const checkoutUrl = `https://lauralai-one.myshopify.com/cart/${shopifyVariantId}:1?attributes[order_id]=${orderId}`;

        res.json({ success: true, orderId: orderId, checkoutUrl: checkoutUrl });

    } catch (err) {
        console.error("Error creating checkout session:", err);
        res.status(500).json({ error: 'Failed to create checkout session', details: err.message });
    }
});

// ---------------------------------------------------------
// Temporary Route to Debug Resend API Errors on Vercel
// ---------------------------------------------------------
app.get('/api/test-resend', async (req, res) => {
    try {
        const apiKey = process.env.RESEND_API_KEY;
        if (!apiKey) {
            return res.status(400).json({ error: "RESEND_API_KEY is missing from environment" });
        }
        
        const resend = new Resend(apiKey);
        const data = await resend.emails.send({
            from: '250PROUD Fulfillment <delivery@250proud.net>',
            to: 'michael.price@example.com', // fake email to trigger a bounce or send
            subject: 'Test Resend API Configuration',
            html: '<p>This is a test of the Resend API configuration.</p>'
        });
        
        res.json({ success: true, message: "Resend triggered without crashing", result: data });
    } catch (err) {
        res.status(500).json({ error: "Resend Threw an Error", details: err.message, raw: err });
    }
});

// ---------------------------------------------------------
// Step 2 - Webhook Receiver (Triggered after payment)
// ---------------------------------------------------------
app.post('/api/shopify/webhook', async (req, res) => {
    try {
        const payload = req.body;
        // In a real scenario, Shopify sends note_attributes inside the order payload.
        // For testing, we send { order_id: "uuid" }
        const orderId = payload.order_id || (payload.note_attributes && payload.note_attributes.find(n => n.name === 'order_id')?.value);

        if (!orderId) {
            console.error('No order_id found in webhook payload');
            return res.status(400).send('Missing order_id');
        }

        console.log(`🔔 Received Webhook from Shopify for Order: ${orderId}...`);

        // Fetch order from Supabase
        const { data: orderData, error: fetchError } = await supabase
            .from('b2b_orders')
            .select('*')
            .eq('order_id', orderId)
            .single();

        if (fetchError || !orderData) {
            console.error(`Order ${orderId} not found in database.`);
            return res.status(404).send('Order not found');
        }

        if (orderData.status === 'completed' || orderData.status === 'processing') {
            return res.status(200).send('Already processing or completed');
        }

        // Mark as processing immediately to prevent duplicate webhook runs
        await supabase.from('b2b_orders').update({ status: 'processing' }).eq('order_id', orderId);

        // In Vercel serverless, we MUST await the background task before sending the response
        // Otherwise Vercel terminates the function and the PDF is never generated.
        await generateAndDeliverPDF(orderData);
        res.status(200).json({ success: true, message: 'Webhook processed, PDF generated.' });

    } catch (err) {
        console.error("Webhook processing error:", err);
        if (!res.headersSent) res.status(500).send('Server Error');
    }
});

async function generateAndDeliverPDF(order) {
    try {
        console.log("Starting PDF generation pipeline...");

        // Build HTML for the back cover
        const templatePath = path.join(__dirname, 'back_cover_template.html');
        let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

        // Replace placeholders with Supabase Storage URLs or fallback text
        htmlTemplate = htmlTemplate.replace(/{{COMPANY_NAME}}/g, order.company_name || 'Your Company LLC');
        htmlTemplate = htmlTemplate.replace('{{WEBSITE}}', order.website || 'www.yourwebsite.com');
        htmlTemplate = htmlTemplate.replace('{{PHONE}}', order.phone || '555-0198');
        htmlTemplate = htmlTemplate.replace('{{EMAIL}}', order.email || 'hello@yourcompany.com');
        htmlTemplate = htmlTemplate.replace('{{HEADLINE}}', order.headline || 'Built on Grit.');
        htmlTemplate = htmlTemplate.replace('{{COPY}}', order.copy || 'Thank you for supporting American values.');
        
        // Inject images (Base64 or external URLs)
        htmlTemplate = htmlTemplate.replace('{{LOGO_URL}}', order.logo_path || 'https://via.placeholder.com/300x150.png?text=YOUR+LOGO');
        htmlTemplate = htmlTemplate.replace('{{HEADSHOT_URL}}', order.headshot_path || 'https://via.placeholder.com/200x200.png?text=YOUR+PHOTO');
        htmlTemplate = htmlTemplate.replace('{{HEADSHOT_DISPLAY}}', order.headshot_path ? 'block' : 'none');
        htmlTemplate = htmlTemplate.replace('{{HERO_URL}}', order.hero_path || 'https://via.placeholder.com/600x400.png?text=YOUR+HERO+IMAGE');
        htmlTemplate = htmlTemplate.replace('{{INTERIOR_URL}}', order.interior_path || 'https://via.placeholder.com/400x500.png?text=INTERIOR+PREVIEW');

        console.log("Launching serverless browser...");
        
        // Vercel Serverless Puppeteer Config using Sparticuz
        const executablePath = await chromium.executablePath();
        const browser = await puppeteer.launch({
            args: chromium.args,
            defaultViewport: chromium.defaultViewport,
            executablePath: executablePath || undefined,
            headless: chromium.headless,
        });

        const page = await browser.newPage();
        await page.setContent(htmlTemplate, { waitUntil: 'load', timeout: 15000 });

        const backCoverPdfBuffer = await page.pdf({
            format: 'Letter',
            printBackground: true,
            margin: { top: '0', right: '0', bottom: '0', left: '0' }
        });
        // We will keep the browser open to generate the marketing card later

        console.log("Merging customized back cover with main book...");
        const mainBookPath = path.join(__dirname, '250Proud_ColoringBook_B2B_Base_Final.pdf');
        const mainPdfBytes = fs.readFileSync(mainBookPath);
        const mainPdfDoc = await PDFDocument.load(mainPdfBytes);
        const backCoverPdfDoc = await PDFDocument.load(backCoverPdfBuffer);
        
        const [backCoverPage] = await mainPdfDoc.copyPages(backCoverPdfDoc, [0]);
        mainPdfDoc.addPage(backCoverPage);

        mainPdfDoc.setTitle('250 Strong: Built By Hand');
        mainPdfDoc.setAuthor('250PROUD');
        mainPdfDoc.setSubject('Custom B2B Digital Coloring Book');

        const finalPdfBytes = await mainPdfDoc.save();
        const finalPdfBuffer = Buffer.from(finalPdfBytes);

        console.log("Uploading final PDF to Supabase...");
        const safeName = (order.company_name || 'Edition').replace(/[^a-zA-Z0-9]/g, '');
        const shortId = order.order_id.substring(0, 5);
        const fileSuffix = `${safeName}_${shortId}`;
        
        const pdfFileName = `250Proud_ColoringBook_${fileSuffix}.pdf`;
        
        const { data, error: uploadError } = await supabase.storage
            .from('b2b_pdfs')
            .upload(`completed/${pdfFileName}`, finalPdfBuffer, {
                contentType: 'application/pdf',
                upsert: true
            });

        if (uploadError) throw uploadError;

        const { data: publicUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`completed/${pdfFileName}`);
        const pdfDownloadUrl = publicUrlData.publicUrl;

        console.log(`✅ PDF Uploaded to Supabase! URL: ${pdfDownloadUrl}`);

        // --- NEW: Generate Marketing Card & Update Resource Center ---
        console.log("Looking up user for Resource Center...");
        let qrCodeLink = pdfDownloadUrl; // fallback
        let qrCodePublicUrl = null;
        let bookSlug = null;
        
        const { data: userData } = await supabase.from('users').select('book_slug, username').eq('email', order.email).single();
        if (userData && userData.book_slug) {
            bookSlug = userData.book_slug;
            qrCodeLink = `https://250proud.net/book/${bookSlug}`;
            console.log(`User found. Generating QR code for shortlink: ${qrCodeLink}`);
        }

        console.log("Generating QR Code and Marketing Card...");
        const qrCodeDataUri = await QRCode.toDataURL(qrCodeLink, {
            color: { dark: '#000000', light: '#FFFFFF' },
            margin: 1,
            width: 800
        });

        // Upload QR Code to Supabase Storage for the Resource Center
        const qrBuffer = Buffer.from(qrCodeDataUri.split(',')[1], 'base64');
        const qrFileName = `250Proud_QRCode_${fileSuffix}.png`;
        await supabase.storage.from('b2b_pdfs').upload(`completed/${qrFileName}`, qrBuffer, { contentType: 'image/png', upsert: true });
        const { data: qrPublicUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`completed/${qrFileName}`);
        qrCodePublicUrl = qrPublicUrlData.publicUrl;

        const cardTemplatePath = path.join(__dirname, 'marketing_card_template.html');
        let cardHtmlTemplate = fs.readFileSync(cardTemplatePath, 'utf8');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{COMPANY_NAME}}', order.company_name || 'Your Company LLC');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{LOGO_URL}}', order.logo_path || 'https://placehold.co/300x150/png?text=YOUR+LOGO');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{QR_CODE_DATA_URI}}', qrCodeDataUri);
        cardHtmlTemplate = cardHtmlTemplate.replace('{{COVER_URL}}', 'https://250proud.net/nc_assets/img/generated_true_cover.png');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{PHONE}}', order.phone || '');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{PHONE_DISPLAY}}', order.phone ? 'flex' : 'none');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{EMAIL}}', order.email || '');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{EMAIL_DISPLAY}}', order.email ? 'flex' : 'none');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{WEBSITE}}', order.website || '');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{WEBSITE_DISPLAY}}', order.website ? 'flex' : 'none');

        const cardPage = await browser.newPage();
        await cardPage.setContent(cardHtmlTemplate, { waitUntil: 'load', timeout: 15000 });
        
        const cardPdfBufferRaw = await cardPage.pdf({
            width: '6.25in',
            height: '4.25in',
            printBackground: true,
            margin: { top: '0', right: '0', bottom: '0', left: '0' }
        });
        await browser.close();

        const cardPdfDoc = await PDFDocument.load(cardPdfBufferRaw);
        cardPdfDoc.setTitle('250PROUD Marketing Postcard');
        cardPdfDoc.setAuthor('250PROUD');
        const cardPdfBuffer = Buffer.from(await cardPdfDoc.save());

        const cardFileName = `250Proud_Postcard_${fileSuffix}.pdf`;
        const { error: cardUploadError } = await supabase.storage
            .from('b2b_pdfs')
            .upload(`completed/${cardFileName}`, cardPdfBuffer, {
                contentType: 'application/pdf',
                upsert: true
            });

        if (cardUploadError) throw cardUploadError;
        const { data: cardPublicUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`completed/${cardFileName}`);
        const cardDownloadUrl = cardPublicUrlData.publicUrl;
        console.log(`✅ Marketing Card Uploaded! URL: ${cardDownloadUrl}`);
        // ------------------------------------

        // Update Order Status
        await supabase.from('b2b_orders').update({ status: 'completed' }).eq('order_id', order.order_id);

        // Update Users Table (Resource Center)
        await supabase.from('users').update({
            book_download_url: pdfDownloadUrl,
            postcard_download_url: cardDownloadUrl,
            qr_code_url: qrCodePublicUrl
        }).eq('email', order.email);

        const email = order.email;

        // 1. Send Transactional Fulfillment Email via Resend
        if (process.env.RESEND_API_KEY && email) {
            console.log(`📧 Resend: Sending fulfillment email to ${email}...`);
            const resend = new Resend(process.env.RESEND_API_KEY);
            try {
                const { data, error } = await resend.emails.send({
                    from: '250PROUD Fulfillment <delivery@250proud.net>',
                    to: email,
                    subject: `Your Custom 250PROUD Edition is Ready, ${order.company_name || 'Partner'}! 🇺🇸`,
                    html: `
                        <!DOCTYPE html>
                        <html>
                        <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        </head>
                        <body style="margin: 0; padding: 0; background-color: #f8f9fa; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                            <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8f9fa; padding: 40px 0;">
                                <tr>
                                    <td align="center">
                                        <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); overflow: hidden; margin: 0 auto; max-width: 600px;">
                                            <!-- Header -->
                                            <tr>
                                                <td align="center" style="background-color: #0A3161; padding: 30px 20px;">
                                                    <h2 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 3px;">250PROUD</h2>
                                                    <p style="color: #D4AF37; margin: 8px 0 0 0; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Digital Master Fulfillment</p>
                                                </td>
                                            </tr>
                                            <!-- Body Content -->
                                            <tr>
                                                <td style="padding: 40px 30px;">
                                                    <h1 style="color: #1a1a1a; font-size: 22px; font-weight: 800; margin: 0 0 20px 0; text-align: center;">YOUR MASTER EDITION IS READY</h1>
                                                    <p style="font-size: 16px; line-height: 1.6; color: #444444; margin: 0 0 35px 0;">
                                                        Thank you for your partnership, <strong>${order.company_name || 'Partner'}</strong>. Your digitally licensed, white-labeled master copy of <strong>250 Strong: Built By Hand</strong> has been generated successfully and is ready for deployment.
                                                    </p>
                                                    
                                                    <!-- Buttons -->
                                                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 35px;">
                                                        <tr>
                                                            <td align="center" style="padding-bottom: 15px;">
                                                                <a href="${pdfDownloadUrl}?download=" style="background-color: #D4AF37; color: #ffffff; padding: 16px 30px; text-decoration: none; font-size: 15px; font-weight: bold; border-radius: 6px; display: inline-block; width: 80%; max-width: 280px; text-align: center; text-transform: uppercase;">
                                                                    Download Coloring Book
                                                                </a>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td align="center" style="padding-bottom: 15px;">
                                                                <a href="${cardDownloadUrl}?download=" style="background-color: #f8f9fa; color: #1a1a1a; border: 2px solid #eaeaea; padding: 14px 30px; text-decoration: none; font-size: 15px; font-weight: bold; border-radius: 6px; display: inline-block; width: 80%; max-width: 280px; text-align: center; text-transform: uppercase;">
                                                                    Download 4x6 Postcard
                                                                </a>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <td align="center">
                                                                <a href="https://250proud.net/resources" style="background-color: #0A3161; color: #ffffff; padding: 16px 30px; text-decoration: none; font-size: 15px; font-weight: bold; border-radius: 6px; display: inline-block; width: 80%; max-width: 280px; text-align: center; text-transform: uppercase;">
                                                                    Marketing Resource Center
                                                                </a>
                                                            </td>
                                                        </tr>
                                                    </table>

                                                    ${bookSlug ? `
                                                    <div style="background-color: #f0f4f8; border-left: 4px solid #0A3161; padding: 25px; border-radius: 4px; margin-bottom: 30px;">
                                                        <h3 style="color: #0A3161; font-size: 15px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px;">Your Marketing Dashboard</h3>
                                                        <p style="font-size: 14px; line-height: 1.6; color: #555555; margin: 0 0 15px 0;">
                                                            We have unlocked your exclusive Marketing Resource Center. Access your AI Marketing Copy generator, download social media graphics, and manage your account.
                                                        </p>
                                                        <ul style="font-size: 14px; line-height: 1.6; color: #555555; margin: 0; padding-left: 20px;">
                                                            <li><strong>Dashboard:</strong> <a href="https://250proud.net/resources.html" style="color: #0A3161; font-weight: bold;">Login Here</a></li>
                                                            <li><strong>Your Shortened Book Link:</strong> <a href="https://250proud.net/book/${bookSlug}" style="color: #0A3161;">https://250proud.net/book/${bookSlug}</a></li>
                                                        </ul>
                                                    </div>` : ''}


                                                    <!-- Instructions -->
                                                    <div style="background-color: #f8f9fa; border-left: 4px solid #D4AF37; padding: 25px; border-radius: 4px; margin-bottom: 30px;">
                                                        <h3 style="color: #1a1a1a; font-size: 15px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 0.5px;">How to use your Postcard:</h3>
                                                        <p style="font-size: 14px; line-height: 1.6; color: #555555; margin: 0;">
                                                            We have automatically generated a print-ready, <strong>4x6 inch postcard</strong> featuring your branding and a custom QR Download Code. You can print these cards through any standard print service or on your own printer. Use it as a marketing tool at open houses, schools, or community events. When scanned, it instantly delivers your customized Coloring Book !
                                                        </p>
                                                    </div>
                                                    
                                                    <p style="font-size: 13px; line-height: 1.6; color: #888888; margin: 0; padding-top: 25px; border-top: 1px solid #eaeaea; text-align: center;">
                                                        <strong>Distribution License:</strong> These files grant you an Unlimited Digital Distribution License. You may distribute them to your clients indefinitely. If you’re interested in a bulk printing quote reach out to info@250Proud with your desired quantity for a quote.<br><br>
                                                        If you have any trouble downloading the files, simply reply directly to this email.<br>
                                                        <em>- The 250PROUD Team</em>
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </body>
                        </html>
                    `
                });

                if (error) {
                    console.error("Resend API returned error:", error);
                } else {
                    console.log(`✅ Resend: Fulfillment email successfully delivered to ${email}.`, data);
                }
            } catch (resendError) {
                console.error("Resend Fulfillment Exception:", resendError);
            }
        }

        // 2. Mailchimp Integration
        // 2. Mailchimp Integration
        if (process.env.MAILCHIMP_API_KEY && process.env.MAILCHIMP_API_KEY !== 'missing_key' && email) {
            const listId = process.env.MAILCHIMP_LIST_ID;
            const subscriberHash = crypto.createHash('md5').update(email.toLowerCase()).digest('hex');

            try {
                await mailchimp.lists.setListMember(listId, subscriberHash, {
                    email_address: email,
                    status_if_new: 'subscribed',
                    merge_fields: { 
                        COMPANY: order.company_name,
                        PHONE: order.phone,
                        PDF_URL: pdfDownloadUrl
                    },
                });
                console.log(`📧 Mailchimp: Upserted ${email} with PDF_URL.`);

                await mailchimp.lists.updateListMemberTags(listId, subscriberHash, {
                    tags: [{ name: 'b2b-delivered', status: 'active' }]
                });
                console.log(`📧 Mailchimp: Tagged ${email} with 'b2b-delivered'.`);
            } catch (mcError) {
                console.error("Mailchimp error:", mcError.response ? mcError.response.body : mcError);
            }
        }

        // 2. Supabase Logging
        const { error: supaError } = await supabase
            .from('subscribers')
            .insert([{ 
                email: email, 
                first_name: order.company_name, 
                phone: order.phone,
                source: 'b2b-configurator-paid' 
            }]);
        
        if (supaError && supaError.code === '23505') {
            console.log(`💾 Supabase: Email ${email} already in subscribers database. Proceeding.`);
        } else if (supaError) {
            console.error('Supabase subscriber logging error:', supaError);
        } else {
            console.log(`💾 Supabase: Logged order for ${email}.`);
        }

    } catch (error) {
        console.error("Critical error in PDF Generation Pipeline:", error);
    }
}

// ---------------------------------------------------------
// Copy API (ElevenLabs)
// ---------------------------------------------------------
app.post('/api/generate-text', async (req, res) => {
    try {
        const { companyName, industry } = req.body;
        
        let mockCopy = `For 250 years, this country has been sustained by those who wake up early, work hard, and put family first. At ${companyName}, we share those exact values. That's why we're thrilled to gift you '250 Strong, Built By Hand'. This exclusive 24-page collection features beautifully detailed illustrations of American history and local heroes. Print it out, grab some colored pencils, and take a moment to reflect on the freedoms we cherish.`;
        let mockHeadline = `Built on Grit. Proudly Supported by ${companyName}.`;

        if (industry === 'Real Estate') {
            mockHeadline = `Building Communities Since 1776. Proudly Supported by ${companyName}.`;
            mockCopy = `America was built on the idea of home—a place to raise a family, build a future, and put down roots. For 250 years, the American dream of homeownership has driven our nation forward. At ${companyName}, we help families find their piece of that dream. Enjoy this exclusive 24-page coloring book celebrating the history and heroes of the land we love.`;
        } else if (industry === 'Mortgage') {
            mockHeadline = `Financing the American Dream. Proudly Supported by ${companyName}.`;
            mockCopy = `From the first homesteaders to modern-day neighborhoods, America was built by those who invested in their future. At ${companyName}, we are proud to help families finance their piece of the American Dream. Grab some colored pencils and enjoy this 24-page tribute to the history, grit, and enduring spirit of this great nation.`;
        } else if (industry === 'Insurance') {
            mockHeadline = `Protecting What Matters. Proudly Supported by ${companyName}.`;
            mockCopy = `For 250 years, Americans have worked tirelessly to build businesses, homes, and legacies. At ${companyName}, we exist to protect what you’ve built. As we celebrate our nation’s history, we invite you to enjoy '250 Strong, Built By Hand'. Share this 24-page coloring book with your family and reflect on the enduring strength of the American spirit.`;
        } else if (industry === 'Home Services') {
            mockHeadline = `Built By Hand. Maintained With Pride by ${companyName}.`;
            mockCopy = `This country wasn't built in a boardroom; it was built by tradesmen, builders, and hard workers who weren't afraid to get their hands dirty. At ${companyName}, we honor that tradition of hard work every day. Enjoy this beautiful 24-page coloring book celebrating the makers and builders of America's 250-year history.`;
        } else if (industry === 'Wealth Management') {
            mockHeadline = `Securing Legacies. Proudly Supported by ${companyName}.`;
            mockCopy = `America’s 250-year history is a testament to vision, planning, and perseverance. At ${companyName}, we help families and businesses plan for the long term so they can leave a lasting legacy. We hope you enjoy this 24-page coloring book highlighting the pivotal moments and everyday heroes that built our nation's incredible wealth of history.`;
        }

        res.json({ headline: mockHeadline, copy: mockCopy });
    } catch (err) {
        console.error("Copy generation failed:", err);
        res.status(500).json({ error: 'Failed to generate copy' });
    }
});

app.get('/api/test-pipeline', async (req, res) => {
    try {
        const orderId = 'test-pipeline-' + Date.now();
        const orderData = {
            order_id: orderId,
            company_name: 'Test Pipeline LLC',
            phone: '555-0199',
            email: req.query.email || 'mike+pipeline@lauralai.llc',
            website: 'www.testpipeline.com',
            headline: 'Pipeline Built on Grit',
            copy: 'This is a live pipeline test directly from the edge.',
            logo_path: null,
            headshot_path: null,
            hero_path: null,
            interior_path: null,
            status: 'pending_payment'
        };

        const logs = [];
        const originalLog = console.log;
        const originalError = console.error;
        console.log = (...args) => { logs.push(args.join(' ')); originalLog(...args); };
        console.error = (...args) => { logs.push('ERROR: ' + args.join(' ')); originalError(...args); };

        await supabase.from('b2b_orders').insert(orderData);
        await generateAndDeliverPDF(orderData);

        console.log = originalLog;
        console.error = originalError;

        res.json({ success: true, logs: logs });
    } catch (e) {
        res.status(500).json({ error: e.message, stack: e.stack });
    }
});

// ---------------------------------------------------------
// Redirect Route for Shortened Book URLs
// ---------------------------------------------------------
app.get('/book/:slug', async (req, res) => {
    try {
        const slug = req.params.slug;
        if (!slug) return res.status(400).send('Missing slug');

        const { data: userData, error } = await supabase
            .from('users')
            .select('book_download_url')
            .eq('book_slug', slug)
            .single();

        if (error || !userData || !userData.book_download_url) {
            return res.status(404).send('Book not found or not ready yet. Please check back in a few minutes.');
        }

        res.redirect(302, userData.book_download_url);
    } catch (e) {
        res.status(500).send('Server Error');
    }
});

// ---------------------------------------------------------
// QR Code Page Route
// ---------------------------------------------------------
app.get('/qr/:slug', async (req, res) => {
    try {
        const slug = req.params.slug;
        if (!slug) return res.status(400).send('Missing slug');

        const { data: userData, error } = await supabase
            .from('users')
            .select('qr_code_url, company_name')
            .eq('book_slug', slug)
            .single();

        if (error || !userData || !userData.qr_code_url) {
            return res.status(404).send('QR Code not found or not ready yet. Please check back in a few minutes.');
        }

        const html = `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>250 Strong - Your Custom QR Code</title>
            <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@500;700&family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
            <style>
                body {
                    margin: 0;
                    padding: 0;
                    background: #020617;
                    color: white;
                    font-family: 'Inter', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 100vh;
                    text-align: center;
                }
                .container {
                    max-width: 600px;
                    padding: 2rem;
                    background: rgba(255,255,255,0.05);
                    border-radius: 16px;
                    border: 1px solid rgba(255,255,255,0.1);
                }
                h1 {
                    font-family: 'Oswald', sans-serif;
                    color: #D4AF37;
                    text-transform: uppercase;
                    margin-bottom: 1rem;
                    letter-spacing: 1px;
                }
                p {
                    color: #94a3b8;
                    line-height: 1.6;
                    margin-bottom: 2rem;
                }
                .qr-wrapper {
                    background: white;
                    padding: 2rem;
                    border-radius: 12px;
                    display: inline-block;
                    margin-bottom: 2rem;
                }
                .qr-wrapper img {
                    max-width: 300px;
                    height: auto;
                    display: block;
                }
                .btn {
                    background: #D4AF37;
                    color: #020617;
                    text-decoration: none;
                    padding: 1rem 2rem;
                    border-radius: 8px;
                    font-weight: bold;
                    display: inline-block;
                    text-transform: uppercase;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Your 250 Strong Custom QR Code</h1>
                <p><strong>${userData.company_name || 'Partner'}</strong>, here is your custom QR code.</p>
                
                <div class="qr-wrapper">
                    <img src="${userData.qr_code_url}" alt="QR Code">
                </div>
                
                <p>Right-click and save the image above to use on your flyers, business cards, and event signage. When scanned, it will redirect users straight to your custom coloring book download.</p>
                
                <a href="${userData.qr_code_url}" download="250PROUD_QRCode.png" target="_blank" class="btn">Download PNG</a>
            </div>
        </body>
        </html>
        `;

        res.send(html);
    } catch (e) {
        res.status(500).send('Server Error');
    }
});

// ---------------------------------------------------------
// Config Route for Frontend
// ---------------------------------------------------------
app.get('/api/config', (req, res) => {
    res.json({
        SUPABASE_URL: process.env.SUPABASE_URL,
        SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY
    });
});

// ---------------------------------------------------------
// Marketing Resource Center Endpoints
// ---------------------------------------------------------

app.get('/book/:slug', async (req, res) => {
    try {
        const slug = req.params.slug;
        const { data, error } = await supabase
            .from('users')
            .select('book_download_url')
            .eq('book_slug', slug)
            .single();

        if (error || !data || !data.book_download_url) {
            return res.status(404).send("Book not found or still generating. If you just placed an order, please wait a minute and refresh.");
        }

        res.redirect(301, data.book_download_url);
    } catch (err) {
        console.error("Error resolving shortlink:", err);
        res.status(500).send("Internal server error");
    }
});

// 1. Generate AI Marketing Copy
app.post('/api/generate-marketing-copy', async (req, res) => {
    try {
        const { promptText, format, context, userId } = req.body;
        const apiKey = process.env.GEMINI_API_KEY;

        if (!apiKey) return res.status(500).json({ error: 'Gemini API Key missing' });

        const prompt = `You are an expert real estate and corporate marketing copywriter. 
Write a high-converting ${format} based on this context: "${context}". 
The copy should be engaging, professional, and focus on the value of the custom 250 Strong book they are giving away.
Do not include any placeholders like [Name]. Keep it ready to copy and paste.`;

        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{ parts: [{ text: prompt }] }]
            })
        });

        const data = await response.json();
        
        if (!response.ok) throw new Error(data.error?.message || 'Gemini API Error');

        const generatedText = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Failed to generate copy.';

        // Log it to Supabase
        if (userId) {
            await supabase.from('resource_center_logs').insert([{
                user_id: userId,
                copy_type: format,
                generated_text: generatedText
            }]);
        }

        res.json({ success: true, text: generatedText });
    } catch (e) {
        console.error('Gemini error:', e);
        res.status(500).json({ error: e.message });
    }
});

// 2. Request Print Quote
app.post('/api/request-print-quote', async (req, res) => {
    try {
        const { quantity, zipCode, notes, email, companyName } = req.body;
        const resend = new Resend(process.env.RESEND_API_KEY);

        // Email to 250PROUD Team
        await resend.emails.send({
            from: 'Resource Center <system@250proud.net>',
            to: 'info@250proud.net',
            subject: `New Bulk Print Quote Request - ${companyName}`,
            html: `
                <h3>New Print Quote Request</h3>
                <p><strong>Company:</strong> ${companyName}</p>
                <p><strong>Email:</strong> ${email}</p>
                <p><strong>Quantity:</strong> ${quantity}</p>
                <p><strong>Zip Code:</strong> ${zipCode}</p>
                <p><strong>Notes:</strong> ${notes}</p>
            `
        });

        // Email to Client
        await resend.emails.send({
            from: '250PROUD Team <info@250proud.net>',
            to: email,
            subject: 'We received your print quote request! 🇺🇸',
            html: `<p>Hi ${companyName},</p><p>We received your request for a bulk print quote of ${quantity} books shipped to ${zipCode}. Our team is calculating the best freight and print costs and will get back to you shortly.</p><p>Stay Strong,<br>The 250PROUD Team</p>`
        });

        res.json({ success: true });
    } catch (e) {
        console.error('Resend Quote Error:', e);
        res.status(500).json({ error: e.message });
    }
});

// ---------------------------------------------------------
// LAURALAI SCHEDULER API ENDPOINTS
// ---------------------------------------------------------
const BOOKINGS_FILE = path.join(__dirname, 'bookings.json');

function getLocalBookings() {
    try {
        if (!fs.existsSync(BOOKINGS_FILE)) {
            fs.writeFileSync(BOOKINGS_FILE, JSON.stringify([]));
        }
        const data = fs.readFileSync(BOOKINGS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (err) {
        console.error("Error reading local bookings:", err);
        return [];
    }
}

function saveLocalBooking(booking) {
    try {
        const bookings = getLocalBookings();
        bookings.push(booking);
        fs.writeFileSync(BOOKINGS_FILE, JSON.stringify(bookings, null, 2));
    } catch (err) {
        console.error("Error saving local booking:", err);
    }
}

// Zoom API helpers (Server-to-Server OAuth)
async function getZoomAccessToken() {
    const accountId = process.env.ZOOM_ACCOUNT_ID;
    const clientId = process.env.ZOOM_CLIENT_ID;
    const clientSecret = process.env.ZOOM_CLIENT_SECRET;

    if (!accountId || !clientId || !clientSecret) {
        console.warn("⚠️ Zoom API credentials are not fully configured in .env");
        return null;
    }

    try {
        const authHeader = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
        const response = await fetch(`https://zoom.us/oauth/token?grant_type=account_credentials&account_id=${accountId}`, {
            method: 'POST',
            headers: {
                'Authorization': `Basic ${authHeader}`,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.reason || data.error || 'OAuth Request Failed');
        }

        return data.access_token;
    } catch (err) {
        console.error("Zoom OAuth error:", err.message);
        return null;
    }
}

async function createZoomMeeting(token, hostEmail, topic, startTimeISO, duration) {
    if (!token) return null;

    // Try hostEmail first, fallback to 'me'
    const usersToTry = [hostEmail, 'me'];
    for (const user of usersToTry) {
        try {
            const response = await fetch(`https://api.zoom.us/v2/users/${user}/meetings`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    topic: topic || 'LauralAI Scheduled Meeting',
                    type: 2, // Scheduled meeting
                    start_time: startTimeISO,
                    duration: duration || 30,
                    timezone: 'America/Chicago',
                    settings: {
                        host_video: true,
                        participant_video: true,
                        join_before_host: false,
                        mute_upon_entry: true,
                        waiting_room: true
                    }
                })
            });

            const data = await response.json();
            if (response.ok && data.join_url) {
                return data.join_url;
            }
            console.warn(`Zoom meeting creation failed for user ${user}:`, data.message || 'Unknown Error');
        } catch (err) {
            console.error(`Zoom meeting creation error for user ${user}:`, err.message);
        }
    }
    return null;
}


// 1. Fetch Available Time Slots
app.get('/api/bookings/slots', async (req, res) => {
    try {
        const { host, date } = req.query; // host: 'mike' or 'laurie', date: 'YYYY-MM-DD'
        if (!host || !date) {
            return res.status(400).json({ error: "Missing host or date parameters." });
        }

        // Standard time slots (30-minute intervals)
        const allSlots = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
            "15:00", "15:30", "16:00", "16:30"
        ];

        // Fetch existing bookings for this host and date
        let bookedTimes = [];
        try {
            const { data, error } = await supabase
                .from('bookings')
                .select('meeting_time')
                .eq('host', host.toLowerCase())
                .eq('meeting_date', date);

            if (error) throw error;
            bookedTimes = (data || []).map(b => b.meeting_time.substring(0, 5));
        } catch (dbError) {
            console.warn("Supabase fetch failed, falling back to local storage:", dbError.message);
            // Fallback to local bookings.json
            const localBookings = getLocalBookings();
            bookedTimes = localBookings
                .filter(b => b.host.toLowerCase() === host.toLowerCase() && b.date === date)
                .map(b => b.time);
        }

        // Determine if selected date is today in Central Time
        const nowInCT = new Date(new Date().toLocaleString("en-US", { timeZone: "America/Chicago" }));
        const currentYear = nowInCT.getFullYear();
        const currentMonth = String(nowInCT.getMonth() + 1).padStart(2, '0');
        const currentDate = String(nowInCT.getDate()).padStart(2, '0');
        const todayStr = `${currentYear}-${currentMonth}-${currentDate}`;

        // Filter out booked slots and past slots (if today)
        const availableSlots = allSlots.filter(slot => {
            // Check if already booked
            if (bookedTimes.includes(slot)) return false;

            // If today, filter out past slots
            if (date === todayStr) {
                const [slotHour, slotMinute] = slot.split(':').map(Number);
                const currentHour = nowInCT.getHours();
                const currentMinute = nowInCT.getMinutes();

                if (slotHour < currentHour) return false;
                if (slotHour === currentHour && slotMinute <= currentMinute) return false;
            }

            return true;
        });

        res.json({ success: true, host, date, slots: availableSlots });
    } catch (e) {
        console.error("Error fetching slots:", e);
        res.status(500).json({ error: e.message });
    }
});

// 2. Submit a New Booking
app.post('/api/bookings', async (req, res) => {
    try {
        const {
            host,
            date,
            time,
            guest_name,
            guest_email,
            guest_phone,
            guest_company,
            topic,
            meeting_type = 'gmeet', // 'phone', 'gmeet', or 'zoom'
            duration = 30
        } = req.body;

        if (!host || !date || !time || !guest_name || !guest_email) {
            return res.status(400).json({ error: "Missing required booking details." });
        }

        const cleanHost = host.toLowerCase();
        const hostName = cleanHost === 'mike' ? 'Mike Price' : 'Laurie Price';
        const hostEmail = cleanHost === 'mike' ? 'mike@lauralai.llc' : 'laurie@lauralai.llc';
        const notificationEmails = [hostEmail, '360podcast@gmail.com'];

        // Determine format/location and create Zoom meeting if chosen
        let finalLocation = 'Google Meet';
        if (meeting_type === 'zoom') {
            try {
                const zoomToken = await getZoomAccessToken();
                if (zoomToken) {
                    const localStartStr = `${date}T${time}:00`;
                    const zoomLink = await createZoomMeeting(zoomToken, hostEmail, topic, localStartStr, duration);
                    if (zoomLink) {
                        finalLocation = zoomLink;
                    } else {
                        console.warn("⚠️ Zoom meeting creation returned null. Falling back to Google Meet.");
                        finalLocation = 'Google Meet (Zoom creation failed)';
                    }
                } else {
                    console.warn("⚠️ Zoom token could not be retrieved. Falling back to Google Meet.");
                    finalLocation = 'Google Meet (Zoom authentication failed)';
                }
            } catch (zoomErr) {
                console.error("Error creating Zoom meeting:", zoomErr);
                finalLocation = 'Google Meet (Zoom creation error)';
            }
        } else if (meeting_type === 'phone') {
            finalLocation = `Phone Call (${guest_phone || 'Number not provided'})`;
        }

        // Prep Supabase topic to include meeting format information without schema changes
        let supabaseTopic = topic || '';
        if (finalLocation) {
            supabaseTopic = `[Format: ${meeting_type.toUpperCase()} | Loc: ${finalLocation}] ${supabaseTopic}`.trim();
        }

        // Save booking data object
        const bookingRecord = {
            host: cleanHost,
            meeting_date: date,
            meeting_time: time,
            guest_name,
            guest_email,
            guest_phone: guest_phone || null,
            guest_company: guest_company || null,
            topic: supabaseTopic || null,
            duration
        };

        // Try inserting into Supabase
        let bookingId = crypto.randomUUID();
        let savedToDB = false;
        try {
            const { data, error } = await supabase
                .from('bookings')
                .insert([{
                    id: bookingId,
                    ...bookingRecord
                }])
                .select();

            if (error) throw error;
            savedToDB = true;
            console.log(`💾 Supabase: Saved booking in DB with ID: ${bookingId}`);
        } catch (dbError) {
            console.warn("Supabase insert failed, falling back to local JSON:", dbError.message);
            // Save to local JSON fallback
            saveLocalBooking({
                id: bookingId,
                host: cleanHost,
                date,
                time,
                guest_name,
                guest_email,
                guest_phone,
                guest_company,
                topic,
                meeting_type,
                location: finalLocation,
                duration,
                created_at: new Date().toISOString()
            });
        }

        // Calculate UTC ISO times for Google Calendar link & ICS
        // Central Daylight Time (CDT) is UTC-5
        const startDate = new Date(`${date}T${time}:00-05:00`);
        const endDate = new Date(startDate.getTime() + duration * 60 * 1000);
        const startUTC = startDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
        const endUTC = endDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
        const nowUTC = new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

        // Google Calendar Add Link
        const gCalSummary = encodeURIComponent(`Meeting with ${guest_name} (LauralAI)`);
        const gCalDetails = encodeURIComponent(`Guest: ${guest_name}\nEmail: ${guest_email}\nPhone: ${guest_phone || 'N/A'}\nCompany: ${guest_company || 'N/A'}\nTopic: ${topic || 'N/A'}\nFormat/Location: ${finalLocation}\n\nScheduled via LauralAI Meetings.`);
        const gCalLink = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${gCalSummary}&dates=${startUTC}/${endUTC}&details=${gCalDetails}&location=${encodeURIComponent(finalLocation)}`;

        // Generate ICS file string
        const icsContent = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//LauralAI//Booking App//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:REQUEST',
            'BEGIN:VEVENT',
            `UID:${bookingId}`,
            `DTSTAMP:${nowUTC}`,
            `DTSTART:${startUTC}`,
            `DTEND:${endUTC}`,
            `SUMMARY:Meeting: ${guest_name} <> ${hostName}`,
            `DESCRIPTION:Meeting booked via LauralAI Scheduler.\\n\\nGuest: ${guest_name}\\nEmail: ${guest_email}\\nPhone: ${guest_phone || 'N/A'}\\nCompany: ${guest_company || 'N/A'}\\nTopic: ${topic || 'N/A'}\\nFormat/Location: ${finalLocation}`,
            `LOCATION:${finalLocation}`,
            `ORGANIZER;CN="${hostName}":mailto:${hostEmail}`,
            `ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE;CN="${guest_name}":mailto:${guest_email}`,
            'STATUS:CONFIRMED',
            'SEQUENCE:0',
            'END:VEVENT',
            'END:VCALENDAR'
        ].join('\r\n');

        const icsBase64 = Buffer.from(icsContent).toString('base64');

        // Send Email Notifications via Resend
        if (process.env.RESEND_API_KEY) {
            const resend = new Resend(process.env.RESEND_API_KEY);

            try {
                // 1. Send confirmation to Guest
                await resend.emails.send({
                    from: 'LauralAI Meetings <meetings@250proud.net>',
                    to: guest_email,
                    subject: `Confirmed: Meeting with ${hostName} (LauralAI) 🇺🇸`,
                    html: `
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
                            <h2 style="color: #0A3161; border-bottom: 2px solid #D4AF37; padding-bottom: 10px;">Meeting Confirmed</h2>
                            <p>Hi <strong>${guest_name}</strong>,</p>
                            <p>Your meeting with <strong>${hostName}</strong> has been successfully scheduled.</p>
                            
                            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold; width: 120px;">Host:</td><td style="padding: 10px;">${hostName}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Date:</td><td style="padding: 10px;">${date}</td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Time:</td><td style="padding: 10px;">${time} (Central Time)</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Duration:</td><td style="padding: 10px;">${duration} minutes</td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Format / Link:</td><td style="padding: 10px;">${finalLocation.startsWith('http') ? `<a href="${finalLocation}">${finalLocation}</a>` : finalLocation}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Topic:</td><td style="padding: 10px;">${topic || 'General Catch Up'}</td></tr>
                            </table>

                            <p>We've attached a calendar invitation (.ics) to this email to add it directly to your agenda.</p>
                            
                            <div style="text-align: center; margin-top: 30px;">
                                <a href="${gCalLink}" style="background-color: #D4AF37; color: black; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">Add to Google Calendar</a>
                            </div>
                            
                            <p style="font-size: 12px; color: #888; margin-top: 40px; border-top: 1px solid #eaeaea; padding-top: 20px; text-align: center;">
                                Sent by LauralAI LLC. If you need to reschedule, please reply directly to this email.
                            </p>
                        </div>
                    `,
                    attachments: [
                        {
                            filename: 'meeting.ics',
                            content: icsBase64
                        }
                    ]
                });

                // 2. Send notification to Host (Mike/Laurie & 360podcast)
                await resend.emails.send({
                    from: 'LauralAI Meetings <meetings@250proud.net>',
                    to: notificationEmails,
                    subject: `[New Booking] ${guest_name} - ${date} @ ${time} CT`,
                    html: `
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
                            <h2 style="color: #B31942; border-bottom: 2px solid #0A3161; padding-bottom: 10px;">New Meeting Booked</h2>
                            <p>A new meeting has been scheduled on your LauralAI calendar.</p>
                            
                            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold; width: 120px;">Guest Name:</td><td style="padding: 10px;">${guest_name}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Guest Email:</td><td style="padding: 10px;"><a href="mailto:${guest_email}">${guest_email}</a></td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Phone:</td><td style="padding: 10px;">${guest_phone || 'N/A'}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Company:</td><td style="padding: 10px;">${guest_company || 'N/A'}</td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Date:</td><td style="padding: 10px;">${date}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Time:</td><td style="padding: 10px;">${time} (Central Time)</td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Format / Link:</td><td style="padding: 10px;">${finalLocation.startsWith('http') ? `<a href="${finalLocation}">${finalLocation}</a>` : finalLocation}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Topic:</td><td style="padding: 10px;">${topic || 'N/A'}</td></tr>
                            </table>

                            <div style="text-align: center; margin-top: 30px;">
                                <a href="${gCalLink}" style="background-color: #0A3161; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">Add to Google Calendar</a>
                            </div>
                        </div>
                    `,
                    attachments: [
                        {
                            filename: 'invite.ics',
                            content: icsBase64
                        }
                    ]
                });
                
                console.log("📧 Resend: Booking emails sent successfully.");
            } catch (emailErr) {
                console.error("Resend booking notification failure:", emailErr);
            }
        }

        res.json({
            success: true,
            booking_id: bookingId,
            gcal_link: gCalLink,
            location: finalLocation,
            message: "Meeting scheduled successfully."
        });

    } catch (e) {
        console.error("Booking error:", e);
        res.status(500).json({ error: e.message });
    }
});

// Vercel requires exporting the app
module.exports = app;

// Local development server fallback
if (require.main === module) {
    const PORT = process.env.PORT || 3000;
    app.listen(PORT, () => {
        console.log(`B2B Configurator API listening on port ${PORT}`);
    });
}

