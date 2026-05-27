const fs = require('fs');
const path = require('path');

const templates = [
    'web_banner_template.html',
    'social_square_template.html',
    'story_template.html',
    'x_post_template.html',
    'lead_capture_graphic.html'
];

for (const t of templates) {
    let content = fs.readFileSync(path.join(__dirname, t), 'utf8');

    // 1. Change instructions copy
    content = content.replace(
        'If the button fails, please take a screenshot of the graphic below.',
        'You can alternatively right click the graphic and save it to your device.'
    );

    // 2. Remove crossorigin="anonymous" which breaks Supabase storage image loading
    content = content.replace(/crossorigin="anonymous" /g, '');

    // 3. Make sure the error alert matches the new instruction
    content = content.replace(
        "Please take a screenshot of the graphic to save it!",
        "You can alternatively right click the graphic and save it to your device."
    );

    fs.writeFileSync(path.join(__dirname, t), content, 'utf8');
    console.log('Updated ' + t);
}
