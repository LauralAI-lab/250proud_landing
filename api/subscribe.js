// /api/subscribe.js — Vercel serverless function
// Handles Mailchimp subscription + Supabase logging

const { createClient } = require('@supabase/supabase-js');
const mailchimp = require('@mailchimp/mailchimp_marketing');
const crypto = require('crypto');
const { Resend } = require('resend');

module.exports = async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    const rawBody = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    const { first_name, last_name, email, address, city, state, zip, 
            phone, comm_pref, source } = rawBody;

    // 1. Add/Update Mailchimp
    mailchimp.setConfig({
      apiKey: process.env.MAILCHIMP_API_KEY || 'missing_key',
      server: process.env.MAILCHIMP_SERVER_PREFIX || 'us21', 
    });

    let mcDebugInfo = { status: 'skipped', message: 'No API Key' };

    if (process.env.MAILCHIMP_API_KEY && process.env.MAILCHIMP_API_KEY !== 'missing_key') {
      const listId = process.env.MAILCHIMP_LIST_ID;
      const subscriberHash = crypto.createHash('md5').update((email || '').toLowerCase()).digest('hex');

      // Build merge fields
      const mergeFields = {
        FNAME: first_name || '',
        LNAME: last_name || ''
      };
      
      if (address && city && state && zip) {
        mergeFields.ADDRESS = { 
          addr1: address, addr2: '', city: city, state: state, zip: zip, country: 'US' 
        };
      }
      
      if (phone && phone.trim() !== '') {
        mergeFields.PHONE = phone;
      }
      if (comm_pref) mergeFields.COMM_PREF = comm_pref;
      if (source) mergeFields.SOURCE = source;

      try {
        // PASS 1: Attempt Upsert with all fields
        await mailchimp.lists.setListMember(listId, subscriberHash, {
          email_address: email || '',
          status_if_new: 'subscribed',
          merge_fields: mergeFields,
        });
        mcDebugInfo = { status: 'success', pass: 1 };
      } catch (mcError) {
        // PASS 2: If Mailchimp rejects custom fields, fallback to basic fields
        console.warn('Mailchimp Pass 1 Failed. Trying Pass 2 with basic fields...', mcError.message);
        try {
          await mailchimp.lists.setListMember(listId, subscriberHash, {
            email_address: email || '',
            status_if_new: 'subscribed',
            merge_fields: { FNAME: first_name || '', LNAME: last_name || '' },
          });
          mcDebugInfo = { status: 'success', pass: 2, fallbackUsed: true };
        } catch (mcError2) {
          console.error('Mailchimp Pass 2 error:', mcError2);
          let errMsg = mcError2.response?.body?.detail || mcError2.message;
          mcDebugInfo = { status: 'failed', error: errMsg };
        }
      }

      // Explicitly Add Tags to trigger Automations
      try {
        await mailchimp.lists.updateListMemberTags(listId, subscriberHash, {
          tags: [
            { name: 'coloring-book-lead', status: 'active' },
            { name: '250proud-launch', status: 'active' }
          ]
        });
      } catch (tagError) {
        console.warn('Mailchimp Tagging Warning: Could not apply tags', tagError.message);
      }
    }

    // 2. Log to Supabase
    const supaUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supaKey = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supaUrl || !supaKey) {
      return res.status(500).json({ error: `Missing Supabase Environment Variables.` });
    }

    const supabase = createClient(supaUrl, supaKey);
    const full_name = last_name ? `${first_name || ''} ${last_name}`.trim() : (first_name || null);

    const { error: dbError } = await supabase
      .from('subscribers')
      .insert([{
        first_name: full_name,
        email: email || null,
        address: address || null,
        city: city || null,
        state: state || null,
        zip: zip || null,
        phone: phone || null,
        comm_pref: comm_pref || null,
        source: source || null,
        created_at: new Date().toISOString()
      }]);

    if (dbError) {
      // Gracefully handle Duplicate Email constraint (23505)
      const errStr = String(dbError.message || '').toLowerCase();
      if (dbError.code === '23505' || errStr.includes('duplicate') || errStr.includes('unique')) {
        console.log(`Email ${email} is already in the database. Gracefully proceeding.`);
      } else {
        console.error('Supabase error:', dbError);
        return res.status(500).json({ error: `Database error: ${dbError.message || JSON.stringify(dbError)}` });
      }
    }

    // 3. Send Internal Notification via Resend
    if (process.env.RESEND_API_KEY) {
      const resend = new Resend(process.env.RESEND_API_KEY);
      try {
        await resend.emails.send({
          from: '250PROUD Notifications <notifications@send.250proud.net>',
          to: 'info@250proud.net',
          subject: `🎉 New Sign Up: ${full_name || email}`,
          html: `
            <h2>New Lead Captured!</h2>
            <p><strong>Name:</strong> ${full_name || 'Not provided'}</p>
            <p><strong>Email:</strong> ${email || 'Not provided'}</p>
            <p><strong>Phone:</strong> ${phone || 'Not provided'}</p>
            <p><strong>Source:</strong> ${source || 'Website Form'}</p>
          `
        });
        console.log("Internal notification email sent successfully.");
      } catch (emailError) {
        console.error("Failed to send internal notification email:", emailError);
      }
    }

    return res.status(200).json({ 
      success: true,
      mc_debug: mcDebugInfo
    });
  } catch (err) {
    console.error("FATAL BINDING ERROR:", err);
    return res.status(500).json({ error: 'Fatal Exception in endpoint', details: err.message });
  }
}
