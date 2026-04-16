import os
from PIL import Image, ImageFont, ImageDraw

def append_text():
    print("Appending typography to Master Crest...")
    
    # Target our flawless transparent asset directly
    path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Logos/Blueprint_Collection_Master_Crest_Transparent.png"
    
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    
    # Literal text translation with Trademarks
    txt = "Blueprint Collection™ 250Proud™.net"
    
    # Establish extremely thick, authoritative streetwear typography scaling relative to the ~900px canvas
    try:
        font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 60)
    except:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 60)
        
    # Virtual draw instance to mathematically pull dimensions of the text block prior to canvas construction
    dummy_draw = ImageDraw.Draw(img)
    txt_w = int(dummy_draw.textlength(txt, font=font))
    
    # Structural buffer calculations
    padding = 50
    new_h = h + padding + 80 # Accounts for text height & generous bottom visual margin
    
    # Expand canvas horizontally if text overflows the crest significantly
    new_w = max(w, txt_w + 100)
    
    master = Image.new("RGBA", (new_w, new_h), (0, 0, 0, 0))
    
    # Map the crest dead-center atop the new structure
    crest_x = (new_w - w) // 2
    master.paste(img, (crest_x, 0))
    
    # Map the font absolutely centered directly below the crest anchor
    txt_x = (new_w - txt_w) // 2
    txt_y = h + padding // 2
    
    draw = ImageDraw.Draw(master)
    # Print natively in the Navy/Black signature corporate color hex
    draw.text((txt_x, txt_y), txt, font=font, fill=(20, 25, 30, 255))
    
    # Overwrite the original crest permanently injecting the text
    master.save(path, "PNG", dpi=(300, 300))
    print(f"Brutalist typography securely anchored: {path}")

if __name__ == "__main__":
    append_text()
