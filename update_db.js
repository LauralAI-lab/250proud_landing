require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

async function run() {
    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
    
    if (!supabaseKey) {
        console.error("Missing SUPABASE_SERVICE_ROLE_KEY");
        return;
    }
    
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/exec_sql`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'apikey': supabaseKey,
            'Authorization': `Bearer ${supabaseKey}`
        },
        body: JSON.stringify({
            query: `ALTER TABLE public.b2b_orders ADD COLUMN IF NOT EXISTS account_email TEXT;`
        })
    });
    
    if (response.ok) {
        console.log("Column added successfully or already exists.");
    } else {
        // If RPC isn't available, we might need to use standard REST insert or do it from the dashboard.
        console.log("Failed via RPC, checking if column exists by making a query...");
        const res2 = await fetch(`${supabaseUrl}/rest/v1/b2b_orders?select=account_email&limit=1`, {
            headers: {
                'apikey': supabaseKey,
                'Authorization': `Bearer ${supabaseKey}`
            }
        });
        if (res2.ok) {
            console.log("Column account_email exists.");
        } else {
            console.error("Error checking column:", await res2.text());
        }
    }
}
run();
