import os
import numpy as np
from PIL import Image

def build():
    # 1. Load the RAW Original Declaration Schema
    path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_declaration_1774361524211.png"
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
    alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
    arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
    
    clean_art = Image.fromarray(arr.astype(np.uint8))
    
    # 4. Fit 4500x5400 beautifully framed, dropping the brand box!
    canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
    scale = 4400 / clean_art.size[0]
    art_w, art_h = int(clean_art.size[0] * scale), int(clean_art.size[1] * scale)
    clean_art = clean_art.resize((art_w, art_h), Image.Resampling.LANCZOS)
    
    # Center perfectly without custom logo shift constraint 
    canvas.paste(clean_art, ((4500-art_w)//2, (5400-art_h)//2), clean_art)
    
    # 5. Overwrite the branded one in Blueprint Collection, securely lock at 300 DPI
    out_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection/Declaration_Blueprint_Official_4500x5400.png"
    canvas.save(out_path, "PNG", dpi=(300, 300))
    
    # True White BG Proof
    white_proof = Image.new("RGB", canvas.size, (255, 255, 255))
    white_proof.paste(canvas, (0, 0), canvas)
    white_proof.save(out_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=95)
    print(f"Safely Restored Unbranded Original Declaration at 300 DPI: {out_path}")

if __name__ == "__main__":
    build()
