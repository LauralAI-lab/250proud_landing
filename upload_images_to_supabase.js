const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);

const BUCKET_NAME = 'daily_cards';

const directories = [
  './250Proud_Daily_Cards/2026-05/Batch_2026-05-19_to_2026-05-25/Images',
  './250Proud_Daily_Cards/2026-05/Batch_2026-05-26_to_2026-06-01/Images'
];

async function run() {
  console.log('Starting Supabase Storage upload...');

  // 1. Check or create bucket
  const { data: buckets, error: listError } = await supabase.storage.listBuckets();
  if (listError) {
    console.error('Error listing buckets:', listError);
    return;
  }

  let bucketExists = buckets.some(b => b.name === BUCKET_NAME);
  if (!bucketExists) {
    console.log(`Creating public bucket "${BUCKET_NAME}"...`);
    const { error: createError } = await supabase.storage.createBucket(BUCKET_NAME, {
      public: true,
      allowedMimeTypes: ['image/png'],
      fileSizeLimit: 5242880 // 5MB
    });
    if (createError) {
      console.error('Error creating bucket:', createError);
      return;
    }
    console.log(`Bucket "${BUCKET_NAME}" created successfully.`);
  } else {
    console.log(`Bucket "${BUCKET_NAME}" already exists.`);
  }

  // 2. Upload images
  const uploadedFiles = {};
  
  for (const dir of directories) {
    const resolvedDir = path.resolve(dir);
    if (!fs.existsSync(resolvedDir)) {
      console.warn(`Directory not found: ${resolvedDir}`);
      continue;
    }

    const files = fs.readdirSync(resolvedDir).filter(f => f.endsWith('.png'));
    console.log(`Found ${files.length} images in ${path.basename(resolvedDir)}`);

    for (const file of files) {
      const filePath = path.join(resolvedDir, file);
      const fileBuffer = fs.readFileSync(filePath);
      
      console.log(`Uploading ${file}...`);
      const { data, error } = await supabase.storage
        .from(BUCKET_NAME)
        .upload(file, fileBuffer, {
          contentType: 'image/png',
          upsert: true
        });

      if (error) {
        console.error(`Failed to upload ${file}:`, error.message);
      } else {
        const { data: publicUrlData } = supabase.storage
          .from(BUCKET_NAME)
          .getPublicUrl(file);
        
        uploadedFiles[file] = publicUrlData.publicUrl;
        console.log(`Uploaded ${file} -> ${publicUrlData.publicUrl}`);
      }
    }
  }

  console.log('\nAll uploads processed. Results summary:');
  console.log(JSON.stringify(uploadedFiles, null, 2));

  // Save the mapping to a JSON file in the same folder
  fs.writeFileSync(
    './daily_images_mapping.json',
    JSON.stringify(uploadedFiles, null, 2)
  );
}

run();
