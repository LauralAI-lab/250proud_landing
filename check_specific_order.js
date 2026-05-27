require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
const supabase = createClient(process.env.SUPABASE_URL, supabaseKey);


async function run() {
    console.log("Searching for Whoopie or Schmoe in b2b_orders...");
    const { data: orders, error: ordersError } = await supabase
        .from('b2b_orders')
        .select('*');
    
    if (ordersError) {
        console.error(ordersError);
    } else {
        const matches = orders.filter(o => 
            (o.company_name && o.company_name.toLowerCase().includes('whoopie')) ||
            (o.company_name && o.company_name.toLowerCase().includes('schmoe')) ||
            (o.email && o.email.toLowerCase().includes('whoopie')) ||
            (o.email && o.email.toLowerCase().includes('schmoe'))
        );
        console.log(`Found ${matches.length} matching orders:`, matches);
    }

    console.log("\nSearching for Whoopie or Schmoe in users...");
    const { data: users, error: usersError } = await supabase
        .from('users')
        .select('*');
    
    if (usersError) {
        console.error(usersError);
    } else {
        const matches = users.filter(u => 
            (u.company_name && u.company_name.toLowerCase().includes('whoopie')) ||
            (u.company_name && u.company_name.toLowerCase().includes('schmoe')) ||
            (u.username && u.username.toLowerCase().includes('whoopie')) ||
            (u.username && u.username.toLowerCase().includes('schmoe')) ||
            (u.email && u.email.toLowerCase().includes('whoopie')) ||
            (u.email && u.email.toLowerCase().includes('schmoe'))
        );
        console.log(`Found ${matches.length} matching users:`, matches);
    }
}
run();

