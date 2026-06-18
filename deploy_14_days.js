const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);
const BUCKET_NAME = 'daily_cards';

const factsToAdd = {
  "6-18": {
    "year": "1812",
    "text": "The United States declares war on Great Britain, beginning the War of 1812 and asserting its sovereignty as an independent nation.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1812_06_18_war_1781729133672.png",
    "filename": "1812-06-18_war_of_1812.png"
  },
  "6-19": {
    "year": "1865",
    "text": "Juneteenth - Union General Gordon Granger arrives in Galveston, Texas, and issues General Order No. 3, proclaiming the end of slavery in the state.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1865_06_19_juneteenth_1781729144317.png",
    "filename": "1865-06-19_juneteenth.png"
  },
  "6-20": {
    "year": "1863",
    "text": "West Virginia is admitted to the Union as the 35th U.S. state, born out of the turbulent separation from Virginia during the American Civil War.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1863_06_20_wv_statehood_1781730967921.png",
    "filename": "1863-06-20_wv_statehood.png"
  },
  "6-21": {
    "year": "1788",
    "text": "New Hampshire becomes the ninth state to ratify the United States Constitution, officially making it the supreme law of the land.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1788_06_21_nh_ratification_1781729165078.png",
    "filename": "1788-06-21_nh_ratification.png"
  },
  "6-22": {
    "year": "1944",
    "text": "President Franklin D. Roosevelt signs the G.I. Bill into law, providing immense educational and housing benefits for returning World War II veterans.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1944_06_22_gi_bill_edited_1781730987625.png",
    "filename": "1944-06-22_gi_bill.png"
  },
  "6-23": {
    "year": "1972",
    "text": "Title IX of the Education Amendments is signed into law, guaranteeing equal opportunity for women in any educational program receiving federal funds.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1972_06_23_title_ix_1781729194165.png",
    "filename": "1972-06-23_title_ix.png"
  },
  "6-24": {
    "year": "1948",
    "text": "The Berlin Airlift begins as the United States and its allies start dropping massive amounts of supplies into blockaded West Berlin.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1948_06_24_berlin_airlift_1781729202750.png",
    "filename": "1948-06-24_berlin_airlift.png"
  },
  "6-25": {
    "year": "1876",
    "text": "The Battle of the Little Bighorn begins in the Montana Territory, where Lt. Col. George Custer and the 7th Cavalry clash with Lakota and Cheyenne warriors.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1876_06_25_little_bighorn_1781729212794.png",
    "filename": "1876-06-25_little_bighorn.png"
  },
  "6-26": {
    "year": "1917",
    "text": "The first United States combat troops arrive in France during World War I, marking America's entry onto the battlefields of Europe.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1917_06_26_ww1_france_1781729232381.png",
    "filename": "1917-06-26_ww1_france.png"
  },
  "6-27": {
    "year": "1844",
    "text": "Joseph Smith, the founder of the Latter Day Saint movement, and his brother Hyrum are killed by a mob at the Carthage Jail in Illinois.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1844_06_27_carthage_jail_1781729242007.png",
    "filename": "1844-06-27_carthage_jail.png"
  },
  "6-28": {
    "year": "1778",
    "text": "The Battle of Monmouth takes place during the intense summer heat, as George Washington rallies the Continental Army against British forces in New Jersey.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1778_06_28_battle_of_monmouth_1781729252483.png",
    "filename": "1778-06-28_battle_of_monmouth.png"
  },
  "6-29": {
    "year": "1956",
    "text": "President Dwight D. Eisenhower signs the Federal-Aid Highway Act, authorizing the creation of the massive 41,000-mile Interstate Highway System.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1956_06_29_highway_act_1781729272420.png",
    "filename": "1956-06-29_highway_act.png"
  },
  "6-30": {
    "year": "1906",
    "text": "President Theodore Roosevelt signs the Pure Food and Drug Act into law, creating federal regulations to protect consumers and ensure truth in labeling.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1906_06_30_food_drug_act_1781729282562.png",
    "filename": "1906-06-30_food_drug_act.png"
  },
  "7-1": {
    "year": "1863",
    "text": "The Battle of Gettysburg begins. It becomes the largest battle ever fought in North America and a major turning point of the American Civil War.",
    "local_image": "/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/1863_07_01_gettysburg_1781729292514.png",
    "filename": "1863-07-01_gettysburg.png"
  }
};

async function run() {
  console.log('Starting Supabase Storage upload...');
  let htmlPath = './today-in-history.html';
  let html = fs.readFileSync(htmlPath, 'utf8');

  for (const [dateKey, factInfo] of Object.entries(factsToAdd)) {
    const fileBuffer = fs.readFileSync(factInfo.local_image);
    console.log(`Uploading ${factInfo.filename}...`);
    
    const { data, error } = await supabase.storage
      .from(BUCKET_NAME)
      .upload(factInfo.filename, fileBuffer, {
        contentType: 'image/png',
        upsert: true
      });

    if (error) {
      console.error(`Failed to upload ${factInfo.filename}:`, error.message);
      continue;
    }

    const { data: publicUrlData } = supabase.storage
      .from(BUCKET_NAME)
      .getPublicUrl(factInfo.filename);
      
    const publicUrl = publicUrlData.publicUrl;
    console.log(`Uploaded -> ${publicUrl}`);
    
    // Inject into HTML
    // We look for "6-8": { ... }, and append the new facts after it or just replace the end of the historyFacts object
    // A simple robust way is to just find the `const historyFacts = {` and parse/stringify, but it's embedded in script.
    // Instead, let's insert before `                "7-4": {`
    
    const insertionStr = `                "${dateKey}": {
                    "year": "${factInfo.year}",
                    "text": "${factInfo.text.replace(/"/g, '\\"')}",
                    "supabase_image": "${publicUrl}"
                },\n`;
                
    // Insert right before "7-4": {
    html = html.replace('"7-4": {', insertionStr + '                "7-4": {');
  }

  fs.writeFileSync(htmlPath, html);
  console.log('Successfully patched today-in-history.html with 14 new days!');
}

run();
