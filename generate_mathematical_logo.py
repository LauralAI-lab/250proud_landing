import os
import math
from PIL import Image, ImageDraw, ImageFont

def draw_mathematical_logo():
    w, h = 4500, 4500
    img = Image.new('RGBA', (w, h), (0,0,0,0))
    d = ImageDraw.Draw(img)
    ink = (25, 25, 30, 255) # Deep technical charcoal
    
    cx, cy = w//2, h//2
    
    # 1. Outer Technical Rings (Blueprint style)
    r1, r2, r3 = 1600, 1550, 1500
    d.ellipse([cx-r1, cy-r1, cx+r1, cy+r1], outline=ink, width=15)
    d.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], outline=ink, width=4)
    
    # 2. Draw 13 intersecting geometric nodal lines (The 13 colonies as pure math)
    points = []
    for i in range(13):
        angle = math.radians((i * (360/13)) - 90)
        px = cx + r3 * math.cos(angle)
        py = cy + r3 * math.sin(angle)
        points.append((px, py))
        # Draw technical crosshair at each node
        d.line([px-40, py, px+40, py], fill=ink, width=8)
        d.line([px, py-40, px, py+40], fill=ink, width=8)
        
    # Connect every node to every other node to create a dense, beautiful mathematical web
    for i in range(len(points)):
        for j in range(i+2, len(points)):
            if i == 0 and j == len(points)-1: continue
            d.line([points[i], points[j]], fill=ink, width=2)
            
    # Connect adjacent nodes for a solid inner boundary
    for i in range(13):
        p1 = points[i]
        p2 = points[(i+1)%13]
        d.line([p1, p2], fill=ink, width=12)
            
    # 3. Brutalist Center Typography (Knockout box to ensure legibility)
    box_w, box_h = 2400, 1000
    d.rectangle([cx-box_w//2, cy-box_h//2, cx+box_w//2, cy+box_h//2], fill=(255,255,255,255))
    d.rectangle([cx-box_w//2, cy-box_h//2, cx+box_w//2, cy+box_h//2], outline=ink, width=20)
    
    try:
        font_hero = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 400)
        font_tech = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New Bold.ttf", 100)
    except:
        font_hero = ImageFont.load_default()
        font_tech = ImageFont.load_default()
        
    text_main = "2 5 0 P R O U D"
    bbox1 = d.textbbox((0,0), text_main, font=font_hero)
    tw1 = bbox1[2] - bbox1[0]
    th1 = bbox1[3] - bbox1[1]
    
    # Mathematical tracking
    d.text((cx - tw1//2, cy - th1//2 - 200), text_main, font=font_hero, fill=ink)
    
    # Technical readout
    tech_data = "OBJ:CULTURAL_ARTIFACT // LAT:17.76 LON:20.26 // SYS.SEC:ALPHA"
    bbox2 = d.textbbox((0,0), tech_data, font=font_tech)
    tw2 = bbox2[2] - bbox2[0]
    d.text((cx - tw2//2, cy + 180), tech_data, font=font_tech, fill=ink)
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Technical_Wireframe_Master_Mark.png")
    
    # Post-process: strip the white background safely so only the raw lines and text remain floating
    arr = np.array(img.convert("RGBA"))
    r, g, b, a = arr[:,:,0], arr[:,:,1], arr[:,:,2], arr[:,:,3]
    is_white = (r > 240) & (g > 240) & (b > 240)
    arr[is_white, 3] = 0
    
    # Save perfectly transparent matrix
    Image.fromarray(arr).save(out_path, "PNG")
    print(f"Generated Mathematical Artifact Logo at {out_path}")

if __name__ == "__main__":
    import numpy as np
    draw_mathematical_logo()
