import os
from PIL import Image

def just_upscale(input_path, output_path, target_w, target_h, top_heavy=True):
    print(f"Upscaling flat white graphic {input_path}")
    img = Image.open(input_path).convert("RGBA")
    
    # Scale to dimensions without removing background
    max_w = int(target_w * 0.90)
    max_h = int(target_h * 0.90)
    ratio = min(max_w / img.width, max_h / img.height)
    new_w = int(img.width * ratio)
    new_h = int(img.height * ratio)
    
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Solid White Canvas
    final = Image.new("RGBA", (target_w, target_h), (255,255,255,255))
    paste_x = (target_w - new_w) // 2
    if top_heavy:
        paste_y = int(target_h * 0.15)
    else:
        paste_y = (target_h - new_h) // 2
        
    # We must paste using the image itself since it's just a square white graphic
    final.paste(img, (paste_x, paste_y))
    final.save(output_path, "PNG", dpi=(300, 300))
    print(f"Saved {output_path}")

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_tee_concept_1774272572521.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    os.makedirs(out_dir, exist_ok=True)
    
    just_upscale(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v2_CorrectText_RAW_WHITE_4500x5400.png", 4500, 5400, top_heavy=True)
    just_upscale(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v2_CorrectText_RAW_WHITE_1200x1200.png", 1200, 1200, top_heavy=False)
