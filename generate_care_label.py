import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

def draw_wash_bucket(draw, x, y, size):
    # Base bucket
    w = size
    h = size * 0.7
    pts = [(x, y), (x+w, y), (x+w*0.8, y+h), (x+w*0.2, y+h)]
    draw.polygon(pts, outline=(40,40,40,255), width=25)
    # Wave line
    draw.line([(x, y+h*0.3), (x+w, y+h*0.3)], fill=(40,40,40,255), width=25)
    # 30C text inside
    # (Leaving it abstracted for the industrial style)

def draw_triangle(draw, x, y, size):
    h = size * 0.866 # equilateral
    pts = [(x+size/2, y), (x+size, y+h), (x, y+h)]
    draw.polygon(pts, outline=(40,40,40,255), width=25)
    # Cross it out to say "DO NOT BLEACH"
    draw.line([(x, y), (x+size, y+h)], fill=(40,40,40,255), width=25)
    draw.line([(x+size, y), (x, y+h)], fill=(40,40,40,255), width=25)

def draw_square_circle(draw, x, y, size):
    draw.rectangle([x, y, x+size, y+size], outline=(40,40,40,255), width=25)
    margin = size * 0.15
    draw.ellipse([x+margin, y+margin, x+size-margin, y+size-margin], outline=(40,40,40,255), width=25)
    # Cross out
    draw.line([(x, y), (x+size, y+size)], fill=(40,40,40,255), width=25)
    draw.line([(x+size, y), (x, y+size)], fill=(40,40,40,255), width=25)

def draw_iron(draw, x, y, size):
    w = size
    h = size * 0.6
    # Base iron
    pts = [(x, y+h), (x+w, y+h), (x+w*0.8, y), (x+w*0.3, y), (x, y+h)]
    draw.polygon(pts, outline=(40,40,40,255), width=25)
    # Iron handle
    draw.line([(x+w*0.8, y), (x+w*0.9, y-h*0.4), (x+w*0.4, y-h*0.4), (x+w*0.3, y)], fill=(40,40,40,255), width=25)

def create_care_label():
    width, height = 4500, 5400
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Trebuchet MS Bold.ttf",
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
    ]
    
    font_large = None
    font_med = None
    font_small = None
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                font_large = ImageFont.truetype(path, 380)
                font_med = ImageFont.truetype(path, 180)
                font_small = ImageFont.truetype(path, 100)
                print(f"Loaded font: {path}")
                break
            except Exception as e:
                continue
                
    if font_large is None:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()
        
    text_color = (35, 35, 35, 255)
    thick = 35
    
    # Outer Border Box
    margin_x = 500
    margin_y = 600
    draw.rectangle([margin_x, margin_y, width-margin_x, height-margin_y], outline=text_color, width=thick)
    
    # Top massive text
    draw.text((margin_x + 150, margin_y + 150), "2  5  0  P  R  O  U  D", font=font_large, fill=text_color)
    draw.line([(margin_x, margin_y + 650), (width-margin_x, margin_y + 650)], fill=text_color, width=thick)
    
    # Authenticity subheader
    draw.text((margin_x + 150, margin_y + 750), "AUTHENTIC AMERICAN GARMENT", font=font_med, fill=text_color)
    draw.line([(margin_x, margin_y + 1050), (width-margin_x, margin_y + 1050)], fill=text_color, width=thick)
    
    # Content block
    y_start = margin_y + 1150
    draw.text((margin_x + 150, y_start), "CONTENT:", font=font_small, fill=text_color)
    draw.text((margin_x + 150, y_start + 150), "100% HEAVYWEIGHT COTTON", font=font_med, fill=text_color)
    
    y_start += 450
    draw.text((margin_x + 150, y_start), "ORIGIN:", font=font_small, fill=text_color)
    draw.text((margin_x + 150, y_start + 150), "ESTABLISHED 1776", font=font_med, fill=text_color)
    
    y_start += 450
    draw.text((margin_x + 150, y_start), "LOT NO:", font=font_small, fill=text_color)
    draw.text((margin_x + 150, y_start + 150), "07-04-76", font=font_med, fill=text_color)
    
    draw.line([(margin_x, y_start + 450), (width-margin_x, y_start + 450)], fill=text_color, width=thick)
    
    # Warning block (Brutalist style)
    y_start += 550
    draw.text((margin_x + 150, y_start), "!! WARNING !!", font=font_med, fill=text_color)
    draw.text((margin_x + 150, y_start + 250), "DO NOT COMPROMISE VALUES.", font=font_med, fill=text_color)
    draw.text((margin_x + 150, y_start + 500), "ENGINEERED TO LAST 250", font=font_med, fill=text_color)
    draw.text((margin_x + 150, y_start + 700), "CONTINUOUS YEARS.", font=font_med, fill=text_color)
    
    draw.line([(margin_x, y_start + 1000), (width-margin_x, y_start + 1000)], fill=text_color, width=thick)
    
    # Laundry icons
    y_start += 1150
    icon_size = 250
    spacing = 400
    base_x = margin_x + 400
    
    draw_wash_bucket(draw, base_x, y_start, icon_size)
    draw_triangle(draw, base_x + spacing, y_start, icon_size)
    draw_square_circle(draw, base_x + spacing*2, y_start, icon_size)
    draw_iron(draw, base_x + spacing*3, y_start, icon_size)
    
    draw.text((margin_x + 150, y_start + 350), "WASH COLD. HANG DRY.", font=font_med, fill=text_color)
    draw.text((margin_x + 150, y_start + 550), "WEAR WITH ABSOLUTE PRIDE.", font=font_med, fill=text_color)
    
    # Distressing algorithms
    # Rotate very slightly like imperfect screenprint alignment
    img = img.rotate(1.5, resample=Image.Resampling.BICUBIC, center=(width//2, height//2))
    
    arr = np.array(img)
    noise = np.random.randint(0, 255, (height, width), dtype=np.uint8)
    
    # Punch out microscopic dots simulating old block printing
    distress_mask = noise > 210
    alpha_channel = arr[:, :, 3]
    has_ink = alpha_channel > 0
    arr[distress_mask & has_ink, 3] = 0
    
    # Small gaussian blur to make the text thick and bleeding natively into the fabric
    final_img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(2.0))
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/New_Concepts"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Care_Label_250PROUD_4500x5400.png")
    final_img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Generated brutalist label at {out_path}")

if __name__ == "__main__":
    create_care_label()
