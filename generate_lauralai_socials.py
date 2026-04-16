import os
from PIL import Image, ImageDraw, ImageOps, ImageFilter

output_dir = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/socials"
os.makedirs(output_dir, exist_ok=True)
logo_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1773502605554.png"

# Load the logo (Ensure it's RGBA)
try:
    original_logo = Image.open(logo_path).convert("RGBA")
except Exception as e:
    print(f"Error loading logo: {e}")
    exit(1)

# Create an inverted white version of the logo for dark backgrounds
r, g, b, a = original_logo.split()
rgb_image = Image.merge("RGB", (r, g, b))
inverted_rgb = ImageOps.invert(rgb_image)
r2, g2, b2 = inverted_rgb.split()
white_logo = Image.merge("RGBA", (r2, g2, b2, a))

def draw_rounded_rect(draw, bbox, radius, fill):
    """Draw a rounded rectangle with Pillow."""
    x0, y0, x1, y1 = bbox
    draw.rectangle([x0+radius, y0, x1-radius, y1], fill=fill)
    draw.rectangle([x0, y0+radius, x1, y1-radius], fill=fill)
    draw.pieslice([x0, y0, x0+radius*2, y0+radius*2], 180, 270, fill=fill)
    draw.pieslice([x1-radius*2, y0, x1, y0+radius*2], 270, 360, fill=fill)
    draw.pieslice([x0, y1-radius*2, x0+radius*2, y1], 90, 180, fill=fill)
    draw.pieslice([x1-radius*2, y1-radius*2, x1, y1], 0, 90, fill=fill)

def create_banner(filename, bg_color, is_dark):
    """Generates a 1500x500 Page Banner at 300 DPI with transparent rounded corners."""
    width, height = 3000, 1000 # 2x resolution for high quality, saved with 300 DPI metadata
    # True transparent background
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background with rounded corners
    draw_rounded_rect(draw, [50, 50, width-50, height-50], 100, fill=bg_color)
    
    # Add some tasteful minimalist geometry as background texture
    accent_color = (255, 255, 255, 10) if is_dark else (0, 0, 0, 10)
    for i in range(5):
        rad = 300 + (i * 200)
        draw.ellipse([width - rad, height//2 - rad, width + rad, height//2 + rad], outline=accent_color, width=8)
    
    # Add the logo
    logo_to_use = white_logo if is_dark else original_logo
    
    # Resize logo appropriately (height around 500px to fit well inside 1000px layout)
    logo_w, logo_h = logo_to_use.size
    aspect = logo_w / logo_h
    new_h = 500
    new_w = int(new_h * aspect)
    resized_logo = logo_to_use.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Calculate perfect center position
    x_pos = (width - new_w) // 2
    y_pos = (height - new_h) // 2
    
    # Composite the logo
    img.paste(resized_logo, (x_pos, y_pos), resized_logo)
    
    # Save the file with 300 DPI exactly
    save_path = os.path.join(output_dir, filename)
    img.save(save_path, "PNG", dpi=(300, 300))
    print(f"Generated {filename} (300 DPI, transparent edges)")

def create_profile_pic(filename, bg_color, is_dark):
    """Generates a perfectly circular 1080x1080 profile graphic at 300 DPI."""
    size = 1080
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw perfect circle background
    draw.ellipse([20, 20, size-20, size-20], fill=bg_color)
    
    logo_to_use = white_logo if is_dark else original_logo
    logo_w, logo_h = logo_to_use.size
    aspect = logo_w / logo_h
    new_h = 450
    new_w = int(new_h * aspect)
    resized_logo = logo_to_use.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    x_pos = (size - new_w) // 2
    y_pos = (size - new_h) // 2
    
    img.paste(resized_logo, (x_pos, y_pos), resized_logo)
    
    save_path = os.path.join(output_dir, filename)
    img.save(save_path, "PNG", dpi=(300, 300))
    print(f"Generated {filename} (300 DPI, transparent edges)")

# Generate Concept 1: Slate Dark Mode
create_banner("lauralai_banner_dark_concept.png", (20, 25, 32, 255), True)

# Generate Concept 2: Minimalist Light Mode
create_banner("lauralai_banner_light_concept.png", (245, 246, 250, 255), False)

# Generate supporting circular profile pics / graphics
create_profile_pic("lauralai_profile_dark.png", (20, 25, 32, 255), True)
create_profile_pic("lauralai_profile_light.png", (245, 246, 250, 255), False)

print(f"All 300 DPI transparent social graphics ready in: {output_dir}")
