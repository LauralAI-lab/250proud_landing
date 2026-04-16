import os
from PIL import Image, ImageDraw, ImageFont

def build_numeral(color_name, fill_color):
    # Lock absolutely rigid dimensions compatible with flat-panel embroidery constraints
    w, h = 1200, 800
    canvas = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_250 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 550)
        font_proud = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", 200)
    except:
        font_250 = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 550)
        font_proud = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 200)
        
    t1 = "250"
    t2 = "PROUD"
    
    w1 = int(draw.textlength(t1, font=font_250))
    w2 = int(draw.textlength(t2, font=font_proud))
    
    # Horizontally center geometry across the hat panel
    x1 = (w - w1) // 2
    y1 = 0
    draw.text((x1, y1), t1, font=font_250, fill=fill_color)
    
    x2 = (w - w2) // 2
    # The cap-height of 'PROUD' organically tucks directly into the baseline footprint of '250'
    y2 = 500
    draw.text((x2, y2), t2, font=font_proud, fill=fill_color)
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Headwear"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"Hat_Graphic_Numeral_Stacked_{color_name}_1200x800.png")
    
    # Exclusively output 300DPI physical matrices 
    canvas.save(out_path, "PNG", dpi=(300,300))
    print(f"Generated {color_name} Headwear Numeral: {out_path}")

if __name__ == "__main__":
    # Native streetwear dark vector ink (suitable for light color substrates)
    build_numeral("Dark", (20, 25, 30, 255))
    # Brilliant white inversion (suitable for completely black/dark substrates)
    build_numeral("Light", (245, 245, 245, 255))
