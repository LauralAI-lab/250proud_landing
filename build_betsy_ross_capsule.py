import os
import numpy as np
from PIL import Image

def alpha_extract(img_path):
    img_raw = Image.open(img_path).convert("RGBA")
    arr = np.array(img_raw)
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
    # Push vectors natively to pure Streetwear Navy ink
    arr[:,:,0] = 20
    arr[:,:,1] = 25
    arr[:,:,2] = 30
    normalized = gray / 255.0
    alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
    arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
    
    clean_art = Image.fromarray(arr.astype(np.uint8))
    bbox = clean_art.getbbox()
    if bbox:
        clean_art = clean_art.crop(bbox)
        
    return clean_art

def build_tshirt(flag_raw):
    print("Drafting T-Shirt Architecture...")
    canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
    art = alpha_extract(flag_raw)
    
    # Scale purely for massive central chest alignment (4200px wide limits)
    sc = 4200 / art.size[0]
    art_w, art_h = int(art.size[0]*sc), int(art.size[1]*sc)
    art_resized = art.resize((art_w, art_h), Image.Resampling.LANCZOS)
    
    # Mathematically lock exactly horizontally structured to absolute core metrics
    py = (5400 - art_h) // 2 - 200
    px = (4500 - art_w) // 2
    canvas.paste(art_resized, (px, py), mask=art_resized.split()[3])
    
    # Fetch authentic full-color master Tech Block
    b_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Official_Blueprint_Tech_Block_Logo.png"
    badge = Image.open(b_path).convert("RGBA")
    sc_b = 1200 / badge.size[0]
    b_w, b_h = int(badge.size[0]*sc_b), int(badge.size[1]*sc_b)
    badge = badge.resize((b_w, b_h), Image.Resampling.LANCZOS)
    
    # Anchor the Tech block directly onto the structural footings in the bottom right hemisphere
    margin = 150
    box_x = (px + art_w) - b_w
    box_y = (py + art_h) + margin
    canvas.paste(badge, (box_x, box_y), mask=badge.split()[3])
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Betsy_Ross_1776_Blueprint_Tshirt_4500x5400.png")
    
    canvas.save(out_path, "PNG", dpi=(300,300))
    w_proof = Image.new("RGB", canvas.size, (255, 255, 255))
    w_proof.paste(canvas, (0, 0), mask=canvas.split()[3])
    w_proof.save(out_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=90)

def build_headwear(flag_raw):
    print("Drafting Headwear Architecture...")
    canvas = Image.new('RGBA', (1200, 1200), (0,0,0,0))
    art = alpha_extract(flag_raw)
    
    # Tightly bind layout explicitly to Cap/Embroidery margins
    sc = 1150 / max(art.size[0], art.size[1])
    art_w, art_h = int(art.size[0]*sc), int(art.size[1]*sc)
    art_resized = art.resize((art_w, art_h), Image.Resampling.LANCZOS)
    
    px = (1200 - art_w) // 2
    py = (1200 - art_h) // 2
    canvas.paste(art_resized, (px, py), mask=art_resized.split()[3])
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Headwear"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Hat_Graphic_Betsy_Ross_Blueprint_1200x1200.png")
    
    canvas.save(out_path, "PNG", dpi=(300,300))

if __name__ == "__main__":
    flag_raw = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_betsy_ross_raw_1774638044737.png"
    build_tshirt(flag_raw)
    build_headwear(flag_raw)
