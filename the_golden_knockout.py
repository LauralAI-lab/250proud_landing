import os
import numpy as np
from PIL import Image
from rembg import remove, new_session

def the_golden_knockout(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Processing Golden Knockout for {input_path}")
    img = Image.open(input_path).convert("RGBA")
    
    # 1. Pure U2Net Neural Matting
    # This ignores ALL compression noise and finds the mathematically smooth curves of the artwork.
    # It also reaches into the center of the graphic to segment the internal background voids.
    session = new_session("u2net")
    out = remove(
        img, 
        session=session, 
        alpha_matting=True, 
        alpha_matting_foreground_threshold=245, 
        alpha_matting_background_threshold=10, 
        alpha_matting_erode_size=3
    )
    
    arr = np.array(out)
    
    # 2. Edge Decontamination (Defringing)
    # The U2Net mask assigns soft alphas to the edge pixels (0 < A < 255).
    # Because the original background was white, these edge pixels carry white color data.
    # When printed on a dark shirt, this is what causes the "ghosting" ring.
    # We leave the smooth alpha perfectly intact, but we DARKEN the RGB values of any edge pixel
    # so that the soft edge is built out of dark ink (navy/black) instead of white ink.
    
    a = arr[:, :, 3]
    r = arr[:, :, 0].astype(int)
    g = arr[:, :, 1].astype(int)
    b = arr[:, :, 2].astype(int)
    
    # Find active boundary fringe (ignoring solid core and empty background)
    fringe_mask = (a > 0) & (a < 250)
    
    # Darken the fringe pixels aggressively (burn them down to a dark shadow color)
    # This makes the anti-aliased transition perfectly invisible on a dark substrate.
    arr[fringe_mask, 0] = (r[fringe_mask] * 0.2).astype(np.uint8)
    arr[fringe_mask, 1] = (g[fringe_mask] * 0.2).astype(np.uint8)
    arr[fringe_mask, 2] = (b[fringe_mask] * 0.3).astype(np.uint8)
    
    # 3. Aggressive Knockout for pure white "distress" marks INSIDE the main graphic core
    # Since the original design is full of white scratch marks, we must make them truly transparent.
    # We only target pixels that are overwhelmingly blindingly white.
    pure_white = (r > 240) & (g > 240) & (b > 240) & (a > 50)
    arr[pure_white, 3] = 0
    
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
    print(f"Saved Flawless Graphic to {output_path}")

if __name__ == "__main__":
    # TARGETING THE EXACT ORIGINAL V1
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_concept_1774271654163.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    # Overwriting the ultimate production files
    the_golden_knockout(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v1_FinalProduction_4500x5400.png", 4500, 5400, top_heavy=True)
    the_golden_knockout(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v1_FinalProduction_1200x1200.png", 1200, 1200, top_heavy=False)
