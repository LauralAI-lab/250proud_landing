import cv2
import numpy as np
from PIL import Image

def perfect_knockout(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Processing {input_path}")
    # Read image
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    # If image lacks alpha, add it
    if img.shape[2] == 3:
        b, g, r = cv2.split(img)
        a = np.ones(b.shape, dtype=b.dtype) * 255
        img_bgra = cv2.merge((b, g, r, a))
    else:
        b, g, r, a = cv2.split(img)
        img = cv2.merge((b,g,r)) # Use 3 channels for floodfill
        img_bgra = cv2.merge((b,g,r,a))

    h, w = img.shape[:2]
    
    # Create mask for floodfill
    # floodFill mask needs to be 2 pixels wider and taller than the image
    mask = np.zeros((h + 2, w + 2), np.uint8)
    
    # We flood fill from the top-left corner, which is background white
    # Tolerance for what is considered 'white background'
    lo_diff = (10, 10, 10)
    up_diff = (10, 10, 10)
    
    # floodFill on 3-channel BGR
    cv2.floodFill(img, mask, (0, 0), (255, 255, 255), lo_diff, up_diff, cv2.FLOODFILL_FIXED_RANGE)
    # The mask array now contains 1 in areas that were filled.
    
    # The true background mask
    bg_mask = mask[1:h+1, 1:w+1]
    
    # To eliminate "white ghosting", we need to bite slightly into the fg.
    # Dilate the background mask by 1-2 pixels
    kernel = np.ones((3,3), np.uint8)
    bg_mask_dilated = cv2.dilate(bg_mask, kernel, iterations=2)
    
    # Set alpha channel to 0 where bg_mask_dilated is > 0
    img_bgra[bg_mask_dilated > 0, 3] = 0
    
    # Convert back to PIL
    b, g, r, a = cv2.split(img_bgra)
    pil_img = Image.fromarray(cv2.merge((r, g, b, a)))
    
    # Crop to transparent bounding box
    bbox = pil_img.getbbox()
    pil_img = pil_img.crop(bbox)
    
    # Resize to dimensions
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
    print(f"Saved {output_path} successfully without white ghosting.")

if __name__ == "__main__":
    # Original beloved graphic
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_concept_1774271654163.png"
    # Badge graphic (we liked it, so we keep processing it the same way)
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    import os
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    perfect_knockout(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v1_Original_4500x5400.png", 4500, 5400, top_heavy=True)
    perfect_knockout(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v1_1200x1200.png", 1200, 1200, top_heavy=False)

