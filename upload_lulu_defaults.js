require('dotenv').config();
const fs = require('fs');
const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY);

async function run() {
    console.log("Uploading Interior...");
    const interiorBuffer = fs.readFileSync('Lulu_Default_Interior.pdf');
    await supabase.storage.from('b2b_pdfs').upload('completed/Lulu_Default_Interior.pdf', interiorBuffer, { contentType: 'application/pdf', upsert: true });
    
    console.log("Uploading Cover...");
    const coverBuffer = fs.readFileSync('Lulu_Default_Cover_v2.pdf');
    await supabase.storage.from('b2b_pdfs').upload('completed/Lulu_Default_Cover_v2.pdf', coverBuffer, { contentType: 'application/pdf', upsert: true });

    const { data: intData } = supabase.storage.from('b2b_pdfs').getPublicUrl('completed/Lulu_Default_Interior.pdf');
    const { data: covData } = supabase.storage.from('b2b_pdfs').getPublicUrl('completed/Lulu_Default_Cover_v2.pdf');

    console.log("Interior URL: " + intData.publicUrl);
    console.log("Cover URL: " + covData.publicUrl);
}

run().catch(console.error);
