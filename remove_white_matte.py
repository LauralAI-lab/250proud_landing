import os
import numpy as np
from PIL import Image

def remove_white_matte(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Executing Chroma-Luma Split Key on {input_path}")
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img)
    
    r = arr[..., 0].astype(float)
    g = arr[..., 1].astype(float)
    b = arr[..., 2].astype(float)
    a = arr[..., 3]
    
    # 1. Calculate Chroma Difference (How "colorful" the pixel is)
    # A perfectly grey/white pixel has R = G = B, so diff = 0
    # Vintage cream (245, 235, 215) has diff ~60
    color_diff = np.abs(r - g) + np.abs(g - b) + np.abs(b - r)
    
    # 2. Calculate Luma (Brightness)
    luma = (r + g + b) / 3.0
    
    # Base configuration
    new_r, new_g, new_b, new_a = r.copy(), g.copy(), b.copy(), a.copy()
    
    # 3. Create masks
    # "Colorful" pixels belong to the graphic (Navy, Red, Gold, Cream)
    is_colorful = color_diff >= 18  # Set slightly lower than 25 to catch faint creams
    
    # Monochrome pixels are either White Background, Grey Halo, or Deep Black
    is_monochrome = ~is_colorful
    
    # Within monochromatic areas:
    is_pure_white = is_monochrome & (luma > 248)
    is_grey_halo = is_monochrome & (luma > 80) & (luma <= 248)
    is_deep_black = is_monochrome & (luma <= 80)
    
    # 4. Apply rules
    # A) Colorful ink: 100% opaque
    new_a[is_colorful] = 255
    
    # B) Pure white background: 100% transparent
    new_a[is_pure_white] = 0
    
    # C) Grey Halo (anti-aliased edges transitioning into the white background)
    # We map alpha inversely to brightness so lighter greys are more transparent
    # luma 248 -> Alpha 0
    # luma 80 -> Alpha 255
    # y = -(255/168)*x + (255*248/168)
    halo_alpha = np.clip(((248 - luma[is_grey_halo]) / 168.0) * 255.0, 0, 255)
    new_a[is_grey_halo] = halo_alpha
    
    # To fix "white ghosting" completely on dark shirts, we decontaminate the remaining grey halo
    # by darkening it to deep navy (30, 40, 60) so it blends seamlessly into the shirt fabric.
    new_r[is_grey_halo] = 30
    new_g[is_grey_halo] = 40
    new_b[is_grey_halo] = 60
    
    # D) Deep Black: 100% opaque
    new_a[is_deep_black] = 255
    
    # 5. Reconstruct Array
    arr[..., 0] = new_r.astype(np.uint8)
    arr[..., 1] = new_g.astype(np.uint8)
    arr[..., 2] = new_b.astype(np.uint8)
    arr[..., 3] = new_a.astype(np.uint8)
    
    pil_img = Image.fromarray(arr)
    
    # 6. Autocrop
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    # 7. Scale
    max_w = int(target_w * 0.90)
    max_h = int(target_h * 0.90)
    ratio = min(max_w / pil_img.width, max_h / pil_img.height)
    new_w = int(pil_img.width * ratio)
    new_h = int(pil_img.height * ratio)
    
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 8. Canvas Prep
    final = Image.new("RGBA", (target_w, target_h), (0,0,0,0))
    paste_x = (target_w - new_w) // 2
    if top_heavy:
        paste_y = int(target_h * 0.15)
    else:
        paste_y = (target_h - new_h) // 2
        
    final.paste(pil_img, (paste_x, paste_y), pil_img)
    final.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved Flawless Graphic to {output_path}")

if __name__ == "__main__":
    # Point precisely back to the original V1 files as requested!
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_concept_1774271654163.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    remove_white_matte(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v1_ChromaKey_4500x5400.png", 4500, 5400, top_heavy=True)
    remove_white_matte(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v1_ChromaKey_1200x1200.png", 1200, 1200, top_heavy=False)
