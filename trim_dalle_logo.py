import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def build():
    img_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/logo_master_raster_v2_1774363066585.png"
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    
    # 1. Chroma-key out all black and grayscale pixels
    r, g, b, a = arr[:,:,0].astype(int), arr[:,:,1].astype(int), arr[:,:,2].astype(int), arr[:,:,3].astype(int)
    
    diff_rb = np.abs(r - b)
    diff_rg = np.abs(r - g)
    is_gray = (diff_rb < 30) & (diff_rg < 30) & (r < 220)
    arr[is_gray] = [255, 255, 255, 255]
    
    # 2. Extract the remaining text tightly (the Vintage Blue & Faded Red)
    r_new, g_new, b_new = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    non_white = (r_new < 240) | (g_new < 240) | (b_new < 240)
    coords = np.column_stack(np.where(non_white))
    
    if coords.size == 0:
        print("Failed to isolate colored text!")
        return
        
    min_y, min_x = coords.min(axis=0)
    max_y, max_x = coords.max(axis=0)
    
    cleaned_img = Image.fromarray(arr)
    hero_text_img = cleaned_img.crop((min_x, min_y, max_x, max_y))
    
    # Size for clarity
    hero_text_img = hero_text_img.resize((2400, 360), Image.Resampling.LANCZOS)
    
    # 3. Rebuild the tightest, narrowest possible boundary box
    pad_h = 60
    pad_v = 70
    box_w = hero_text_img.size[0] + (pad_h * 2)
    box_h = hero_text_img.size[1] + (pad_v * 2)
    
    final_img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
    d = ImageDraw.Draw(final_img)
    
    d.rectangle([0, 0, box_w, box_h], fill=(255, 255, 255, 255))
    d.rectangle([4, 4, box_w-4, box_h-4], outline=(20, 20, 25, 255), width=8)
    
    final_img.paste(hero_text_img, (pad_h, pad_v), hero_text_img)
    
    # Native technical tracking
    font_sub_path = "/System/Library/Fonts/HelveticaNeue.ttc"
    font_sub = ImageFont.truetype(font_sub_path, 40) if os.path.exists(font_sub_path) else ImageFont.load_default()
    
    black = (20, 20, 25, 255)
    d.text((pad_h + 10, 15), "1776 - 2026", font=font_sub, fill=black)
    d.text((pad_h + 10, box_h - 60), "SEMIQUINCENTENNIAL", font=font_sub, fill=black)
    
    # Crosshairs to solidify extreme technical styling
    c_x, c_y = box_w // 2, box_h // 2
    d.line([(0, c_y), (40, c_y)], fill=black, width=6)
    d.line([(box_w-40, c_y), (box_w, c_y)], fill=black, width=6)
    d.line([(c_x, 0), (c_x, 40)], fill=black, width=6)
    d.line([(c_x, box_h-40), (c_x, box_h)], fill=black, width=6)
    
    # Save Logo Block
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    master_path = os.path.join(out_dir, "Official_Blueprint_Tech_Block_Logo.png")
    final_img.save(master_path, "PNG")
    
    white = Image.new("RGB", final_img.size, (255, 255, 255))
    white.paste(final_img, (0, 0), final_img)
    white.save(master_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=95)
    print(f"Saved Extracted Squat Logo to {master_path}")
    
    # 4. Roll out over all schemas
    out_dir_tees = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    
    def process_schema(raw_path, out_name):
        img_raw = Image.open(raw_path).convert("RGBA")
        arr = np.array(img_raw)
        r, g, b, a = arr[:,:,0].astype(int), arr[:,:,1].astype(int), arr[:,:,2].astype(int), arr[:,:,3].astype(int)
        is_white = (r > 240) & (g > 240) & (b > 240)
        arr[is_white, 3] = 0
        clean_art = Image.fromarray(arr.astype(np.uint8))
        
        canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
        scale = 4400 / clean_art.size[0]
        art_w = int(clean_art.size[0] * scale)
        art_h = int(clean_art.size[1] * scale)
        clean_art = clean_art.resize((art_w, art_h), Image.Resampling.LANCZOS)
        
        canvas.paste(clean_art, ((4500-art_w)//2, (5400-art_h)//2 - 100), clean_art)
        
        # Shrink the logo on the schemas to keep it elegant and narrow
        lb_w = 2000 
        lb_h = int(final_img.size[1] * (lb_w / final_img.size[0]))
        resized_logo = final_img.resize((lb_w, lb_h), Image.Resampling.LANCZOS)
        box_x = (4500 - lb_w) // 2
        box_y = (5400 - lb_h) // 2 + 300
        canvas.paste(resized_logo, (box_x, box_y), resized_logo)
        
        out_png = os.path.join(out_dir_tees, out_name + ".png")
        canvas.save(out_png, "PNG")
        
        white_proof = Image.new("RGB", canvas.size, (255, 255, 255))
        white_proof.paste(canvas, (0, 0), canvas)
        white_proof.save(out_png.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=85)
        print(f"Saved Schema with True Extract: {out_name}")
        
    schemas = [
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_yosemite_half_dome_1774362305187.png", "Yosemite_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_golden_gate_1774362320667.png", "GoldenGate_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_minuteman_clean_1774363147444.png", "Minuteman_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_musket_clean_1774363163585.png", "Musket_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_eagle_clean_1774363196078.png", "Apollo_Eagle_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_declaration_clean_1774363209598.png", "Declaration_Blueprint_Official_4500x5400")
    ]
    
    for rp, oname in schemas:
        process_schema(rp, oname)

if __name__ == "__main__":
    build()
