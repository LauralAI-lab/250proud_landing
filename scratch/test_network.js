const puppeteer = require('puppeteer-core');

async function run() {
  console.log("Launching browser...");
  const browser = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true
  });
  
  const page = await browser.newPage();
  
  // Log all requests
  page.on('requestfailed', request => {
    console.log(`[REQUEST FAILED] ${request.method()} ${request.url()} - Error: ${request.failure().errorText}`);
  });

  // Log response status codes
  page.on('response', response => {
    if (response.status() >= 400) {
      console.log(`[RESPONSE ERROR] ${response.status()} ${response.url()}`);
    }
  });
  
  page.on('console', msg => {
    console.log(`[CONSOLE] ${msg.type().toUpperCase()}: ${msg.text()}`);
  });

  page.on('pageerror', err => {
    console.log(`[EXCEPTION]: ${err.toString()}`);
  });

  console.log("Navigating to https://250proud.net/resources...");
  await page.goto('https://250proud.net/resources', { waitUntil: 'networkidle2' });

  await new Promise(r => setTimeout(r, 2000));
  await browser.close();
}

run().catch(console.error);
