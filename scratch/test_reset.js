require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_ANON_KEY);

async function run() {
  const email = '360podcast@gmail.com';
  console.log("Triggering resetPasswordForEmail for:", email);
  const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: 'https://250proud.net/resources'
  });
  console.log("Result:", data, error);
}
run();
