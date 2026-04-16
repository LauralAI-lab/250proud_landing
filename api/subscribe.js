// /api/subscribe.js — Vercel serverless function
// Handles Mailchimp subscription + Supabase logging

const { createClient } = require('@supabase/supabase-js');
const mailchimp = require('@mailchimp/mailchimp_marketing');

module.exports = async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    const { first_name, email, address, city, state, zip, 
            phone, comm_pref, source } = req.body;

    // 1. Add to Mailchimp
    mailchimp.setConfig({
      apiKey: process.env.MAILCHIMP_API_KEY || 'missing_key',
      server: process.env.MAILCHIMP_SERVER_PREFIX || 'us21', 
    });

    try {
      if (process.env.MAILCHIMP_API_KEY) {
        await mailchimp.lists.addListMember(process.env.MAILCHIMP_LIST_ID, {
          email_address: email,
          status: 'subscribed',
          merge_fields: {
            FNAME: first_name || '',
            ADDRESS: { addr1: address || '', city: city || '', state: state || '', zip: zip || '', country: 'US' },
            PHONE: phone || '',
            COMM_PREF: comm_pref || '',
            SOURCE: source || ''
          },
          tags: ['coloring-book-lead', '250proud-launch']
        });
      }
    } catch (mcError) {
      console.error('Mailchimp error:', mcError);
    }

    // 2. Log to Supabase
    const supaUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supaKey = process.env.SUPABASE_SERVICE_KEY || process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!supaUrl || !supaKey) {
      const activeSupaKeys = Object.keys(process.env).filter(k => k.includes('SUPA') || k.includes('supa')).join(', ');
      return res.status(500).json({ error: `Missing Database ENV routing variables. Vercel memory sees these keys: [${activeSupaKeys || 'NONE FOUND'}]` });
    }

    const supabase = createClient(supaUrl, supaKey);

    const { error: dbError } = await supabase
      .from('subscribers')
      .insert([{
        first_name: first_name || null,
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
      console.error('Supabase error:', dbError);
      return res.status(500).json({ error: 'Database constraint or schema rejection', details: dbError });
    }

    return res.status(200).json({ success: true });
  } catch (err) {
    console.error("FATAL BINDING ERROR:", err);
    return res.status(500).json({ error: 'Fatal Exception in endpoint', details: err.message, stack: err.stack });
  }
}
