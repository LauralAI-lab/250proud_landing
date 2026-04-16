import numpy as np
import os
from PIL import Image, ImageFont, ImageDraw

def process():
    print("Rebuilding Stacked Typography for Master Crest...")
    
    # Pull pure raster geometry straight from the DALL-E drop
    raw_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_collection_crest_1774552523886.png"
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Blueprint_Collection_Master_Crest_Transparent.png")
    
    # 1. Native Alpha Extraction via Supreme Matte array mechanics
    img_raw = Image.open(raw_path).convert("RGBA")
    arr = np.array(img_raw)
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
    # Corporate layout coloring
    arr[:,:,0] = 20
    arr[:,:,1] = 25
    arr[:,:,2] = 30
    
    # Bind transparent mathematical thresholds
    normalized = gray / 255.0
    alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
    arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
    
    clean_art = Image.fromarray(arr.astype(np.uint8))
    
    # Slices away native margin voids ensuring exact text proximity to physical line art
    bbox = clean_art.getbbox()
    if bbox:
        clean_art = clean_art.crop(bbox)
        
    w, h = clean_art.size
    
    # User's literal copy strings
    txt1 = "Blueprint Collection™"
    txt2 = "250Proud™.net"
    
    try:
        font1 = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 48)
        font2 = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 36)
    except:
        font1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 48)
        font2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 36)
        
    dummy_draw = ImageDraw.Draw(clean_art)
    w1 = int(dummy_draw.textlength(txt1, font=font1))
    w2 = int(dummy_draw.textlength(txt2, font=font2))
    
    # Construct exact bounding framework for stacked structural load
    padding = 40
    line_spacing = 15
    new_h = h + padding + 48 + line_spacing + 36 + 60
    new_w = max(w, w1 + 100, w2 + 100)
    
    # Inject graphic matrix
    master = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    crest_x = (new_w - w) // 2
    master.paste(clean_art, (crest_x, 0), mask=clean_art.split()[3])
    
    draw = ImageDraw.Draw(master)
    
    # Map topmost title string dead-center natively beneath the anchor
    y1 = h + padding
    x1 = (new_w - w1) // 2
    draw.text((x1, y1), txt1, font=font1, fill=(20, 25, 30, 255))
    
    # Drop second block text physically below line one via exact spacing calculation
    y2 = y1 + 48 + line_spacing
    x2 = (new_w - w2) // 2
    draw.text((x2, y2), txt2, font=font2, fill=(20, 25, 30, 255))
    
    master.save(out_path, "PNG", dpi=(300, 300))
    print(f"Stacked Typography rendered purely: {out_path}")

if __name__ == "__main__":
    process()
