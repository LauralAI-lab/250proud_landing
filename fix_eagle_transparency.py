import os
import numpy as np
from PIL import Image

def build():
    # 1. Load the beloved "Datum A" Eagle
    path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Raster_Tech_Marks/Apollo_Eagle_Schema_Transparent.png"
    img = Image.open(path).convert("RGBA")
    arr = np.array(img)
    
    # 2. Extract RGB
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    
    # 3. Supreme Alpha Matte processing
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
    arr[:,:,0] = 20
    arr[:,:,1] = 25
    arr[:,:,2] = 30
    
    normalized = gray / 255.0
    # Any pixel that was white/fringe (normalized > 0.85) becomes deeply transparent.
    # Solid black drafting lines (normalized < 0.4) become fully opaque, natively anti-aliased.
    alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
    arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
    
    clean_art = Image.fromarray(arr.astype(np.uint8))
    
    # 4. Fit 4500x5400 beautifully framed, entirely dropping the logo box
    canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
    scale = 4400 / clean_art.size[0]
    art_w, art_h = int(clean_art.size[0] * scale), int(clean_art.size[1] * scale)
    clean_art = clean_art.resize((art_w, art_h), Image.Resampling.LANCZOS)
    
    # Center perfectly without custom logo shifting
    canvas.paste(clean_art, ((4500-art_w)//2, (5400-art_h)//2), clean_art)
    
    # 5. Overwrite the one in Blueprint Collection, securely lock at 300 DPI
    out_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection/Apollo_Eagle_Blueprint_Official_4500x5400.png"
    canvas.save(out_path, "PNG", dpi=(300, 300))
    
    # Create True White BG Proof
    white_proof = Image.new("RGB", canvas.size, (255, 255, 255))
    white_proof.paste(canvas, (0, 0), canvas)
    white_proof.save(out_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=95)
    print(f"Fixed Eagle Transparency and Scaled at 300 DPI: {out_path}")

if __name__ == "__main__":
    build()
