import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

def build_mockup():
    print("Starting Agency White-Room Composite...")
    
    hoodie_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/premium_agency_hoodie_1774463724960.png"
    eagle_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection/eagle_blueprint.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Mockups/Editorial_Hero_Mockups"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Apollo_Eagle_Agency_Hero.jpg")
    
    hoodie = Image.open(hoodie_path).convert("RGB")
    eagle = Image.open(eagle_path).convert("RGBA")
    
    bbox = eagle.getbbox()
    if bbox:
        eagle = eagle.crop(bbox)
        
    # Scale to typical full-chest DTP standards natively against a 1024px canvas
    target_w = 280 
    scale = target_w / eagle.size[0]
    eagle_w = target_w
    eagle_h = int(eagle.size[1] * scale)
    eagle_resized = eagle.resize((eagle_w, eagle_h), Image.Resampling.LANCZOS)
    
    transfer_layer = Image.new("RGBA", hoodie.size, (0, 0, 0, 0))
    
    # Anchor meticulously on the chest, y=320, perfectly dropping below the pristine hood 
    paste_x = (hoodie.size[0] - eagle_w) // 2
    paste_y = 320
    
    transfer_layer.paste(eagle_resized, (paste_x, paste_y), mask=eagle_resized.split()[3])
    
    d = ImageDraw.Draw(transfer_layer)
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 38)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 16)
    except:
        font_large = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 38)
        font_small = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 16)
        
    txt_main = "250PROUD"
    txt_sub = "1776 - 2026"
    
    w_main = int(d.textlength(txt_main, font=font_large))
    w_sub = int(d.textlength(txt_sub, font=font_small))
    
    txt_y_start = paste_y + eagle_h + 8 
    
    d.text(((hoodie.size[0] - w_main) // 2, txt_y_start), txt_main, font=font_large, fill=(10, 10, 15, 255))
    d.text(((hoodie.size[0] - w_sub) // 2, txt_y_start + 42), txt_sub, font=font_small, fill=(10, 10, 15, 255))
    
    # Render mathematics proxy canvas
    white_proxy = Image.new("RGB", hoodie.size, (255, 255, 255))
    white_proxy.paste(transfer_layer, (0, 0), mask=transfer_layer.split()[3])
    
    # Pure 'Multiply' engine embedding ink dynamically inside high-key studio shadows
    mockup = ImageChops.multiply(hoodie, white_proxy)
    
    mockup.save(out_path, "JPEG", quality=98)
    print(f"Agency White-Room composite perfectly mapped: {out_path}")

if __name__ == "__main__":
    build_mockup()
