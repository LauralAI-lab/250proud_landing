const fetch = require('node-fetch');

async function run() {
    const res = await fetch('http://localhost:3000/api/shopify/webhook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            order_id: "test-card-gen-1234",
            note_attributes: [{ name: 'order_id', value: 'b2b-demo-uuid' }]
        })
    });
    
    const text = await res.text();
    console.log(res.status, text);
}

run();
