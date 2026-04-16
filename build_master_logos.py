import os
from PIL import Image, ImageDraw, ImageFont

def load_fonts():
    fonts = {}
    
    # Try loading luxury serif
    serif_paths = ["/System/Library/Fonts/Times.ttc", "/System/Library/Fonts/Supplemental/Georgia.ttf"]
    for path in serif_paths:
        if os.path.exists(path):
            fonts['serif'] = path
            break
            
    # Try loading brutalist sans-serif
    sans_paths = ["/System/Library/Fonts/Supplemental/Arial Black.ttf", "/System/Library/Fonts/HelveticaNeue-CondensedBlack.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]
    for path in sans_paths:
        if os.path.exists(path):
            fonts['sans'] = path
            break
            
    return fonts

def center_text(draw, text, y, font, width, fill, tracking=0):
    # Simulated tracking (letter spacing)
    if tracking > 0:
        total_w = sum(draw.textlength(char, font=font) for char in text) + tracking * (len(text) - 1)
        x = (width - total_w) / 2
        for char in text:
            draw.text((x, y), char, font=font, fill=fill)
            x += draw.textlength(char, font=font) + tracking
    else:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) / 2
        draw.text((x, y), text, font=font, fill=fill)

def generate_luxury_serif(out_dir, fonts):
    w, h = 4500, 4500
    img = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    font_main = ImageFont.truetype(fonts.get('serif'), 500) if 'serif' in fonts else ImageFont.load_default()
    font_sub = ImageFont.truetype(fonts.get('sans'), 180) if 'sans' in fonts else ImageFont.load_default()
    
    ink = (30, 30, 30, 255)
    
    center_y = h // 2
    
    center_text(draw, "250PROUD", center_y - 400, font_main, w, ink, tracking=15)
    
    # Draw thin elegant divider line
    line_w = 2000
    line_x = (w - line_w) // 2
    draw.line([(line_x, center_y + 200), (line_x + line_w, center_y + 200)], fill=ink, width=15)
    
    center_text(draw, "1776 — 2026", center_y + 350, font_sub, w, ink, tracking=50)
    
    out_path = os.path.join(out_dir, "MasterLogo_Luxury_Serif.png")
    img.save(out_path, "PNG")
    print(f"Generated {out_path}")

def generate_brutalist_block(out_dir, fonts):
    w, h = 4500, 4500
    img = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    font_main = ImageFont.truetype(fonts.get('sans'), 650) if 'sans' in fonts else ImageFont.load_default()
    font_sub = ImageFont.truetype(fonts.get('serif'), 220) if 'serif' in fonts else ImageFont.load_default()
    
    ink = (30, 30, 30, 255)
    
    # Draw massive heavy box
    box_w = 3800
    box_h = 1600
    box_x = (w - box_w) // 2
    box_y = (h - box_h) // 2
    draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], outline=ink, width=80)
    
    center_text(draw, "250PROUD", box_y + 250, font_main, w, ink, tracking=0)
    center_text(draw, "EST. 1776   •   FW26", box_y + 1050, font_sub, w, ink, tracking=20)
    
    out_path = os.path.join(out_dir, "MasterLogo_Brutalist_Block.png")
    img.save(out_path, "PNG")
    print(f"Generated {out_path}")

def generate_stacked_seal(out_dir, fonts):
    w, h = 4500, 4500
    img = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    font_huge = ImageFont.truetype(fonts.get('sans'), 1000) if 'sans' in fonts else ImageFont.load_default()
    font_med = ImageFont.truetype(fonts.get('sans'), 350) if 'sans' in fonts else ImageFont.load_default()
    font_small = ImageFont.truetype(fonts.get('serif'), 180) if 'serif' in fonts else ImageFont.load_default()
    
    ink = (30, 30, 30, 255)
    
    center_y = h // 2
    
    # Draw circular boundaries
    rad_out = 1600
    rad_in = 1530
    cx, cy = w//2, h//2
    draw.ellipse([cx - rad_out, cy - rad_out, cx + rad_out, cy + rad_out], outline=ink, width=45)
    draw.ellipse([cx - rad_in, cy - rad_in, cx + rad_in, cy + rad_in], outline=ink, width=15)
    
    center_text(draw, "250", cy - 750, font_huge, w, ink)
    center_text(draw, "PROUD", cy + 250, font_med, w, ink, tracking=80)
    
    # Small stars and dates
    center_text(draw, "★  1776 — 2026  ★", cy + 850, font_small, w, ink, tracking=30)
    
    out_path = os.path.join(out_dir, "MasterLogo_Stacked_Seal.png")
    img.save(out_path, "PNG")
    print(f"Generated {out_path}")

if __name__ == "__main__":
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    
    fonts = load_fonts()
    generate_luxury_serif(out_dir, fonts)
    generate_brutalist_block(out_dir, fonts)
    generate_stacked_seal(out_dir, fonts)
