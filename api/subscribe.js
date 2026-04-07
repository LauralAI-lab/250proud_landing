// /api/subscribe.js — Vercel serverless function
// Handles Mailchimp subscription + Supabase logging

import { createClient } from '@supabase/supabase-js';
const mailchimp = require('@mailchimp/mailchimp_marketing');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { first_name, email, address, city, state, zip, 
          phone, comm_pref, source } = req.body;

  // 1. Add to Mailchimp
  mailchimp.setConfig({
    apiKey: process.env.MAILCHIMP_API_KEY,
    server: process.env.MAILCHIMP_SERVER_PREFIX, // e.g. 'us21'
  });

  try {
    await mailchimp.lists.addListMember(process.env.MAILCHIMP_LIST_ID, {
      email_address: email,
      status: 'subscribed',
      merge_fields: {
        FNAME: first_name,
        ADDRESS: { addr1: address, city, state, zip, country: 'US' },
        PHONE: phone || '',
        COMM_PREF: comm_pref,
        SOURCE: source
      },
      tags: ['coloring-book-lead', '250proud-launch']
    });
  } catch (mcError) {
    // Log but don't fail — still save to Supabase
    console.error('Mailchimp error:', mcError);
  }

  // 2. Log to Supabase
  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );

  const { error: dbError } = await supabase
    .from('subscribers')
    .insert([{
      first_name,
      email,
      address,
      city,
      state,
      zip,
      phone: phone || null,
      comm_pref,
      source,
      created_at: new Date().toISOString()
    }]);

  if (dbError) {
    console.error('Supabase error:', dbError);
    return res.status(500).json({ error: 'Database error' });
  }

  return res.status(200).json({ success: true });
}
