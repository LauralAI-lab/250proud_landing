import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

output_dir = "shopify_theme_assets/campaign"
os.makedirs(output_dir, exist_ok=True)

# Load assets
bg_path = "american_journey_RAW_for_photoshop.png"
book_path = "nc_assets/img/generated_true_cover.png"
hat_path = "nc_assets/img/mockup_snapback.png"
mug_path = "nc_assets/img/mockup_mug.jpg"
font_path_bold = "fonts/RobotoSlab-Bold.ttf"
font_path_sans = "fonts/OpenSans-Bold.ttf"

bg_img = Image.open(bg_path).convert("RGBA")
book_img = Image.open(book_path).convert("RGBA")

try:
    hat_img = Image.open(hat_path).convert("RGBA")
    mug_img = Image.open(mug_path).convert("RGBA")
except Exception as e:
    print(f"Error loading merch mockups: {e}")
    hat_img = Image.new("RGBA", (100, 100), (0,0,0,0))
    mug_img = Image.new("RGBA", (100, 100), (0,0,0,0))

def add_border(img, border_size=6, color=(255,255,255,255)):
    w, h = img.size
    new_img = Image.new("RGBA", (w + border_size*2, h + border_size*2), color)
    new_img.paste(img, (border_size, border_size))
    return new_img

def add_shadow(img, offset=(20, 20), radius=30, shadow_color=(0, 0, 0, 180)):
    w, h = img.size
    shadow = Image.new("RGBA", (w + abs(offset[0]) + radius*2, h + abs(offset[1]) + radius*2), (0,0,0,0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_rect = (radius + offset[0], radius + offset[1], radius + offset[0] + w, radius + offset[1] + h)
    shadow_draw.rectangle(shadow_rect, fill=shadow_color)
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius))
    shadow.paste(img, (radius, radius), img)
    return shadow

# 1. SHOPIFY HERO BANNER (2560 x 1000)
def build_hero():
    print("Building Shopify Hero Banner...")
    W, H = 2560, 1000
    canvas = Image.new("RGBA", (W, H))
    
    bg_w, bg_h = bg_img.size
    scale = max(W/bg_w, H/bg_h)
    bg_scaled = bg_img.resize((int(bg_w * scale), int(bg_h * scale)), Image.Resampling.LANCZOS)
    
    left = (bg_scaled.width - W) // 2
    top = (bg_scaled.height - H) // 2
    bg_cropped = bg_scaled.crop((left, top, left + W, top + H))
    bg_cropped = ImageEnhance.Brightness(bg_cropped).enhance(0.3)
    canvas.paste(bg_cropped, (0, 0))
    
    # Book
    book_h = int(H * 0.8)
    book_w = int(book_img.width * (book_h / book_img.height))
    book_r = book_img.resize((book_w, book_h), Image.Resampling.LANCZOS)
    book_s = add_shadow(book_r)
    
    # Merch Stack
    merch_h = int((book_h - 100) / 2) # Make them smaller so they fit on the right
    
    mug_w = int(mug_img.width * (merch_h / mug_img.height))
    mug_r = add_border(mug_img.resize((mug_w, merch_h), Image.Resampling.LANCZOS))
    mug_s = add_shadow(mug_r, offset=(10, 10), radius=15)
    
    hat_w = int(hat_img.width * (merch_h / hat_img.height))
    hat_r = add_border(hat_img.resize((hat_w, merch_h), Image.Resampling.LANCZOS))
    hat_s = add_shadow(hat_r, offset=(10, 10), radius=15)
    
    # Paste Book
    center_x = W - 850 # Shift book further left to give merch room
    bx = center_x - book_s.width // 2
    by = (H - book_s.height) // 2
    canvas.paste(book_s, (bx, by), book_s)
    
    # Paste Stacked Merch
    stack_x = bx + book_s.width + 40
    stack_y1 = by + 20
    stack_y2 = stack_y1 + hat_s.height + 10
    
    canvas.paste(hat_s, (stack_x, stack_y1), hat_s)
    canvas.paste(mug_s, (stack_x, stack_y2), mug_s)
    
    # Text
    draw = ImageDraw.Draw(canvas)
    try:
        font_title = ImageFont.truetype(font_path_bold, 110)
        font_subtitle = ImageFont.truetype(font_path_sans, 45)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        
    text_x = 150
    draw.text((text_x, 300), "THE AMERICAN STORY.", font=font_title, fill="#FFFFFF")
    draw.text((text_x, 420), "IN YOUR HANDS.", font=font_title, fill="#D4AF37")
    
    draw.text((text_x, 580), "The 250th Anniversary book & merch collection.", font=font_subtitle, fill="#94A3B8")
    draw.text((text_x, 640), "Built for leaders. Designed to be shared.", font=font_subtitle, fill="#94A3B8")
    
    canvas.save(os.path.join(output_dir, "Shopify_Hero_Banner.png"))

# 2. SOCIAL SQUARE (1080 x 1080)
def build_square():
    print("Building Social Square...")
    W, H = 1080, 1080
    canvas = Image.new("RGBA", (W, H))
    
    bg_w, bg_h = bg_img.size
    scale = max(W/bg_w, H/bg_h)
    bg_scaled = bg_img.resize((int(bg_w * scale), int(bg_h * scale)), Image.Resampling.LANCZOS)
    left = (bg_scaled.width - W) // 2
    top = (bg_scaled.height - H) // 2
    bg_cropped = bg_scaled.crop((left, top, left + W, top + H))
    bg_cropped = ImageEnhance.Brightness(bg_cropped).enhance(0.4)
    canvas.paste(bg_cropped, (0, 0))
    
    # Book
    book_h = int(H * 0.50)
    book_w = int(book_img.width * (book_h / book_img.height))
    book_r = book_img.resize((book_w, book_h), Image.Resampling.LANCZOS)
    book_s = add_shadow(book_r)
    
    # Merch
    merch_h = int(book_h * 0.35)
    mug_w = int(mug_img.width * (merch_h / mug_img.height))
    mug_r = add_border(mug_img.resize((mug_w, merch_h), Image.Resampling.LANCZOS))
    mug_s = add_shadow(mug_r, offset=(10, 10), radius=15)
    
    hat_w = int(hat_img.width * (merch_h / hat_img.height))
    hat_r = add_border(hat_img.resize((hat_w, merch_h), Image.Resampling.LANCZOS))
    hat_s = add_shadow(hat_r, offset=(10, 10), radius=15)
    
    # Paste
    center_y = (H // 2) + 20
    
    bx = (W - book_s.width) // 2
    by = center_y - book_s.height // 2 - 80
    canvas.paste(book_s, (bx, by), book_s)
    
    # Paste Merch below book
    total_merch_w = mug_s.width + hat_s.width + 40
    start_x = (W - total_merch_w) // 2
    merch_y = by + book_s.height + 10
    
    canvas.paste(mug_s, (start_x, merch_y), mug_s)
    canvas.paste(hat_s, (start_x + mug_s.width + 40, merch_y), hat_s)
    
    # Text
    draw = ImageDraw.Draw(canvas)
    try:
        font_title = ImageFont.truetype(font_path_bold, 80)
    except:
        font_title = ImageFont.load_default()
        
    title = "AVAILABLE NOW"
    try:
        bbox = draw.textbbox((0, 0), title, font=font_title)
        tw = bbox[2] - bbox[0]
    except:
        tw = 400
    draw.text(((W - tw) // 2, 50), title, font=font_title, fill="#D4AF37")
    
    canvas.save(os.path.join(output_dir, "Social_Square.png"))

# 3. SOCIAL STORY (1080 x 1920)
def build_story():
    print("Building Social Story...")
    W, H = 1080, 1920
    canvas = Image.new("RGBA", (W, H))
    
    bg_w, bg_h = bg_img.size
    scale = max(W/bg_w, H/bg_h)
    bg_scaled = bg_img.resize((int(bg_w * scale), int(bg_h * scale)), Image.Resampling.LANCZOS)
    left = (bg_scaled.width - W) // 2
    top = (bg_scaled.height - H) // 2
    bg_cropped = bg_scaled.crop((left, top, left + W, top + H))
    bg_cropped = ImageEnhance.Brightness(bg_cropped).enhance(0.3)
    canvas.paste(bg_cropped, (0, 0))
    
    # Book
    book_h = int(H * 0.40)
    book_w = int(book_img.width * (book_h / book_img.height))
    book_r = book_img.resize((book_w, book_h), Image.Resampling.LANCZOS)
    book_s = add_shadow(book_r)
    
    # Merch
    merch_h = int(book_h * 0.4)
    mug_w = int(mug_img.width * (merch_h / mug_img.height))
    mug_r = add_border(mug_img.resize((mug_w, merch_h), Image.Resampling.LANCZOS))
    mug_s = add_shadow(mug_r, offset=(10, 10), radius=15)
    
    hat_w = int(hat_img.width * (merch_h / hat_img.height))
    hat_r = add_border(hat_img.resize((hat_w, merch_h), Image.Resampling.LANCZOS))
    hat_s = add_shadow(hat_r, offset=(10, 10), radius=15)
    
    center_y = H // 2 + 50
    
    bx = (W - book_s.width) // 2
    by = center_y - book_s.height // 2 - 120
    canvas.paste(book_s, (bx, by), book_s)
    
    # Paste Merch below book
    total_merch_w = mug_s.width + hat_s.width + 40
    start_x = (W - total_merch_w) // 2
    merch_y = by + book_s.height + 40
    
    canvas.paste(mug_s, (start_x, merch_y), mug_s)
    canvas.paste(hat_s, (start_x + mug_s.width + 40, merch_y), hat_s)
    
    # Text
    draw = ImageDraw.Draw(canvas)
    try:
        font_title = ImageFont.truetype(font_path_bold, 90)
        font_sub = ImageFont.truetype(font_path_sans, 40)
    except:
        font_title = font_sub = ImageFont.load_default()
        
    draw.text((100, 200), "THE 250TH", font=font_title, fill="#FFFFFF")
    draw.text((100, 300), "IS COMING.", font=font_title, fill="#D4AF37")
    draw.text((100, 410), "Book & Original Design Merch", font=font_sub, fill="#94A3B8")
    
    # Fake Button
    btn_w, btn_h = 400, 80
    btn_x = (W - btn_w) // 2
    btn_y = H - 200
    try:
        draw.rounded_rectangle([btn_x, btn_y, btn_x+btn_w, btn_y+btn_h], fill="#D4AF37", radius=40)
    except:
        draw.rectangle([btn_x, btn_y, btn_x+btn_w, btn_y+btn_h], fill="#D4AF37")
    
    try:
        bbox = draw.textbbox((0, 0), "LINK IN BIO", font=font_sub)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except:
        tw, th = 200, 40
    draw.text((btn_x + (btn_w - tw)//2, btn_y + (btn_h - th)//2 - 5), "LINK IN BIO", font=font_sub, fill="#000000")
    
    canvas.save(os.path.join(output_dir, "Social_Story.png"))

# 4. LINKEDIN LANDSCAPE (1200 x 627)
def build_linkedin():
    print("Building LinkedIn Landscape...")
    W, H = 1200, 627
    canvas = Image.new("RGBA", (W, H))
    
    bg_w, bg_h = bg_img.size
    scale = max(W/bg_w, H/bg_h)
    bg_scaled = bg_img.resize((int(bg_w * scale), int(bg_h * scale)), Image.Resampling.LANCZOS)
    
    left = (bg_scaled.width - W) // 2
    top = (bg_scaled.height - H) // 2
    bg_cropped = bg_scaled.crop((left, top, left + W, top + H))
    bg_cropped = ImageEnhance.Brightness(bg_cropped).enhance(0.3)
    canvas.paste(bg_cropped, (0, 0))
    
    # Book
    book_h = int(H * 0.65) # Scale down to fit all 3 columns
    book_w = int(book_img.width * (book_h / book_img.height))
    book_r = book_img.resize((book_w, book_h), Image.Resampling.LANCZOS)
    book_s = add_shadow(book_r)
    
    # Merch Stack
    merch_h = int((book_s.height - 40) / 2)
    
    mug_w = int(mug_img.width * (merch_h / mug_img.height))
    mug_r = add_border(mug_img.resize((mug_w, merch_h), Image.Resampling.LANCZOS), border_size=4)
    mug_s = add_shadow(mug_r, offset=(5, 5), radius=10)
    
    hat_w = int(hat_img.width * (merch_h / hat_img.height))
    hat_r = add_border(hat_img.resize((hat_w, merch_h), Image.Resampling.LANCZOS), border_size=4)
    hat_s = add_shadow(hat_r, offset=(5, 5), radius=10)
    
    # Paste Book (Manual placement to ensure it fits between text and merch)
    bx = 520
    by = (H - book_s.height) // 2
    canvas.paste(book_s, (bx, by), book_s)
    
    # Paste Stacked Merch
    stack_x = bx + book_s.width + 30
    stack_y1 = by + 20
    stack_y2 = stack_y1 + hat_s.height + 10
    
    canvas.paste(hat_s, (stack_x, stack_y1), hat_s)
    canvas.paste(mug_s, (stack_x, stack_y2), mug_s)
    
    # Text
    draw = ImageDraw.Draw(canvas)
    try:
        font_title = ImageFont.truetype(font_path_bold, 45)
        font_subtitle = ImageFont.truetype(font_path_sans, 18)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        
    text_x = 40
    draw.text((text_x, 150), "THE AMERICAN STORY.", font=font_title, fill="#FFFFFF")
    draw.text((text_x, 205), "IN YOUR HANDS.", font=font_title, fill="#D4AF37")
    
    draw.text((text_x, 300), "The 250th Anniversary book & merch collection.", font=font_subtitle, fill="#94A3B8")
    draw.text((text_x, 330), "Built for leaders. Designed to be shared.", font=font_subtitle, fill="#94A3B8")
    
    canvas.save(os.path.join(output_dir, "LinkedIn_Landscape.png"))

build_hero()
build_square()
build_story()
build_linkedin()

print("✅ All graphics generated successfully!")
