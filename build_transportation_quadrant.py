import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def alpha_extract(img_path):
    # Perfect structural Supreme Alpha Matrix extraction subroutine
    img_raw = Image.open(img_path).convert("RGBA")
    arr = np.array(img_raw)
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
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

def process():
    print("Building Massive Transportation Grid Masterpiece...")
    
    paths = {
        "carriage": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_horse_carriage_raw_1774617189574.png",
        "train": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_locomotive_raw_1774614793807.png",
        "plane": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_wright_flyer_raw_1774614807691.png",
        "cybertruck": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_cybertruck_raw_1774617203146.png",
        "crest": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_collection_crest_1774552523886.png"
    }
    
    # Grid physics: Extends canvas down organically to house massive technical footings
    canvas_w, canvas_h = 4500, 5600
    grid_w, grid_h = 2250, 2700
    
    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0,0,0,0))
    
    # Chronological mapping orientation parameters
    assets = [
        ("carriage", 0, 0),     # Top Left (1700s)
        ("train", 2250, 0),     # Top Right (1800s)
        ("plane", 0, 2700),     # Bottom Left (1900s)
        ("cybertruck", 2250, 2700) # Bottom Right (2000s)
    ]
    
    # Structural architectural edge spacing
    pad_x = 200
    pad_y = 200
    target_w = grid_w - (pad_x * 2)
    target_h = grid_h - (pad_y * 2)
    
    # Master vector iteration extraction and bounding routine
    for key, bx, by in assets:
        art = alpha_extract(paths[key])
        
        # Flawless geometry scaling enforcing limits per quadrant box
        scale = min(target_w / art.size[0], target_h / art.size[1])
        art_w, art_h = int(art.size[0] * scale), int(art.size[1] * scale)
        art_resized = art.resize((art_w, art_h), Image.Resampling.LANCZOS)
        
        # Math mapping precise dead-center coordinates relative to local box origins
        px = bx + (grid_w - art_w) // 2
        py = by + (grid_h - art_h) // 2
        canvas.paste(art_resized, (px, py), mask=art_resized.split()[3])
        
    # Inject heavy graphic crosshair framing separating the timelines natively
    draw = ImageDraw.Draw(canvas)
    fill_c = (20, 25, 30, 255)
    
    # User Request 1: Remove quadrant lines explicitly
    # center_thickness = 15
    # draw.rectangle([2250 - center_thickness//2, 200, 2250 + center_thickness//2, 5200], fill=fill_c)
    # draw.rectangle([200, 2700 - center_thickness//2, 4300, 2700 + center_thickness//2], fill=fill_c)
    
    # User Request 2: Drop Master Red/Blue 250PROUD corporate block into absolute center
    master_logo_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Official_Blueprint_Tech_Block_Logo.png"
    master_logo_base = Image.open(master_logo_path).convert("RGBA")
    
    # User Request 5: Strip off the bounding outer box strokes natively
    b_val = 35
    master_logo = master_logo_base.crop((b_val, b_val, master_logo_base.width - b_val, master_logo_base.height - b_val))
    
    # User Request 4: Crush Corporate Logo exactly to 70% Grayscale Blueprint Ink + Alpha Null White Background
    l_arr = np.array(master_logo)
    lr, lg, lb, la = l_arr[:,:,0].astype(float), l_arr[:,:,1].astype(float), l_arr[:,:,2].astype(float), l_arr[:,:,3].astype(float)
    lgray = 0.2989 * lr + 0.5870 * lg + 0.1140 * lb
    
    # Dialing back to 70% Ash/Gray mapping
    l_arr[:,:,0] = 76
    l_arr[:,:,1] = 76
    l_arr[:,:,2] = 76

    
    # Map colors to solid opacity, aggressively rendering white as fully transparent
    l_alpha = np.clip((240.0 - lgray) / 50.0, 0, 1)
    l_arr[:,:,3] = (l_alpha * la).astype(np.uint8)
    master_logo_alpha = Image.fromarray(l_arr.astype(np.uint8))
    
    logo_w = 1200
    scale_l = logo_w / master_logo_alpha.size[0]
    logo_h = int(master_logo_alpha.size[1] * scale_l)
    master_resized = master_logo_alpha.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    
    # Calculate exact intersection vector for dynamic overlay
    logo_x = (canvas_w - logo_w) // 2
    logo_y = (5400 - logo_h) // 2
    canvas.paste(master_resized, (logo_x, logo_y), mask=master_resized.split()[3])
    
    # User Request 3: Escalate bottom copyright bounds 25% (Font 60->75 | Crest 160->200)
    crest = alpha_extract(paths["crest"])
    c_h = 200
    c_scale = c_h / crest.size[1]
    c_w = int(crest.size[0] * c_scale)
    crest_resized = crest.resize((c_w, c_h), Image.Resampling.LANCZOS)
    
    footer_text = "250Proud™ - Blueprint Collection™ - Copyright Lauralai LLC 2026"
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 75)
    except:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 75)
        
    txt_w = int(draw.textlength(footer_text, font=font))
    
    # Recalculate horizontal center anchors accommodating the new 25% expansion array
    total_footer_w = c_w + 40 + txt_w
    start_x = (canvas_w - total_footer_w) // 2
    
    # Shift vertical boundaries slightly up to frame the larger font natively 
    start_y = 5350
    canvas.paste(crest_resized, (start_x, start_y), mask=crest_resized.split()[3])
    
    # Perfectly center typographic elements relative to new 200px Crest icon cap
    text_y = start_y + (c_h - 75) // 2 - 10
    draw.text((start_x + c_w + 40, text_y), footer_text, font=font, fill=fill_c)
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Decades_Collection"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Transportation_Evolution_Quad_Blueprint_4500x5600.png")
    
    canvas.save(out_path, "PNG", dpi=(300,300))
    
    white_proof = Image.new("RGB", canvas.size, (255, 255, 255))
    white_proof.paste(canvas, (0, 0), canvas)
    white_proof.save(out_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=90)
    print(f"Master Quad-Grid finalized securely: {out_path}")

if __name__ == "__main__":
    process()
