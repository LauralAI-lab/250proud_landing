import os
import numpy as np
from PIL import Image

def build_mustang():
    print("Extracting P-51 Mustang via Supreme Alpha Matte...")
    
    raw_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/mustang_blueprint_v1_1774464136556.png"
    badge_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Official_Blueprint_Tech_Block_Logo.png"
    
    img_raw = Image.open(raw_path).convert("RGBA")
    arr = np.array(img_raw)
    r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
    
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    
    # Pure dark concrete navy/black vector extraction
    arr[:,:,0] = 20
    arr[:,:,1] = 25
    arr[:,:,2] = 30
    
    # Force high-contrast anti-aliasing transparency algorithm 
    normalized = gray / 255.0
    alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.4), 0, 1)
    arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
    
    clean_art = Image.fromarray(arr.astype(np.uint8))
    
    canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
    scale = 4400 / clean_art.size[0]
    art_w, art_h = int(clean_art.size[0] * scale), int(clean_art.size[1] * scale)
    clean_art = clean_art.resize((art_w, art_h), Image.Resampling.LANCZOS)
    
    art_x = (4500-art_w)//2
    art_y = (5400-art_h)//2 - 100
    
    canvas.paste(clean_art, (art_x, art_y), clean_art)
    
    # Map the validated 1200px width master Tech Block 
    badge = Image.open(badge_path).convert("RGBA")
    badge_w = 1200
    badge_scale = badge_w / badge.size[0]
    badge_h = int(badge.size[1] * badge_scale)
    badge_resized = badge.resize((badge_w, badge_h), Image.Resampling.LANCZOS)
    
    # Physically mapping to the absolute limits of the drafting border with equal padding natively
    margin = 150
    box_x = art_x + margin
    box_y = (art_y + art_h) - badge_h - margin
    
    canvas.paste(badge_resized, (box_x, box_y), badge_resized.split()[3])
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Decades_Collection"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "1940s_Mustang_Blueprint_Official_4500x5400.png")
    
    canvas.save(out_path, "PNG", dpi=(300,300))
    
    # Verification formatting mapping exactly to standard background rules
    white_proof = Image.new("RGB", canvas.size, (255, 255, 255))
    white_proof.paste(canvas, (0, 0), canvas)
    white_proof.save(out_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=90)
    print(f"Mustang Decades Graphic generated natively and solidly stamped: {out_path}")

if __name__ == "__main__":
    build_mustang()
