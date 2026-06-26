require('dotenv').config();

const webhookUrl = 'http://localhost:3000/api/lulu/webhook'; // Change this to your Vercel URL when testing production

const payload = {
    "event_type": "PRINT_JOB_SHIPPED",
    "print_job": {
        "id": 999999, // Replace with an actual test lulu_job_id from your DB if you want to fully test Shopify fulfillment
        "status": {
            "name": "SHIPPED"
        },
        "line_items": [
            {
                "tracking_urls": [
                    "https://www.fedex.com/fedextrack/?trknbr=123456789"
                ],
                "tracking_id": "123456789"
            }
        ]
    }
};

async function testWebhook() {
    console.log(`🚀 Sending mock Lulu webhook to ${webhookUrl}...`);
    try {
        const res = await fetch(webhookUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        const responseText = await res.text();
        console.log(`✅ Response Status: ${res.status}`);
        console.log(`✅ Response Body: ${responseText}`);
    } catch (error) {
        console.error('❌ Error sending webhook:', error);
    }
}

testWebhook();
