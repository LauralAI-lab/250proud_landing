require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

async function runTest() {
    console.log("1. Starting E2E Test on Production (Vercel)...");
    const testEmail = "mike+e2e_vercel2@lauralai.llc";
    const username = "mike_vercel_2";
    const password = "Password123!";
    const company = "Vercel E2E Corp";
    const baseUrl = "https://250proud.net";
    
    // 1. Checkout (Account Creation)
    console.log("2. Simulating Checkout / Account Creation...");
    const checkoutRes = await fetch(`${baseUrl}/api/checkout-session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: testEmail,
            companyName: company,
            phone: '555-0100',
            username: username,
            password: password,
            industry: 'Testing'
        })
    });
    
    if(!checkoutRes.ok) {
        console.log("Error Status:", checkoutRes.status);
        console.log("Text:", await checkoutRes.text());
        return;
    }

    const checkoutData = await checkoutRes.json();
    console.log("Checkout Response:", checkoutData);
    
    if (!checkoutData.success) return;
    
    // 2. Webhook
    console.log(`3. Simulating Webhook Fulfillment for Order ID: ${checkoutData.orderId}...`);
    const webhookRes = await fetch(`${baseUrl}/api/shopify/webhook`, {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'x-shopify-topic': 'orders/paid',
            'x-shopify-shop-domain': 'lauralai-one.myshopify.com'
        },
        body: JSON.stringify({
            id: checkoutData.orderId,
            contact_email: testEmail,
            note_attributes: [{ name: "order_id", value: checkoutData.orderId }]
        })
    });
    
    console.log("Webhook triggered. Awaiting response (will take ~30s for PDF generation)...");
    const webhookData = await webhookRes.text();
    console.log("Webhook Response:", webhookData);
    
    // 3. Check DB
    console.log("4. Checking Supabase Users Table for Resource Center URLs...");
    const { data: userRecord, error: userErr } = await supabase
        .from('users')
        .select('*')
        .eq('email', testEmail)
        .single();
        
    console.log("User Record:", userRecord);
    
    if(userRecord) {
        // 4. Test AI Generator
        console.log("5. Testing AI Marketing Copy Generation...");
        const aiRes = await fetch(`${baseUrl}/api/generate-marketing-copy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                format: "SMS / Text Message",
                context: "Testing the Vercel API connection.",
                userId: userRecord.id
            })
        });
        const aiData = await aiRes.json();
        console.log("AI Response:", aiData);
    }
}

runTest();
