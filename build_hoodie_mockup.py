import os
from PIL import Image, ImageChops

def build_mockup():
    print("Starting hyper-realistic editorial mockup composite...")
    
    hoodie_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/premium_blank_hoodie_v2_1774374647615.png"
    eagle_path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection/Apollo_Eagle_Blueprint_Official_4500x5400.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Mockups/Editorial_Hero_Mockups"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Apollo_Eagle_Hoodie_Editorial_Hero.jpg")
    
    hoodie = Image.open(hoodie_path).convert("RGB")
    eagle = Image.open(eagle_path).convert("RGBA")
    
    # Scale the eagle to perfectly bridge the chest without bleeding onto the pocket
    scale = 320 / eagle.size[0]
    eagle_w = int(eagle.size[0] * scale)
    eagle_h = int(eagle.size[1] * scale)
    eagle_resized = eagle.resize((eagle_w, eagle_h), Image.Resampling.LANCZOS)
    
    # Pure white proxy layer for the math 
    transfer_layer = Image.new("RGB", hoodie.size, (255, 255, 255))
    
    # Anchor the drop zone exactly beneath the drawstring tips
    paste_x = 512 - (eagle_w // 2)
    paste_y = 310
    
    # Paste utilizing Native Alpha transparency map
    transfer_layer.paste(eagle_resized, (paste_x, paste_y), mask=eagle_resized.split()[3])
    
    # Fire the Multiply command
    # White acts as neutral 1 (ignores hoodie), Black inks dynamically absorb shadows/creases
    mockup = ImageChops.multiply(hoodie, transfer_layer)
    
    # Master Export
    mockup.save(out_path, "JPEG", quality=95)
    print(f"Editorial Mockup completely rendered: {out_path}")

if __name__ == "__main__":
    build_mockup()
