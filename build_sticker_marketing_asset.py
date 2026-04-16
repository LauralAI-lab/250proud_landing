import os
from PIL import Image, ImageFilter, ImageDraw, ImageFont

def build_marketing_mockup():
    print("Initiating Sticker Visual Optimization...")
    raw_path = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/final-pod-artwork/eagle_kiss_cut_w_url.png"
    out_dir = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img"
    
    if not os.path.exists(raw_path):
        print("CRITICAL: Raw Source Not Found.")
        return
        
    sticker = Image.open(raw_path).convert("RGBA")
    
    # Restrict sticker dimensions safely for sharp web rendering
    sc = 800 / max(sticker.size[0], sticker.size[1])
    sw, sh = int(sticker.size[0]*sc), int(sticker.size[1]*sc)
    sticker = sticker.resize((sw, sh), Image.Resampling.LANCZOS)
    
    # Draft a fully 1200x1200 modern vector presentation canvas
    # Using the exact 250PROUD corporate colors: off-white to grey gradient feel
    canvas = Image.new('RGBA', (1200, 1200), (245, 240, 232, 255))
    
    # Hardcode a heavily diffused mechanical drop shadow simulating physical lighting
    shadow = Image.new('RGBA', (1200, 1200), (0,0,0,0))
    s_offset_y = 45
    s_offset_x = 0
    shadow.paste((0,0,0, 110), ((1200-sw)//2 + s_offset_x, (1200-sh)//2 + s_offset_y), mask=sticker.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=25))
    
    # Layer shadow and core sticker down onto geometry
    canvas.alpha_composite(shadow)
    
    center_y = (1200 - sh) // 2 - 40 # Nudge geometry up slightly
    canvas.paste(sticker, ((1200 - sw)//2, center_y), mask=sticker.split()[3])
    
    # Forge a bold 'FREE EXCLUSIVE STICKER' taxonomy bar dynamically into the canvas architecture
    draw = ImageDraw.Draw(canvas)
    fill_c = (20, 25, 30, 255) # Native Streetwear Navy Ink
    
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 95)
        font_sub = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 55)
    except:
        try:
            font_large = ImageFont.truetype("/Library/Fonts/Arial.ttf", 80)
            font_sub = font_large
        except:
            font_large = ImageFont.load_default()
            font_sub = font_large
        
    txt_1 = "THE 250PROUD SHIELD"
    txt_2 = "FREE WITH NEWSLETTER SIGNUP!"
    
    w1 = int(draw.textlength(txt_1, font=font_large))
    w2 = int(draw.textlength(txt_2, font=font_sub))
    
    # Deeply anchor typography natively below sticker asset
    bar_y_1 = center_y + sh + 70
    bar_y_2 = bar_y_1 + 110
    
    draw.text(((1200 - w1)//2, bar_y_1), txt_1, font=font_large, fill=fill_c)
    draw.text(((1200 - w2)//2, bar_y_2), txt_2, font=font_sub, fill=(179, 25, 66, 255)) # Brutal Red 
    
    out_path = os.path.join(out_dir, "free_eagle_sticker_asset.png")
    canvas.save(out_path, "PNG", dpi=(300,300), optimize=True)
    
    print(f"Sticker Marketing Asset structurally locked: {out_path}")

if __name__ == "__main__":
    build_marketing_mockup()
