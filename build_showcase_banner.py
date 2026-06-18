import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# File paths matching build_fb_banner.py
bg_path = "american_journey_RAW_for_photoshop.png"
book_path = "nc_assets/img/generated_true_cover.png"
hat_path = "nc_assets/img/mockup_snapback.png"
mug_path = "nc_assets/img/mockup_mug.jpg"
font_path_bold = "fonts/RobotoSlab-Bold.ttf"
font_path_sans = "fonts/OpenSans-Bold.ttf"

output_dir = "socials"
output_path = os.path.join(output_dir, "linkedin_showcase_banner.png")
os.makedirs(output_dir, exist_ok=True)

# 1. Load assets
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

# 2. Target Dimensions for high-res LinkedIn Showcase Banner: 4200 x 700 (aspect ratio 6:1)
W, H = 4200, 700
canvas = Image.new("RGBA", (W, H))

# Scale and crop background
bg_w, bg_h = bg_img.size
scale = max(W/bg_w, H/bg_h)
bg_scaled = bg_img.resize((int(bg_w * scale), int(bg_h * scale)), Image.Resampling.LANCZOS)

left = (bg_scaled.width - W) // 2
top = (bg_scaled.height - H) // 2
bg_cropped = bg_scaled.crop((left, top, left + W, top + H))
# Darken background to 0.38 brightness to match standard campaign templates and ensure text readability
bg_cropped = ImageEnhance.Brightness(bg_cropped).enhance(0.38)
canvas.paste(bg_cropped, (0, 0))

# 3. Process & Scale layout components
book_h = int(H * 0.78) # Take up 78% of height (546px)
book_w = int(book_img.width * (book_h / book_img.height))
book_r = book_img.resize((book_w, book_h), Image.Resampling.LANCZOS)
book_s = add_shadow(book_r, offset=(15, 15), radius=25)

# Merch Stack sizing (fit perfectly to the right of the book)
# With height 700, book_h is 546. Let's make merch height 230px to fit two stacked with margins
merch_h = int((book_h - 70) / 2) # 238px

mug_w = int(mug_img.width * (merch_h / mug_img.height))
mug_r = add_border(mug_img.resize((mug_w, merch_h), Image.Resampling.LANCZOS))
mug_s = add_shadow(mug_r, offset=(10, 10), radius=15)

hat_w = int(hat_img.width * (merch_h / hat_img.height))
hat_r = add_border(hat_img.resize((hat_w, merch_h), Image.Resampling.LANCZOS))
hat_s = add_shadow(hat_r, offset=(10, 10), radius=15)

# Position Book and Merch Stack
# Place them on the right side but within the safe area for mobile cropping (right edge safe zone is around x=3450)
bx = 2450 
by = (H - book_s.height) // 2
canvas.paste(book_s, (bx, by), book_s)

# Place the hat and mug to the right of the book
stack_x = bx + book_s.width - 20 # Overlay shadow adjustment
stack_y1 = by + 20
stack_y2 = stack_y1 + hat_s.height + 15

canvas.paste(hat_s, (stack_x, stack_y1), hat_s)
canvas.paste(mug_s, (stack_x, stack_y2), mug_s)

# 4. Render typography
draw = ImageDraw.Draw(canvas)
try:
    font_title = ImageFont.truetype(font_path_bold, 95)
    font_subtitle = ImageFont.truetype(font_path_sans, 38)
except Exception as e:
    print(f"Error loading fonts: {e}, falling back.")
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()

# Start text at x=800. This is safely to the right of the LinkedIn logo overlay (x=167 to x=583 on desktop)
# and well within the mobile viewable center.
text_x = 800
title_y1 = 150
title_y2 = 260
sub_y1 = 400
sub_y2 = 460

# Draw headers
draw.text((text_x, title_y1), "THE AMERICAN STORY.", font=font_title, fill="#FFFFFF")
draw.text((text_x, title_y2), "IN YOUR HANDS.", font=font_title, fill="#D4AF37")

# Draw subheadings
draw.text((text_x, sub_y1), "The 250th Anniversary book & merch collection.", font=font_subtitle, fill="#94A3B8")
draw.text((text_x, sub_y2), "Built for leaders. Designed to be shared.", font=font_subtitle, fill="#94A3B8")

# Save
canvas.save(output_path, "PNG", dpi=(300, 300))
print(f"✅ Successfully generated LinkedIn Showcase Page banner at: {output_path}")
