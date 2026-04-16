import os
import numpy as np
from PIL import Image, ImageDraw

def extract_white_bg(img_path):
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    
    # Establish a secondary alpha extraction channel
    # Deeply scan the four perimeter corners natively using a thresholded flood-fill
    # to perfectly strip the generation background while preserving structural internal whites (Eagle's head).
    mask = Image.new('L', img.size, 255)
    
    # Push 15% tolerance to catch DALL-E compression artifacts along the border
    ImageDraw.floodfill(mask, (0, 0), 0, thresh=15)
    ImageDraw.floodfill(mask, (img.size[0]-1, 0), 0, thresh=15)
    ImageDraw.floodfill(mask, (0, img.size[1]-1), 0, thresh=15)
    ImageDraw.floodfill(mask, (img.size[0]-1, img.size[1]-1), 0, thresh=15)
    
    mask_arr = np.array(mask)
    arr[:,:,3] = mask_arr
    
    clean = Image.fromarray(arr)
    bbox = clean.getbbox()
    if bbox:
        clean = clean.crop(bbox)
        
    return clean

def build_formats(raw_path):
    print("Drafting Technical Heritage Formats...")
    art = extract_white_bg(raw_path)
    
    # 1. Primary T-Shirt Format (4500x5400) Locked Execution
    shirt_canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
    sc_s = 4000 / art.size[0]
    w_s, h_s = int(art.size[0]*sc_s), int(art.size[1]*sc_s)
    art_shirt = art.resize((w_s, h_s), Image.Resampling.LANCZOS)
    
    px_s = (4500 - w_s) // 2
    py_s = (5400 - h_s) // 2 - 200
    shirt_canvas.paste(art_shirt, (px_s, py_s), mask=art_shirt.split()[3])
    
    out_dir_t = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Heritage_Collection"
    os.makedirs(out_dir_t, exist_ok=True)
    out_path_t = os.path.join(out_dir_t, "Heritage_Betsy_Ross_Eagle_Tshirt_4500x5400.png")
    shirt_canvas.save(out_path_t, "PNG", dpi=(300,300))
    
    # White layout visual proof configuration
    w_proof = Image.new("RGB", shirt_canvas.size, (255, 255, 255))
    w_proof.paste(shirt_canvas, (0, 0), mask=shirt_canvas.split()[3])
    w_proof.save(out_path_t.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=90)
    print(f"Secured Heritage Master T-Shirt Matrix: {out_path_t}")
    
    # 2. Compact Headwear Geometry Format (1200x1200)
    hat_canvas = Image.new('RGBA', (1200, 1200), (0,0,0,0))
    sc_h = 1150 / max(art.size[0], art.size[1])
    w_h, h_h = int(art.size[0]*sc_h), int(art.size[1]*sc_h)
    art_hat = art.resize((w_h, h_h), Image.Resampling.LANCZOS)
    
    px_h = (1200 - w_h) // 2
    py_h = (1200 - h_h) // 2
    hat_canvas.paste(art_hat, (px_h, py_h), mask=art_hat.split()[3])
    
    out_dir_h = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Headwear"
    os.makedirs(out_dir_h, exist_ok=True)
    out_path_h = os.path.join(out_dir_h, "Hat_Graphic_Heritage_Betsy_Ross_1200x1200.png")
    hat_canvas.save(out_path_h, "PNG", dpi=(300,300))
    print(f"Secured Heritage Compact Hat Patch Matrix: {out_path_h}")

if __name__ == "__main__":
    raw_pth = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/heritage_betsy_ross_raw_1774638789025.png"
    build_formats(raw_pth)
