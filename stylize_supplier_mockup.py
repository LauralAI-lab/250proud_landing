import cv2
import numpy as np
from PIL import Image, ImageFilter
import glob
import os

def build_supplier_mockup():
    print("Isolating Native Printify layout...")
    
    # Target User's flat white supplier mockup
    raw_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1774374574741.png"
    img = cv2.imread(raw_path, cv2.IMREAD_UNCHANGED)
    
    # Assume 4 channels might already exist, but we force flood over white bounds
    if img.shape[2] == 4:
        b, g, r, a = cv2.split(img)
        img = cv2.merge((b,g,r))
        
    h, w = img.shape[:2]
    
    # Extract authentic outline directly from the pure white printify void
    mask = np.zeros((h + 2, w + 2), np.uint8)
    lo_diff = (8, 8, 8)
    up_diff = (8, 8, 8)
    cv2.floodFill(img, mask, (0, 0), (0, 255, 0), lo_diff, up_diff, cv2.FLOODFILL_FIXED_RANGE)
    
    # Read the flooded void territory
    bg_mask = mask[1:h+1, 1:w+1]
    
    # Micro-dilate to bite physically onto any white aliasing edges 
    kernel = np.ones((2,2), np.uint8)
    bg_mask = cv2.dilate(bg_mask, kernel, iterations=1)
    
    orig = cv2.imread(raw_path, cv2.IMREAD_UNCHANGED)
    ob, og, or_ = cv2.split(orig)[:3]
    
    alpha = np.ones(ob.shape, dtype=np.uint8) * 255
    alpha[bg_mask > 0] = 0
    
    isolated_hoodie = Image.fromarray(cv2.merge((or_, og, ob, alpha)))
    
    bbox = isolated_hoodie.getbbox()
    if bbox:
        isolated_hoodie = isolated_hoodie.crop(bbox)
        
    # Scale to a dominant hero-graphic physical dimension
    target_w = 800
    scale = target_w / isolated_hoodie.size[0]
    new_h = int(isolated_hoodie.size[1] * scale)
    isolated_hoodie = isolated_hoodie.resize((target_w, new_h), Image.Resampling.LANCZOS)
    
    # Force organic studio lighting (heavy directional drop shadow)
    shadow_alpha = isolated_hoodie.split()[3]
    shadow = Image.new("RGBA", isolated_hoodie.size, (5, 5, 8, 255))
    shadow.putalpha(shadow_alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(18)) # Huge organic studio blur
    
    # Find the dynamically generated dark concrete backdrop
    brain_dir = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/slate_studio_floor_*.png"
    floor_files = glob.glob(brain_dir)
    floor_files.sort(key=os.path.getmtime, reverse=True)
    floor_path = floor_files[0]
    
    print(f"Compositing over raw concrete studio: {floor_path}")
    bg = Image.open(floor_path).convert("RGBA")
    
    # Center exact placement on the shadow block
    paste_x = (bg.size[0] - shadow.size[0]) // 2
    paste_y = (bg.size[1] - shadow.size[1]) // 2
    
    # Drop shadow natively mapped beneath
    bg.paste(shadow, (paste_x - 5, paste_y + 15), mask=shadow.split()[3])
    
    # Drop native authentic structured garment on top
    bg.paste(isolated_hoodie, (paste_x, paste_y), mask=isolated_hoodie.split()[3])
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Mockups/Editorial_Hero_Mockups"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Supplier_Verified_Apollo_Eagle_Hero.jpg")
    
    bg.convert("RGB").save(out_path, "JPEG", quality=98)
    print(f"Completely stylized native verification composite saved: {out_path}")

if __name__ == "__main__":
    build_supplier_mockup()
