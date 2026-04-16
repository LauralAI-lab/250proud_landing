import os
from PIL import Image, ImageDraw, ImageFont
import urllib.request

def build():
    font_path = "/System/Library/Fonts/HelveticaNeue.ttc"
    
    font_hero = ImageFont.truetype(font_path, 400)
    
    blue = (30, 60, 140, 255)
    red = (180, 45, 40, 255)
    black = (20, 20, 25, 255)
    
    text_250 = "250"
    text_proud = " PROUD" # Add leading space to fuse the blocks smoothly
    
    # 1. Render the hero text individually to squash it
    temp = Image.new('RGBA', (4000, 600), (0,0,0,0))
    d_temp = ImageDraw.Draw(temp)
    
    w_250 = int(d_temp.textlength(text_250, font=font_hero))
    w_proud = int(d_temp.textlength(text_proud, font=font_hero))
    
    img_250 = Image.new('RGBA', (w_250 + 50, 600), (0,0,0,0))
    d2 = ImageDraw.Draw(img_250)
    d2.text((0,0), text_250, font=font_hero, fill=blue)
    
    # DRAW THE SLASH THROUGH THE ZERO mathematically
    # Orbitron 0 is approximately between w_250*0.65 and w_250
    zero_x_start = int(w_250 * 0.70)
    zero_x_end = w_250 - 25
    zero_y_top = 110
    zero_y_bot = 400
    d2.line([(zero_x_start, zero_y_bot), (zero_x_end, zero_y_top)], fill=blue, width=28)
    
    img_proud = Image.new('RGBA', (w_proud + 100, 600), (0,0,0,0))
    d_proud = ImageDraw.Draw(img_proud)
    d_proud.text((0,0), text_proud, font=font_hero, fill=red)
    
    # SQUASH AND STRETCH 
    # Make it incredibly wide and extremely squat/short
    squash_factor_y = 0.40
    stretch_factor_x = 1.30
    
    new_w_250 = int(img_250.size[0] * stretch_factor_x)
    new_h_250 = int(img_250.size[1] * squash_factor_y)
    img_250 = img_250.resize((new_w_250, new_h_250), Image.Resampling.LANCZOS)
    
    new_w_proud = int(img_proud.size[0] * stretch_factor_x)
    new_h_proud = int(img_proud.size[1] * squash_factor_y)
    img_proud = img_proud.resize((new_w_proud, new_h_proud), Image.Resampling.LANCZOS)
    
    # Assembly
    space = -10 # Tight tracking exactly like the design
    hero_w = new_w_250 + new_w_proud + space
    hero_h = new_h_250
    
    # Create final extremely tight bounding box
    padding_x = 80
    padding_y = 70
    box_w = hero_w + (padding_x * 2)
    box_h = int(img_250.size[1] * 0.9)  # Cropped tightly to the text bounds vertically
    
    final_img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
    d_final = ImageDraw.Draw(final_img)
    
    # White background, thin tight black border
    d_final.rectangle([0, 0, box_w, box_h], fill=(255,255,255,255))
    d_final.rectangle([4, 4, box_w-4, box_h-4], outline=black, width=8) 
    
    # Paste the squashed text
    start_x = padding_x
    start_y = 60 # Snug vertical placement
    final_img.paste(img_250, (start_x, start_y), img_250)
    final_img.paste(img_proud, (start_x + new_w_250 + space, start_y), img_proud)
    
    # Tiny precise tech text
    font_sub = ImageFont.truetype(font_path, 60)
    d_final.text((start_x + 20, 15), "1776 - 2026", font=font_sub, fill=black)
    d_final.text((start_x + 20, box_h - 75), "SEMIQUINCENTENNIAL", font=font_sub, fill=black)
    
    # Crosshairs on border
    c_y = box_h // 2
    c_x = box_w // 2
    d_final.line([(0, c_y), (40, c_y)], fill=black, width=6)
    d_final.line([(box_w-40, c_y), (box_w, c_y)], fill=black, width=6)
    d_final.line([(c_x, 0), (c_x, 40)], fill=black, width=6)
    d_final.line([(c_x, box_h-40), (c_x, box_h)], fill=black, width=6)

    # Save
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    master_path = os.path.join(out_dir, "Official_Blueprint_Tech_Block_Logo.png")
    final_img.save(master_path, "PNG")
    
    # White BG Proof
    white = Image.new("RGB", final_img.size, (255, 255, 255))
    white.paste(final_img, (0, 0), final_img)
    white.save(master_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=95)
    print(f"Saved squatted logo to {master_path}")

if __name__ == "__main__":
    build()
