const mailchimp = require('@mailchimp/mailchimp_marketing');
const crypto = require('crypto');
const fs = require('fs');
const { execSync } = require('child_process');

mailchimp.setConfig({
    apiKey: "efec3bce6afca256fa0642f492f4f648-us9",
    server: "us9", 
});
const listId = "c316e2d1eb";
const email = "mike@lauralai.llc";
const subscriberHash = crypto.createHash('md5').update(email.toLowerCase()).digest('hex');

async function removeTagAndTest() {
    try {
        console.log(`Removing tag from ${email} so we can trigger it again...`);
        // Remove the tag
        await mailchimp.lists.updateListMemberTags(listId, subscriberHash, {
            tags: [{ name: 'b2b-delivered', status: 'inactive' }]
        });
        console.log("Tag removed successfully.");
    } catch(e) {
        console.log("Tag wasn't there or contact didn't exist.");
    }
    
    // Give Mailchimp a second to process the tag removal
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const ORDERS_DB_FILE = './orders.json';
    let data = {};
    if (fs.existsSync(ORDERS_DB_FILE)) {
        data = JSON.parse(fs.readFileSync(ORDERS_DB_FILE, 'utf8'));
    }
    const testOrderId = 'test-order-tag-reset';
    data[testOrderId] = {
        data: { email: email, companyName: "LauraLai LLC", phone: "555-0199" },
        status: 'pending_payment',
        createdAt: new Date().toISOString()
    };
    fs.writeFileSync(ORDERS_DB_FILE, JSON.stringify(data, null, 2));
    console.log("Order injected. Firing webhook...");

    try {
        execSync(`curl -s -X POST http://localhost:3000/api/shopify/webhook -H "Content-Type: application/json" -d '{"order_id": "test-order-tag-reset"}'`);
        console.log("Webhook fired successfully!");
    } catch (err) {
        console.error("Webhook curl failed", err);
    }
}
removeTagAndTest();
