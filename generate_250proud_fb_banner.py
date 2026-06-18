import os
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFont

# Input Paths
bg_fixed_path = "/Users/michaelprice/.gemini/antigravity/brain/cdaeee96-824d-42e1-bfd2-1a54b945a5dd/epic_usa_250_bg_fixed_1775410588729.png"
bg_fallback_path = "/Users/michaelprice/.gemini/antigravity/brain/cdaeee96-824d-42e1-bfd2-1a54b945a5dd/epic_usa_250_bg_1775356119171.png"
logo_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/logo.png"
font_bold_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/fonts/RobotoSlab-Bold.ttf"
font_sans_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/fonts/OpenSans-Bold.ttf"

output_dir = "/Users/michaelprice/Desktop/lauralai/250proud_landing/socials"
os.makedirs(output_dir, exist_ok=True)

# Select Background
if os.path.exists(bg_fixed_path):
    bg_path = bg_fixed_path
else:
    bg_path = bg_fallback_path

print(f"Using background: {bg_path}")

# Load Background and Logo
bg_full = Image.open(bg_path).convert("RGBA")
original_logo = Image.open(logo_path).convert("RGBA")

# Isolate logo to pure white for dark/patriotic backgrounds
_, _, _, a = original_logo.split()
white_rgb = Image.new("RGB", original_logo.size, (255, 255, 255))
r2, g2, b2 = white_rgb.split()
white_logo = Image.merge("RGBA", (r2, g2, b2, a))

# Dimensions for high-res Facebook Cover (300 DPI layout)
target_w, target_h = 2460, 936

# Crop & Resize Background
bg_w, bg_h = bg_full.size
scale_w = target_w / bg_w
scale_h = target_h / bg_h
scale = max(scale_w, scale_h)

scaled_w = int(bg_w * scale)
scaled_h = int(bg_h * scale)
bg_scaled = bg_full.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

left = (scaled_w - target_w) // 2
top = (scaled_h - target_h) // 2
bg_cropped_base = bg_scaled.crop((left, top, left + target_w, top + target_h))

# ----------------- OPTION 1: CLASSIC LOGO ONLY -----------------
bg_classic = bg_cropped_base.copy()
enhancer = ImageEnhance.Brightness(bg_classic)
bg_classic = enhancer.enhance(0.55) # Darken to pop logo

# Process logo (take up about 45% of banner height)
logo_w, logo_h = white_logo.size
aspect = logo_w / logo_h
new_logo_h = int(target_h * 0.45)
new_logo_w = int(new_logo_h * aspect)
resized_logo = white_logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)

# Perfect center alignment
x_pos = (target_w - new_logo_w) // 2
y_pos = (target_h - new_logo_h) // 2
bg_classic.paste(resized_logo, (x_pos, y_pos), resized_logo)

classic_out = os.path.join(output_dir, "fb_banner_250_classic.png")
bg_classic.save(classic_out, "PNG", dpi=(300, 300))
print(f"✅ Generated Classic Facebook Banner: {classic_out}")

# ----------------- OPTION 2: LOGO + TAGLINE ("HONOR OUR HISTORY") -----------------
bg_tagline = bg_cropped_base.copy()
enhancer = ImageEnhance.Brightness(bg_tagline)
bg_tagline = enhancer.enhance(0.50) # Darken slightly more for text legibility

# Adjust logo slightly smaller to fit tagline underneath
new_logo_h = int(target_h * 0.35)
new_logo_w = int(new_logo_h * aspect)
resized_logo_tagline = white_logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)

# Tagline and font configuration
tagline = "HONOR OUR HISTORY. WEAR YOUR PRIDE."
try:
    font_size = int(target_h * 0.05) # ~46px
    font = ImageFont.truetype(font_bold_path, font_size)
except Exception:
    font = ImageFont.load_default()

# Layout spacing
vertical_spacing = 50
total_content_h = new_logo_h + vertical_spacing + 50 # height of logo + gap + text

start_y = (target_h - total_content_h) // 2
logo_x = (target_w - new_logo_w) // 2
bg_tagline.paste(resized_logo_tagline, (logo_x, start_y), resized_logo_tagline)

# Draw text
draw = ImageDraw.Draw(bg_tagline)
text_bbox = draw.textbbox((0, 0), tagline, font=font)
text_w = text_bbox[2] - text_bbox[0]
text_x = (target_w - text_w) // 2
text_y = start_y + new_logo_h + vertical_spacing

# High-contrast elegant drop shadow
draw.text((text_x + 3, text_y + 3), tagline, font=font, fill=(0, 0, 0, 200))
# Pure white/gold color matching the brand style
draw.text((text_x, text_y), tagline, font=font, fill=(245, 240, 230, 255))

tagline_out = os.path.join(output_dir, "fb_banner_250_with_tagline.png")
bg_tagline.save(tagline_out, "PNG", dpi=(300, 300))
print(f"✅ Generated Tagline Facebook Banner: {tagline_out}")
