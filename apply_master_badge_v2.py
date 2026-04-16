import os
import numpy as np
from PIL import Image

def build():
    out_dir_tees = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection"
    
    # Load the official Syncopate Master Mark
    logo_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Declaration_Style_Master_Mark.png"
    logo = Image.open(logo_path).convert("RGBA")
    
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
        
        lb_w = 2600 
        lb_h = int(logo.size[1] * (lb_w / logo.size[0]))
        resized_logo = logo.resize((lb_w, lb_h), Image.Resampling.LANCZOS)
        
        box_x = (4500 - lb_w) // 2
        box_y = (5400 - lb_h) // 2 + 300
        canvas.paste(resized_logo, (box_x, box_y), resized_logo)
        
        out_png = os.path.join(out_dir_tees, out_name + ".png")
        canvas.save(out_png, "PNG")
        
        # Save Proof with white background
        white = Image.new("RGB", canvas.size, (255, 255, 255))
        white.paste(canvas, (0, 0), canvas)
        white.save(out_png.replace(".png", "_White_BG_Proof.jpg"), "JPEG", quality=95)
        print(f"Saved completed schema: {out_name}")

    img1 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_minuteman_clean_1774363147444.png"
    img2 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_musket_clean_1774363163585.png"
    img3 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_eagle_clean_1774363196078.png"
    img4 = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_declaration_clean_1774363209598.png"
    
    process_schema(img1, "Minuteman_Blueprint_Official_4500x5400")
    process_schema(img2, "Musket_Blueprint_Official_4500x5400")
    process_schema(img3, "Apollo_Eagle_Blueprint_Official_4500x5400")
    process_schema(img4, "Declaration_Blueprint_Official_4500x5400")

if __name__ == "__main__":
    build()
