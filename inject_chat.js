const fs = require('fs');
const path = require('path');

const directoryPath = __dirname;
const htmlFiles = [
    'index.html',
    'b2b-configurator.html',
    'configurator.html',
    'contact.html',
    'privacy.html',
    'resources.html',
    'schedule.html',
    'terms.html',
    'thank-you.html',
    'today-in-history.html'
];

const cssTag = `<link rel="stylesheet" href="nc_assets/css/lauralai-chat.css">\n</head>`;
const jsTag = `<script src="nc_assets/js/lauralai-chat.js"></script>\n</body>`;

htmlFiles.forEach(file => {
    const filePath = path.join(directoryPath, file);
    if (fs.existsSync(filePath)) {
        let content = fs.readFileSync(filePath, 'utf8');
        let modified = false;

        // Inject CSS if not present
        if (!content.includes('lauralai-chat.css') && content.includes('</head>')) {
            content = content.replace('</head>', cssTag);
            modified = true;
        }

        // Inject JS if not present
        if (!content.includes('lauralai-chat.js') && content.includes('</body>')) {
            content = content.replace('</body>', jsTag);
            modified = true;
        }

        if (modified) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ Injected Chatbot tags into ${file}`);
        } else {
            console.log(`ℹ️ Tags already exist in ${file}`);
        }
    }
});
