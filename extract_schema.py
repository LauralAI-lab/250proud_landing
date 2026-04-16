import os
import numpy as np
from PIL import Image

def extract_schema(input_path, output_path, target_w, target_h):
    print(f"Extracting Schema Matte from {input_path}")
    img = Image.open(input_path).convert("RGBA")
    arr = np.array(img).astype(float)
    
    r = arr[..., 0]
    g = arr[..., 1]
    b = arr[..., 2]
    
    # Calculate pure Luma (how bright the pixel is)
    luma = (r + g + b) / 3.0
    
    # Calculate Chroma difference (how colored the pixel is)
    color_diff = np.abs(r - g) + np.abs(g - b) + np.abs(b - r)
    
    # The SMPTE color blocks are highly saturated. The white schema lines are completely desaturated.
    # We protect any strong color patch
    is_colored = color_diff > 30
    
    # For all neutral pixels (the white lines, grey glowing edges, and black background)
    is_line = ~is_colored
    
    # We map Luma directly to Alpha! 
    # A dark grey blur around a white line (Luma 50) becomes a 20% transparent White pixel!
    # Pure black (Luma 0) becomes 0% transparent!
    # This completely eliminates "jagged edges" and creates mathematically flawless antialiasing glow.
    new_a = np.clip(luma * (255.0 / 220.0), 0, 255) 
    
    # Force the color of the neutral glow strictly to Pure White to avoid murky gray prints
    arr[is_line, 0] = 255
    arr[is_line, 1] = 255
    arr[is_line, 2] = 255
    arr[is_line, 3] = new_a[is_line]
    
    # Lock the colored SMPTE blocks at 100% opacity
    arr[is_colored, 3] = 255
    
    pil_img = Image.fromarray(arr.astype(np.uint8))
    
    # Scale to fill the requested canvas
    bbox = pil_img.getbbox()
    if bbox:
        pil_img = pil_img.crop(bbox)
        
    max_w = int(target_w * 0.95)
    max_h = int(target_h * 0.95)
    ratio = min(max_w / pil_img.width, max_h / pil_img.height)
    new_w = int(pil_img.width * ratio)
    new_h = int(pil_img.height * ratio)
    
    pil_img = pil_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    final_canvas = Image.new("RGBA", (target_w, target_h), (0,0,0,0))
    paste_x = (target_w - new_w) // 2
    paste_y = int(target_h * 0.05)
        
    final_canvas.paste(pil_img, (paste_x, paste_y), pil_img)
    final_canvas.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved Flawless Schema to {output_path}")

if __name__ == "__main__":
    schema_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/apollo_telemetry_raw_black_1774313009623.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/New_Concepts"
    os.makedirs(out_dir, exist_ok=True)
    
    out_path = os.path.join(out_dir, "Apollo_Telemetry_250PROUD_4500x5400.png")
    extract_schema(schema_input, out_path, 4500, 5400)
