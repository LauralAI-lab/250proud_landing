const fetch = require('node-fetch');

class LuluService {
    constructor() {
        // Will use sandbox by default unless explicitly set to production
        this.isSandbox = process.env.LULU_ENVIRONMENT !== 'production';
        this.authUrl = this.isSandbox 
            ? 'https://api.sandbox.lulu.com/auth/realms/glasgow/protocol/openid-connect/token'
            : 'https://api.lulu.com/auth/realms/glasgow/protocol/openid-connect/token';
        this.apiUrl = this.isSandbox
            ? 'https://api.sandbox.lulu.com'
            : 'https://api.lulu.com';
        
        this.clientId = process.env.LULU_CLIENT_KEY;
        this.clientSecret = process.env.LULU_CLIENT_SECRET;
        this.token = null;
        this.tokenExpiry = null;
    }

    async authenticate() {
        if (!this.clientId || !this.clientSecret) {
            console.warn('⚠️ Lulu API keys not found in environment variables. Skipping Lulu authentication.');
            return null;
        }

        // Return cached token if it's still valid (with a 5 min buffer)
        if (this.token && this.tokenExpiry && Date.now() < this.tokenExpiry - 300000) {
            return this.token;
        }

        console.log('🔐 Authenticating with Lulu Print API...');
        const authString = Buffer.from(`${this.clientId}:${this.clientSecret}`).toString('base64');

        const params = new URLSearchParams();
        params.append('grant_type', 'client_credentials');

        try {
            const response = await fetch(this.authUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': `Basic ${authString}`
                },
                body: params
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Lulu Auth failed (${response.status}): ${text}`);
            }

            const data = await response.json();
            this.token = data.access_token;
            // expires_in is in seconds
            this.tokenExpiry = Date.now() + (data.expires_in * 1000);
            console.log('✅ Lulu authentication successful!');
            return this.token;
        } catch (error) {
            console.error('❌ Lulu Authentication Error:', error);
            throw error;
        }
    }

    /**
     * Creates a print job for the customized book
     * @param {Object} orderData - The order data from Supabase
     * @param {Object} shippingAddress - The shipping address object
     * @param {number} quantity - Number of books to print
     */
    async createPrintJob(orderData, shippingAddress, quantity = 50) {
        if (!this.clientId) {
            console.warn('⚠️ Lulu API keys missing. Simulating print job creation for Order:', orderData.order_id);
            return { id: 'mock-job-id', status: 'simulated' };
        }

        const token = await this.authenticate();
        if (!token) return null;

        // Ensure we have the Lulu PDF URLs
        if (!orderData.lulu_cover_url || !orderData.lulu_interior_url) {
            throw new Error(`Cannot submit print job ${orderData.order_id}: Missing Lulu PDF URLs.`);
        }

        // The exact POD package ID depends on the physical specs of the book
        const podPackageId = process.env.LULU_POD_PACKAGE_ID || '0850X1100FCSTDPB80CW444MXX'; 

        const payload = {
            contact_email: orderData.email || 'hello@250proud.com',
            external_id: `250proud-${orderData.order_id}`,
            line_items: [
                {
                    external_id: `item-${orderData.order_id}`,
                    printable_normalization: {
                        cover: {
                            source_url: orderData.lulu_cover_url
                        },
                        interior: {
                            source_url: orderData.lulu_interior_url
                        },
                        pod_package_id: podPackageId
                    },
                    quantity: quantity,
                    title: `250Proud Custom Book - ${orderData.company_name || 'Customer'}`
                }
            ],
            shipping_address: {
                name: shippingAddress.name || orderData.company_name || 'Customer',
                street1: shippingAddress.street1 || '123 Test St',
                city: shippingAddress.city || 'Raleigh',
                country_code: shippingAddress.country_code || 'US',
                state_code: shippingAddress.state_code || 'NC',
                postcode: shippingAddress.postcode || '27601',
                phone_number: shippingAddress.phone || orderData.phone || '844-212-0689'
            },
            shipping_level: 'MAIL' // Standard mail
        };

        console.log(`🖨️ Submitting print job to Lulu for Order ${orderData.order_id}...`);

        try {
            const response = await fetch(`${this.apiUrl}/print-jobs/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ Lulu Print Job Error Response:', JSON.stringify(errorData, null, 2));
                throw new Error(`Lulu Print Job failed (${response.status})`);
            }

            const jobData = await response.json();
            console.log(`✅ Lulu Print Job Created Successfully! Job ID: ${jobData.id}`);
            return jobData;
        } catch (error) {
            console.error('❌ Error submitting to Lulu API:', error);
            throw error;
        }
    }
}

module.exports = new LuluService();
