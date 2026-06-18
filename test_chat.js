const puppeteer = require('puppeteer-core');
const chromium = require('@sparticuz/chromium');
const express = require('express');
const app = express();

app.use(express.static(__dirname, { extensions: ['html'] }));

const server = app.listen(3002, async () => {
    console.log('Server running on 3002');
    try {
        const browser = await puppeteer.launch({
            args: chromium.args,
            defaultViewport: chromium.defaultViewport,
            executablePath: await chromium.executablePath(),
            headless: chromium.headless,
        });
        const page = await browser.newPage();
        
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', error => console.log('PAGE ERROR:', error.message));

        await page.goto('http://localhost:3002/index.html', { waitUntil: 'networkidle0' });
        
        const widgetHTML = await page.evaluate(() => {
            const widget = document.querySelector('.lauralai-chat-widget');
            return widget ? widget.outerHTML : 'NOT FOUND';
        });

        console.log('Widget HTML:', widgetHTML.substring(0, 100) + '...');
        
        await browser.close();
        server.close();
    } catch (e) {
        console.error("Puppeteer error:", e);
        server.close();
    }
});
