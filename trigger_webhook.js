// removed

async function run() {
    console.log("Starting fetch...");
    const start = Date.now();
    const res = await fetch('https://250proud.net/api/shopify/webhook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            order_id: "711ad3f9-52fe-419f-806c-1f773b8755ee",
            note_attributes: [{ name: 'order_id', value: '711ad3f9-52fe-419f-806c-1f773b8755ee' }]
        })
    });
    
    const text = await res.text();
    console.log(res.status, text);
    console.log(`Took ${Date.now() - start}ms`);
}

run();
