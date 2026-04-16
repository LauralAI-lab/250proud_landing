import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            # For font collections, index 0 is usually the standard/bold depending on the path
            # To be safe, try to load it
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def process_and_composite(img_path, out_path, title_text=""):
    print(f"Processing {img_path}")
    
    # 1. Load and Strip Background
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    r, g, b, a = arr[:,:,0].astype(int), arr[:,:,1].astype(int), arr[:,:,2].astype(int), arr[:,:,3].astype(int)
    is_white = (r > 240) & (g > 240) & (b > 240)
    arr[is_white, 3] = 0
    clean_art = Image.fromarray(arr.astype(np.uint8))
    
    # 2. Setup 4500x5400 Canvas
    canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
    d = ImageDraw.Draw(canvas)
    
    # Scale art to fit the top portion
    art_w = int(clean_art.size[0] * 1.05)
    art_h = int(clean_art.size[1] * 1.05)
    clean_art = clean_art.resize((art_w, art_h), Image.Resampling.LANCZOS)
    canvas.paste(clean_art, ((4500-art_w)//2, 100), clean_art)
    
    # 3. Typography
    path_heavy = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/Library/Fonts/Arial Bold.ttf"
    ]
    path_tech = [
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
        "/System/Library/Fonts/Menlo.ttc"
    ]
    
    font_hero = get_font(path_heavy, 600)
    font_sub = get_font(path_heavy, 150)
    font_tech = get_font(path_tech, 100)
    
    blue = (30, 60, 140, 255) # Vintage Navy
    red = (180, 45, 40, 255)  # Vintage Brick Red
    black = (20, 20, 25, 255)
    
    # Top subtitle
    sub1 = "S E M I Q U I N C E N T E N N I A L   •   1 7 7 6 - 2 0 2 6"
    bbox = d.textbbox((0,0), sub1, font=font_sub)
    d.text(((4500 - (bbox[2]-bbox[0]))//2, 4300), sub1, font=font_sub, fill=black)
    
    # Hero text (Split color)
    w_250 = d.textlength("250", font=font_hero)
    w_space = 80 # space between words
    w_proud = d.textlength("PROUD", font=font_hero)
    
    total_hero_w = w_250 + w_space + w_proud
    start_x = (4500 - total_hero_w) // 2
    
    d.text((start_x, 4450), "250", font=font_hero, fill=blue)
    d.text((start_x + w_250 + w_space, 4450), "PROUD", font=font_hero, fill=red)
    
    # Tech line
    tech_str = f"DAT: {title_text} // REF: ESTABLISHMENT // DATUM A"
    bbox_tech = d.textbbox((0,0), tech_str, font=font_tech)
    d.text(((4500 - (bbox_tech[2]-bbox_tech[0]))//2, 5100), tech_str, font=font_tech, fill=black)
    
    # Save
    canvas.save(out_path, "PNG")
    print(f"Saved completed composited layout to {out_path}")

if __name__ == "__main__":
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    os.makedirs(out_dir, exist_ok=True)
    
    img1 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_yosemite_half_dome_1774362305187.png"
    img2 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_golden_gate_1774362320667.png"
    
    out1 = os.path.join(out_dir, "Yosemite_Topo_Schema_BlueRed_4500x5400.png")
    out2 = os.path.join(out_dir, "GoldenGate_Schema_BlueRed_4500x5400.png")
    
    process_and_composite(img1, out1, "NATIONAL_PARK_YSMT")
    process_and_composite(img2, out2, "INFRASTRUCTURE_GG_BRIDGE")
