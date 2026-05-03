const puppeteer = require('puppeteer');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');
const path = require('path');

async function generateCustomBook(data, logoPath, headshotPath, heroPath, interiorPath) {
    let browser = null;
    let tempHtmlPath = null;
    try {
        console.log("Starting PDF generation pipeline...");
        
        // 0. Inject Data into HTML
        const templatePath = path.resolve(__dirname, 'back_cover_template.html');
        let htmlContent = fs.readFileSync(templatePath, 'utf8');
        
        const logoUrl = logoPath ? `file://${logoPath}` : 'https://placehold.co/400x150/e0e0e0/555555?text=Replace+Logo+Here';
        const headshotUrl = headshotPath ? `file://${headshotPath}` : '';
        const headshotDisplay = headshotPath ? 'block' : 'none';
        const heroUrl = heroPath ? `file://${heroPath}` : 'nc_assets/img/configurator/agent_exterior_home.jpeg';
        const interiorUrl = interiorPath ? `file://${interiorPath}` : 'nc_assets/img/configurator/agent_interior_home.jpeg';

        htmlContent = htmlContent.replace(/{{COMPANY_NAME}}/g, data.companyName || 'Your Company Name');
        htmlContent = htmlContent.replace(/{{PHONE}}/g, data.phone || '(555) 012-3456');
        htmlContent = htmlContent.replace(/{{EMAIL}}/g, data.email || 'example@example.com');
        htmlContent = htmlContent.replace(/{{WEBSITE}}/g, data.website || 'Your website address');
        htmlContent = htmlContent.replace(/{{HEADLINE}}/g, data.headline || 'Your headline here');
        htmlContent = htmlContent.replace(/{{COPY}}/g, data.copy || 'Replace this paragraph with your copy here.');
        htmlContent = htmlContent.replace(/{{LOGO_URL}}/g, logoUrl);
        htmlContent = htmlContent.replace(/{{HEADSHOT_URL}}/g, headshotUrl);
        htmlContent = htmlContent.replace(/{{HEADSHOT_DISPLAY}}/g, headshotDisplay);
        htmlContent = htmlContent.replace(/{{HERO_URL}}/g, heroUrl);
        htmlContent = htmlContent.replace(/{{INTERIOR_URL}}/g, interiorUrl);

        tempHtmlPath = path.resolve(__dirname, `temp_back_cover_${Date.now()}.html`);
        fs.writeFileSync(tempHtmlPath, htmlContent);

        // 1. Render HTML to PDF
        console.log("Launching headless browser...");
        browser = await puppeteer.launch({ headless: 'new' });
        const page = await browser.newPage();
        
        console.log(`Loading HTML from: ${tempHtmlPath}`);
        await page.goto(`file://${tempHtmlPath}`, { waitUntil: 'networkidle0' });
        
        console.log("Rendering HTML to PDF...");
        const backCoverPdfBytes = await page.pdf({
            format: 'Letter',
            printBackground: true,
            margin: { top: 0, right: 0, bottom: 0, left: 0 }
        });
        
        await browser.close();
        browser = null;
        
        // Clean up temp HTML
        if (fs.existsSync(tempHtmlPath)) fs.unlinkSync(tempHtmlPath);

        // 2. Merge PDFs
        console.log("Loading main coloring book PDF...");
        const mainBookPath = path.resolve(__dirname, 'coloring_book', '250Proud_ColoringBook_B2B_Base.pdf');
        
        if (!fs.existsSync(mainBookPath)) {
            throw new Error(`Main book PDF not found at ${mainBookPath}`);
        }
        
        const mainPdfBytes = fs.readFileSync(mainBookPath);
        
        console.log("Merging customized back cover...");
        const mainPdfDoc = await PDFDocument.load(mainPdfBytes);
        const backCoverPdfDoc = await PDFDocument.load(backCoverPdfBytes);
        
        const [backCoverPage] = await mainPdfDoc.copyPages(backCoverPdfDoc, [0]);
        mainPdfDoc.addPage(backCoverPage);
        
        // 3. Return final PDF bytes
        const pdfBytes = await mainPdfDoc.save();
        console.log(`Successfully generated complete book buffer.`);
        return pdfBytes;
        
    } catch (err) {
        console.error("Error during PDF generation:", err);
        if (browser) await browser.close();
        if (tempHtmlPath && fs.existsSync(tempHtmlPath)) fs.unlinkSync(tempHtmlPath);
        throw err;
    }
}

module.exports = { generateCustomBook };
