require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const luluService = require('./luluService');
const shopifyService = require('./shopifyService');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');
const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium');
const { createClient } = require('@supabase/supabase-js');
const mailchimp = require('@mailchimp/mailchimp_marketing');
const { Resend } = require('resend');
const QRCode = require('qrcode');
const { GoogleGenAI } = require('@google/genai');

const app = express();
app.use(cors());
// IMPORTANT: Keep raw body for webhook verification if needed in the future
app.use('/api/shopify/webhook', express.json());
app.use(express.json());
app.use(express.static(__dirname, { extensions: ['html'] }));

// Init Supabase (Use Service Role Key to bypass RLS in the serverless environment)
const supabaseUrl = process.env.SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || 'placeholder_key';
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
    { name: 'interiorUpload', maxCount: 1 },
    { name: 'magnetImage', maxCount: 1 }
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
        const logoUrl = req.files && req.files['logoUpload'] ? await uploadBufferToSupabase(req.files['logoUpload'][0].buffer, req.files['logoUpload'][0].originalname, req.files['logoUpload'][0].mimetype) : null;
        const headshotUrl = req.files && req.files['headshotUpload'] ? await uploadBufferToSupabase(req.files['headshotUpload'][0].buffer, req.files['headshotUpload'][0].originalname, req.files['headshotUpload'][0].mimetype) : null;
        const heroUrl = req.files && req.files['heroUpload'] ? await uploadBufferToSupabase(req.files['heroUpload'][0].buffer, req.files['heroUpload'][0].originalname, req.files['heroUpload'][0].mimetype) : null;
        const interiorUrl = req.files && req.files['interiorUpload'] ? await uploadBufferToSupabase(req.files['interiorUpload'][0].buffer, req.files['interiorUpload'][0].originalname, req.files['interiorUpload'][0].mimetype) : null;

        let finalMagnetUrl = null;
        if (data.type === 'magnet') {
            if (req.files && req.files['magnetImage']) {
                finalMagnetUrl = await uploadBufferToSupabase(req.files['magnetImage'][0].buffer, req.files['magnetImage'][0].originalname, req.files['magnetImage'][0].mimetype);
            } else if (data.magnetImageUrl) {
                if (data.magnetImageUrl.startsWith('http')) {
                    finalMagnetUrl = data.magnetImageUrl;
                } else {
                    finalMagnetUrl = `https://250proud.net/${data.magnetImageUrl.replace(/^\//, '')}`;
                }
            }
        }

        // Save to Supabase b2b_orders table
        const { error } = await supabase
            .from('b2b_orders')
            .insert([{
                order_id: orderId,
                email: data.accountEmail || data.email || 'magnet_order@250proud.net',
                company_name: data.companyName,
                phone: data.phone,
                website: data.type === 'magnet' ? data.qrUrl : data.website,
                headline: data.type === 'magnet' ? data.orientation : (data.headline ? data.headline.substring(0, 60) : null),
                copy: data.type === 'magnet' ? data.message : (data.copy ? data.copy.substring(0, 350) : null),
                logo_path: logoUrl,
                headshot_path: headshotUrl,
                hero_path: data.type === 'magnet' ? finalMagnetUrl : heroUrl,
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
        let shopifyVariantId = "46498770059463"; // Default: Digital coloring book
        if (data.type === 'magnet') {
            shopifyVariantId = "46700272320711"; // Custom 250PROUD Commemorative Marketing Magnet
        }
        
        const orderType = data.type === 'magnet' ? 'magnet' : 'coloring_book';
        const quantity = data.type === 'magnet' && data.quantity ? data.quantity : 1;
        const checkoutUrl = `https://lauralai-one.myshopify.com/cart/${shopifyVariantId}:${quantity}?attributes[order_id]=${orderId}&attributes[order_type]=${orderType}`;

        res.json({ success: true, orderId: orderId, checkoutUrl: checkoutUrl });

    } catch (err) {
        console.error("Error creating checkout session:", err);
        res.status(500).json({ error: 'Failed to create checkout session', details: err.message });
    }
});

// ---------------------------------------------------------
// Book Editing & Refreshing Routes (Phase 3)
// ---------------------------------------------------------

app.get('/api/my-book', async (req, res) => {
    try {
        const { email } = req.query;
        if (!email) return res.status(400).json({ error: "Email required" });

        // Fetch the latest order for this email
        const { data, error } = await supabase
            .from('b2b_orders')
            .select('*')
            .eq('email', email)
            .order('created_at', { ascending: false })
            .limit(1)
            .single();

        if (error || !data) {
            return res.status(404).json({ error: "No book found for this email." });
        }

        res.json({ success: true, book: data });
    } catch (err) {
        console.error("Error fetching book:", err);
        res.status(500).json({ error: "Server error" });
    }
});

app.post('/api/update-book', upload.fields(uploadFields), async (req, res) => {
    try {
        const data = req.body;
        const email = data.email;
        if (!email) return res.status(400).json({ error: "Email required" });

        // Fetch the existing order to get current image URLs
        const { data: existingOrder, error: fetchError } = await supabase
            .from('b2b_orders')
            .select('*')
            .eq('email', email)
            .order('created_at', { ascending: false })
            .limit(1)
            .single();

        if (fetchError || !existingOrder) {
            return res.status(404).json({ error: "No existing book found to update." });
        }

        // Handle Image Uploads (only update if a new file was provided)
        let heroUrl = existingOrder.hero_path;
        let interiorUrl = existingOrder.interior_path;
        let logoUrl = existingOrder.logo_path;
        let headshotUrl = existingOrder.headshot_path;

        if (req.files && req.files['heroUpload']) heroUrl = await uploadBufferToSupabase(req.files['heroUpload'][0].buffer, req.files['heroUpload'][0].originalname, req.files['heroUpload'][0].mimetype);
        if (req.files && req.files['interiorUpload']) interiorUrl = await uploadBufferToSupabase(req.files['interiorUpload'][0].buffer, req.files['interiorUpload'][0].originalname, req.files['interiorUpload'][0].mimetype);
        if (req.files && req.files['logoUpload']) logoUrl = await uploadBufferToSupabase(req.files['logoUpload'][0].buffer, req.files['logoUpload'][0].originalname, req.files['logoUpload'][0].mimetype);
        if (req.files && req.files['headshotUpload']) headshotUrl = await uploadBufferToSupabase(req.files['headshotUpload'][0].buffer, req.files['headshotUpload'][0].originalname, req.files['headshotUpload'][0].mimetype);

        // Update the order in the database
        const { error: updateError } = await supabase
            .from('b2b_orders')
            .update({
                company_name: data.companyName || existingOrder.company_name,
                phone: data.phone || existingOrder.phone,
                website: data.website || existingOrder.website,
                headline: data.headline ? data.headline.substring(0, 60) : existingOrder.headline,
                copy: data.copy ? data.copy.substring(0, 350) : existingOrder.copy,
                logo_path: logoUrl,
                headshot_path: headshotUrl,
                hero_path: heroUrl,
                interior_path: interiorUrl
            })
            .eq('order_id', existingOrder.order_id);

        if (updateError) throw updateError;

        // Fetch the fully updated row
        const { data: updatedOrder } = await supabase
            .from('b2b_orders')
            .select('*')
            .eq('order_id', existingOrder.order_id)
            .single();

        // We MUST await this so Vercel doesn't freeze the process mid-execution and cause ETXTBSY errors on the next wake
        await generateAndDeliverPDF(updatedOrder);

        res.json({ success: true, message: "Book is being refreshed in the background." });

    } catch (err) {
        console.error("Error updating book:", err);
        res.status(500).json({ error: "Failed to update book", details: err.message });
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
        
        const targetEmail = req.query.email || 'michael.price@example.com';
        const resend = new Resend(apiKey);
        const data = await resend.emails.send({
            from: '250PROUD Fulfillment <delivery@250proud.net>',
            to: targetEmail,
            subject: 'Test Resend API Configuration',
            html: '<p>This is a test of the Resend API configuration.</p>'
        });
        
        res.json({ success: true, message: "Resend triggered without crashing", result: data });
    } catch (err) {
        res.status(500).json({ error: "Resend Threw an Error", details: err.message, raw: err });
    }
});

app.get('/api/diag', async (req, res) => {
    try {
        const { data, error } = await supabase.from('b2b_orders').select('*').order('created_at', { ascending: false }).limit(5);
        res.json({
            hasResend: !!process.env.RESEND_API_KEY,
            orders: data,
            dbError: error
        });
    } catch (e) {
        res.json({ error: e.message });
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

        // Attempt to log raw webhook to an existing table just in case we need to see it.
        // We'll update the b2b_orders row with the raw payload IF we have the orderId.
        if (orderId) {
             await supabase.from('b2b_orders').update({ phone: payload.email || 'webhook_received' }).eq('order_id', orderId);
        }

        if (!orderId) {
            console.error('No order_id found in webhook payload');
            return res.status(400).send('Missing order_id');
        }

        if (payload.id) {
            await supabase.from('b2b_orders').update({ shopify_order_id: payload.id.toString() }).eq('order_id', orderId);
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
        const orderType = payload.note_attributes && payload.note_attributes.find(n => n.name === 'order_type')?.value;
        
        try {
            if (orderType === 'magnet') {
                await generateMagnetPDF(orderData);
            } else {
                await generateAndDeliverPDF(orderData);
            }
            res.status(200).json({ success: true, message: 'Webhook processed, PDF generated.' });
        } catch (pdfErr) {
            console.error("PDF Generation failed, resetting status:", pdfErr);
            await supabase.from('b2b_orders').update({ status: 'pending' }).eq('order_id', orderId);
            throw pdfErr; // let the outer catch block handle the 500
        }

    } catch (err) {
        console.error("Webhook processing error:", err);
        if (!res.headersSent) res.status(500).send('Server Error');
    }
});

// --- LULU WEBHOOK HANDLER ---
app.post('/api/lulu/webhook', async (req, res) => {
    try {
        const payload = req.body;
        console.log("🔔 Received Webhook from Lulu:", JSON.stringify(payload, null, 2));

        const eventType = payload.event_type || (payload.print_job && payload.print_job.status && payload.print_job.status.name);
        
        if (!payload.print_job || !payload.print_job.id) {
            return res.status(200).send('No print job ID');
        }

        const luluJobId = payload.print_job.id.toString();
        await supabase.from('b2b_orders').update({ lulu_status: eventType }).eq('lulu_job_id', luluJobId);

        if (eventType === 'PRINT_JOB_SHIPPED' || eventType === 'SHIPPED') {
            const { data: orderData } = await supabase.from('b2b_orders').select('*').eq('lulu_job_id', luluJobId).single();
            if (orderData && orderData.shopify_order_id) {
                let trackingUrl = '';
                let trackingNumber = '';
                if (payload.print_job.line_items && payload.print_job.line_items.length > 0) {
                    trackingUrl = payload.print_job.line_items[0].tracking_urls?.[0] || '';
                    trackingNumber = payload.print_job.line_items[0].tracking_id || '';
                }
                await shopifyService.fulfillOrder(orderData.shopify_order_id, trackingNumber, trackingUrl);
            }
        }
        res.status(200).send('OK');
    } catch (err) {
        console.error("Lulu webhook error:", err);
        res.status(500).send('Error');
    }
});

async function generateAndDeliverPDF(orderData) {
    try {
        console.log("Starting PDF generation pipeline...");

        // Build HTML for the back cover
        const templatePath = path.join(__dirname, 'back_cover_template.html');
        let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

        // Replace placeholders with Supabase Storage URLs or fallback text
        htmlTemplate = htmlTemplate.replace(/{{COMPANY_NAME}}/g, orderData.company_name || 'Your Company LLC');
        htmlTemplate = htmlTemplate.replace('{{WEBSITE}}', orderData.website || 'www.yourwebsite.com');
        htmlTemplate = htmlTemplate.replace('{{PHONE}}', orderData.phone || '555-0198');
        htmlTemplate = htmlTemplate.replace('{{EMAIL}}', orderData.email || 'hello@yourcompany.com');
        htmlTemplate = htmlTemplate.replace('{{HEADLINE}}', orderData.headline || 'Built on Grit.');
        htmlTemplate = htmlTemplate.replace('{{COPY}}', orderData.copy || 'Thank you for supporting American values.');
        
        let safeLogoPath = orderData.logo_path;
        let safeHeadshotPath = orderData.headshot_path;

        if (!safeLogoPath && safeHeadshotPath) safeLogoPath = safeHeadshotPath;
        if (!safeHeadshotPath && safeLogoPath) safeHeadshotPath = safeLogoPath;

        // Inject images (Base64 or external URLs)
        htmlTemplate = htmlTemplate.replace('{{LOGO_URL}}', safeLogoPath || 'https://via.placeholder.com/300x150.png?text=YOUR+LOGO');
        htmlTemplate = htmlTemplate.replace('{{HEADSHOT_URL}}', safeHeadshotPath || 'https://via.placeholder.com/200x200.png?text=YOUR+PHOTO');
        htmlTemplate = htmlTemplate.replace('{{HEADSHOT_DISPLAY}}', safeHeadshotPath ? 'block' : 'none');
        htmlTemplate = htmlTemplate.replace('{{HERO_URL}}', orderData.hero_path || 'https://via.placeholder.com/600x400.png?text=YOUR+HERO+IMAGE');
        htmlTemplate = htmlTemplate.replace('{{INTERIOR_URL}}', orderData.interior_path || 'https://via.placeholder.com/400x500.png?text=INTERIOR+PREVIEW');

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
        
        // Draw company name on Page 2 (index 1)
        const pages = mainPdfDoc.getPages();
        if (pages.length > 1) {
            const page2 = pages[1];
            const font = await mainPdfDoc.embedFont(StandardFonts.Helvetica);
            page2.drawText(orderData.company_name || 'Your Company LLC', {
                x: 72, // 1 inch
                y: page2.getHeight() - (4.2 * 72) - 16, // matching the python script coordinates
                size: 16,
                font: font,
                color: rgb(0.2, 0.2, 0.2), // Dark gray
            });
        }
        const backCoverPdfDoc = await PDFDocument.load(backCoverPdfBuffer);
        
        const [backCoverPage] = await mainPdfDoc.copyPages(backCoverPdfDoc, [0]);
        mainPdfDoc.addPage(backCoverPage);

        mainPdfDoc.setTitle('250 Strong: Built By Hand');
        mainPdfDoc.setAuthor('250PROUD');
        mainPdfDoc.setSubject('Custom B2B Digital Coloring Book');

        const finalPdfBytes = await mainPdfDoc.save();
        const finalPdfBuffer = Buffer.from(finalPdfBytes);

        console.log("Uploading final PDF to Supabase...");
        const safeName = (orderData.company_name || 'Edition').replace(/[^a-zA-Z0-9]/g, '');
        const shortId = orderData.order_id.substring(0, 5);
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
        const timestamp = Date.now();
        const digitalPdfUrl = `${publicUrlData.publicUrl}?v=${timestamp}`;
        console.log(`✅ Digital PDF Uploaded! URL: ${digitalPdfUrl}`);

        // ------------------------------------
        // LULU PRINT API FILE GENERATION
        // ------------------------------------
        console.log("Generating Lulu Print-on-Demand files...");
        
        // 1. Lulu Interior (Pages 1-22, bypassing front cover and back cover)
        const luluInteriorDoc = await PDFDocument.create();
        const interiorPages = await luluInteriorDoc.copyPages(mainPdfDoc, Array.from({length: 22}, (_, i) => i + 1));
        interiorPages.forEach(p => luluInteriorDoc.addPage(p));
        const luluInteriorBuffer = Buffer.from(await luluInteriorDoc.save());

        // 2. Lulu Wraparound Cover (Left: Back Cover, Right: Front Cover)
        const luluCoverDoc = await PDFDocument.create();
        const wrapPage = luluCoverDoc.addPage([1224, 792]); // 17 x 11 inches
        
        const [embeddedFront] = await luluCoverDoc.embedPdf(mainPdfBytes, [0]);
        const [embeddedBack] = await luluCoverDoc.embedPdf(backCoverPdfBuffer, [0]);
        
        wrapPage.drawPage(embeddedBack, { x: 0, y: 0, width: 612, height: 792 });
        wrapPage.drawPage(embeddedFront, { x: 612, y: 0, width: 612, height: 792 });
        
        const luluCoverBuffer = Buffer.from(await luluCoverDoc.save());

        // Upload Lulu Files
        const luluInteriorName = `250Proud_LuluInterior_${fileSuffix}.pdf`;
        const luluCoverName = `250Proud_LuluCover_${fileSuffix}.pdf`;
        
        await supabase.storage.from('b2b_pdfs').upload(`completed/${luluInteriorName}`, luluInteriorBuffer, { contentType: 'application/pdf', upsert: true });
        await supabase.storage.from('b2b_pdfs').upload(`completed/${luluCoverName}`, luluCoverBuffer, { contentType: 'application/pdf', upsert: true });
        
        const { data: luluIntUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`completed/${luluInteriorName}`);
        const { data: luluCovUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`completed/${luluCoverName}`);
        const luluInteriorUrl = luluIntUrlData.publicUrl;
        const luluCoverUrl = luluCovUrlData.publicUrl;
        console.log(`✅ Lulu Cover URL: ${luluCoverUrl}`);
        console.log(`✅ Lulu Interior URL: ${luluInteriorUrl}`);
        // ------------------------------------

        // --- NEW: Generate Marketing Card & Update Resource Center ---
        console.log("Looking up user for Resource Center...");
        let qrCodeLink = digitalPdfUrl; // fallback
        let qrCodePublicUrl = null;
        let bookSlug = null;
        
        const { data: userData } = await supabase.from('users').select('book_slug, username').eq('email', orderData.email).single();
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
        const { error: qrUploadError } = await supabase.storage.from('b2b_pdfs').upload(`completed/${qrFileName}`, qrBuffer, { contentType: 'image/png', upsert: true });
        if (qrUploadError) console.error("QR Upload Error:", qrUploadError);
        const { data: qrUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`completed/${qrFileName}`);
        qrCodePublicUrl = `${qrUrlData.publicUrl}?v=${timestamp}`;

        const cardTemplatePath = path.join(__dirname, 'marketing_card_template.html');
        let cardHtmlTemplate = fs.readFileSync(cardTemplatePath, 'utf8');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{COMPANY_NAME}}', orderData.company_name || 'Your Company LLC');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{LOGO_URL}}', safeLogoPath || 'https://placehold.co/300x150/png?text=YOUR+LOGO');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{QR_CODE_DATA_URI}}', qrCodeDataUri);
        cardHtmlTemplate = cardHtmlTemplate.replace('{{COVER_URL}}', 'https://250proud.net/nc_assets/img/generated_true_cover.png');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{PHONE}}', orderData.phone || '');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{PHONE_DISPLAY}}', orderData.phone ? 'flex' : 'none');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{EMAIL}}', orderData.email || '');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{EMAIL_DISPLAY}}', orderData.email ? 'flex' : 'none');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{WEBSITE}}', orderData.website || '');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{WEBSITE_DISPLAY}}', orderData.website ? 'flex' : 'none');

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
        const { data: cardUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`completed/${cardFileName}`);
        const cardDownloadUrl = `${cardUrlData.publicUrl}?v=${timestamp}`;
        console.log(`✅ Marketing Card Uploaded! URL: ${cardDownloadUrl}`);
        // ------------------------------------

        // Update Users Table (Resource Center)
        await supabase.from('users').update({
            book_download_url: digitalPdfUrl,
            postcard_download_url: cardDownloadUrl,
            qr_code_url: qrCodePublicUrl
        }).eq('email', orderData.email);

        // Fire off to Lulu automatically
        orderData.lulu_cover_url = luluCoverUrl;
        orderData.lulu_interior_url = luluInteriorUrl;
        let luluJobId = null;
        try {
            const shippingAddress = {
                name: orderData.company_name || 'Customer',
                street1: '123 Test St', // We will need to pull this from Shopify payloads eventually
                city: 'Raleigh',
                state_code: 'NC',
                postcode: '27601',
                country_code: 'US'
            };
            const jobData = await luluService.createPrintJob(orderData, shippingAddress, 1);
            if (jobData && jobData.id) {
                luluJobId = jobData.id.toString();
            }
        } catch (e) {
            console.error("Failed to create Lulu Print Job:", e);
        }

        const { error: finalUpdateError } = await supabase
            .from('b2b_orders')
            .update({
                status: 'completed'
            })
            .eq('order_id', orderData.order_id);

        if (finalUpdateError) throw finalUpdateError;

        console.log(`✅ Order ${orderData.order_id} marked as completed!`);

        // --- SUBMIT PRINT JOB TO LULU API ---
        try {
            // In a production environment, shipping details should come from Shopify Webhook 
            // payload stored in b2b_orders, or the user's input.
            // For now, we pass placeholder/fallback values until we capture exact addresses.
            const shippingAddress = {
                name: orderData.company_name || 'Customer',
                street1: '123 Print St',
                city: 'Raleigh',
                state_code: 'NC',
                postcode: '27601',
                country_code: 'US',
                phone: orderData.phone || '555-555-5555'
            };
            
            // Assume 50 quantity for the bulk order by default, can be dynamically mapped
            const luluJob = await luluService.createPrintJob(
                { ...orderData, lulu_cover_url: luluCoverUrl, lulu_interior_url: luluInteriorUrl }, 
                shippingAddress, 
                50 
            );
            
            if (luluJob && luluJob.id) {
                console.log(`✅ Lulu Print Job Created! Job ID: ${luluJob.id}`);
            }
        } catch (luluErr) {
            console.error('⚠️ Failed to submit print job to Lulu. Digital PDFs were still delivered.', luluErr);
            // We don't throw here to avoid failing the email delivery step
        }

        const email = orderData.email;

        // 1. Send Transactional Fulfillment Email via Resend
        if (process.env.RESEND_API_KEY && email) {
            console.log(`📧 Resend: Sending fulfillment email to ${email}...`);
            const resend = new Resend(process.env.RESEND_API_KEY);
            try {
                const { data, error } = await resend.emails.send({
                    from: '250PROUD Fulfillment <info@250proud.net>',
                    to: email,
                    subject: `Your Custom 250PROUD Edition is Ready, ${orderData.company_name || 'Partner'}! 🇺🇸`,
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
                                                    <p style="font-size: 16px; line-height: 1.6; color: #444444; margin: 0 0 25px 0;">
                                                        Thank you for your partnership, <strong>${orderData.company_name || 'Partner'}</strong>. Your digitally licensed, white-labeled master copy of <strong>250 Strong: Built By Hand</strong> has been generated successfully and is ready for deployment.
                                                    </p>
                                                    
                                                    <!-- Create Campaigns Block -->
                                                    <div style="background-color: #ffffff; border: 2px solid #D4AF37; padding: 25px; border-radius: 8px; margin-bottom: 35px;">
                                                        <h3 style="color: #0A3161; font-size: 18px; margin: 0 0 15px 0; text-transform: uppercase; letter-spacing: 1px;">Create Campaigns That Convert</h3>
                                                        <p style="font-size: 14px; color: #444; margin-bottom: 15px; line-height: 1.6;">Leverage your new digital asset with highly targeted messaging. Here are proven calls-to-action based on who you are sending it to:</p>
                                                        
                                                        <ul style="font-size: 14px; line-height: 1.6; color: #444; margin: 0; padding-left: 20px;">
                                                            <li style="margin-bottom: 10px;"><strong>Past Clients:</strong> "Thank you for trusting us with your business. As we approach America's 250th, we wanted to gift your family this exclusive history book to celebrate the quiet hands that built our nation."</li>
                                                            <li style="margin-bottom: 10px;"><strong>Current Prospects:</strong> "We believe in building legacies. Download our custom 250PROUD edition of 'Built By Hand' and let's discuss how we can build something great together."</li>
                                                            <li><strong>Vendors & Partners:</strong> "Our success is built on strong partnerships. We licensed this exclusive 250PROUD historical collection to share with the partners who keep America moving."</li>
                                                        </ul>
                                                    </div>
                                                    
                                                    <!-- Buttons -->
                                                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="margin-bottom: 35px;">
                                                        <tr>
                                                            <td align="center" style="padding-bottom: 15px;">
                                                                <a href="${digitalPdfUrl}?download=" style="background-color: #D4AF37; color: #ffffff; padding: 16px 30px; text-decoration: none; font-size: 15px; font-weight: bold; border-radius: 6px; display: inline-block; width: 80%; max-width: 280px; text-align: center; text-transform: uppercase;">
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

                                                    <!-- Support Block -->
                                                    <div style="background-color: #071E3D; color: #ffffff; padding: 25px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                                                        <h3 style="color: #D4AF37; font-size: 16px; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1px;">Meet LauralAI</h3>
                                                        <p style="font-size: 14px; line-height: 1.6; margin: 0 0 15px 0; color: #e2e8f0;">
                                                            If you have questions or would like customized suggestions on how to leverage your new digital marketing tool, click the chat bubble on our site to ask <strong>LauralAI</strong>, our expert digital support agent.
                                                        </p>
                                                        <p style="font-size: 13px; color: #94a3b8; margin: 0;">
                                                            If you don't get the answers you need, reach out to our human team at <a href="mailto:info@250proud.net" style="color: #D4AF37; text-decoration: none;">info@250proud.net</a>.
                                                        </p>
                                                    </div>


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
                    console.error("Resend API returned error:", JSON.stringify(error));
                    // Temporarily avoiding lulu_status update due to PGRST204 cache error
                    // await supabase.from('b2b_orders').update({ lulu_status: 'email_error: ' + error.message }).eq('order_id', orderData.order_id);
                } else {
                    console.log(`✅ Resend: Fulfillment email successfully delivered to ${email}.`, data);
                    // Temporarily avoiding lulu_status update due to PGRST204 cache error
                    // await supabase.from('b2b_orders').update({ lulu_status: 'email_sent' }).eq('order_id', orderData.order_id);
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
                        COMPANY: orderData.company_name,
                        PHONE: orderData.phone,
                        PDF_URL: digitalPdfUrl
                    },
                });
                console.log(`📧 Mailchimp: Upserted ${email} with PDF_URL.`);

                await mailchimp.lists.updateListMemberTags(listId, subscriberHash, {
                    tags: [{ name: 'b2b-delivered', status: 'active' }]
                });
                console.log(`📧 Mailchimp: Tagged ${email} with 'b2b-delivered'.`);
            } catch (mcError) {
                console.error("Mailchimp error:", JSON.stringify(mcError.response ? mcError.response.body : mcError));
            }
        }

        // 2. Supabase Logging
        const { error: supaError } = await supabase
            .from('subscribers')
            .insert([{ 
                email: email, 
                first_name: orderData.company_name, 
                phone: orderData.phone,
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
// ====== MAGNET EXIT INTENT CAPTURE ======
app.post('/api/capture-discount', async (req, res) => {
    try {
        const { firstName, lastName, email } = req.body;
        if (!email || !firstName) {
            return res.status(400).json({ error: 'Missing required fields' });
        }

        const fullName = `${firstName} ${lastName}`.trim();

        // 1. Save to Supabase `users` table as a magnet_lead
        if (supabase) {
            await supabase.from('users').insert({
                email: email,
                username: fullName,
                vertical: 'magnet_lead'
            });
            console.log(`✅ Saved Magnet Lead to Supabase: ${email}`);
        }

        // 2. Add to Mailchimp with Tag
        const listId = process.env.MAILCHIMP_LIST_ID;
        if (listId) {
            const subscriberHash = require('crypto').createHash('md5').update(email.toLowerCase()).digest('hex');
            try {
                await mailchimp.lists.setListMember(listId, subscriberHash, {
                    email_address: email,
                    status_if_new: 'subscribed',
                    merge_fields: {
                        FNAME: firstName,
                        LNAME: lastName || ''
                    }
                });

                await mailchimp.lists.updateListMemberTags(listId, subscriberHash, {
                    tags: [{ name: 'Magnet_Discount_Capture', status: 'active' }]
                });
                console.log(`📧 Added ${email} to Mailchimp with Magnet_Discount_Capture tag.`);
            } catch (mcErr) {
                console.error("Mailchimp error:", mcErr.response ? mcErr.response.body : mcErr);
                // Non-fatal, continue to send email
            }
        }

        // 3. Send 15% Discount Email via Resend
        if (process.env.RESEND_API_KEY) {
            const { Resend } = require('resend');
            const resend = new Resend(process.env.RESEND_API_KEY);
            await resend.emails.send({
                from: '250PROUD <info@250proud.net>',
                to: email,
                subject: 'Your 15% Off Code for 250PROUD Commemorative Magnets!',
                html: `
                    <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #111;">
                        <h1 style="color: #D4AF37;">Welcome to 250PROUD!</h1>
                        <p>Hi ${firstName},</p>
                        <p>Thank you for your interest in our American-made Commemorative Magnets. As promised, here is your 15% off discount code to use at checkout:</p>
                        <div style="background: #f4f4f4; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                            <span style="font-size: 24px; font-weight: bold; letter-spacing: 2px;">PROUD15</span>
                        </div>
                        <p>You can <a href="https://250proud.net/magnet-configurator.html" style="color: #D4AF37; font-weight: bold;">click here to start designing your magnet right now.</a></p>
                        <p>Best,<br>The 250PROUD Team</p>
                    </div>
                `
            });
            console.log(`✉️ Sent discount email to ${email}`);
        }

        res.json({ success: true });
    } catch (err) {
        console.error("Error capturing discount lead:", err);
        res.status(500).json({ success: false, error: "Internal Server Error" });
    }
});

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
        } else if (industry === 'Education') {
            mockHeadline = `Fostering Future Generations. Proudly Supported by ${companyName}.`;
            mockCopy = `Education is the foundation upon which the American spirit thrives. At ${companyName}, we are proud to support the learners and leaders of tomorrow. As we celebrate our 250-year history, we invite you to use this 24-page coloring book in your classroom or home to spark curiosity about the people and events that built our nation.`;
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
            duration = 30,
            guest_timezone = 'America/Chicago'
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
                guest_timezone,
                created_at: new Date().toISOString()
            });
        }

        // Calculate UTC ISO times for Google Calendar link & ICS
        // Self-correct Central Time offset (CDT is -05:00, CST is -06:00)
        let offset = "-05:00";
        try {
            const tempDate = new Date(`${date}T${time}:00-05:00`);
            const formattedTemp = tempDate.toLocaleTimeString("en-US", {
                timeZone: "America/Chicago",
                hour: "2-digit",
                minute: "2-digit",
                hour12: false
            });
            if (formattedTemp !== time) {
                offset = "-06:00";
            }
        } catch (offsetErr) {
            console.error("Offset calculation error:", offsetErr);
        }

        const startDate = new Date(`${date}T${time}:00${offset}`);
        const endDate = new Date(startDate.getTime() + duration * 60 * 1000);
        const startUTC = startDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
        const endUTC = endDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
        const nowUTC = new Date().toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

        function format12HourLocal(time24) {
            const [hours, minutes] = time24.split(':').map(Number);
            const ampm = hours >= 12 ? 'PM' : 'AM';
            const hours12 = hours % 12 || 12;
            return `${hours12}:${String(minutes).padStart(2, '0')} ${ampm}`;
        }

        // Calculate guest and host local date & time display strings
        let guestDisplayTime = '';
        let guestDisplayDate = '';
        let hostDisplayTime = '';
        let hostDisplayDate = '';

        try {
            // Guest formats
            const guestTimeFormatted = startDate.toLocaleTimeString("en-US", {
                timeZone: guest_timezone,
                hour: "numeric",
                minute: "2-digit",
                hour12: true
            });
            const guestDateFormatted = startDate.toLocaleDateString("en-US", {
                timeZone: guest_timezone,
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });
            const guestTZLabel = startDate.toLocaleDateString("en-US", {
                timeZone: guest_timezone,
                timeZoneName: "short"
            }).split(', ').pop() || '';

            guestDisplayTime = `${guestTimeFormatted} (${guestTZLabel})`;
            guestDisplayDate = guestDateFormatted;

            // Host formats (America/Chicago)
            const hostTimeFormatted = startDate.toLocaleTimeString("en-US", {
                timeZone: "America/Chicago",
                hour: "numeric",
                minute: "2-digit",
                hour12: true
            });
            const hostDateFormatted = startDate.toLocaleDateString("en-US", {
                timeZone: "America/Chicago",
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });
            const hostTZLabel = startDate.toLocaleDateString("en-US", {
                timeZone: "America/Chicago",
                timeZoneName: "short"
            }).split(', ').pop() || '';

            hostDisplayTime = `${hostTimeFormatted} (${hostTZLabel})`;
            hostDisplayDate = hostDateFormatted;

        } catch (tzFormatErr) {
            console.error("Timezone display formatting error:", tzFormatErr);
            guestDisplayTime = `${format12HourLocal(time)} (Central Time)`;
            guestDisplayDate = date;
            hostDisplayTime = `${format12HourLocal(time)} (Central Time)`;
            hostDisplayDate = date;
        }

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
                                <tr><td style="padding: 10px; font-weight: bold;">Date:</td><td style="padding: 10px;">${guestDisplayDate}</td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Time:</td><td style="padding: 10px;">${guestDisplayTime}${guest_timezone.toLowerCase() !== 'america/chicago' ? ` / ${hostDisplayTime}` : ''}</td></tr>
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
                    subject: `[New Booking] ${guest_name} - ${date} @ ${format12HourLocal(time)} CT`,
                    html: `
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eaeaea; border-radius: 8px;">
                            <h2 style="color: #B31942; border-bottom: 2px solid #0A3161; padding-bottom: 10px;">New Meeting Booked</h2>
                            <p>A new meeting has been scheduled on your LauralAI calendar.</p>
                            
                            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold; width: 120px;">Guest Name:</td><td style="padding: 10px;">${guest_name}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Guest Email:</td><td style="padding: 10px;"><a href="mailto:${guest_email}">${guest_email}</a></td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Phone:</td><td style="padding: 10px;">${guest_phone || 'N/A'}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Company:</td><td style="padding: 10px;">${guest_company || 'N/A'}</td></tr>
                                <tr style="background: #f8f9fa;"><td style="padding: 10px; font-weight: bold;">Date:</td><td style="padding: 10px;">${hostDisplayDate}${guestDisplayDate !== hostDisplayDate ? ` (Guest Local: ${guestDisplayDate})` : ''}</td></tr>
                                <tr><td style="padding: 10px; font-weight: bold;">Time:</td><td style="padding: 10px;">${hostDisplayTime}${guest_timezone.toLowerCase() !== 'america/chicago' ? ` (Guest Local: ${guestDisplayTime})` : ''}</td></tr>
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

// ---------------------------------------------------------
// Chatbot Route (LauralAI)
// ---------------------------------------------------------
app.post('/api/chat', async (req, res) => {
    try {
        const { messages } = req.body;
        
        if (!process.env.GEMINI_API_KEY) {
            return res.status(500).json({ error: "Gemini API key is not configured." });
        }

        // Dynamically load the knowledge base markdown to support live updates
        let supportKb = "";
        try {
            const kbPath = path.join(__dirname, 'lauralai_knowledge_base.md');
            if (fs.existsSync(kbPath)) {
                supportKb = fs.readFileSync(kbPath, 'utf8');
            }
        } catch (kbErr) {
            console.error("Error reading lauralai_knowledge_base.md:", kbErr);
        }

        const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
        
        const systemInstruction = `You are LauralAI, an expert digital support agent and proactive sales/growth partner for the 250PROUD platform. Your primary job is to help business partners (real estate agents, brokers, mortgage lenders, etc.) use their custom co-branded coloring books ("250 Strong: Built By Hand") and custom patriotic magnets to generate leads, build relationships, and drive local business growth.

Here is your official corporate Knowledge Base, Product Guide, and FAQ:
${supportKb || "Product: 250PROUD custom co-branded coloring books and marketing materials."}

Adhere to these conversational directives:
1. Always maintain a professional, patriotic, warm, and highly encouraging tone.
2. Provide direct, helpful answers to user questions using details from the Knowledge Base above. Avoid giving out the email address (info@250proud.net) unless it is a highly complex technical issue or custom order modification request.
3. Be commercially proactive. If a user asks about co-branding, pricing, or templates, answer them clearly, then encourage them to upload their logo on the B2B Configurator (b2b-configurator.html) or book a strategy call on our calendar. Keep it natural, conversational, and high-value.`;

        // Format history for Gemini
        const history = [];
        let latestUserMsg = "Hello";

        if (messages && messages.length > 0) {
            latestUserMsg = messages[messages.length - 1].content;
            
            // Map previous messages (excluding the last one which is the prompt)
            for (let i = 0; i < messages.length - 1; i++) {
                const msg = messages[i];
                history.push({
                    role: msg.role === 'assistant' ? 'model' : 'user',
                    parts: [{ text: msg.content }]
                });
            }
        }

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: [
                ...history,
                { role: 'user', parts: [{ text: latestUserMsg }] }
            ],
            config: {
                systemInstruction: systemInstruction,
                temperature: 0.7
            }
        });

        res.json({ reply: response.text });

    } catch (e) {
        console.error("LauralAI Chat Error:", e);
        res.status(500).json({ error: "Failed to generate a response. Please try again or email info@250proud.net." });
    }
});

// ==========================================
// BLOG API ROUTES
// ==========================================

// --- PUBLIC ROUTES ---
app.get('/rss.xml', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('blog_posts')
            .select('*')
            .order('published_at', { ascending: false })
            .limit(20);
        if (error) throw error;

        let rss = `<?xml version="1.0" encoding="UTF-8" ?>
<?xml-stylesheet href="/rss-style.xsl" type="text/xsl"?>
<rss version="2.0">
<channel>
    <title>250Proud Journal</title>
    <link>https://250proud.net/blog.html</link>
    <description>News, insights, and stories celebrating 250 years of American heritage.</description>
`;
        for (const post of data) {
            rss += `
    <item>
        <title><![CDATA[${post.title}]]></title>
        <link>https://250proud.net/post.html?slug=${post.slug}</link>
        <description><![CDATA[${post.content.substring(0, 300)}...]]></description>
        <pubDate>${new Date(post.published_at).toUTCString()}</pubDate>
        <guid>https://250proud.net/post.html?slug=${post.slug}</guid>
    </item>`;
        }
        rss += `
</channel>
</rss>`;

        res.set('Content-Type', 'text/xml');
        res.send(rss);
    } catch (err) {
        console.error("RSS Error:", err);
        res.status(500).send("Error generating RSS feed");
    }
});
app.get('/api/blog/posts', async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('blog_posts')
            .select('slug, title, hero_image_url, published_at')
            .order('published_at', { ascending: false });
        if (error) throw error;
        res.json(data);
    } catch (err) {
        console.error("Blog Posts Error:", err);
        res.status(500).json({ error: "Failed to fetch posts" });
    }
});

app.get('/api/blog/posts/:slug', async (req, res) => {
    try {
        const { data: post, error: postError } = await supabase
            .from('blog_posts')
            .select('*')
            .eq('slug', req.params.slug)
            .single();
        if (postError) throw postError;

        const { data: comments, error: commentsError } = await supabase
            .from('blog_comments')
            .select('author_name, content, created_at')
            .eq('post_id', post.id)
            .eq('approved', true)
            .order('created_at', { ascending: true });
        if (commentsError) throw commentsError;

        res.json({ post, comments });
    } catch (err) {
        console.error("Blog Post Error:", err);
        res.status(500).json({ error: "Failed to fetch post" });
    }
});

app.post('/api/blog/subscribe', express.json(), async (req, res) => {
    try {
        const { email } = req.body;
        const { error } = await supabase.from('blog_subscribers').insert([{ email }]);
        if (error && error.code !== '23505') throw error; // Ignore unique constraint error
        res.json({ success: true });
    } catch (err) {
        console.error("Subscribe Error:", err);
        res.status(500).json({ error: "Failed to subscribe" });
    }
});

app.post('/api/blog/comment', express.json(), async (req, res) => {
    try {
        const { post_id, author_name, author_email, content } = req.body;
        const { error } = await supabase.from('blog_comments').insert([{
            post_id, author_name, author_email, content
        }]);
        if (error) throw error;
        res.json({ success: true });
    } catch (err) {
        console.error("Comment Error:", err);
        res.status(500).json({ error: "Failed to submit comment" });
    }
});

// --- ADMIN ROUTES ---
const adminAuth = (req, res, next) => {
    const token = req.headers.authorization;
    if (token === 'Lauralai2026') return next();
    res.status(401).json({ error: "Unauthorized" });
};

app.post('/api/admin/blog/post', adminAuth, express.json(), async (req, res) => {
    try {
        const { title, slug, hero_image_url, content } = req.body;
        const { error } = await supabase.from('blog_posts').upsert({
            title, slug, hero_image_url, content
        }, { onConflict: 'slug' });
        if (error) throw error;
        res.json({ success: true });
    } catch (err) {
        console.error("Create Post Error:", err);
        res.status(500).json({ error: "Failed to save post" });
    }
});

app.get('/api/admin/blog/comments', adminAuth, async (req, res) => {
    try {
        const { data, error } = await supabase
            .from('blog_comments')
            .select('*, blog_posts(title)')
            .eq('approved', false)
            .order('created_at', { ascending: false });
        if (error) throw error;
        res.json(data);
    } catch (err) {
        console.error("Fetch Comments Error:", err);
        res.status(500).json({ error: "Failed to fetch pending comments" });
    }
});

app.post('/api/admin/blog/comments/:id/approve', adminAuth, async (req, res) => {
    try {
        const { error } = await supabase.from('blog_comments').update({ approved: true }).eq('id', req.params.id);
        if (error) throw error;
        res.json({ success: true });
    } catch (err) {
        console.error("Approve Comment Error:", err);
        res.status(500).json({ error: "Failed to approve comment" });
    }
});

app.get('/api/briefings', async (req, res) => {
    try {
        const briefingsDir = path.join(__dirname, '..', 'board_comms', 'briefings');
        
        if (!fs.existsSync(briefingsDir)) {
            return res.json([]);
        }
        
        const files = fs.readdirSync(briefingsDir);
        const briefings = [];
        
        for (const file of files) {
            if (file.startsWith('briefing_') && file.endsWith('.md')) {
                const filePath = path.join(briefingsDir, file);
                const content = fs.readFileSync(filePath, 'utf8');
                
                const dateMatch = file.match(/briefing_(\d{4}-\d{2}-\d{2})\.md/);
                const date = dateMatch ? dateMatch[1] : null;
                
                // Try to find subject in frontmatter, subject headers, or email lines
                const subjectMatch = content.match(/Subject:\s*(.*)/i) || content.match(/#\s*(.*)/);
                const subject = subjectMatch ? subjectMatch[1].replace(/#+\s*/, '').trim() : `Daily Briefing - ${date}`;
                
                briefings.push({
                    filename: file,
                    date: date,
                    subject: subject,
                    content: content
                });
            }
        }
        
        briefings.sort((a, b) => {
            if (!a.date) return 1;
            if (!b.date) return -1;
            return b.date.localeCompare(a.date);
        });
        
        res.json(briefings);
    } catch (err) {
        console.error("Get Briefings Error:", err);
        res.status(500).json({ error: "Failed to retrieve briefings" });
    }
});

app.post('/api/blueprint/subscribe', express.json(), async (req, res) => {
    try {
        const { email, name, brokerage, phone } = req.body;
        if (!email) {
            return res.status(400).json({ error: "Email is required" });
        }
        
        // Strict Backend Validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return res.status(400).json({ error: "Invalid email format" });
        }
        
        if (phone) {
            const numericPhone = phone.replace(/\D/g, '');
            if (numericPhone.length < 10) {
                return res.status(400).json({ error: "Invalid phone number format" });
            }
        }

        // Calculate Sequential Member Number
        let memberNumber = 79;
        try {
            const supaUrl = process.env.SUPABASE_URL || 'https://iohdigyivypgyphcliuo.supabase.co';
            const supaKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_ANON_KEY;
            const resCount = await fetch(`${supaUrl}/rest/v1/subscribers?select=id`, {
                headers: {
                    'apikey': supaKey,
                    'Authorization': `Bearer ${supaKey}`,
                    'Prefer': 'count=exact',
                    'Range': '0-0'
                }
            });
            const contentRange = resCount.headers.get('content-range');
            if (contentRange && contentRange.includes('/')) {
                const totalRows = parseInt(contentRange.split('/')[1], 10);
                if (!isNaN(totalRows) && totalRows > 0) {
                    memberNumber = totalRows + 1;
                }
            }
        } catch (cntErr) {
            console.warn("Could not query waitlist count, defaulting memberNumber to 79:", cntErr.message);
        }

        try {
            await supabase.from('subscribers').insert([{
                first_name: name || null,
                email: email.toLowerCase().trim(),
                phone: phone || null,
                comm_pref: 'email',
                source: 'agent_blueprint_founding_member',
            }]);
        } catch (dbErr) {
            console.error("Supabase connection error, continuing to Mailchimp & Resend:", dbErr.message);
        }

        // Mailchimp Integration
        if (process.env.MAILCHIMP_API_KEY && process.env.MAILCHIMP_API_KEY !== 'missing_key') {
            const listId = process.env.MAILCHIMP_LIST_ID;
            const subscriberHash = crypto.createHash('md5').update(email.toLowerCase().trim()).digest('hex');
            
            try {
                await mailchimp.lists.setListMember(listId, subscriberHash, {
                    email_address: email.toLowerCase().trim(),
                    status_if_new: 'subscribed',
                    merge_fields: {
                        FNAME: name ? name.split(' ')[0] : '',
                        LNAME: name && name.split(' ').length > 1 ? name.split(' ').slice(1).join(' ') : '',
                        COMPANY: brokerage || '',
                        PHONE: phone || '',
                        MEMBER_NUM: memberNumber
                    }
                });

                await mailchimp.lists.updateListMemberTags(listId, subscriberHash, {
                    tags: [
                        { name: 'Founding Spot Secured', status: 'active' },
                        { name: 'agent-blueprint-waitlist', status: 'active' },
                        { name: 'founding-member-launch', status: 'active' }
                    ]
                });
                console.log(`📧 Mailchimp: Successfully subscribed & tagged ${email} for Agent Blueprint (Founding Spot Secured).`);
            } catch (mcError) {
                console.error("Mailchimp Sync Error for Agent Blueprint:", mcError.response?.body?.detail || mcError.message);
            }
        }

        // Resend Integration — Immediate Founding Member Welcome Email
        if (process.env.RESEND_API_KEY) {
            try {
                const resend = new Resend(process.env.RESEND_API_KEY);
                const firstName = name && name.trim() ? name.trim().split(' ')[0] : 'there';
                
                let htmlTemplate = '';
                const templatePathLocal = path.join(__dirname, 'emails', 'agent_blueprint_founding_member_welcome.html');
                const templatePathParent = path.join(__dirname, '..', 'emails', 'agent_blueprint_founding_member_welcome.html');
                if (fs.existsSync(templatePathLocal)) {
                    htmlTemplate = fs.readFileSync(templatePathLocal, 'utf8');
                } else if (fs.existsSync(templatePathParent)) {
                    htmlTemplate = fs.readFileSync(templatePathParent, 'utf8');
                } else {
                    htmlTemplate = `
                        <div style="font-family: sans-serif; background-color: #0a0a0a; color: #fff; padding: 30px;">
                            <h2>Founding Member #${memberNumber}</h2>
                            <p>Hey ${firstName},</p>
                            <p>Thanks for grabbing founding spot #${memberNumber} in Agent Blueprint!</p>
                            <p>Your Founder Code: <strong>AB-FOUNDER-2026</strong></p>
                            <p>Reply to this email with your AI experience level (1-10).</p>
                            <p>- Mike Price, Founder Lauralai LLC</p>
                        </div>
                    `;
                }

                const formattedHtml = htmlTemplate
                    .replace(/\{\{MEMBER_NUMBER\}\}/g, memberNumber)
                    .replace(/\{\{FIRST_NAME\}\}/g, firstName);

                await resend.emails.send({
                    from: 'Mike Price | Agent Blueprint <info@250proud.net>',
                    reply_to: 'mike@lauralai.llc',
                    to: email.toLowerCase().trim(),
                    subject: "You're in. Here's what happens next.",
                    html: formattedHtml
                });
                console.log(`✉️ Resend: Founding member welcome email sent to ${email} (Member #${memberNumber}).`);

                // Send Internal Notification to Mike
                await resend.emails.send({
                    from: 'Agent Blueprint System <info@250proud.net>',
                    to: 'mike@lauralai.llc',
                    subject: `🚀 New Agent Blueprint Founding Member #${memberNumber}: ${name || email}`,
                    html: `
                        <h2>🎉 New Agent Blueprint Founding Member Signed Up!</h2>
                        <p><strong>Member Number:</strong> #${memberNumber}</p>
                        <p><strong>Name:</strong> ${name || 'Not provided'}</p>
                        <p><strong>Email:</strong> ${email}</p>
                        <p><strong>Brokerage:</strong> ${brokerage || 'Not provided'}</p>
                        <p><strong>Phone:</strong> ${phone || 'Not provided'}</p>
                        <p><em>Welcome email sent automatically via Resend.</em></p>
                    `
                });
            } catch (resendErr) {
                console.error("Resend Welcome Email Error:", resendErr.message || resendErr);
            }
        }

        res.json({ success: true, memberNumber });
    } catch (err) {
        console.error("Blueprint Subscribe Endpoint Error:", err);
        res.status(500).json({ error: "Failed to submit subscription", details: err.message });
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

// ---------------------------------------------------------
// Magnet PDF Generation Pipeline
// ---------------------------------------------------------
async function generateMagnetPDF(orderData) {
    console.log(`Starting Magnet PDF generation for order: ${orderData.order_id}`);
    
    // Default to portrait if not specified
    const orientation = orderData.headline || 'portrait';
    const isLandscape = orientation === 'landscape';
    
    // Exact sizing at 300 DPI
    const widthInches = isLandscape ? 4.202 : 3.204;
    const heightInches = isLandscape ? 3.204 : 4.202;
    const qrUrl = orderData.website || 'https://250proud.net';
    const message = orderData.copy || 'Proudly supporting our community!';

    const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
        <style>
            @page { margin: 0; size: ${widthInches}in ${heightInches}in; }
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; }
            .magnet-container {
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                background: white;
                position: relative;
                overflow: hidden;
            }
            .bleed-top, .bleed-bottom {
                height: 0.35in;
                background: #111;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 8pt;
                font-family: 'Inter', sans-serif;
                letter-spacing: 2px;
                width: 100%;
            }
            .bleed-top { transform: rotate(180deg); }
            .safe-zone {
                flex: 1;
                display: flex;
                background: white;
            }
            .col-left {
                background-color: #ddd;
                background-image: url('${orderData.hero_path || 'https://via.placeholder.com/400x600'}');
                background-size: cover;
                background-position: center;
                border-right: 2px solid #fff;
            }
            .col-right {
                padding: 0.15in;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                background: #f8f9fa;
            }
            
            /* Portrait vs Landscape Layout */
            ${isLandscape 
                ? `.col-left { width: 45%; height: 100%; } .col-right { width: 55%; height: 100%; }`
                : `.col-left { width: 55%; height: 100%; } .col-right { width: 45%; height: 100%; }`
            }

            .realtor-name { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 16pt; margin-bottom: 2px; line-height: 1.1; word-wrap: break-word; color: #0a1122; }
            .realtor-company { font-family: 'Inter', sans-serif; font-weight: 600; font-size: 10pt; color: #b31942; margin-bottom: 6px; line-height: 1.1; text-transform: uppercase; }
            .realtor-phone { font-family: 'Inter', sans-serif; font-size: 10pt; color: #333; font-weight: 500; margin-bottom: 8px; }
            .realtor-message { font-family: 'Inter', sans-serif; font-size: 9pt; color: #555; font-style: italic; line-height: 1.3; }

            .qr-container { align-self: flex-end; margin-top: 5px; border: 1px solid #ddd; padding: 4px; background: white; border-radius: 4px; }
            .qr-container img { width: 0.85in; height: 0.85in; display: block; }
        </style>
    </head>
    <body>
        <div class="magnet-container">
            <div class="bleed-top">250PROUD.NET</div>
            <div class="safe-zone">
                <div class="col-left"></div>
                <div class="col-right">
                    <div>
                        <div class="realtor-name">${orderData.email.split('@')[0]}</div>
                        <div class="realtor-company">${orderData.company_name || ''}</div>
                        <div class="realtor-phone">${orderData.phone || ''}</div>
                        <div class="realtor-message">${message}</div>
                    </div>
                    <div class="qr-container">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(qrUrl)}" alt="QR Code">
                    </div>
                </div>
            </div>
            <div class="bleed-bottom">250PROUD.NET - ORDER #${orderData.order_id.substring(0,8).toUpperCase()}</div>
        </div>
    </body>
    </html>
    `;

    const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
    const page = await browser.newPage();
    
    // Wait for network idle to ensure fonts and QR code image load
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
    
    const pdfBuffer = await page.pdf({
        width: `${widthInches}in`,
        height: `${heightInches}in`,
        printBackground: true,
        pageRanges: '1'
    });

    await browser.close();

    // Upload to Supabase
    const fileName = `magnet_${orderData.order_id}.pdf`;
    const { data: uploadData, error: uploadError } = await supabase.storage
        .from('b2b_pdfs')
        .upload(`final/${fileName}`, pdfBuffer, { contentType: 'application/pdf', upsert: true });

    if (uploadError) {
        console.error("Magnet PDF Upload Error:", uploadError);
        return;
    }

    const { data: publicUrlData } = supabase.storage.from('b2b_pdfs').getPublicUrl(`final/${fileName}`);
    const finalPdfUrl = publicUrlData.publicUrl;

    console.log(`✅ Magnet PDF generated and uploaded: ${finalPdfUrl}`);

    // Update database status
    await supabase.from('b2b_orders').update({
        status: 'completed',
        pdf_url: finalPdfUrl
    }).eq('order_id', orderData.order_id);
}
