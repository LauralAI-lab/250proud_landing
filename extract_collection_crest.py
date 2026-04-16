import numpy as np
import os
from PIL import Image

def process():
    print("Extracting Blueprint Collection Master Crest...")
    
    raw_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_collection_crest_1774552523886.png"
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Blueprint_Collection_Master_Crest_Transparent.png")
    
    img_raw = Image.open(raw_path).convert("RGBA")
    arr = np.array(img_raw)
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
    # Bold pure black/navy streetwear branding color mapping
    arr[:,:,0] = 20
    arr[:,:,1] = 25
    arr[:,:,2] = 30
    
    # Extract tight antialiased transparency structure
    normalized = gray / 255.0
    alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
    arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
    
    clean_art = Image.fromarray(arr.astype(np.uint8))
    
    # Slice off dead white-space bounding box accurately
    bbox = clean_art.getbbox()
    if bbox:
        clean_art = clean_art.crop(bbox)
        
    clean_art.save(out_path, "PNG", dpi=(300,300))
    print(f"Master Crest generated cleanly: {out_path}")

if __name__ == "__main__":
    process()
