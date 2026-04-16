import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def alpha_extract(img):
    img_raw = img.convert("RGBA")
    arr = np.array(img_raw)
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
    arr[:,:,0] = 20
    arr[:,:,1] = 25
    arr[:,:,2] = 30
    normalized = gray / 255.0
    alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
    arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
    
    clean_art = Image.fromarray(arr.astype(np.uint8))
    bbox = clean_art.getbbox()
    if bbox:
        clean_art = clean_art.crop(bbox)
    return clean_art

def process():
    paths = {
        "crest": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_collection_crest_1774552523886.png",
        "blueprint_text": "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_type_lockup_raw_1774636792029.png",
    }
    
    c_img = alpha_extract(Image.open(paths["crest"]))
    b_txt_img = alpha_extract(Image.open(paths["blueprint_text"]))
    
    w_target = 1800
    
    sc_c = min(1200 / c_img.size[0], 1200 / c_img.size[1])
    c_img = c_img.resize((int(c_img.size[0]*sc_c), int(c_img.size[1]*sc_c)), Image.Resampling.LANCZOS)
    
    sc_b = w_target / b_txt_img.size[0]
    b_txt_img = b_txt_img.resize((int(b_txt_img.size[0]*sc_b), int(b_txt_img.size[1]*sc_b)), Image.Resampling.LANCZOS)
    
    pad_y = 120
    
    total_h = c_img.size[1] + pad_y + b_txt_img.size[1] + pad_y + 150
    canvas = Image.new('RGBA', (2200, total_h + 400), (0,0,0,0))
    
    curr_y = 200
    canvas.paste(c_img, ((2200 - c_img.size[0])//2, curr_y), c_img)
    curr_y += c_img.size[1] + pad_y
    
    canvas.paste(b_txt_img, ((2200 - b_txt_img.size[0])//2, curr_y), b_txt_img)
    curr_y += b_txt_img.size[1] + pad_y
    
    # 4. Inject 100% stable Python topography for literal copyright string array
    draw = ImageDraw.Draw(canvas)
    footer_text = "Copyright 2026 - 250Proud™"
    fill_c = (20, 25, 30, 255)
    
    try:
        font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 75)
    except:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 75)
        
    txt_w = int(draw.textlength(footer_text, font=font))
    start_x = (2200 - txt_w) // 2
    draw.text((start_x, curr_y), footer_text, font=font, fill=fill_c)
    
    # Rerouting to master Print_Ready directory for DTG format instead of Headwear
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Master_SubBrand_Vertical_Tshirt_Lockup.png")
    
    # Structurally crop the entire frame directly matching Printify boundaries
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
        
    # Inject healthy absolute transparency pad buffering for Printify 
    final_canvas = Image.new('RGBA', (canvas.size[0] + 300, canvas.size[1] + 300), (0,0,0,0))
    final_canvas.paste(canvas, (150, 150), mask=canvas.split()[3])
    
    final_canvas.save(out_path, "PNG", dpi=(300,300))
    
    w_proof = Image.new("RGB", final_canvas.size, (255,255,255))
    w_proof.paste(final_canvas, (0,0), final_canvas)
    w_proof.save(out_path.replace(".png", "_Proof.jpg"), "JPEG", quality=90)
    print(f"Master Vertical SubBrand Tshirt Graphic Locked securely: {out_path}")

if __name__ == "__main__":
    process()
