const domain = process.env.SHOPIFY_STORE_DOMAIN;
const token = process.env.SHOPIFY_ACCESS_TOKEN;

class ShopifyService {
    /**
     * Fulfills a Shopify order with tracking information
     * Uses the modern FulfillmentOrders API
     */
    async fulfillOrder(orderId, trackingNumber, trackingUrl, trackingCompany = 'Other') {
        if (!domain || !token) {
            console.warn('⚠️ Shopify API keys missing. Skipping fulfillment.');
            return false;
        }

        console.log(`📦 Attempting to fulfill Shopify Order ${orderId} with tracking ${trackingNumber}`);
        
        try {
            // 1. Fetch fulfillment orders for the given order
            const getUrl = `https://${domain}/admin/api/2024-01/orders/${orderId}/fulfillment_orders.json`;
            const res = await fetch(getUrl, {
                headers: { 'X-Shopify-Access-Token': token, 'Content-Type': 'application/json' }
            });
            
            if (!res.ok) {
                console.error('❌ Failed to fetch Shopify fulfillment orders:', await res.text());
                return false;
            }

            const getResult = await res.json();
            const fulfillmentOrders = getResult.fulfillment_orders;
            
            if (!fulfillmentOrders || fulfillmentOrders.length === 0) {
                console.error(`❌ No fulfillment orders found for order ${orderId}`);
                return false;
            }

            // Filter to OPEN or IN_PROGRESS ones
            const openFos = fulfillmentOrders.filter(fo => fo.status === 'OPEN' || fo.status === 'IN_PROGRESS');
            
            if (openFos.length === 0) {
                console.error(`❌ No open fulfillment orders found for order ${orderId}. Already fulfilled?`);
                return false;
            }

            // Map open fulfillment orders to the fulfillment payload
            const lineItemsByFo = openFos.map(fo => ({
                fulfillment_order_id: fo.id
            }));

            // 2. Create the fulfillment
            const fulfillUrl = `https://${domain}/admin/api/2024-01/fulfillments.json`;
            const payload = {
                fulfillment: {
                    message: "Your custom book has been printed and is on its way!",
                    notify_customer: true,
                    tracking_info: {
                        number: trackingNumber,
                        url: trackingUrl,
                        company: trackingCompany
                    },
                    line_items_by_fulfillment_order: lineItemsByFo
                }
            };

            const fulfillRes = await fetch(fulfillUrl, {
                method: 'POST',
                headers: { 
                    'X-Shopify-Access-Token': token, 
                    'Content-Type': 'application/json' 
                },
                body: JSON.stringify(payload)
            });

            if (!fulfillRes.ok) {
                console.error('❌ Shopify Fulfillment Error:', await fulfillRes.text());
                return false;
            }
            
            const data = await fulfillRes.json();
            console.log(`✅ Shopify Order ${orderId} fulfilled successfully!`);
            return data.fulfillment;
        } catch (error) {
            console.error('❌ Error fulfilling Shopify order:', error);
            return false;
        }
    }
}

module.exports = new ShopifyService();
