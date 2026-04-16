import os
import numpy as np
from PIL import Image
from rembg import remove, new_session

def premium_knockout(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Processing {input_path}")
    img = Image.open(input_path).convert("RGBA")
    
    # Use rembg with alpha matting. This uses a neural network to find the exact edge map 
    # of the foreground, including internal loops like the inside of letters, without destroying shapes.
    # Alpha matting pulls soft edges perfectly for distressed graphics.
    session = new_session("u2net")
    # Tweak matting thresholds to protect the graphic while dropping the background
    out = remove(
        img, 
        session=session, 
        alpha_matting=True, 
        alpha_matting_foreground_threshold=240, 
        alpha_matting_background_threshold=10, 
        alpha_matting_erode_size=7
    )
    
    # Convert to numpy array to mathematically deal with 'white ghosting' (halation)
    arr = np.array(out)
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    
    # Halation fix: Any pixel that is partially transparent (edge) AND computationally very close to white,
    # we force its alpha to 0 to prevent a white glow on dark shirts.
    is_fringe = (a > 0) & (a < 255)
    is_whitish = (r > 220) & (g > 220) & (b > 220)
    
    # Force purely anti-aliased white edge pixels to be invisible
    arr[is_fringe & is_whitish, 3] = 0
    
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
    
    # Core upscale
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
    print(f"Saved highly refined structural PNG to {output_path}")

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_tee_concept_1774272572521.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    premium_knockout(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v2_Corrected_4500x5400.png", 4500, 5400, top_heavy=True)
    premium_knockout(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v1_1200x1200.png", 1200, 1200, top_heavy=False)

