import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_diner_receipt():
    width, height = 4500, 5400
    # Transparent canvas
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load a nice monospace font
    font_paths = [
        "/System/Library/Fonts/Supplemental/Courier New Bold.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/Supplemental/Andale Mono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/Library/Fonts/Courier New Bold.ttf"
    ]
    
    font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                # Large font size for 4500x5400
                font = ImageFont.truetype(path, 180)
                print(f"Loaded font: {path}")
                break
            except Exception as e:
                continue
                
    if font is None:
        font = ImageFont.load_default()
        print("WARNING: Using default font. Monospace fonts not found.")
        
    text_content = [
        "           250PROUD",
        "        ** GUEST CHECK **",
        "===============================",
        "",
        "DATE: 07-04-1776  ",
        "TABLE: 250",
        "GUESTS: 50",
        "SERVER: LIBERTY",
        "",
        "===============================",
        "QTY   ITEM               PRICE",
        "-------------------------------",
        " 1    BLACK COFFEE        0.25",
        " 1    CHERRY PIE          0.75",
        " 2    QTRS FOR JUKEBOX    0.50",
        " 1    GALLON 100 OCTANE   0.45",
        "-------------------------------",
        "SUBTOTAL                  1.95",
        "TAX (NO TAX W/O REP)      0.00",
        "-------------------------------",
        "AMOUNT DUE:           PRICELESS",
        "",
        "",
        "CHK #1776-2026",
        "===============================",
        "      GRATUITY INCLUDED",
        "         SINCE '76",
        "===============================",
        "",
        "         THANK YOU!",
        "         COME AGAIN",
        ""
    ]
    
    # Text Color: Washed, faded vintage navy
    text_color = (25, 40, 60, 255)
    
    # Start Y position
    y_pos = 1000
    # X starting position
    x_pos = 900
    
    # We will draw the text onto a separate transparent layer so we can apply rotation and distress
    text_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    
    for line in text_content:
        # Give a slight jitter to Y to simulate old thermal/impact printers
        jitter_y = random.randint(-5, 5)
        text_draw.text((x_pos, y_pos + jitter_y), line, font=font, fill=text_color)
        y_pos += 200 # line spacing
        
    # Rotate the receipt slightly for a natural lay on the shirt
    text_layer = text_layer.rotate(-2, resample=Image.Resampling.BICUBIC, center=(width//2, height//2))
    
    # Adding distressed screen-print effects using numpy
    arr = np.array(text_layer)
    
    # Create random noise map to punch out pixels (simulate missing ink/faded print)
    noise = np.random.randint(0, 255, (height, width), dtype=np.uint8)
    
    # Where noise > 210 (roughly 15% of pixels), we set Alpha to 0 to simulate heavy distress
    distress_mask = noise > 220
    
    # We only want to distress where there is actually ink!
    alpha_channel = arr[:, :, 3]
    has_ink = alpha_channel > 0
    
    arr[distress_mask & has_ink, 3] = 0
    
    # Add a slight blur to simulate ink bleed/fuzziness of vintage printing
    final_img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(1.5))
    
    # Save the output
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/New_Concepts"
    os.makedirs(out_dir, exist_ok=True)
    
    out_path = os.path.join(out_dir, "Diner_Receipt_250PROUD_4500x5400.png")
    final_img.save(out_path, "PNG", dpi=(300, 300))
    print(f"Successfully generated full-res typography concept at {out_path}")

if __name__ == "__main__":
    create_diner_receipt()
