import numpy as np
import os
from PIL import Image, ImageFont, ImageDraw

def process():
    print("Rebuilding Precise Trademark Layout...")
    
    # Target our flawless 1024 DALL-E asset sequence entirely from scratch 
    raw_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/blueprint_collection_crest_1774552523886.png"
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Blueprint_Collection_Master_Crest_Transparent.png")
    
    # Native Alpha Extraction Loop
    img_raw = Image.open(raw_path).convert("RGBA")
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
        
    w, h = clean_art.size

    # Establish highly technical typography mapped to fractional scaling for legal marks
    try:
        f1 = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 48)
        f1_tm = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 12) # ~Quarter Scale
        f2 = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 36)
        f2_tm = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 9) # ~Quarter Scale
    except:
        f1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 48)
        f1_tm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 12)
        f2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 36)
        f2_tm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 9)
        
    dummy = ImageDraw.Draw(clean_art)
    
    # Mathematically split boundaries to maintain perfect dead-center coordinates
    p1_w = int(dummy.textlength("Blueprint Collection", font=f1))
    p1_tm_w = int(dummy.textlength("™", font=f1_tm))
    w1_total = p1_w + p1_tm_w
    
    p2_w1 = int(dummy.textlength("250Proud", font=f2))
    p2_tm_w = int(dummy.textlength("™", font=f2_tm))
    p2_w2 = int(dummy.textlength(".net", font=f2))
    w2_total = p2_w1 + p2_tm_w + p2_w2
    
    # Establish bounding margins exactly mirroring previous stack array
    padding = 40
    line_spacing = 15
    new_h = h + padding + 48 + line_spacing + 36 + 60
    new_w = max(w, w1_total + 100, w2_total + 100)
    
    master = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    crest_x = (new_w - w) // 2
    master.paste(clean_art, (crest_x, 0), mask=clean_art.split()[3])
    
    draw = ImageDraw.Draw(master)
    fill_col = (20, 25, 30, 255)
    
    # Dynamically draw line 1
    y1 = h + padding
    x1 = (new_w - w1_total) // 2
    draw.text((x1, y1), "Blueprint Collection", font=f1, fill=fill_col)
    
    # Force organic superscript scaling right at the cap line (y1 anchor operates top-down)
    draw.text((x1 + p1_w, y1), "™", font=f1_tm, fill=fill_col)
    
    # Dynamically draw line 2 directly into nested string interpolation
    y2 = y1 + 48 + line_spacing
    x2 = (new_w - w2_total) // 2
    draw.text((x2, y2), "250Proud", font=f2, fill=fill_col)
    draw.text((x2 + p2_w1, y2), "™", font=f2_tm, fill=fill_col)
    draw.text((x2 + p2_w1 + p2_tm_w, y2), ".net", font=f2, fill=fill_col)
    
    master.save(out_path, "PNG", dpi=(300, 300))
    print(f"Quarter-scale typography perfectly layered and fused: {out_path}")

if __name__ == "__main__":
    process()
