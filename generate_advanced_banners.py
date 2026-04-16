import os
import math
from PIL import Image, ImageDraw, ImageOps, ImageFilter

output_dir = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/socials"
os.makedirs(output_dir, exist_ok=True)
logo_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1773502605554.png"

# Load the logo
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

width, height = 3000, 1000 # High res 3:1 banner, 300 DPI target

def resize_logo(logo, target_height):
    logo_w, logo_h = logo.size
    aspect = logo_w / logo_h
    new_w = int(target_height * aspect)
    return logo.resize((new_w, target_height), Image.Resampling.LANCZOS)

def save_banner(img, filename):
    save_path = os.path.join(output_dir, filename)
    img.save(save_path, "PNG", dpi=(300, 300))
    print(f"✅ Generated {filename} (300 DPI)")

# --- CONCEPT 1: NEON CYBER GLOW ---
def create_cyber_glow():
    img = Image.new("RGBA", (width, height), (13, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    
    # Create an intense background glow behind the logo
    glow = Image.new("RGBA", (width, height), (0,0,0,0))
    glow_draw = ImageDraw.Draw(glow)
    
    center_x, center_y = width // 2, height // 2
    glow_radius = 800
    
    # Draw radial gradient for the glow (Deep Indigo/Cyan)
    for i in range(glow_radius, 0, -20):
        alpha = int(255 * (1 - (i / glow_radius)) ** 1.5)
        # Deep blue/purple glow
        color = (59, 130, 246, alpha//3) 
        glow_draw.ellipse(
            [center_x - i, center_y - i, center_x + i, center_y + i],
            fill=color
        )
    
    # Add a subtle dot grid overlay for tech/agentic feel
    dot_spacing = 60
    for x in range(0, width, dot_spacing):
        for y in range(0, height, dot_spacing):
            draw.ellipse([x-2, y-2, x+2, y+2], fill=(255, 255, 255, 10))
            
    img = Image.alpha_composite(img, glow)
    
    # Paste Logo
    logo = resize_logo(white_logo, 550)
    logo_w, logo_h = logo.size
    img.paste(logo, ((width - logo_w) // 2, (height - logo_h) // 2), logo)
    
    save_banner(img, "lauralai_dark_concept_1_cyber_glow.png")

# --- CONCEPT 2: PREMIUM MIDNIGHT ELEGANCE ---
def create_midnight_elegance():
    img = Image.new("RGBA", (width, height), (10, 10, 12, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw sharp, elegant geometric diagonal lines in the background
    for i in range(-1500, width + 1500, 200):
        # Very subtle silver/grey lines
        draw.line([(i, 0), (i + 1500, height)], fill=(255, 255, 255, 8), width=3)
        
    # Draw a soft linear gradient at the bottom edge (simulated reflection)
    gradient = Image.new("RGBA", (width, height), (0,0,0,0))
    grad_draw = ImageDraw.Draw(gradient)
    for y in range(height//2, height):
        alpha = int((y - height//2) / (height//2) * 40)
        grad_draw.line([(0, y), (width, y)], fill=(139, 92, 246, alpha)) # Subtle violet tint
    img = Image.alpha_composite(img, gradient)

    # Paste Logo
    logo = resize_logo(white_logo, 500)
    logo_w, logo_h = logo.size
    img.paste(logo, ((width - logo_w) // 2, (height - logo_h) // 2), logo)
    
    save_banner(img, "lauralai_dark_concept_2_midnight_elegant.png")

# --- CONCEPT 3: ABSTRACT INK/SPLATTER (VIBING WITH LOGO) ---
def create_abstract_splatter():
    img = Image.new("RGBA", (width, height), (15, 15, 18, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw some abstract organic shapes mimicking the logo's paint splatter
    import random
    random.seed(42) # Consistent randomness
    
    for _ in range(80):
        # Larger subtle blobs
        x = random.randint(-200, width)
        y = random.randint(-200, height)
        r = random.randint(50, 400)
        opacity = random.randint(5, 25)
        # Using subtle brand-adjacent colors (muted indigo/grey)
        color = (139, 92, 246, opacity) if random.random() > 0.5 else (255, 255, 255, opacity)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

    # Blur the abstract background slightly so it doesn't compete with the sharp logo
    img = img.filter(ImageFilter.GaussianBlur(15))

    # Paste Logo
    logo = resize_logo(white_logo, 550)
    logo_w, logo_h = logo.size
    img.paste(logo, ((width - logo_w) // 2, (height - logo_h) // 2), logo)
    
    save_banner(img, "lauralai_dark_concept_3_abstract_ink.png")


# Execute all generators
print("Generating Advanced Dark Mode Concepts at 300 DPI...")
create_cyber_glow()
create_midnight_elegance()
create_abstract_splatter()
print("All renders complete.")
