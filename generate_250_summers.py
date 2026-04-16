import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def draw_star(draw, cx, cy, R, fill, rotation_deg=0):
    r = R * 0.382
    pts = []
    # Start pointing straight up, offset by overall rotation
    for i in range(10):
        angle_deg = i * 36 - 90 + rotation_deg
        angle_rad = math.radians(angle_deg)
        radius = R if i % 2 == 0 else r
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)
        pts.append((x, y))
    draw.polygon(pts, fill=fill)

def create_250_summers():
    width, height = 4500, 5400
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_paths = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Times.ttc",
        "/System/Library/Fonts/Supplemental/Arial Narrow.ttf"
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                # Small, clean type for the beach town feel
                font = ImageFont.truetype(path, 140)
                print(f"Loaded font: {path}")
                break
            except Exception as e:
                continue
                
    if font is None:
        font = ImageFont.load_default()
        
    # Sun-washed vintage navy ink
    ink_color = (40, 50, 75, 255)
    
    # 1. Draw the Arc of 5 Stars
    arc_center_x = width // 2
    arc_center_y = 2600 
    arc_radius = 1200
    
    angles_deg = [-42, -21, 0, 21, 42]
    star_radius = 160
    
    for angle in angles_deg:
        rad = math.radians(angle - 90) # -90 makes 0 straight up
        sx = arc_center_x + arc_radius * math.cos(rad)
        sy = arc_center_y + arc_radius * math.sin(rad)
        # We rotate the star slightly to align with the arc center
        draw_star(draw, sx, sy, star_radius, ink_color, rotation_deg=angle)
        
    # 2. Draw the Text
    text = "2 5 0   S U M M E R S   ·   1 7 7 6 - 2 0 2 6"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    
    tx = (width - text_w) / 2
    ty = arc_center_y - arc_radius + 450 # Place beneath the top star arc
    
    draw.text((tx, ty), text, font=font, fill=ink_color)
    
    # Very slight distress to look like sun-washed printed cotton
    arr = np.array(img)
    noise = np.random.randint(0, 255, (height, width), dtype=np.uint8)
    distress_mask = noise > 235 
    has_ink = arr[:, :, 3] > 0
    arr[distress_mask & has_ink, 3] = 0
    
    # Tiny blur for ink spread
    final_img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(1.2))
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/New_Concepts"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "250_Summers_4500x5400.png")
    final_img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Generated {out_path}")

if __name__ == "__main__":
    create_250_summers()
