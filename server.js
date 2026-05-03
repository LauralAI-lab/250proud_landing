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

const app = express();
app.use(cors());
// IMPORTANT: Keep raw body for webhook verification if needed in the future
app.use('/api/shopify/webhook', express.json());
app.use(express.json());

// Init Supabase
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

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
                email: data.email,
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

        // Redirect to Shopify Cart Permalink
        const shopifyVariantId = "8694513828039"; 
        const checkoutUrl = `https://lauralai-one.myshopify.com/cart/${shopifyVariantId}:1?attributes[order_id]=${orderId}`;

        res.json({ success: true, orderId: orderId, checkoutUrl: checkoutUrl });

    } catch (err) {
        console.error("Error creating checkout session:", err);
        res.status(500).json({ error: 'Failed to create checkout session', details: err.message });
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

        if (orderData.status === 'completed') {
            return res.status(200).send('Already processed');
        }

        // Start PDF generation asynchronously so we can return 200 OK to Shopify instantly
        res.status(200).json({ success: true, message: 'Webhook received, generating PDF.' });

        generateAndDeliverPDF(orderData).catch(err => console.error("PDF Generation Pipeline failed:", err));

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
        htmlTemplate = htmlTemplate.replace('{{COMPANY_NAME}}', order.company_name || 'Your Company LLC');
        htmlTemplate = htmlTemplate.replace('{{WEBSITE}}', order.website || 'www.yourwebsite.com');
        htmlTemplate = htmlTemplate.replace('{{PHONE}}', order.phone || '555-0198');
        htmlTemplate = htmlTemplate.replace('{{HEADLINE}}', order.headline || 'Built on Grit.');
        htmlTemplate = htmlTemplate.replace('{{COPY}}', order.copy || 'Thank you for supporting American values.');
        
        // Inject images (Base64 or external URLs)
        htmlTemplate = htmlTemplate.replace('{{LOGO_SRC}}', order.logo_path || 'https://via.placeholder.com/300x150.png?text=YOUR+LOGO');
        htmlTemplate = htmlTemplate.replace('{{HEADSHOT_SRC}}', order.headshot_path || 'https://via.placeholder.com/200x200.png?text=YOUR+PHOTO');
        htmlTemplate = htmlTemplate.replace('{{HERO_SRC}}', order.hero_path || 'https://via.placeholder.com/600x400.png?text=YOUR+HERO+IMAGE');
        htmlTemplate = htmlTemplate.replace('{{INTERIOR_SRC}}', order.interior_path || 'https://via.placeholder.com/400x500.png?text=INTERIOR+PREVIEW');

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
        await page.setContent(htmlTemplate, { waitUntil: 'networkidle0' });

        const backCoverPdfBuffer = await page.pdf({
            format: 'Letter',
            printBackground: true,
            margin: { top: '0', right: '0', bottom: '0', left: '0' }
        });
        await browser.close();

        console.log("Merging customized back cover with main book...");
        const mainBookPath = path.join(__dirname, '250Proud_ColoringBook_2026_v1.pdf');
        const mainPdfBytes = fs.readFileSync(mainBookPath);
        const mainPdfDoc = await PDFDocument.load(mainPdfBytes);
        const backCoverPdfDoc = await PDFDocument.load(backCoverPdfBuffer);
        
        const [backCoverPage] = await mainPdfDoc.copyPages(backCoverPdfDoc, [0]);
        mainPdfDoc.removePage(mainPdfDoc.getPageCount() - 1);
        mainPdfDoc.addPage(backCoverPage);

        const finalPdfBytes = await mainPdfDoc.save();
        const finalPdfBuffer = Buffer.from(finalPdfBytes);

        console.log("Uploading final PDF to Supabase...");
        const pdfFileName = `250Proud_Custom_${order.order_id}.pdf`;
        
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

        // Update Order Status
        await supabase.from('b2b_orders').update({ status: 'completed' }).eq('order_id', order.order_id);

        // 1. Mailchimp Integration
        const email = order.email;
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
        const { companyName } = req.body;
        const options = {
            method: 'POST',
            headers: {
                'xi-api-key': process.env.ELEVENLABS_API_KEY,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: `You are an expert copywriter... [Shortened for brevity] ... Company: ${companyName}`,
                agent_id: "default" 
            })
        };
        // Simulated response for now since Elevenlabs conversational AI endpoint isn't fully set up here.
        // The frontend will receive this mock for now, or you can restore the real fetch.
        const mockCopy = `For 250 years, this country has been sustained by those who wake up early, work hard, and put family first. At ${companyName}, we share those exact values. That's why we're thrilled to gift you '250 Strong, Built By Hand'. This exclusive 24-page collection features beautifully detailed illustrations of American history and local heroes. Print it out, grab some colored pencils, and take a moment to reflect on the freedoms we cherish.`;

        res.json({ headline: `Built on Grit. Proudly Supported by ${companyName}.`, copy: mockCopy });
    } catch (err) {
        console.error("Copy generation failed:", err);
        res.status(500).json({ error: 'Failed to generate copy' });
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
