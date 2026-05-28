require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY;
const SUPABASE_SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

async function run() {
  const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
  const client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

  const testEmail = `test_rls_${Date.now()}@example.com`;
  const testPassword = 'password123!';

  console.log("1. Creating test user in Supabase Auth...");
  const { data: authData, error: authError } = await adminClient.auth.admin.createUser({
    email: testEmail,
    password: testPassword,
    email_confirm: true
  });

  if (authError) {
    console.error("Auth creation failed:", authError);
    return;
  }

  const userId = authData.user.id;
  console.log("Created User ID:", userId);

  console.log("2. Inserting test user record into 'users' table...");
  const { error: insertError } = await adminClient.from('users').insert({
    id: userId,
    email: testEmail,
    username: 'test_rls_user',
    company_name: 'Test RLS Corp',
    book_slug: `test-rls-${Date.now()}`
  });

  if (insertError) {
    console.error("Database insert failed:", insertError);
    // Cleanup
    await adminClient.auth.admin.deleteUser(userId);
    return;
  }

  console.log("3. Logging in as the test user via the public Anon client...");
  const { data: loginData, error: loginError } = await client.auth.signInWithPassword({
    email: testEmail,
    password: testPassword
  });

  if (loginError) {
    console.error("Public client login failed:", loginError);
    // Cleanup
    await adminClient.from('users').delete().eq('id', userId);
    await adminClient.auth.admin.deleteUser(userId);
    return;
  }

  console.log("4. Attempting to select from 'users' table using the public Anon client...");
  const { data: userData, error: selectError } = await client
    .from('users')
    .select('*')
    .eq('id', userId)
    .single();

  if (selectError) {
    console.log("❌ Select failed! Error:", selectError.message, selectError);
  } else {
    console.log("✅ Select succeeded! Data:", userData);
  }

  console.log("5. Cleaning up test user and database record...");
  await adminClient.from('users').delete().eq('id', userId);
  await adminClient.auth.admin.deleteUser(userId);
  console.log("Done.");
}

run();
