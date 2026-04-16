import numpy as np
from PIL import Image, ImageDraw, ImageFont

def build():
    path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/schema_declaration_v2_1774365273907.png"
    img = Image.open(path).convert("RGBA")
    d = ImageDraw.Draw(img)
    
    font_path = "/System/Library/Fonts/HelveticaNeue.ttc"
    font = ImageFont.truetype(font_path, 35)
    
    title = "DECLARATION OF INDEPENDENCE"
    w = int(d.textlength(title, font=font))
    
    # Center perfectly at the top header area
    d.text(((1024 - w) // 2, 30), title, font=font, fill=(30, 30, 35, 255))
    
    fixed_path = path.replace(".png", "_spelling_fixed.png")
    img.save(fixed_path, "PNG")
    print(f"Saved natively printed Declaration schema to {fixed_path}")

build()
