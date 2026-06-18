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

const oldCssTag = '<link rel="stylesheet" href="nc_assets/css/lauralai-chat.css">';
const oldJsTag = '<script src="nc_assets/js/lauralai-chat.js"></script>';

const newCssTag = '<link rel="stylesheet" href="/nc_assets/css/lauralai-chat.css?v=2">';
const newJsTag = '<script src="/nc_assets/js/lauralai-chat.js?v=2"></script>';

htmlFiles.forEach(file => {
    const filePath = path.join(directoryPath, file);
    if (fs.existsSync(filePath)) {
        let content = fs.readFileSync(filePath, 'utf8');
        let modified = false;

        if (content.includes(oldCssTag)) {
            content = content.replace(oldCssTag, newCssTag);
            modified = true;
        }

        if (content.includes(oldJsTag)) {
            content = content.replace(oldJsTag, newJsTag);
            modified = true;
        }

        if (modified) {
            fs.writeFileSync(filePath, content, 'utf8');
            console.log(`✅ Updated tags with cache-buster in ${file}`);
        } else {
            console.log(`ℹ️ No old tags found to replace in ${file}`);
        }
    }
});
