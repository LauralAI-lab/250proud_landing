require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY);

async function run() {
  const { data, error } = await supabase.from('users').select('*');
  console.log("All users:", data);
  if (error) console.log("Error:", error);
}
run();
