import os
import numpy as np
from PIL import Image, ImageDraw

def build():
    hero_path = "/Users/michaelprice/Desktop/lauralai/DirectPrint/250proud_corporate_color_DirectPrint.png"
    if not os.path.exists(hero_path):
        hero_path = "/Users/michaelprice/Desktop/lauralai/logos/250proud_corporate_color.png"
        
    img = Image.open(hero_path).convert("RGBA")
    
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    target_w = 1700
    h_scale = target_w / img.size[0]
    target_h = int(img.size[1] * h_scale)
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    padding = 100
    box_w = target_w + (padding * 2)
    box_h = target_h + (padding * 2)
    
    box_img = Image.new('RGBA', (box_w, box_h), (0,0,0,0))
    d = ImageDraw.Draw(box_img)
    
    d.rectangle([0, 0, box_w, box_h], fill=(255, 255, 255, 255))
    d.rectangle([4, 4, box_w-4, box_h-4], outline=(20, 20, 25, 255), width=8)
    
    box_img.paste(img, (padding, padding), img)
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos"
    os.makedirs(out_dir, exist_ok=True)
    master_path = os.path.join(out_dir, "Official_Blueprint_Tech_Block_Logo.png")
    box_img.save(master_path, "PNG", dpi=(300, 300))
    print(f"Saved Correct Corporate Box (300 DPI): {master_path}")
    
    out_dir_tees = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    
    def process_schema(raw_path, out_name):
        img_raw = Image.open(raw_path).convert("RGBA")
        arr = np.array(img_raw)
        r, g, b = arr[:,:,0].astype(float), arr[:,:,1].astype(float), arr[:,:,2].astype(float)
        
        # SUPREME ALPHA MATTE:
        # Convert physical darkness directly into Alpha Opacity
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        
        # Force all ink to be completely crisp dark Vintage Navy/Black
        arr[:,:,0] = 20
        arr[:,:,1] = 25
        arr[:,:,2] = 30
        
        # If the original pixel was white (gray=255), Alpha becomes 0.
        # If the original pixel was black (gray<100), Alpha becomes 255.
        # This perfectly preserves sub-pixel anti-aliasing without ANY white fringing!
        normalized = gray / 255.0
        # Curve: clip anything lighter than 0.85 to completely transparent. Everything below 0.5 is solid.
        alpha_float = np.clip((0.85 - normalized) / (0.85 - 0.5), 0, 1)
        arr[:,:,3] = (alpha_float * 255).astype(np.uint8)
        
        clean_art = Image.fromarray(arr.astype(np.uint8))
        
        canvas = Image.new('RGBA', (4500, 5400), (0,0,0,0))
        scale = 4400 / clean_art.size[0]
        art_w, art_h = int(clean_art.size[0] * scale), int(clean_art.size[1] * scale)
        clean_art = clean_art.resize((art_w, art_h), Image.Resampling.LANCZOS)
        
        canvas.paste(clean_art, ((4500-art_w)//2, (5400-art_h)//2 - 100), clean_art)
        
        badge_w = 1200
        badge_scale = badge_w / box_img.size[0]
        badge_h = int(box_img.size[1] * badge_scale)
        badge = box_img.resize((badge_w, badge_h), Image.Resampling.LANCZOS)
        
        box_x = (4500 - badge_w) // 2
        box_y = (5400 - badge_h) // 2 + 800
        
        # SPECIFIC OVERRIDES FOR ALIGNMENT
        if "Musket" in out_name:
            box_y = (5400 - badge_h) // 2 + 350 # Intersect trigger guard
        elif "Declaration" in out_name:
            box_y = (5400 - badge_h) // 2 + 1300 
            
        # Paste the Corporate stamp!
        canvas.paste(badge, (box_x, box_y), badge)
        
        out_png = os.path.join(out_dir_tees, out_name + ".png")
        # Ensure strict 300 DPI for Print!
        canvas.save(out_png, "PNG", dpi=(300, 300))
        
        white_proof_tee = Image.new("RGB", canvas.size, (255, 255, 255))
        white_proof_tee.paste(canvas, (0, 0), canvas)
        white_proof_tee.save(out_png.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=85)
        print(f"Saved Supreme Vector Layout (300 DPI): {out_name}")
        
    schemas = [
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_yosemite_half_dome_1774362305187.png", "Yosemite_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_golden_gate_1774362320667.png", "GoldenGate_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_minuteman_1774361494835.png", "Minuteman_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_rifle_1774361509984.png", "Musket_Blueprint_Official_4500x5400"),
        ("/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_declaration_1774361524211.png", "Declaration_Blueprint_Official_4500x5400") # BACK TO RAW ORIGINAL!
    ]
    
    for rp, oname in schemas:
        process_schema(rp, oname)

if __name__ == "__main__":
    build()
