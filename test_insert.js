require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

async function run() {
  const { data, error } = await supabase
            .from('b2b_orders')
            .insert([{
                order_id: "test-order-123",
                email: "test@example.com",
                status: 'pending_payment'
            }]);
  console.log("Insert response data:", data);
  console.log("Insert response error:", error);
}
run();
