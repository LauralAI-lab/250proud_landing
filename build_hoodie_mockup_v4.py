import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

def build_mockup():
    hoodie_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/premium_blank_hoodie_v2_1774374647615.png"
    eagle_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection/eagle_blueprint.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Mockups/Editorial_Hero_Mockups"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Apollo_Eagle_Hoodie_Editorial_Hero_V4.jpg")
    
    hoodie = Image.open(hoodie_path).convert("RGB")
    eagle = Image.open(eagle_path).convert("RGBA")
    
    bbox = eagle.getbbox()
    if bbox:
        eagle = eagle.crop(bbox)
        
    print(f"Eagle cropped size: {eagle.size}")
    
    # Highly constrained to exactly 260px to behave like a standard ~10 inch chest print natively!
    target_w = 260 
    scale = target_w / eagle.size[0]
    eagle_w = target_w
    eagle_h = int(eagle.size[1] * scale)
    eagle_resized = eagle.resize((eagle_w, eagle_h), Image.Resampling.LANCZOS)
    
    transfer_layer = Image.new("RGBA", hoodie.size, (0, 0, 0, 0))
    
    # Drop specifically to y=380 so it perfectly hits center chest right below drawstrings.
    paste_x = (hoodie.size[0] - eagle_w) // 2
    paste_y = 380
    
    transfer_layer.paste(eagle_resized, (paste_x, paste_y), mask=eagle_resized.split()[3])
    
    d = ImageDraw.Draw(transfer_layer)
    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 36)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 15)
    except:
        font_large = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 36)
        font_small = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 15)
        
    txt_main = "250PROUD"
    txt_sub = "1776 - 2026"
    
    w_main = int(d.textlength(txt_main, font=font_large))
    w_sub = int(d.textlength(txt_sub, font=font_small))
    
    txt_y_start = paste_y + eagle_h + 8 
    
    d.text(((hoodie.size[0] - w_main) // 2, txt_y_start), txt_main, font=font_large, fill=(10, 10, 15, 255))
    d.text(((hoodie.size[0] - w_sub) // 2, txt_y_start + 40), txt_sub, font=font_small, fill=(10, 10, 15, 255))
    
    # Render pure mathematical proxy canvas
    white_proxy = Image.new("RGB", hoodie.size, (255, 255, 255))
    white_proxy.paste(transfer_layer, (0, 0), mask=transfer_layer.split()[3])
    
    # Multiplier bleeds pure vectors seamlessly underneath the garment shadows natively
    mockup = ImageChops.multiply(hoodie, white_proxy)
    
    mockup.save(out_path, "JPEG", quality=98)
    print(f"Editorial Mockup V4 natively constrained: {out_path}")

if __name__ == "__main__":
    build_mockup()
