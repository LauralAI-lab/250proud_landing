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

const cssRegex = /<link rel="stylesheet" href="\/nc_assets\/css\/lauralai-chat\.css\?v=\d+">/g;
const jsRegex = /<script src="\/nc_assets\/js\/lauralai-chat\.js\?v=\d+"><\/script>/g;

const newCssTag = '<link rel="stylesheet" href="/nc_assets/css/lauralai-assistant.css?v=3">';
const newJsTag = '<script src="/nc_assets/js/lauralai-assistant.js?v=3"></script>';

htmlFiles.forEach(file => {
    const filePath = path.join(directoryPath, file);
    if (fs.existsSync(filePath)) {
        let content = fs.readFileSync(filePath, 'utf8');
        let modified = false;

        if (cssRegex.test(content)) {
            content = content.replace(cssRegex, newCssTag);
            modified = true;
        }

        if (jsRegex.test(content)) {
            content = content.replace(jsRegex, newJsTag);
            modified = true;
        }

        if (modified) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ Updated to assistant script in ${file}`);
        } else {
            console.log(`ℹ️ No matching tags found in ${file}`);
        }
    }
});
