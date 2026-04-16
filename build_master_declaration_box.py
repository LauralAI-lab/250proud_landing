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

def create_declaration_style_logo():
    path_heavy = [
        "/tmp/Syncopate-Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/Library/Fonts/Arial Bold.ttf"
    ]
    path_tech = [
        "/tmp/Syncopate-Bold.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
    ]
    
    font_hero = get_font(path_heavy, 420)
    font_tm = get_font(path_heavy, 80)
    font_sub = get_font(path_tech, 70)
    
    blue = (30, 60, 140, 255)
    red = (180, 45, 40, 255)
    black = (20, 20, 25, 255)
    
    # Fake canvas to calculate widths
    img = Image.new('RGBA', (3200, 800), (0,0,0,0))
    d = ImageDraw.Draw(img)
    
    w_250 = d.textlength("250", font=font_hero)
    w_proud = d.textlength("PROUD", font=font_hero)
    space = 25
    hero_w = w_250 + space + w_proud
    
    # Box dimensions (snug)
    pad_h = 160
    pad_v = 130
    box_w = int(hero_w + (pad_h * 2))
    box_h = 750
    
    # Real canvas
    img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    
    # Background and thin precise outline
    d.rectangle([0, 0, box_w, box_h], fill=(255, 255, 255, 255))
    d.rectangle([5, 5, box_w-5, box_h-5], outline=black, width=12) # Thin, technical line
    
    start_x = pad_h
    start_y = pad_v + 60
    
    # 1. Micro TOP (Left-aligned)
    d.text((start_x, pad_v - 15), "1776 - 2026", font=font_sub, fill=black)
    
    # 2. Hero Center
    d.text((start_x, start_y), "250", font=font_hero, fill=blue)
    d.text((start_x + w_250 + space, start_y), "PROUD", font=font_hero, fill=red)
    
    # 3. TM Mark
    d.text((start_x + w_250 + space + w_proud + 10, start_y - 10), "TM", font=font_tm, fill=black)
    
    # 4. Micro BOTTOM (Left-aligned)
    d.text((start_x, start_y + 440), "SEMIQUINCENTENNIAL", font=font_sub, fill=black)
    
    return img

def build():
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    
    logo = create_declaration_style_logo()
    out1 = os.path.join(out_dir, "Declaration_Style_Master_Mark.png")
    logo.save(out1, "PNG")
    
    # Save the white background proof for Google Drive viewing
    white = Image.new("RGB", logo.size, (255, 255, 255))
    white.paste(logo, (0, 0), logo)
    white.save(out1.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=95)
    print(f"Saved: {out1}")

if __name__ == "__main__":
    build()
