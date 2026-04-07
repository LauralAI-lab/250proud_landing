import os
from PIL import Image, ImageDraw, ImageFont

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def composite_epic_cover(bg_img_path, out_img_path):
    print("Loading epic background...")
    bg = Image.open(bg_img_path).convert("RGBA")
    w, h = bg.size
    
    # Create a gradient overlay to make text pop at the top and bottom
    overlay = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    
    # Top gradient (black to transparent)
    for y in range(int(h * 0.35)):
        alpha = int(220 * (1 - (y / (h * 0.35))))
        d.line([(0, y), (w, y)], fill=(10, 15, 30, alpha))
        
    # Bottom gradient
    for y in range(int(h * 0.8), h):
        alpha = int(220 * ((y - (h * 0.8)) / (h * 0.2)))
        d.line([(0, y), (w, y)], fill=(10, 15, 30, alpha))
        
    bg = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(bg)
    
    # Fonts
    path_impact = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/Library/Fonts/Arial Bold.ttf"
    ]
    path_serif = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf"
    ]
    path_sans = [
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc"
    ]
    
    f_hero = get_font(path_impact, int(h * 0.08))
    f_sub = get_font(path_serif, int(h * 0.025))
    f_mark = get_font(path_sans, int(h * 0.02))
    
    gold = (255, 215, 0, 255)
    white = (255, 255, 255, 255)
    
    # Subtitle (Top)
    sub_text = "INTERESTING FACTS OF THE AMERICAN STORY"
    sub_bbox = draw.textbbox((0,0), sub_text, font=f_sub)
    draw.text(((w - (sub_bbox[2]-sub_bbox[0]))/2, h * 0.05), sub_text, font=f_sub, fill=white)
    
    # Hero Title
    hero1 = "250 STRONG"
    hero2 = "Built By Hand"
    
    f_hero2 = get_font(path_sans, int(h * 0.045)) # Bump size up for shorter text
    
    h1_bbox = draw.textbbox((0,0), hero1, font=f_hero)
    h2_bbox = draw.textbbox((0,0), hero2, font=f_hero2)
    
    # Drop shadow
    sh = int(h * 0.005)
    
    draw.text(((w - (h1_bbox[2]-h1_bbox[0]))/2 + sh, h * 0.08 + sh), hero1, font=f_hero, fill=(0,0,0,200))
    draw.text(((w - (h1_bbox[2]-h1_bbox[0]))/2, h * 0.08), hero1, font=f_hero, fill=gold)
    
    draw.text(((w - (h2_bbox[2]-h2_bbox[0]))/2 + sh, h * 0.17 + sh), hero2, font=f_hero2, fill=(0,0,0,200))
    draw.text(((w - (h2_bbox[2]-h2_bbox[0]))/2, h * 0.17), hero2, font=f_hero2, fill=white)
    
    # Mark (Bottom)
    mark_text = "Fun For All Ages"
    m_bbox = draw.textbbox((0,0), mark_text, font=f_mark)
    draw.text(((w - (m_bbox[2]-m_bbox[0]))/2, h * 0.94), mark_text, font=f_mark, fill=gold)

    # Logo (Above Mark)
    logo_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/logo.png"
    if os.path.exists(logo_path):
        original_logo = Image.open(logo_path).convert("RGBA")
        _, _, _, a = original_logo.split()
        white_rgb = Image.new("RGB", original_logo.size, (255, 255, 255))
        r2, g2, b2 = white_rgb.split()
        white_logo = Image.merge("RGBA", (r2, g2, b2, a))
        
        logo_w, logo_h = white_logo.size
        new_logo_w = int(w * 0.12) # Smaller
        aspect = logo_h / logo_w
        new_logo_h = int(new_logo_w * aspect)
        
        resized_logo = white_logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)
        
        x_pos = int((w - new_logo_w) / 2)
        y_pos = int(h * 0.94) - new_logo_h - int(h * 0.01) # Centered slightly above text
        
        bg.paste(resized_logo, (x_pos, y_pos), resized_logo)
    
    bg.save(out_img_path, "PNG")
    print(f"Saved epic composited cover to {out_img_path}")

if __name__ == "__main__":
    in_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/coloring_book/american_journey_v2.png"
    out_path = "epic_cover_final.png"
    composite_epic_cover(in_path, out_path)
