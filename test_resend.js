require('dotenv').config();
const { Resend } = require('resend');
const resend = new Resend(process.env.RESEND_API_KEY);

async function test() {
    const { data, error } = await resend.emails.send({
        from: '250PROUD Fulfillment <delivery@250proud.net>',
        to: 'mike@mikeprice.net',
        subject: 'Test Email',
        html: '<p>Test</p>'
    });
    console.log({ data, error });
}
test();
