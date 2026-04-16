import os
from PIL import Image
from rembg import remove

def process_image(input_path, output_path, target_width, target_height, top_heavy_offset=False):
    print(f"Processing {input_path}...")
    img = Image.open(input_path).convert("RGBA")
    
    # 1. Remove background
    out = remove(img)
    
    # 2. Autocrop the transparent edges
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
        
    # 3. Scale to fit within target dimensions with some padding (e.g. 5% padding)
    max_w = int(target_width * 0.90)
    max_h = int(target_height * 0.90)
    
    ratio = min(max_w / out.width, max_h / out.height)
    new_w = int(out.width * ratio)
    new_h = int(out.height * ratio)
    
    out = out.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # 4. Create final transparent canvas
    final = Image.new("RGBA", (target_width, target_height), (0,0,0,0))
    
    # Center horizontally
    paste_x = (target_width - new_w) // 2
    
    # Center vertically or shift top-heavy for t-shirts
    if top_heavy_offset:
        # Chest prints usually sit closer to the top of the 5400px canvas
        paste_y = int(target_height * 0.15) 
    else:
        paste_y = (target_height - new_h) // 2
        
    final.paste(out, (paste_x, paste_y), out)
    
    # 5. Save as 300 DPI PNG
    print(f"Saving to {output_path}...")
    final.save(output_path, "PNG", dpi=(300, 300))

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_tee_concept_1774272572521.png"
    badge_input = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/gulf_of_america_badge_concept_1774272585688.png"
    
    out_dir = "/Users/michaelprice/Desktop/lauralai/250proud_landing/temp_print_files"
    os.makedirs(out_dir, exist_ok=True)
    
    # Process Tee Version (4500x5400)
    process_image(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v2_4500x5400.png", 4500, 5400, top_heavy_offset=True)
    
    # Process Badge Version (1200x1200)
    process_image(badge_input, f"{out_dir}/GulfOfAmerica_Badge_v1_1200x1200.png", 1200, 1200, top_heavy_offset=False)
