import os
from PIL import Image, ImageDraw, ImageFont

input_path = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/eagle_logo_transparent_fixed.png"
output_path = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/eagle_logo_with_domain.png"

# Load the fixed logo
logo = Image.open(input_path).convert("RGBA")
width, height = logo.size

# Increase canvas height by 15% to fit the domain comfortably
new_height = int(height * 1.15)
new_img = Image.new("RGBA", (width, new_height), (0, 0, 0, 0))

# Paste original logo at the top
new_img.paste(logo, (0, 0), logo)

# Prepare drawing and font
draw = ImageDraw.Draw(new_img)
domain_text = "250PROUD.NET"

try:
    # Try to load Impact font for that solid, bold, athletic/patriotic feel
    # Impact is widely available on macOS and great for embroidery
    font_path = "/Library/Fonts/Impact.ttf"
    if not os.path.exists(font_path):
        font_path = "/Library/Fonts/Arial Black.ttf"
    
    font_size = int(height * 0.08) # proportional to logo
    font = ImageFont.truetype(font_path, font_size)
except Exception as e:
    print(f"Fallback to default font: {e}")
    font = ImageFont.load_default()

# Get text bounding box to center it
bbox = draw.textbbox((0, 0), domain_text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Calculate exact center
x_pos = (width - text_width) // 2
y_pos = height + int(height * 0.02) # Give a small 2% padding right below the original mark

# Draw the text in a dark charcoal grey that matches typical print illustrations
# We sample a dark color to make it look cohesive
text_color = (40, 42, 45, 255)

# Optional: Draw a thin white stroke underneath to keep it legible if they put it on dark items?
# Since the rest of the logo has a subtle, complex outline, a solid color with a 1px outline works.
outline_color = (255, 255, 255, 255)
stroke_width = 3

# Draw text with outline
draw.text((x_pos, y_pos), domain_text, font=font, fill=text_color, stroke_width=stroke_width, stroke_fill=outline_color)

# Save the final image
new_img.save(output_path, "PNG", dpi=(300, 300))
print(f"✅ Generated new transparent logo for caps/labels at: {output_path}")
