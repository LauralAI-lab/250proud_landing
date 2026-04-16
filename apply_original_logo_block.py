import os
import numpy as np
from PIL import Image, ImageDraw

def build():
    # 1. Load the original Master Logo
    hero_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/250_Hero_Numeral_Transparent.png"
    img = Image.open(hero_path).convert("RGBA")
    
    # 2. Crop excess transparency to guarantee mathematically perfect padding
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    # 3. Scale it to fit the blueprint chest area securely
    target_w = 2000
    h_scale = target_w / img.size[0]
    target_h = int(img.size[1] * h_scale)
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 4. Construct the technical blueprint boundary box
    padding = 100
    box_w = target_w + (padding * 2)
    box_h = target_h + (padding * 2)
    
    box_img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
    d = ImageDraw.Draw(box_img)
    
    # Pristine white background, 3-pt logical outline (approx 8px at 4500x scale)
    d.rectangle([0, 0, box_w, box_h], fill=(255, 255, 255, 255))
    d.rectangle([3, 3, box_w-3, box_h-3], outline=(20, 20, 25, 255), width=8)
    
    # Fuse original logo squarely inside the box
    box_img.paste(img, (padding, padding), img)
    
    # Save the Official Block
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    master_path = os.path.join(out_dir, "Official_Blueprint_Tech_Block_Logo.png")
    box_img.save(master_path, "PNG")
    
    white_proof = Image.new("RGB", box_img.size, (255, 255, 255))
    white_proof.paste(box_img, (0, 0), box_img)
    white_proof.save(master_path.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=95)
    print(f"Saved Original Framed Logo Block: {master_path}")
    
    # 5. Composite onto the 6 Core Blueprints
    out_dir_tees = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    
    def process_schema(raw_path, out_name):
        img_raw = Image.open(raw_path).convert("RGBA")
        arr = np.array(img_raw)
        r, g, b, a = arr[:,:,0].astype(int), arr[:,:,1].astype(int), arr[:,:,2].astype(int), arr[:,:,3].astype(int)
        
        # Erase background to guarantee clean tee layout
        is_white = (r > 240) & (g > 240) & (b > 240)
        arr[is_white, 3] = 0
        clean_art = Image.fromarray(arr.astype(np.uint8))
        
        canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
        scale = 4400 / clean_art.size[0]
        art_w, art_h = int(clean_art.size[0] * scale), int(clean_art.size[1] * scale)
        clean_art = clean_art.resize((art_w, art_h), Image.Resampling.LANCZOS)
        
        # Anchor the blueprint structure natively in the upper-mid
        canvas.paste(clean_art, ((4500-art_w)//2, (5400-art_h)//2 - 100), clean_art)
        
        # Secure the brand block precisely over the structural center
        box_x = (4500 - box_w) // 2
        box_y = (5400 - box_h) // 2 + 300
        canvas.paste(box_img, (box_x, box_y), box_img)
        
        out_png = os.path.join(out_dir_tees, out_name + ".png")
        canvas.save(out_png, "PNG")
        
        white_proof_tee = Image.new("RGB", canvas.size, (255, 255, 255))
        white_proof_tee.paste(canvas, (0, 0), canvas)
        white_proof_tee.save(out_png.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=85)
        print(f"Saved Schema Vector Layout: {out_name}")
        
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
