import os
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "video_renders")

W, H = 1920, 1080

pano_path = os.path.join(script_dir, "american_journey_v2.png")
if os.path.exists(pano_path):
    pano_img = Image.open(pano_path).convert("RGB")
    
    # We want to crop this image dynamically to 16:9 if it is an illustration
    # and save it so the user can just upload it!
    # Actually, let's just resize and crop it cleanly so it perfectly hits 1920x1080
    
    img_ratio = pano_img.width / pano_img.height
    target_ratio = W / H
    
    if img_ratio > target_ratio:
        # Image is wider than 16:9, crop sides
        new_h = H
        new_w = int(new_h * img_ratio)
        resized = pano_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - W) // 2
        bg = resized.crop((left, 0, left + W, H))
    else:
        # Image is taller than 16:9, crop top/bottom
        new_w = W
        new_h = int(new_w / img_ratio)
        resized = pano_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        top = (new_h - H) // 2
        bg = resized.crop((0, top, W, top + H))
        
    bg.save(os.path.join(out_dir, "veo_shot3_pano_16x9.png"))
    print("Saved veo_shot3_pano_16x9.png")
