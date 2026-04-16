import os
import numpy as np
from PIL import Image

def process():
    print("Forging the Crest Headwear Graphic...")
    raw_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_collection_crest_1774552523886.png"
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Headwear"
    os.makedirs(out_dir, exist_ok=True)
    
    img_raw = Image.open(raw_path).convert("RGBA")
    arr = np.array(img_raw)
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
    # Process mathematically precise Dark and Light vectors allowing flexible physical printing options 
    def save_variant(color_name, r_val, g_val, b_val):
        a_arr = arr.copy()
        a_arr[:,:,0] = r_val
        a_arr[:,:,1] = g_val
        a_arr[:,:,2] = b_val
        
        normalized = gray / 255.0
        
        # Leverage algorithmic threshold mapping since AI lines are pure black on pristine white backgrounds
        alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
        a_arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
        
        clean = Image.fromarray(a_arr.astype(np.uint8))
        bbox = clean.getbbox()
        if bbox:
            clean = clean.crop(bbox)
            
        # Target tight 1200px box scaling required by major 3x3in patch arrays 
        scale = 1150 / max(clean.size[0], clean.size[1])
        c_w, c_h = int(clean.size[0] * scale), int(clean.size[1] * scale)
        clean = clean.resize((c_w, c_h), Image.Resampling.LANCZOS)
        
        canvas = Image.new('RGBA', (1200, 1200), (0,0,0,0))
        px = (1200 - c_w) // 2
        py = (1200 - c_h) // 2
        canvas.paste(clean, (px, py), clean)
        
        out_path = os.path.join(out_dir, f"Hat_Graphic_Crest_{color_name}_1200x1200.png")
        canvas.save(out_path, "PNG", dpi=(300,300))
        print(f"Saved {color_name} Crest natively scaled to {out_path}")
        
    save_variant("Dark", 20, 25, 30)
    save_variant("Light", 245, 245, 245)

if __name__ == "__main__":
    process()
