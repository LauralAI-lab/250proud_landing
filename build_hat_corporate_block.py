import os
import numpy as np
from PIL import Image

def build_block():
    print("Forging the Tech Block Headwear Graphic...")
    master_logo_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Official_Blueprint_Tech_Block_Logo.png"
    master_logo_base = Image.open(master_logo_path).convert("RGBA")
    
    # Amputate the rigid framework explicitly freeing the logo type matrix to organic float
    b_val = 35
    master_logo = master_logo_base.crop((b_val, b_val, master_logo_base.width - b_val, master_logo_base.height - b_val))
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Headwear"
    os.makedirs(out_dir, exist_ok=True)
    
    l_arr = np.array(master_logo)
    lr, lg, lb, la = l_arr[:,:,0].astype(float), l_arr[:,:,1].astype(float), l_arr[:,:,2].astype(float), l_arr[:,:,3].astype(float)
    lgray = 0.2989 * lr + 0.5870 * lg + 0.1140 * lb
    
    def save_variant(color_name, r_val, g_val, b_val):
        arr = l_arr.copy()
        arr[:,:,0] = r_val
        arr[:,:,1] = g_val
        arr[:,:,2] = b_val
        
        # Transparent logic mapping pristine array to 0 alpha
        alpha = np.clip((240.0 - lgray) / 50.0, 0, 1)
        arr[:,:,3] = (alpha * la).astype(np.uint8)
        
        img = Image.fromarray(arr.astype(np.uint8))
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        
        # Extreme Wide structure exclusively crafted for frontal curve cap mapping frames
        scale = 1150 / img.size[0]
        c_w, c_h = int(img.size[0]*scale), int(img.size[1]*scale)
        img = img.resize((c_w, c_h), Image.Resampling.LANCZOS)
        
        canvas = Image.new('RGBA', (1200, 600), (0,0,0,0))
        px = (1200 - c_w) // 2
        py = (600 - c_h) // 2
        canvas.paste(img, (px, py), img)
        
        out_path = os.path.join(out_dir, f"Hat_Graphic_Tech_Block_{color_name}_1200x600.png")
        canvas.save(out_path, "PNG", dpi=(300,300))
        print(f"Saved {color_name} Tech Block directly to {out_path}")
        
    save_variant("Color_Null_Dark", 20, 25, 30) # Used essentially on purely white/cream colored hats
    save_variant("Color_Null_Light", 245, 245, 245) # Sits beautifully natively on completely black or navy crowns

if __name__ == "__main__":
    build_block()
