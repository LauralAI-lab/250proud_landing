// /api/subscribe.js — Vercel serverless function
// Handles Mailchimp subscription + Supabase logging

const { createClient } = require('@supabase/supabase-js');
const mailchimp = require('@mailchimp/mailchimp_marketing');

module.exports = async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    const rawBody = typeof req.body === 'string' ? JSON.parse(req.body) : req.body || {};
    const { first_name, last_name, email, address, city, state, zip, 
            phone, comm_pref, source } = rawBody;

    // 1. Add to Mailchimp
    mailchimp.setConfig({
      apiKey: process.env.MAILCHIMP_API_KEY || 'missing_key',
      server: process.env.MAILCHIMP_SERVER_PREFIX || 'us21', 
    });

    try {
      if (process.env.MAILCHIMP_API_KEY) {
        // Build merge fields dynamically to prevent Mailchimp validation crashes
        const mergeFields = {
          FNAME: first_name || '',
          LNAME: last_name || ''
        };
        
        // Mailchimp strictly requires addr2 property if sending ADDRESS
        if (address && city && state && zip) {
          mergeFields.ADDRESS = { 
            addr1: address, 
            addr2: '', 
            city: city, 
            state: state, 
            zip: zip, 
            country: 'US' 
          };
        }
        
        // Only include PHONE if it has a value (empty string crashes Mailchimp phone validation)
        if (phone && phone.trim() !== '') {
          mergeFields.PHONE = phone;
        }

        // Add custom fields (ensure COMM_PREF and SOURCE merge tags are created in Mailchimp)
        if (comm_pref) mergeFields.COMM_PREF = comm_pref;
        if (source) mergeFields.SOURCE = source;

        await mailchimp.lists.addListMember(process.env.MAILCHIMP_LIST_ID, {
          email_address: email || '',
          status: 'subscribed',
          merge_fields: mergeFields,
          tags: ['coloring-book-lead', '250proud-launch']
        });
      }
    } catch (mcError) {
      console.error('Mailchimp error:', mcError);
      let errMsg = mcError.message;
      if (mcError.response && mcError.response.body) {
        errMsg = `${mcError.response.body.title} - ${mcError.response.body.detail} (Check Audience Merge Tags)`;
      }
      return res.status(400).json({ error: `MAILCHIMP REJECTED: ${errMsg}` });
    }

    // 2. Log to Supabase
    const supaUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supaKey = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supaUrl || !supaKey) {
      const activeSupaKeys = Object.keys(process.env).filter(k => k.includes('SUPA') || k.includes('supa')).join(', ');
      return res.status(500).json({ error: `Missing Database ENV routing variables. Vercel memory sees these keys: [${activeSupaKeys || 'NONE FOUND'}]` });
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
      // 23505 is PostgreSQL's error code for a Unique Violation (Duplicate Key)
      if (dbError.code === '23505' || (dbError.message && dbError.message.includes('duplicate'))) {
        console.log(`Email ${email} is already in the database. Gracefully proceeding.`);
      } else {
        console.error('Supabase error:', dbError);
        return res.status(500).json({ error: `Database error: ${dbError.message || JSON.stringify(dbError)}` });
      }
    }

    return res.status(200).json({ 
      success: true,
      mc_debug: {
        key: !!process.env.MAILCHIMP_API_KEY,
        list: !!process.env.MAILCHIMP_LIST_ID,
        prefix: !!process.env.MAILCHIMP_SERVER_PREFIX
      }
    });
  } catch (err) {
    console.error("FATAL BINDING ERROR:", err);
    return res.status(500).json({ error: 'Fatal Exception in endpoint', details: err.message, stack: err.stack });
  }
}
