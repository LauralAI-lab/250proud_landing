import os
import shutil
from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFont

output_dir = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/socials/final_assets_with_tagline"
os.makedirs(output_dir, exist_ok=True)

logo_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1773502605554.png"
bg_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/bg_sleek_metal_1773503403260.png"
profile_pic_path = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/socials/lauralai_profile_light.png"
tagline = "Strategic Creativity. Accelerated by AI."

# Try to load a nice system font for macOS, fallback to default
try:
    # Avenir Next is a very clean, premium font on Macs
    font_path = "/System/Library/Fonts/Avenir Next.ttc"
    # Fallback to Helvetica if Avenir isn't found
    if not os.path.exists(font_path):
        font_path = "/System/Library/Fonts/HelveticaNeue.ttc"
    base_font = ImageFont.truetype(font_path, 60)
except Exception:
    base_font = ImageFont.load_default()

# Isolate the logo to white for dark backgrounds
original_logo = Image.open(logo_path).convert("RGBA")
r, g, b, a = original_logo.split()
rgb_image = Image.merge("RGB", (r, g, b))
inverted_rgb = ImageOps.invert(rgb_image)
r2, g2, b2 = inverted_rgb.split()
white_logo = Image.merge("RGBA", (r2, g2, b2, a))

bg_full = Image.open(bg_path).convert("RGBA")

formats = {
    "Twitter_Header": (3000, 1000),         
    "Facebook_Cover": (2460, 936),          
    "LinkedIn_Company_Cover": (3384, 573),  
    "YouTube_Banner": (2560, 1440)          
}

for platform, (target_w, target_h) in formats.items():
    bg_w, bg_h = bg_full.size
    
    scale_w = target_w / bg_w
    scale_h = target_h / bg_h
    scale = max(scale_w, scale_h)
    
    scaled_w = int(bg_w * scale)
    scaled_h = int(bg_h * scale)
    
    bg_scaled = bg_full.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
    
    left = (scaled_w - target_w) // 2
    top = (scaled_h - target_h) // 2
    bg_cropped = bg_scaled.crop((left, top, left + target_w, top + target_h))
    
    enhancer = ImageEnhance.Brightness(bg_cropped)
    bg_cropped = enhancer.enhance(0.65) # Darken a tiny bit more for text legibility
    
    logo_w, logo_h = white_logo.size
    aspect = logo_w / logo_h
    
    # Make logo slightly smaller to accommodate text below
    new_logo_h = min(int(target_h * 0.35), int(target_w * 0.20 / aspect))
    new_logo_w = int(new_logo_h * aspect)
    resized_logo = white_logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)
    
    # Calculate positions
    vertical_spacing = 40
    total_content_h = new_logo_h + vertical_spacing + 60 # approx font height
    
    start_y = (target_h - total_content_h) // 2
    logo_x = (target_w - new_logo_w) // 2
    
    # Paste logo
    bg_cropped.paste(resized_logo, (logo_x, start_y), resized_logo)
    
    # Draw tagline
    draw = ImageDraw.Draw(bg_cropped)
    try:
        # Scale font size based on banner size
        font_size = int(target_h * 0.06)
        dynamic_font = ImageFont.truetype(font_path, font_size)
    except:
        dynamic_font = base_font
        
    text_bbox = draw.textbbox((0, 0), tagline, font=dynamic_font)
    text_w = text_bbox[2] - text_bbox[0]
    text_x = (target_w - text_w) // 2
    text_y = start_y + new_logo_h + vertical_spacing
    
    # Subtle drop shadow for text
    draw.text((text_x+2, text_y+2), tagline, font=dynamic_font, fill=(0,0,0,150))
    # Elegant silver/white text
    draw.text((text_x, text_y), tagline, font=dynamic_font, fill=(230, 230, 235, 255))
    
    out_path = os.path.join(output_dir, f"{platform}_with_tagline.png")
    bg_cropped.save(out_path, "PNG", dpi=(300, 300))
    print(f"✅ Generated {platform}_with_tagline.png")

# Copy profile pic
try:
    shutil.copy(profile_pic_path, os.path.join(output_dir, "Profile_Picture.png"))
except Exception as e:
    pass

print(f"\nAll assets with tagline saved to: {output_dir}")
