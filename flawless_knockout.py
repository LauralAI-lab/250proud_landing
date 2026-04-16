import cv2
import numpy as np
from PIL import Image
import os

def flawless_knockout(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Processing {input_path}")
    
    # 1. Read Image
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
    h, w = img.shape[:2]
    
    # 2. Add a 10px white border to guarantee the outer background is fully connected
    img = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    new_h, new_w = img.shape[:2]
    
    # 3. Floodfill the outer white background with MAGENTA (255, 0, 255)
    # OpenCV uses BGR, so Magenta is [255, 0, 255]
    mask = np.zeros((new_h + 2, new_w + 2), np.uint8)
    
    # Tolerance for 'white' (leaves heavily anti-aliased grey edges untouched by the initial fill)
    lo_diff = (40, 40, 40)
    up_diff = (40, 40, 40)
    cv2.floodFill(img, mask, (0, 0), (255, 0, 255), lo_diff, up_diff, cv2.FLOODFILL_FIXED_RANGE)
    
    # 4. Create a binary mask of just the MAGENTA area
    # Magenta in BGR is exactly B=255, G=0, R=255
    magenta_mask = cv2.inRange(img, np.array([255, 0, 255]), np.array([255, 0, 255]))
    
    # 5. AGGRESSIVE CHOKE: Dilate the magenta mask by 3 pixels. 
    # This forces the transparent area to physically bite into the graphic, completely
    # consuming the grey/white transition halo that causes printing ghosting.
    kernel = np.ones((3,3), np.uint8)
    magenta_mask_dilated = cv2.dilate(magenta_mask, kernel, iterations=2) # 2 iterations of 3x3 = ~2-3 px choke
    
    # 6. Smooth the mask slightly so the "bite" isn't perfectly jagged
    magenta_mask_dilated = cv2.GaussianBlur(magenta_mask_dilated, (3,3), 0)
    
    # 7. Convert original image (without magenta) to BGRA
    img_bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    # Apply the mask: wherever the dilated magenta mask is > 128, make it transparent
    img_bgra[magenta_mask_dilated > 128, 3] = 0
    img_bgra[magenta_mask_dilated > 128, 0:3] = 0 # Also make the color black to be safe
    
    # Optionally, for the remaining semi-transparent fringe (to avoid it showing up white)
    # We darken any light fringe pixels
    # Find fringe pixels (alpha > 0 and alpha < 255)
    # ... Skipped for now because the firm choke achieves a hard, clean edge.
    
    # 8. Remove the 10px border
    img_bgra = img_bgra[10:new_h-10, 10:new_w-10]
    
    # 9. Convert to PIL
    b, g, r, a = cv2.split(img_bgra)
    pil_img = Image.fromarray(cv2.merge((r, g, b, a)))
    
    # Autocrop
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    # Scale to dimensions
    max_w = int(target_w * 0.90)
    max_h = int(target_h * 0.90)
    ratio = min(max_w / pil_img.width, max_h / pil_img.height)
    new_w = int(pil_img.width * ratio)
    new_h = int(pil_img.height * ratio)
    
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Canvas
    final = Image.new("RGBA", (target_w, target_h), (0,0,0,0))
    paste_x = (target_w - new_w) // 2
    if top_heavy:
        paste_y = int(target_h * 0.15)
    else:
        paste_y = (target_h - new_h) // 2
        
    final.paste(pil_img, (paste_x, paste_y), pil_img)
    final.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved {output_path}")

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_tee_concept_1774272572521.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    flawless_knockout(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v2_Corrected_4500x5400.png", 4500, 5400, top_heavy=True)
    flawless_knockout(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v1_1200x1200.png", 1200, 1200, top_heavy=False)
