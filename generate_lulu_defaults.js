const fs = require('fs');
const { PDFDocument } = require('pdf-lib');
const puppeteer = require('puppeteer-core');
const path = require('path');

async function run() {
    console.log("Loading base book...");
    const mainBookPath = path.join(__dirname, '250Proud_ColoringBook_B2B_Base_Final.pdf');
    const mainPdfBytes = fs.readFileSync(mainBookPath);
    const mainPdfDoc = await PDFDocument.load(mainPdfBytes);

    console.log("Generating default back cover...");
    const templatePath = path.join(__dirname, 'back_cover_template.html');
    let htmlTemplate = fs.readFileSync(templatePath, 'utf8');
    
    htmlTemplate = htmlTemplate.replace(/{{COMPANY_NAME}}/g, '250PROUD');
    htmlTemplate = htmlTemplate.replace('{{WEBSITE}}', 'www.250proud.com');
    htmlTemplate = htmlTemplate.replace('{{PHONE}}', '');
    htmlTemplate = htmlTemplate.replace('{{EMAIL}}', 'info@250proud.com');
    htmlTemplate = htmlTemplate.replace('{{HEADLINE}}', 'Built By Hand.');
    htmlTemplate = htmlTemplate.replace('{{COPY}}', 'Celebrate the history and heroes of the land we love.');
    htmlTemplate = htmlTemplate.replace('{{LOGO_URL}}', 'https://iohdigyivypgyphcliuo.supabase.co/storage/v1/object/public/b2b_pdfs/uploads/bef80dff-ef51-4ac2-9f31-52e14347f186.png'); // Valid Sotheby's logo or similar
    htmlTemplate = htmlTemplate.replace('{{HEADSHOT_URL}}', '');
    htmlTemplate = htmlTemplate.replace('{{HEADSHOT_DISPLAY}}', 'none');
    htmlTemplate = htmlTemplate.replace('{{HERO_URL}}', 'https://iohdigyivypgyphcliuo.supabase.co/storage/v1/object/public/b2b_pdfs/uploads/2f6fee84-9d02-4fa1-840a-0708917899c2.jpg');
    htmlTemplate = htmlTemplate.replace('{{INTERIOR_URL}}', 'https://iohdigyivypgyphcliuo.supabase.co/storage/v1/object/public/b2b_pdfs/uploads/2d7ca5df-95e2-495b-a9d9-2ef74d02e723.jpg');

    const browser = await puppeteer.launch({
        executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless: "new"
    });

    const page = await browser.newPage();
    await page.setContent(htmlTemplate, { waitUntil: 'load' });
    const backCoverPdfBuffer = await page.pdf({
        format: 'Letter',
        printBackground: true,
        margin: { top: '0', right: '0', bottom: '0', left: '0' }
    });
    await browser.close();

    console.log("Generating Lulu Formats...");
    // 1. Lulu Interior
    const luluInteriorDoc = await PDFDocument.create();
    const interiorPages = await luluInteriorDoc.copyPages(mainPdfDoc, Array.from({length: 22}, (_, i) => i + 1));
    interiorPages.forEach(p => luluInteriorDoc.addPage(p));
    const luluInteriorBuffer = await luluInteriorDoc.save();
    fs.writeFileSync('Lulu_Default_Interior.pdf', luluInteriorBuffer);
    console.log("Saved Lulu_Default_Interior.pdf");

    // 2. Lulu Wraparound Cover
    const luluCoverDoc = await PDFDocument.create();
    const wrapPage = luluCoverDoc.addPage([1224, 792]);
    const [embeddedFront] = await luluCoverDoc.embedPdf(mainPdfBytes, [0]);
    const [embeddedBack] = await luluCoverDoc.embedPdf(backCoverPdfBuffer, [0]);
    
    wrapPage.drawPage(embeddedBack, { x: 0, y: 0, width: 612, height: 792 });
    wrapPage.drawPage(embeddedFront, { x: 612, y: 0, width: 612, height: 792 });
    
    const luluCoverBuffer = await luluCoverDoc.save();
    fs.writeFileSync('Lulu_Default_Cover_v2.pdf', luluCoverBuffer);
    console.log("Saved Lulu_Default_Cover_v2.pdf");
}
run().catch(console.error);
