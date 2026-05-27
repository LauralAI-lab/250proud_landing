require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

async function run() {
  const { data, error } = await supabase.rpc('get_policies_for_table', { target_table: 'b2b_orders' }).catch(() => ({}));
  console.log("Policies:", data || "Need to query pg_policies directly");
}
run();
