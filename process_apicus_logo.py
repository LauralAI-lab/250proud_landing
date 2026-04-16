import os
from PIL import Image, ImageChops

def trim_white(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def process_logo_white_bg(input_path, output_path, target_w, target_h):
    print(f"Processing sharp white-background logo: {input_path}")
    img = Image.open(input_path).convert("RGB")
    
    # Trim the excess white to get an exact bounding box
    img = trim_white(img)
        
    # Maintain ~85% of canvas size padding
    max_w = int(target_w * 0.85)
    max_h = int(target_h * 0.85)
    ratio = min(max_w / img.width, max_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    
    # Upscale
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Pure White Canvas
    final_canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
        
    final_canvas.paste(img, (paste_x, paste_y))
    final_canvas.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved high-res RAW WHITE logo to {output_path}")

if __name__ == "__main__":
    src_img = "/Users/michaelprice/.gemini/antigravity/brain/3f81b2e1-cb35-4dab-82df-06c8b30c49e8/aligned_agentics_concept_3_1776189815054.png"
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/aligned agentics"
    os.makedirs(out_dir, exist_ok=True)
    
    out_path = os.path.join(out_dir, "Aligned_Agentics_Logo_Final_RAW_WHITE.png")
    process_logo_white_bg(src_img, out_path, 2048, 2048)
