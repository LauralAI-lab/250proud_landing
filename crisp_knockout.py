import os
import numpy as np
from PIL import Image
from rembg import remove, new_session

def crisp_knockout(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Processing razor-sharp knockout for {input_path}")
    img = Image.open(input_path).convert("RGBA")
    
    session = new_session("u2net")
    # Base removal ignores matting for hard edges, handles the outside perfectly.
    out = remove(img, session=session, alpha_matting=False)
    
    # Array conversion for internal puncturing
    arr = np.array(out)
    r = arr[..., 0].astype(int)
    g = arr[..., 1].astype(int)
    b = arr[..., 2].astype(int)
    
    # Calculate color differential to separate neutral colors (white/grey) from intentional colors (cream/gold/red)
    color_diff = np.abs(r - g) + np.abs(g - b) + np.abs(b - r)
    
    # We strictly target enclosed pixels that are relatively bright (Luma > 150) AND lacking color saturation
    is_colorless = color_diff < 20
    is_bright = (r > 150) & (g > 150) & (b > 150)
    
    # Punch out the internal white negative spaces perfectly (including light grey anti-aliasing rings inside them)
    # This leaves the Vintage Cream untouched because its color_diff is roughly 60.
    arr[is_colorless & is_bright, 3] = 0
    
    pil_img = Image.fromarray(arr)
    
    # Autocrop & Scale
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    max_w = int(target_w * 0.90)
    max_h = int(target_h * 0.90)
    ratio = min(max_w / pil_img.width, max_h / pil_img.height)
    new_w = int(pil_img.width * ratio)
    new_h = int(pil_img.height * ratio)
    
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    final_canvas = Image.new("RGBA", (target_w, target_h), (0,0,0,0))
    paste_x = (target_w - new_w) // 2
    if top_heavy:
        paste_y = int(target_h * 0.15)
    else:
        paste_y = (target_h - new_h) // 2
        
    final_canvas.paste(pil_img, (paste_x, paste_y), pil_img)
    final_canvas.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved razor-sharp transparent output to {output_path}")

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_fresh_clean_concept_1774292101136.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_fresh_clean_badge_1774292142875.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    crisp_knockout(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v5_FlawlessVector_4500x5400.png", 4500, 5400, top_heavy=True)
    crisp_knockout(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v5_FlawlessVector_1200x1200.png", 1200, 1200, top_heavy=False)
