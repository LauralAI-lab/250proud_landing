const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function createMockup() {
    console.log("Generating mockup...");
    
    // 1. Read and process the back cover template
    let templateHtml = fs.readFileSync(path.join(__dirname, 'back_cover_template.html'), 'utf8');
    
    const companyName = "Summit Builders";
    const phone = "(555) 987-6543";
    const email = "sarah@summitbuilders.com";
    const website = "www.summitbuilders.com";
    const headline = "Building Your Legacy With Us.";
    const copy = "250 Strong, Built By Hand is a celebration of American grit — 24 pages of stories you may have never known, paired with original illustrations honoring the makers, builders, and dreamers who've shaped this country from 1776 to 2026. Brought to you proudly by Summit Builders, we believe in the enduring spirit of freedom, family, and American heritage. Share this with anyone proud enough to call themselves American.";
    
    // We must use absolute paths for the images because puppeteer might resolve file:// differently.
    // Or we can use relative paths if we load the file via an absolute path url.
    const baseUrl = `file://${__dirname}/`;
    
    templateHtml = templateHtml.replace(/{{COMPANY_NAME}}/g, companyName);
    templateHtml = templateHtml.replace(/{{PHONE}}/g, phone);
    templateHtml = templateHtml.replace(/{{EMAIL}}/g, email);
    templateHtml = templateHtml.replace(/{{WEBSITE}}/g, website);
    templateHtml = templateHtml.replace(/{{HEADLINE}}/g, headline);
    templateHtml = templateHtml.replace(/{{COPY}}/g, copy);
    
    // We don't have logo-cover-configurator-250proud.png, let's just use what's there
    templateHtml = templateHtml.replace(/{{LOGO_URL}}/g, baseUrl + "nc_assets/img/configurator/logo-cover-configurator-250proud.png");
    templateHtml = templateHtml.replace(/{{HEADSHOT_URL}}/g, baseUrl + "nc_assets/img/configurator/agent_headshot.jpeg");
    templateHtml = templateHtml.replace(/{{HEADSHOT_DISPLAY}}/g, "block");
    templateHtml = templateHtml.replace(/{{HERO_URL}}/g, baseUrl + "nc_assets/img/configurator/agent_exterior_home.jpeg");
    templateHtml = templateHtml.replace(/{{INTERIOR_URL}}/g, baseUrl + "nc_assets/img/configurator/agent_interior_home.jpeg");

    // We need to inject a scale so the back cover fits nicely in the scene
    templateHtml = templateHtml.replace('<body>', '<body style="background: white; margin: 0; transform-origin: top left;">');

    // 2. Create the wrapper HTML scene
    const sceneHtml = `
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                background: #f4f6f8;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                font-family: sans-serif;
            }
            .scene {
                display: flex;
                gap: 80px;
                perspective: 1500px;
                padding: 50px;
            }
            .book {
                width: 500px;
                height: 647px; /* 8.5 x 11 aspect ratio scaled */
                position: relative;
                transform-style: preserve-3d;
                box-shadow: 
                    -20px 20px 40px rgba(0,0,0,0.3),
                    inset -2px 0 5px rgba(0,0,0,0.1);
                border-radius: 2px 8px 8px 2px;
                background: white;
            }
            .book-left {
                transform: rotateY(15deg);
            }
            .book-right {
                transform: rotateY(-15deg);
                box-shadow: 
                    20px 20px 40px rgba(0,0,0,0.3),
                    inset 2px 0 5px rgba(0,0,0,0.1);
            }
            .book img, .book .content-wrapper {
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 2px 8px 8px 2px;
                position: absolute;
                top: 0; left: 0;
            }
            .book::after {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                border-radius: 2px 8px 8px 2px;
                background: linear-gradient(to right, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 5%, rgba(0,0,0,0.05) 98%, rgba(0,0,0,0.1) 100%);
                pointer-events: none;
            }
            /* Spine effect */
            .book-left::before {
                content: '';
                position: absolute;
                left: -15px;
                top: 0;
                width: 15px;
                height: 100%;
                background: #0b1a3d;
                transform-origin: right;
                transform: rotateY(-90deg);
            }
            .book-right::before {
                content: '';
                position: absolute;
                right: -15px;
                top: 0;
                width: 15px;
                height: 100%;
                background: #f0f0f0;
                transform-origin: left;
                transform: rotateY(90deg);
                border-right: 1px solid #ccc;
            }
            .content-wrapper {
                overflow: hidden;
                background: white;
            }
            /* Scale the 816x1056 template down to fit our 500x647 container */
            .iframe-scale {
                width: 816px;
                height: 1056px;
                transform: scale(0.6127); /* 500 / 816 */
                transform-origin: top left;
                background: white;
                border: none;
            }
        </style>
    </head>
    <body>
        <div class="scene">
            <div class="book book-left">
                <img src="${baseUrl}nc_assets/img/generated_true_cover.png" alt="Front Cover">
            </div>
            <div class="book book-right">
                <div class="content-wrapper">
                    <iframe class="iframe-scale" srcdoc="${templateHtml.replace(/"/g, '&quot;')}"></iframe>
                </div>
            </div>
        </div>
    </body>
    </html>
    `;

    const scenePath = path.join(__dirname, 'mockup_scene_temp.html');
    fs.writeFileSync(scenePath, sceneHtml);

    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    
    // Set a nice wide viewport
    await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 2 });
    
    await page.goto(`file://${scenePath}`, { waitUntil: 'networkidle0' });
    
    // Take screenshot
    const outputPath = path.join(__dirname, 'b2b_product_mockup_real.png');
    await page.screenshot({ path: outputPath });
    
    await browser.close();
    
    // Cleanup
    fs.unlinkSync(scenePath);
    console.log(`Mockup saved to ${outputPath}`);
}

createMockup().catch(console.error);
