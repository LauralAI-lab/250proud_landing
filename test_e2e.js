require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

async function runTest() {
    console.log("1. Starting E2E Test on Production (Vercel)...");
    const testEmail = "mike+e2e4@lauralai.llc";
    const username = "mike_e2e_4";
    const password = "Password123!";
    const company = "E2E Production Corp";
    const baseUrl = "https://250proudlanding-c3wgicsof-lauralai-labs-projects.vercel.app";
    
    // Simulate Checkout (Account Creation)
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
    
    const checkoutData = await checkoutRes.json();
    console.log("Checkout Response:", checkoutData);
    if (!checkoutData.success) {
        console.error("Checkout failed!");
        return;
    }
    
    // Simulate Shopify Webhook fulfilling the order
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
    
    console.log("Webhook triggered. Check vercel logs.");
    const webhookData = await webhookRes.text();
    console.log("Webhook Response:", webhookData);
    
}

runTest();
