import os
from PIL import Image, ImageDraw, ImageFont

input_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1774045115610.png"
output_path = "/Users/michaelprice/Desktop/lauralai/recent_ai_generations/250proud_net_labels_transparent.png"
print("Loading image...")
img = Image.open(input_path).convert("RGBA")
width, height = img.size

pixels = img.load()

# Step 1: Remove the white background using BFS flood-fill
from collections import deque
queue = deque([(0, 0), (width-1, 0), (0, height-1)])
visited = set()

def is_bg(c):
    return c[0] > 240 and c[1] > 240 and c[2] > 240

while queue:
    x, y = queue.popleft()
    if (x, y) in visited:
        continue
        
    color = pixels[x, y]
    if is_bg(color):
        pixels[x, y] = (0, 0, 0, 0)
        visited.add((x, y))
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited:
                    queue.append((nx, ny))

# Step 2: Since it's a screenshot, there are scrollbars and bottom lines. 
# We should try to find the bounding box of non-transparent, non-grey pixels to crop tightly.
# Let's crop it tightly based on alpha. 
# But wait, scrollbar is grey. Let's just find the bounding box of the colored logo.
# The logo uses a distinct dark blue and rich red. Scrollbars are light grey (rgb are equal).
min_x, max_x = width, 0
min_y, max_y = height, 0

for y in range(height):
    for x in range(width):
        r, g, b, a = pixels[x, y]
        if a > 0:
            # If it's a grey pixel from the scrollbar, ignore it for bounding box
            if abs(r - g) < 15 and abs(g - b) < 15 and r > 150: 
                # make scrollbar debris transparent too
                pixels[x, y] = (0, 0, 0, 0)
            else:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y

if min_x > max_x:
    min_x, max_x, min_y, max_y = 0, width-1, 0, height-1

# Give some padding to the crop
pad = 20
crop_box = (max(0, min_x-pad), max(0, min_y-pad), min(width, max_x+pad), min(height, max_y+pad))
logo_cropped = img.crop(crop_box)
c_w, c_h = logo_cropped.size

# Step 3: Expand canvas to add new domain text
new_h = c_h + int(c_h * 0.25)
final_img = Image.new("RGBA", (c_w, new_h), (0, 0, 0, 0))
final_img.paste(logo_cropped, (0, 0), logo_cropped)

# Target Dark Blue color used in the design (sampling the '2' in '250')
# Let's use a standard rich navy blue that matches if we can't reliably sample
target_blue = (12, 53, 98, 255) # Roughly the navy used in the image

draw = ImageDraw.Draw(final_img)
domain_text = "250Proud.Net"

try:
    font_path = "/Library/Fonts/Arial Black.ttf"
    if not os.path.exists(font_path):
         font_path = "/System/Library/Fonts/HelveticaNeue.ttc"
    
    font_size = int(c_h * 0.12) # Size comparable to the USA text
    font = ImageFont.truetype(font_path, font_size)
    
    # Check if we got Helvetica instead of Arial Black, Helvetica might need to be bolder
except:
    font = ImageFont.load_default()

bbox = draw.textbbox((0, 0), domain_text, font=font)
text_w = bbox[2] - bbox[0]
text_h = bbox[3] - bbox[1]

# Position text
x_pos = (c_w - text_w) // 2
y_pos = max_y - min_y + pad + 20

# Draw text
draw.text((x_pos, y_pos), domain_text, font=font, fill=target_blue)

# Upscale nicely for print (300 DPI high res output)
w, h = final_img.size
upscaled = final_img.resize((w*3, h*3), Image.Resampling.LANCZOS)
upscaled.save(output_path, "PNG", dpi=(300, 300))

print(f"✅ Extracted screenshot, removed background, and added domain cleanly at: {output_path}")
