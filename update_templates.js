const fs = require('fs');
const path = require('path');

const templates = [
    { file: 'web_banner_template.html', width: 1200, height: 630 },
    { file: 'social_square_template.html', width: 1080, height: 1080 },
    { file: 'story_template.html', width: 1080, height: 1920 },
    { file: 'x_post_template.html', width: 1200, height: 675 },
    { file: 'lead_capture_graphic.html', width: 1200, height: 630 }
];

for (const t of templates) {
    let content = fs.readFileSync(path.join(__dirname, t.file), 'utf8');

    // 1. Add html-to-image to head
    if (!content.includes('html-to-image.min.js')) {
        content = content.replace('</head>', `    <script src="https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js"></script>\n</head>`);
    }

    // 2. Extract the body's original styles to apply to the wrapper
    const bodyStyleMatch = content.match(/body\s*{([^}]+)}/);
    if (bodyStyleMatch) {
        let bodyInner = bodyStyleMatch[1];
        
        // Remove width, height, background, display, overflow, flex-direction, align-items, justify-content from body
        // and put them in a new class .graphic-wrapper
        
        // We just replace the entire body block with a clean body and a .graphic-wrapper
        const newCss = `
        body {
            background: #1e293b;
            font-family: 'Inter', sans-serif;
            color: white;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            overflow-y: auto; /* Enable scrolling */
            overflow-x: auto;
        }

        .controls {
            margin-bottom: 30px;
            text-align: center;
            z-index: 9999;
        }

        .download-btn {
            background: #D4AF37;
            color: #020617;
            padding: 16px 32px;
            border-radius: 8px;
            font-family: 'Oswald', sans-serif;
            font-size: 20px;
            font-weight: 700;
            text-transform: uppercase;
            cursor: pointer;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.2s;
        }
        
        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(212, 175, 55, 0.4);
        }

        .graphic-wrapper {
            ${bodyInner}
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            /* Ensure it is exactly the right size */
            width: ${t.width}px !important;
            height: ${t.height}px !important;
            min-width: ${t.width}px;
            min-height: ${t.height}px;
            position: relative;
            overflow: hidden;
        }
        `;
        content = content.replace(bodyStyleMatch[0], newCss);
    }

    // 3. Wrap everything inside <body> (except scripts) in the wrapper
    // Find everything between <body> and <script>
    const bodyStart = content.indexOf('<body>');
    const scriptStart = content.lastIndexOf('<script>');
    if (bodyStart !== -1 && scriptStart !== -1) {
        const bodyContent = content.substring(bodyStart + 6, scriptStart);
        
        // Don't double wrap
        if (!bodyContent.includes('class="graphic-wrapper"')) {
            const newBodyContent = `
    <div class="controls">
        <button id="downloadBtn" class="download-btn" onclick="downloadGraphic()">Download Graphic</button>
        <p style="margin-top: 10px; color: #94a3b8; font-size: 14px;">If the button fails, please take a screenshot of the graphic below.</p>
    </div>
    <div id="graphic-wrapper" class="graphic-wrapper">
        ${bodyContent}
    </div>
    `;
            content = content.substring(0, bodyStart + 6) + newBodyContent + content.substring(scriptStart);
        }
    }

    // 4. Update the javascript
    const downloadScript = `
        function downloadGraphic() {
            const node = document.getElementById('graphic-wrapper');
            const btn = document.getElementById('downloadBtn');
            btn.innerText = 'Generating PNG...';
            
            htmlToImage.toPng(node, { quality: 1.0, pixelRatio: 2, cacheBust: true })
                .then(function (dataUrl) {
                    var link = document.createElement('a');
                    link.download = '${t.file.replace('.html', '')}.png';
                    link.href = dataUrl;
                    link.click();
                    btn.innerText = 'Download Graphic';
                })
                .catch(function (error) {
                    console.error('oops, something went wrong!', error);
                    btn.innerText = 'Download Failed - Take Screenshot';
                    alert('There was an issue generating the image (likely a CORS security block on the logos). Please take a screenshot of the graphic to save it!');
                });
        }
    `;

    // Make sure to add company name logic back
    const scriptMatch = content.match(/<script>([\s\S]*?)<\/script>/g);
    if (scriptMatch) {
        let lastScript = scriptMatch[scriptMatch.length - 1];
        if (!lastScript.includes('downloadGraphic')) {
            let newScript = lastScript.replace('</script>', `
        if(urlParams.has('company')) {
            const el = document.getElementById('companyNameText');
            if(el) el.innerText = urlParams.get('company');
        }
${downloadScript}
    </script>`);
            content = content.replace(lastScript, newScript);
        }
    }

    // 5. Restore companyNameText IDs in the HTML if they are missing
    // Web Banner
    if (t.file === 'web_banner_template.html') {
        content = content.replace('<span class="headline-partner">Unique American History</span>', '<span class="headline-partner" id="companyNameText">Unique American History</span>');
    }
    // Social Square
    if (t.file === 'social_square_template.html') {
        content = content.replace('<span class="headline-partner">American Grit</span>', '<span class="headline-partner" id="companyNameText">American Grit</span>');
    }
    // Story
    if (t.file === 'story_template.html') {
        content = content.replace('<span style="color:white; font-weight:bold;">Us</span>', '<span id="companyNameText" style="color:white; font-weight:bold;">Us</span>');
    }
    // X Post
    if (t.file === 'x_post_template.html') {
        content = content.replace('<strong>us</strong>', '<strong id="companyNameText">us</strong>');
    }

    // 6. Crossorigin on images to help html2canvas
    content = content.replace(/<img src="nc_assets\/img\/logo\.svg"/g, '<img crossorigin="anonymous" src="nc_assets/img/logo.svg"');
    content = content.replace(/<img src="nc_assets\/img\/generated_true_cover\.png"/g, '<img crossorigin="anonymous" src="nc_assets/img/generated_true_cover.png"');

    fs.writeFileSync(path.join(__dirname, t.file), content, 'utf8');
    console.log('Updated ' + t.file);
}
