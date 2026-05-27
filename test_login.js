require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

async function run() {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: 'mike+050707@lauralai.llc',
    password: 'password123' // Just guessing, probably won't work
  });
  console.log("Login:", data, error);
}
run();
