import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def create_master_logo_block():
    # Define primary floating block dimensions
    box_w, box_h = 3400, 1100
    img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    
    # Draw pure white solid block with thick black border
    thick = 35
    d.rectangle([0, 0, box_w, box_h], fill=(255, 255, 255, 255))
    d.rectangle([thick//2, thick//2, box_w-(thick//2), box_h-(thick//2)], outline=(20, 20, 25, 255), width=thick)

    # Fonts
    path_heavy = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc"
    ]
    path_tech = [
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
        "/System/Library/Fonts/Menlo.ttc"
    ]
    
    font_hero = get_font(path_heavy, 520)
    font_tm = get_font(path_heavy, 120)
    font_sub = get_font(path_tech, 140)
    
    blue = (30, 60, 140, 255)
    red = (180, 45, 40, 255)
    black = (20, 20, 25, 255)
    
    # 1. Top text: 1776 - 2026
    top_str = "1 7 7 6  —  2 0 2 6"
    bbox_top = d.textbbox((0,0), top_str, font=font_sub)
    d.text(((box_w - (bbox_top[2]-bbox_top[0]))//2, 120), top_str, font=font_sub, fill=black)
    
    # Framing line top
    frame_y_top = 300
    frame_y_bot = 820
    d.line([(300, frame_y_top), (box_w - 300, frame_y_top)], fill=black, width=8)
    d.line([(300, frame_y_bot), (box_w - 300, frame_y_bot)], fill=black, width=8)
    
    # 2. Hero Text: 250 (Blue) PROUD (Red) TM (Black)
    w_250 = d.textlength("250", font=font_hero)
    w_space = 45 # Exact spacing to keep it tight
    w_proud = d.textlength("PROUD", font=font_hero)
    total_w = w_250 + w_space + w_proud
    
    start_x = (box_w - total_w) // 2
    # Vertically center the text within the framing lines
    y_hero = 310 
    
    d.text((start_x, y_hero), "250", font=font_hero, fill=blue)
    d.text((start_x + w_250 + w_space, y_hero), "PROUD", font=font_hero, fill=red)
    
    # Add Trademark
    d.text((start_x + w_250 + w_space + w_proud + 15, y_hero - 20), "TM", font=font_tm, fill=black)
    
    # 3. Bottom text: SEMIQUINCENTENNIAL
    bot_str = "S E M I Q U I N C E N T E N N I A L"
    bbox_bot = d.textbbox((0,0), bot_str, font=font_sub)
    d.text(((box_w - (bbox_bot[2]-bbox_bot[0]))//2, 850), bot_str, font=font_sub, fill=black)
    
    return img

def build():
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    
    # Build the official floating logo block directly
    logo_block = create_master_logo_block()
    logo_path = os.path.join(out_dir, "Official_Blueprint_Tech_Block_Logo.png")
    logo_block.save(logo_path, "PNG")
    print(f"Saved the Official Master Brand Logo Block to {logo_path}")
    
    # Composite onto the existing Golden Gate schema
    gg_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_golden_gate_1774362320667.png"
    img_gg = Image.open(gg_path).convert("RGBA")
    
    # Strip background of the bridge
    arr = np.array(img_gg)
    r, g, b, a = arr[:,:,0].astype(int), arr[:,:,1].astype(int), arr[:,:,2].astype(int), arr[:,:,3].astype(int)
    is_white = (r > 240) & (g > 240) & (b > 240)
    arr[is_white, 3] = 0
    clean_gg = Image.fromarray(arr.astype(np.uint8))
    
    # Drop over a huge 4500x5400 Tee print resolution canvas
    canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
    scale = 4400 / clean_gg.size[0]
    art_w = int(clean_gg.size[0] * scale)
    art_h = int(clean_gg.size[1] * scale)
    clean_gg = clean_gg.resize((art_w, art_h), Image.Resampling.LANCZOS)
    canvas.paste(clean_gg, ((4500-art_w)//2, (5400-art_h)//2 - 200), clean_gg)
    
    # Overlay the new Master Logo Block dead center to create the ultimate structural tee 
    lb_w = 2600
    lb_h = int(logo_block.size[1] * (lb_w / logo_block.size[0]))
    resized_logo = logo_block.resize((lb_w, lb_h), Image.Resampling.LANCZOS)
    
    box_x = (4500 - lb_w) // 2
    box_y = (5400 - lb_h) // 2
    canvas.paste(resized_logo, (box_x, box_y), resized_logo)
    
    out_dir_tees = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    os.makedirs(out_dir_tees, exist_ok=True)
    out_path = os.path.join(out_dir_tees, "GoldenGate_Schema_Floating_Block_4500x5400.png")
    canvas.save(out_path, "PNG")
    print(f"Saved completed GoldenGate layout to {out_path}")

if __name__ == "__main__":
    build()
