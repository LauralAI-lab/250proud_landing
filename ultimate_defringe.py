import os
import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session

def ultimate_defringe(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Processing {input_path}")
    img = Image.open(input_path).convert("RGBA")
    
    # 1. Use U2Net Alpha Matting to get perfectly smooth neural boundaries 
    # and properly identify all internal enclosed white spaces.
    session = new_session("u2net")
    out = remove(
        img, 
        session=session, 
        alpha_matting=True, 
        alpha_matting_foreground_threshold=240, 
        alpha_matting_background_threshold=10, 
        alpha_matting_erode_size=5
    )
    
    # 2. Defringe / Decontaminate White Edges
    # rembg leaves a 1-2 pixel fuzzy white halo where the dark ink hits the white background.
    # We will mathematically erode the Alpha channel inward by 2 pixels to eat that halo,
    # then apply a slight blur to keep the edge beautifully smooth for apparel printing.
    arr = np.array(out)
    alpha = arr[:, :, 3]
    
    # Erode the alpha mask (shrinks the visible graphic by 2 pixels, entirely consuming the white edge)
    kernel = np.ones((3,3), np.uint8)
    eroded_alpha = cv2.erode(alpha, kernel, iterations=2)
    
    # Smooth the eroded edge so it prints cleanly without pixel-stepping
    smooth_alpha = cv2.GaussianBlur(eroded_alpha, (3,3), 0)
    
    # Reassign the perfected alpha channel
    arr[:, :, 3] = smooth_alpha
    
    # Extra safety: If there are ANY pixels left with low opacity that are purely white, kill them
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    is_white_fringe = (r > 200) & (g > 200) & (b > 200) & (smooth_alpha < 255) & (smooth_alpha > 0)
    arr[is_white_fringe, 3] = 0
    
    pil_img = Image.fromarray(arr)
    
    # 3. Canvas Prep
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    max_w = int(target_w * 0.90)
    max_h = int(target_h * 0.90)
    ratio = min(max_w / pil_img.width, max_h / pil_img.height)
    new_w = int(pil_img.width * ratio)
    new_h = int(pil_img.height * ratio)
    
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    final = Image.new("RGBA", (target_w, target_h), (0,0,0,0))
    paste_x = (target_w - new_w) // 2
    if top_heavy:
        paste_y = int(target_h * 0.15)
    else:
        paste_y = (target_h - new_h) // 2
        
    final.paste(pil_img, (paste_x, paste_y), pil_img)
    final.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved flawless defringed PNG to {output_path}")

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_tee_concept_1774272572521.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    # Overwriting the V2 corrected files
    ultimate_defringe(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v2_Corrected_4500x5400.png", 4500, 5400, top_heavy=True)
    ultimate_defringe(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v1_1200x1200.png", 1200, 1200, top_heavy=False)
