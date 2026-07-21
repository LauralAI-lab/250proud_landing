// /api/contact.js — Vercel serverless function
// Handles Contact Us form submissions and sends email via Resend

const { Resend } = require('resend');

module.exports = async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    const rawBody = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    const { first_name, last_name, email, phone, message } = rawBody;

    // Validate required fields
    if (!first_name || !last_name || !email || !message) {
      return res.status(400).json({ error: 'First name, last name, email, and message are required.' });
    }

    const full_name = `${first_name} ${last_name}`.trim();
    
    // Subject line formatted for rules/filtering
    let subjectLine = `[Aligned Agentics] Contact Request from ${full_name}`;

    // Send Email via Resend
    if (!process.env.RESEND_API_KEY) {
        console.error("Missing RESEND_API_KEY environment variable.");
        return res.status(500).json({ error: 'Server configuration error.' });
    }

    const resend = new Resend(process.env.RESEND_API_KEY);
    
    try {
      await resend.emails.send({
        from: 'Aligned Agentics Contact Form <notifications@send.250proud.net>',
        to: 'mike@lauralai.llc',
        subject: subjectLine,
        html: `
          <h2 style="color: #D4AF37;">New Contact Request (Aligned Agentics)</h2>
          <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Name:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">${full_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Email:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">${email}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Phone:</strong></td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">${phone || 'Not provided'}</td>
            </tr>
          </table>
          <h3 style="margin-top: 20px;">Message:</h3>
          <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #D4AF37; white-space: pre-wrap; color: #333;">
              ${message}
          </div>
        `
      });
      console.log("Contact notification email sent successfully.");
    } catch (emailError) {
      console.error("Failed to send contact notification email:", emailError);
      return res.status(500).json({ error: 'Failed to send email.' });
    }

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error("FATAL CONTACT ERROR:", err);
    return res.status(500).json({ error: 'Fatal Exception in endpoint', details: err.message });
  }
}
