import os
import numpy as np
from PIL import Image

def black_luma_key(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Processing Black Key knockout for {input_path}")
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    
    # Extract channels
    r = arr[..., 0].astype(float)
    g = arr[..., 1].astype(float)
    b = arr[..., 2].astype(float)
    
    # Calculate geometric color distance from absolute pure Black (0,0,0)
    dist = np.sqrt(r**2 + g**2 + b**2)
    
    # Establish a ramp to blend the anti-aliased edge perfectly.
    # Pixels extremely close to black (dist <= 15) become 100% transparent.
    # Pixels representing Deep Navy (dist >= 60) remain 100% opaque.
    # Everything in between gets a mathematically smooth alpha transition.
    new_a = np.interp(dist, [20, 60], [0, 255]).astype(np.uint8)
    
    # Reassign alpha channel
    arr[..., 3] = new_a
    
    # Rebuild image
    pil_img = Image.fromarray(arr)
    
    # Autocrop transparent borders
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    # Scale to print dimensions safely
    max_w = int(target_w * 0.90)
    max_h = int(target_h * 0.90)
    ratio = min(max_w / pil_img.width, max_h / pil_img.height)
    new_w = int(pil_img.width * ratio)
    new_h = int(pil_img.height * ratio)
    
    # Core upscale using Lanczos
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Build 300 DPI Transparent Canvas
    final = Image.new("RGBA", (target_w, target_h), (0,0,0,0))
    paste_x = (target_w - new_w) // 2
    if top_heavy:
        paste_y = int(target_h * 0.15)
    else:
        paste_y = (target_h - new_h) // 2
        
    final.paste(pil_img, (paste_x, paste_y), pil_img)
    final.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved flawless dark-apparel PNG to {output_path}")

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_v4_black_tee_1774276609474.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_v4_black_badge_1774276625009.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    # Generate the finalized T-shirt
    black_luma_key(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v4_Final_4500x5400.png", 4500, 5400, top_heavy=True)
    black_luma_key(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v4_Final_1200x1200.png", 1200, 1200, top_heavy=False)
