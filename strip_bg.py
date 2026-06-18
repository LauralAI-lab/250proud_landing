import os
import glob
from PIL import Image

def strip_white_background(img_path):
    img = Image.open(img_path).convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    # Using a threshold to catch off-whites and anti-aliasing artifacts
    threshold = 240
    for item in datas:
        # item is (R, G, B, A)
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            # Full transparency for pure white or near white
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    
    filename = os.path.basename(img_path)
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_transparent{ext}"
    output_path = os.path.join(os.path.dirname(img_path), new_filename)
    
    img.save(output_path, "PNG")
    print(f"Processed {filename}:")
    print(f" - Resolution: {img.width}x{img.height} pixels")
    # 1024 / 300 DPI = ~3.4 inches
    print(f" - Max print size at 300 DPI: {img.width/300:.1f}\" x {img.height/300:.1f}\"")
    print(f" - Saved transparent version to {new_filename}")
    print("---")

images = glob.glob("/Users/michaelprice/.gemini/antigravity/brain/56277927-caa0-45f8-acd2-e1f06ff6b557/magnolia_charm_*.png")
# Exclude already processed ones
images = [f for f in images if "transparent" not in f]

for img in images:
    strip_white_background(img)

