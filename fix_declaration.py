import numpy as np
from PIL import Image, ImageDraw, ImageFont

def fix_declaration():
    path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_declaration_clean_1774363209598.png"
    img = Image.open(path).convert("RGBA")
    d = ImageDraw.Draw(img)
    
    # Surgically erase the top-center text area while avoiding outer drafting borders
    # Assuming text is usually in the top 20-75 pixels in a 1024x1024 canvas.
    d.rectangle([50, 15, 974, 65], fill=(0,0,0,0))
    
    # Restamp the perfect vector spelling
    font_path = "/System/Library/Fonts/HelveticaNeue.ttc"
    font = ImageFont.truetype(font_path, 35)
    
    title = "DECLARATION OF INDEPENDENCE"
    w = int(d.textlength(title, font=font))
    
    # Center perfectly against the new empty space
    d.text(((1024 - w) // 2, 22), title, font=font, fill=(80, 80, 85, 255))
    
    fixed_path = path.replace(".png", "_spelling_fixed.png")
    img.save(fixed_path, "PNG")
    print(f"Fixed Declaration spelling natively! Saved to {fixed_path}")

fix_declaration()
