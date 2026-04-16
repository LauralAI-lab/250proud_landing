import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_original_startup():
    width, height = 4500, 5400
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/HelveticaNeue-CondensedBlack.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Trebuchet MS Bold.ttf"
    ]
    
    font_large = None
    font_small = None
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                # Need massive font for "THE ORIGINAL STARTUP"
                font_large = ImageFont.truetype(path, 450)
                font_small = ImageFont.truetype(path, 180)
                print(f"Loaded font: {path}")
                break
            except Exception as e:
                continue
                
    if font_large is None:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
        print("WARNING: Default font used.")
        
    # Sun-washed charcoal ink
    ink_color = (45, 45, 48, 255)
    
    # Text lines
    line1 = "THE ORIGINAL"
    line2 = "STARTUP."
    line3 = "EST. 1776"
    
    # Center everything
    def draw_centered_text(draw_obj, text, y_pos, font, fill):
        bbox = draw_obj.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x_pos = (width - text_w) / 2
        draw_obj.text((x_pos, y_pos), text, font=font, fill=fill)
    
    # Y offsets
    base_y = 1500
    draw_centered_text(draw, line1, base_y, font_large, ink_color)
    draw_centered_text(draw, line2, base_y + 450, font_large, ink_color)
    
    # Small line
    draw_centered_text(draw, line3, base_y + 1050, font_small, ink_color)
    
    # Slight subtle distress
    arr = np.array(img)
    noise = np.random.randint(0, 255, (height, width), dtype=np.uint8)
    distress_mask = noise > 240 # Very light distress 
    alpha_channel = arr[:, :, 3]
    has_ink = alpha_channel > 0
    arr[distress_mask & has_ink, 3] = 0
    
    # Super slight edge bleed
    final_img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(1.0))
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/New_Concepts"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "The_Original_Startup_4500x5400.png")
    final_img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Generated {out_path}")

if __name__ == "__main__":
    create_original_startup()
