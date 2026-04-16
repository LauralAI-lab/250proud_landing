import os
import numpy as np
from PIL import Image

def vector_matte(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Executing Vector Matte on {input_path}")
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img).astype(float)
    
    r = arr[..., 0]
    g = arr[..., 1]
    b = arr[..., 2]
    
    # Calculate neutral chroma differential to identify purely white/grey pixels
    color_diff = np.abs(r - g) + np.abs(g - b) + np.abs(b - r)
    luma = (r + g + b) / 3.0
    
    # Target pure bright white space to strip it
    background_and_halo = (color_diff < 15) & (luma > 180)
    
    # Execute the knockout
    arr[background_and_halo, 3] = 0
    
    pil_img = Image.fromarray(arr.astype(np.uint8))
    
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
    print(f"Saved Flawless Vector to {output_path}")

if __name__ == "__main__":
    img1 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_minuteman_1774361494835.png"
    img2 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_rifle_1774361509984.png"
    img3 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_declaration_1774361524211.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    os.makedirs(out_dir, exist_ok=True)
    
    vector_matte(img1, f"{out_dir}/Minuteman_Schema_Transparent_4500x4500.png", 4500, 4500, top_heavy=False)
    vector_matte(img2, f"{out_dir}/Musket_Schema_Transparent_4500x4500.png", 4500, 4500, top_heavy=False)
    vector_matte(img3, f"{out_dir}/Declaration_Schema_Transparent_4500x4500.png", 4500, 4500, top_heavy=False)
