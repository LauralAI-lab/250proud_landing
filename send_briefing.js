const fs = require('fs');
const path = require('path');
const { Resend } = require('resend');

// Load environment variables
const envPath = path.join(__dirname, '.env.local');
if (fs.existsSync(envPath)) {
    require('dotenv').config({ path: envPath });
} else {
    require('dotenv').config();
}

const resend = new Resend(process.env.RESEND_API_KEY);

async function run() {
    try {
        const todayStr = new Date().toISOString().split('T')[0];
        // Briefing file name format: briefing_YYYY-MM-DD.md
        const filename = `briefing_${todayStr}.md`;
        const briefingPath = path.join(__dirname, '..', 'board_comms', 'briefings', filename);

        if (!fs.existsSync(briefingPath)) {
            console.error(`Briefing file not found at: ${briefingPath}`);
            process.exit(1);
        }

        const mdContent = fs.readFileSync(briefingPath, 'utf8');

        // Extract Email Subject Line from MD
        // Format: "Email Subject: [Subject Text]" or similar
        let subject = `Daily Progress Briefing - ${todayStr}`;
        const subjectMatch = mdContent.match(/(?:Subject|Email Subject):\s*(.+)/i);
        if (subjectMatch && subjectMatch[1]) {
            subject = subjectMatch[1].trim();
        }

        // Simple Markdown to HTML parser for standard headings and list items
        let htmlContent = mdContent
            .replace(/\r\n/g, '\n')
            // Headers
            .replace(/^# (.*$)/gim, '<h1 style="color: #0A3161; font-family: Oswald, sans-serif; font-size: 24px; border-bottom: 2px solid #0A3161; padding-bottom: 6px; margin-bottom: 15px;">$1</h1>')
            .replace(/^## (.*$)/gim, '<h2 style="color: #0A3161; font-family: Oswald, sans-serif; font-size: 18px; margin-top: 20px; margin-bottom: 10px;">$1</h2>')
            .replace(/^### (.*$)/gim, '<h3 style="color: #333; font-family: sans-serif; font-size: 15px; margin-top: 15px; margin-bottom: 5px;">$1</h3>')
            // Lists
            .replace(/^\s*-\s*`\[[x ]\]` (.*$)/gim, '<li style="list-style-type: none; margin-bottom: 8px; font-family: sans-serif; font-size: 14px;">📝 $1</li>')
            .replace(/^\s*-\s*(.*$)/gim, '<li style="margin-bottom: 8px; font-family: sans-serif; font-size: 14px;">$1</li>')
            .replace(/(<li.*<\/li>)/g, '<ul style="padding-left: 20px; margin-bottom: 15px;">$1</ul>')
            // Clean duplicate nested UL tags
            .replace(/<\/ul>\s*<ul[^>]*>/g, '')
            // Paragraphs
            .replace(/([^\n]+)\n([^\n]+)/g, '$1<br>$2')
            .replace(/\n\n/g, '<p style="margin-bottom: 15px; font-family: sans-serif; font-size: 14px; line-height: 1.6;"></p>');

        // Wrap in clean email layout
        const finalHtml = `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: sans-serif; color: #333333; line-height: 1.6; padding: 20px; background-color: #f8fafc; }
                .email-container { max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; border: 1px solid #e2e8f0; }
                .footer { font-size: 12px; color: #888888; text-align: center; margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 15px; }
            </style>
        </head>
        <body>
            <div class="email-container">
                ${htmlContent}
                <div class="footer">
                    Sent automatically by Aligned Agentics OS • © 2026 Lauralai LLC
                </div>
            </div>
        </body>
        </html>
        `;

        console.log(`Sending email briefing to mike@lauralai.llc with subject: "${subject}"...`);

        const data = await resend.emails.send({
            from: 'LauralAI Operations <info@250proud.net>',
            to: 'mike@lauralai.llc',
            subject: subject,
            html: finalHtml
        });

        console.log("Email sent successfully:", data);
    } catch (err) {
        console.error("Failed to compile or send briefing:", err);
        process.exit(1);
    }
}

run();
