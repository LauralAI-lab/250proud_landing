require('dotenv').config();
const { PDFDocument } = require('pdf-lib');
const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium');
const fs = require('fs');
const path = require('path');
const QRCode = require('qrcode');

async function testPipeline() {
    let browser = null;
    try {
        const order = {
            order_id: 'debug-local-999',
            company_name: 'Debug LLC',
            phone: '555-555-5555',
            email: 'test@debug.com',
            website: 'www.debug.com',
            headline: 'Debug Built on Grit',
            copy: 'Debug testing email copy.',
            logo_path: null,
            headshot_path: null,
            hero_path: null,
            interior_path: null
        };

        const templatePath = path.join(__dirname, 'back_cover_template.html');
        let htmlTemplate = fs.readFileSync(templatePath, 'utf8');

        htmlTemplate = htmlTemplate.replace('{{COMPANY_NAME}}', order.company_name);
        htmlTemplate = htmlTemplate.replace('{{WEBSITE}}', order.website);
        htmlTemplate = htmlTemplate.replace('{{PHONE}}', order.phone);
        htmlTemplate = htmlTemplate.replace('{{EMAIL}}', order.email);
        htmlTemplate = htmlTemplate.replace('{{HEADLINE}}', order.headline);
        htmlTemplate = htmlTemplate.replace('{{COPY}}', order.copy);
        
        htmlTemplate = htmlTemplate.replace('{{LOGO_URL}}', 'https://via.placeholder.com/300x150.png?text=YOUR+LOGO');
        htmlTemplate = htmlTemplate.replace('{{HEADSHOT_URL}}', 'https://via.placeholder.com/200x200.png?text=YOUR+PHOTO');
        htmlTemplate = htmlTemplate.replace('{{HEADSHOT_DISPLAY}}', 'none');
        htmlTemplate = htmlTemplate.replace('{{HERO_URL}}', 'https://via.placeholder.com/600x400.png?text=YOUR+HERO+IMAGE');
        htmlTemplate = htmlTemplate.replace('{{INTERIOR_URL}}', 'https://via.placeholder.com/400x500.png?text=INTERIOR+PREVIEW');

        console.log("Launching headless browser...");
        browser = await puppeteer.launch({
            args: chromium.args,
            defaultViewport: chromium.defaultViewport,
            executablePath: await chromium.executablePath(),
            headless: chromium.headless,
        });

        const page = await browser.newPage();
        await page.setContent(htmlTemplate, { waitUntil: 'networkidle0' });
        
        const backCoverPdfBuffer = await page.pdf({
            format: 'Letter',
            printBackground: true,
            margin: { top: '0', right: '0', bottom: '0', left: '0' }
        });

        console.log("Merging customized back cover with main book...");
        const mainBookPath = path.join(__dirname, '250Proud_ColoringBook_B2B_Base_Final.pdf');
        const mainPdfBytes = fs.readFileSync(mainBookPath);
        const mainPdfDoc = await PDFDocument.load(mainPdfBytes);
        const backCoverPdfDoc = await PDFDocument.load(backCoverPdfBuffer);
        
        const [backCoverPage] = await mainPdfDoc.copyPages(backCoverPdfDoc, [0]);
        mainPdfDoc.addPage(backCoverPage);

        const finalPdfBytes = await mainPdfDoc.save();
        fs.writeFileSync('debug-local-final.pdf', finalPdfBytes);
        console.log("✅ Wrote debug-local-final.pdf!");

        // Marketing Card
        const qrCodeDataUri = await QRCode.toDataURL("https://example.com/download.pdf", {
            color: { dark: '#000000', light: '#FFFFFF' },
            margin: 1,
            width: 800
        });

        const cardTemplatePath = path.join(__dirname, 'marketing_card_template.html');
        let cardHtmlTemplate = fs.readFileSync(cardTemplatePath, 'utf8');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{COMPANY_NAME}}', order.company_name);
        cardHtmlTemplate = cardHtmlTemplate.replace('{{LOGO_URL}}', '');
        cardHtmlTemplate = cardHtmlTemplate.replace('{{QR_CODE_DATA_URI}}', qrCodeDataUri);

        const cardPage = await browser.newPage();
        await cardPage.setContent(cardHtmlTemplate, { waitUntil: 'networkidle0' });

        const cardPdfBuffer = await cardPage.pdf({
            width: '3.75in',
            height: '2.25in',
            printBackground: true,
            margin: { top: '0', right: '0', bottom: '0', left: '0' }
        });
        
        fs.writeFileSync('debug-local-card.pdf', cardPdfBuffer);
        console.log("✅ Wrote debug-local-card.pdf!");

        await browser.close();
        console.log("Debug Pipeline Finished!");

    } catch (e) {
        console.error("ERROR:", e);
        if (browser) await browser.close();
    }
}

testPipeline();
