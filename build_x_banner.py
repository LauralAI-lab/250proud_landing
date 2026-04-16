import os
from PIL import Image, ImageOps, ImageEnhance

# File paths
bg_path = "/Users/michaelprice/.gemini/antigravity/brain/cdaeee96-824d-42e1-bfd2-1a54b945a5dd/epic_usa_250_bg_1775356119171.png"
logo_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/logo.png"
output_dir = "/Users/michaelprice/Desktop/lauralai/250proud_landing/socials"
output_path = os.path.join(output_dir, "x_banner_250_official.png")

os.makedirs(output_dir, exist_ok=True)

# 1. Load Background and Logo
bg_full = Image.open(bg_path).convert("RGBA")
original_logo = Image.open(logo_path).convert("RGBA")

# Isolate the logo to pure solid white
# This prevents colors from being inverted into complementary colors like yellow/green
_, _, _, a = original_logo.split()
white_rgb = Image.new("RGB", original_logo.size, (255, 255, 255))
r2, g2, b2 = white_rgb.split()
white_logo = Image.merge("RGBA", (r2, g2, b2, a))

# 2. X background aspect ratio is 3:1 (1500x500). Let's do 3000x1000 for high resolution
target_w, target_h = 3000, 1000

# Calculate crop for background
bg_w, bg_h = bg_full.size
scale_w = target_w / bg_w
scale_h = target_h / bg_h
scale = max(scale_w, scale_h)

scaled_w = int(bg_w * scale)
scaled_h = int(bg_h * scale)
bg_scaled = bg_full.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

# Center crop
left = (scaled_w - target_w) // 2
top = (scaled_h - target_h) // 2
bg_cropped = bg_scaled.crop((left, top, left + target_w, top + target_h))

# Darken background slightly to ensure the logo pops perfectly
enhancer = ImageEnhance.Brightness(bg_cropped)
bg_cropped = enhancer.enhance(0.55) # Darken a bit more for white logo

# 3. Process Logo
logo_w, logo_h = white_logo.size

# We want the logo to take up about 40% of the height vertically
new_logo_h = int(target_h * 0.40)
aspect = logo_w / logo_h
new_logo_w = int(new_logo_h * aspect)

resized_logo = white_logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)

# 4. Composite
# Center horizontally, and perfectly center vertically
x_pos = (target_w - new_logo_w) // 2
y_pos = (target_h - new_logo_h) // 2

bg_cropped.paste(resized_logo, (x_pos, y_pos), resized_logo)

# Save
bg_cropped.save(output_path, "PNG", dpi=(300, 300))
print(f"✅ Successfully created updated X background at: {output_path}")
