import os
import shutil
from PIL import Image, ImageOps, ImageEnhance

output_dir = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/socials/final_assets"
os.makedirs(output_dir, exist_ok=True)

logo_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1773502605554.png"
bg_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/bg_sleek_metal_1773503403260.png"
profile_pic_path = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/socials/lauralai_profile_light.png"

# Isolate the logo to white for dark backgrounds
original_logo = Image.open(logo_path).convert("RGBA")
r, g, b, a = original_logo.split()
rgb_image = Image.merge("RGB", (r, g, b))
inverted_rgb = ImageOps.invert(rgb_image)
r2, g2, b2 = inverted_rgb.split()
white_logo = Image.merge("RGBA", (r2, g2, b2, a))

bg_full = Image.open(bg_path).convert("RGBA")

# Standard social media banner dimensions, scaled up slightly for crisp 300 DPI high-res loading
formats = {
    "Twitter_Header": (3000, 1000),         # Double size of 1500x500
    "Facebook_Cover": (2460, 936),          # High res 820x312
    "LinkedIn_Company_Cover": (3384, 573),  # High res 1128x191
    "YouTube_Banner": (2560, 1440)          # Native full TV size
}

for platform, (target_w, target_h) in formats.items():
    bg_w, bg_h = bg_full.size
    
    # Scale background to perfectly COVER target dimensions
    scale_w = target_w / bg_w
    scale_h = target_h / bg_h
    scale = max(scale_w, scale_h)
    
    scaled_w = int(bg_w * scale)
    scaled_h = int(bg_h * scale)
    
    bg_scaled = bg_full.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)
    
    # Center crop the background
    left = (scaled_w - target_w) // 2
    top = (scaled_h - target_h) // 2
    bg_cropped = bg_scaled.crop((left, top, left + target_w, top + target_h))
    
    # Darken slightly to make logo pop
    enhancer = ImageEnhance.Brightness(bg_cropped)
    bg_cropped = enhancer.enhance(0.75)
    
    # Scale the logo perfectly for the specific banner
    logo_w, logo_h = white_logo.size
    aspect = logo_w / logo_h
    
    # Logo height should hit the golden ratio of the banner height
    new_logo_h = min(int(target_h * 0.45), int(target_w * 0.25 / aspect))
    new_logo_w = int(new_logo_h * aspect)
    resized_logo = white_logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)
    
    # Composite logo onto background perfectly centered
    x_pos = (target_w - new_logo_w) // 2
    y_pos = (target_h - new_logo_h) // 2
    bg_cropped.paste(resized_logo, (x_pos, y_pos), resized_logo)
    
    # Save the 300 DPI PNG
    out_path = os.path.join(output_dir, f"{platform}.png")
    bg_cropped.save(out_path, "PNG", dpi=(300, 300))
    print(f"✅ Generated {platform}.png")

# Copy the approved profile picture into the final payload folder too
try:
    shutil.copy(profile_pic_path, os.path.join(output_dir, "Profile_Picture.png"))
    print("✅ Copied Profile_Picture.png")
except Exception as e:
    print(f"Error copying profile pic: {e}")

print(f"\nAll final social assets successfully saved to: {output_dir}")
