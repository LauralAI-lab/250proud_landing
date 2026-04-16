import os
from PIL import Image, ImageOps, ImageEnhance

output_dir = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/socials"
logo_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1773502605554.png"

# The three generated AI backgrounds
bgs = {
    "neural_glow": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/bg_neural_glow_1773503381872.png",
    "sleek_metal": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/bg_sleek_metal_1773503403260.png",
    "fluid_glass": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/bg_fluid_glass_1773503425623.png",
}

# Ensure logo is cleanly isolated and white for dark modes
original_logo = Image.open(logo_path).convert("RGBA")
r, g, b, a = original_logo.split()
rgb_image = Image.merge("RGB", (r, g, b))
inverted_rgb = ImageOps.invert(rgb_image)
r2, g2, b2 = inverted_rgb.split()
white_logo = Image.merge("RGBA", (r2, g2, b2, a))

target_w, target_h = 3000, 1000

for name, bg_path in bgs.items():
    bg_img = Image.open(bg_path).convert("RGBA")
    bg_w, bg_h = bg_img.size
    
    # Scale background to fit width 3000, then crop center to 1000 height
    scaled_h = int(bg_h * (target_w / bg_w))
    bg_scaled = bg_img.resize((target_w, scaled_h), Image.Resampling.LANCZOS)
    
    # Center crop
    top = (scaled_h - target_h) // 2
    bg_cropped = bg_scaled.crop((0, top, target_w, top + target_h))
    
    # Darken slightly to make logo pop more
    enhancer = ImageEnhance.Brightness(bg_cropped)
    bg_cropped = enhancer.enhance(0.75)
    
    # Scale logo
    logo_w, logo_h = white_logo.size
    aspect = logo_w / logo_h
    new_logo_h = 550
    new_logo_w = int(new_logo_h * aspect)
    resized_logo = white_logo.resize((new_logo_w, new_logo_h), Image.Resampling.LANCZOS)
    
    # Composite
    x_pos = (target_w - new_logo_w) // 2
    y_pos = (target_h - new_logo_h) // 2
    bg_cropped.paste(resized_logo, (x_pos, y_pos), resized_logo)
    
    # Save
    out_path = os.path.join(output_dir, f"lauralai_ai_composite_{name}.png")
    bg_cropped.save(out_path, "PNG", dpi=(300, 300))
    print(f"Generated {out_path} at 300 DPI")
