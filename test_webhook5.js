const mailchimp = require('@mailchimp/mailchimp_marketing');
const crypto = require('crypto');
const fs = require('fs');
const { execSync } = require('child_process');

mailchimp.setConfig({
    apiKey: "efec3bce6afca256fa0642f492f4f648-us9",
    server: "us9", 
});
const listId = "c316e2d1eb";
const email = "mike@mikeprice.me";
const subscriberHash = crypto.createHash('md5').update(email.toLowerCase()).digest('hex');

async function resetAndTest() {
    try {
        console.log(`Removing ${email} from Mailchimp to guarantee a fresh trigger...`);
        await mailchimp.lists.deleteListMemberPermanent(listId, subscriberHash);
        console.log("Successfully removed old contact.");
    } catch(e) {
        console.log("Contact didn't exist or already removed.");
    }
    
    const ORDERS_DB_FILE = './orders.json';
    let data = {};
    if (fs.existsSync(ORDERS_DB_FILE)) {
        data = JSON.parse(fs.readFileSync(ORDERS_DB_FILE, 'utf8'));
    }
    const testOrderId = 'test-order-final';
    data[testOrderId] = {
        data: { email: email, companyName: "Mike Price Media", phone: "555-0199" },
        status: 'pending_payment',
        createdAt: new Date().toISOString()
    };
    fs.writeFileSync(ORDERS_DB_FILE, JSON.stringify(data, null, 2));
    console.log("Order injected. Firing webhook...");

    try {
        execSync(`curl -s -X POST http://localhost:3000/api/shopify/webhook -H "Content-Type: application/json" -d '{"order_id": "test-order-final"}'`);
        console.log("Webhook fired successfully!");
    } catch (err) {
        console.error("Webhook curl failed", err);
    }
}
resetAndTest();
