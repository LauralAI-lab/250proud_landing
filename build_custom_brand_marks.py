import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def strip_white(img):
    img = img.convert("RGBA")
    arr = np.array(img)
    r, g, b, a = arr[:,:,0].astype(int), arr[:,:,1].astype(int), arr[:,:,2].astype(int), arr[:,:,3].astype(int)
    # Strict knockout of pure white backgrounds
    is_white = (r > 245) & (g > 245) & (b > 245)
    
    # Chroma math to protect non-white bright colors (like vintage cream or bright yellow)
    color_diff = np.abs(r - g) + np.abs(r - b) + np.abs(g - b)
    is_paper = is_white & (color_diff < 15)
    
    arr[is_paper, 3] = 0
    return Image.fromarray(arr.astype(np.uint8))

def center_text(draw, text, y, font, width, fill, tracking=0):
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

def get_fonts():
    fonts = {}
    serif_paths = ["/System/Library/Fonts/Times.ttc", "/System/Library/Fonts/Supplemental/Georgia.ttf"]
    for path in serif_paths:
        if os.path.exists(path):
            fonts['serif'] = path
            break
            
    sans_paths = ["/System/Library/Fonts/Supplemental/Arial Black.ttf", "/System/Library/Fonts/HelveticaNeue-CondensedBlack.ttf"]
    for path in sans_paths:
        if os.path.exists(path):
            fonts['sans'] = path
            break
    return fonts

def build():
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Version2_Cultural_Icons"
    os.makedirs(out_dir, exist_ok=True)
    
    fonts = get_fonts()
    font_bold = ImageFont.truetype(fonts.get('sans'), 350) if 'sans' in fonts else ImageFont.load_default()
    font_sub_bold = ImageFont.truetype(fonts.get('sans'), 160) if 'sans' in fonts else ImageFont.load_default()
    font_serif = ImageFont.truetype(fonts.get('serif'), 400) if 'serif' in fonts else ImageFont.load_default()
    font_sub_serif = ImageFont.truetype(fonts.get('serif'), 200) if 'serif' in fonts else ImageFont.load_default()
    
    # 1. Esoteric Sun (Online Ceramics Vibe)
    img_sun = strip_white(Image.open("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/logo_icon_esoteric_sun_1774360362951.png"))
    canvas1 = Image.new('RGBA', (4500, 4500), (0,0,0,0))
    # Resize sun slightly
    sun_w, sun_h = img_sun.size
    target_w = 2800
    ratio = target_w / sun_w
    target_h = int(sun_h * ratio)
    img_sun = img_sun.resize((target_w, target_h), Image.Resampling.LANCZOS)
    canvas1.paste(img_sun, ((4500-target_w)//2, (4500-target_h)//2), img_sun)
    d1 = ImageDraw.Draw(canvas1)
    ink1 = (40, 45, 30, 255) # Deep olive/black
    center_text(d1, "250PROUD", 400, font_serif, 4500, ink1, tracking=80)
    center_text(d1, "1776   •   2026", 3800, font_sub_serif, 4500, ink1, tracking=60)
    canvas1.save(os.path.join(out_dir, "Esoteric_Sun_Brand_Mark.png"), "PNG")

    # 2. Rubber Hose Eagle (CPFM Vibe)
    img_eagle = strip_white(Image.open("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/logo_icon_rubber_eagle_1774360382104.png"))
    canvas2 = Image.new('RGBA', (4500, 4500), (0,0,0,0))
    target_w = 3200
    ratio = target_w / img_eagle.size[0]
    target_h = int(img_eagle.size[1] * ratio)
    img_eagle = img_eagle.resize((target_w, target_h), Image.Resampling.LANCZOS)
    canvas2.paste(img_eagle, ((4500-target_w)//2, 400), img_eagle)
    d2 = ImageDraw.Draw(canvas2)
    ink2 = (30, 30, 40, 255)
    center_text(d2, "250PROUD", 3700, font_bold, 4500, ink2, tracking=15)
    center_text(d2, "1776 - 2026", 4150, font_sub_bold, 4500, ink2, tracking=40)
    canvas2.save(os.path.join(out_dir, "RubberEagle_Mascot_Brand_Mark.png"), "PNG")

    # 3. Currency Crest (Kith Vibe)
    img_crest = strip_white(Image.open("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/logo_icon_currency_crest_1774360397607.png"))
    canvas3 = Image.new('RGBA', (4500, 4500), (0,0,0,0))
    target_w = 3000
    ratio = target_w / img_crest.size[0]
    target_h = int(img_crest.size[1] * ratio)
    img_crest = img_crest.resize((target_w, target_h), Image.Resampling.LANCZOS)
    canvas3.paste(img_crest, ((4500-target_w)//2, (4500-target_h)//2 - 200), img_crest)
    d3 = ImageDraw.Draw(canvas3)
    ink3 = (20, 25, 40, 255) # Deep navy
    center_text(d3, "250PROUD", 3600, font_serif, 4500, ink3, tracking=40)
    # Tiny line
    d3.line([(1800, 4100), (2700, 4100)], fill=ink3, width=12)
    center_text(d3, "1776 — 2026", 4200, font_sub_serif, 4500, ink3, tracking=70)
    canvas3.save(os.path.join(out_dir, "Heritage_Eagle_Crest_Brand_Mark.png"), "PNG")

    print("Successfully built all 3 composited Master Marks.")

if __name__ == "__main__":
    build()
