import urllib.request
import re
import os

def extract_shopify_mockup():
    print("Initializing Shopify Visual Extract Sequence natively...")
    url = "https://lauralai-one.myshopify.com/products/eagle-claw-250-under-armour%C2%AE-dad-hat?variant=46325801648327"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Using Regex to identify the main og:image
            match = re.search(r'<meta\s+(?:property|name)="og:image"\s+content="([^"]+)"', html)
            
            if match:
                img_url = match.group(1)
                
                # Check for standard Shopify format (e.g. "?v=...") and grab main hi-res variant
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                    
                print(f"Target Acquired: {img_url}")
                
                # Pipe the data down into a local asset
                save_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/eagle_claw_cap_live.jpg"
                urllib.request.urlretrieve(img_url, save_path)
                print(f"Extraction Successful: {save_path}")
                
            else:
                print("CRITICAL: Failed to isolate the Og:Image metatag on the Shopify layout.")
                
    except Exception as e:
        print(f"Protocol Error: {e}")

if __name__ == "__main__":
    extract_shopify_mockup()
