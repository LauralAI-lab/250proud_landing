import os
from PIL import Image, ImageDraw, ImageFilter

script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "video_renders")
os.makedirs(out_dir, exist_ok=True)

W, H = 1920, 1080

def create_shadow(img, offset=(20,20), blur=30, shadow_color=(0,0,0,150)):
    shadow = Image.new('RGBA', img.size, shadow_color)
    shadow_mask = img.split()[3] if img.mode == 'RGBA' else Image.new('L', img.size, 255)
    shadow.putalpha(shadow_mask)
    # create a larger canvas to handle blur
    canvas = Image.new('RGBA', (img.width + abs(offset[0]) + blur*2, img.height + abs(offset[1]) + blur*2), (0,0,0,0))
    canvas.paste(shadow, (blur + offset[0], blur + offset[1]))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    # Paste image on top
    canvas.paste(img, (blur, blur), img if img.mode == 'RGBA' else None)
    return canvas

print("Generating 16:9 Veo assets...")

# Shot 1: The Book Cover on a Table Environment
cover_path = os.path.join(script_dir, "epic_cover_final.png")
if os.path.exists(cover_path):
    c_img = Image.open(cover_path).convert("RGBA")
    # Scale cover to fit inside 1080p with padding
    target_h = int(H * 0.8)
    target_w = int(target_h * (c_img.width / c_img.height))
    c_img = c_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Create dark oak / studio backdrop
    bg = Image.new('RGB', (W, H), (20, 22, 25))
    
    # Create slightly overlapping shadow composite
    composite = create_shadow(c_img, offset=(0, 30), blur=40, shadow_color=(0,0,0,220))
    
    # Paste onto center of 16:9 layout
    bg.paste(composite, ((W - composite.width)//2, (H - composite.height)//2), composite)
    
    bg.save(os.path.join(out_dir, "veo_shot1_cover_16x9.png"))
    print("Saved veo_shot1_cover_16x9.png")

# Shot 2: Page
page_path = os.path.join(script_dir, "illustrations", "page_04.png")
if os.path.exists(page_path):
    p_img = Image.open(page_path).convert("RGBA")
    target_h = int(H * 0.8)
    target_w = int(target_h * (p_img.width / p_img.height))
    p_img = p_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    bg = Image.new('RGB', (W, H), (245, 240, 230)) # warm paper background
    comp = create_shadow(p_img, offset=(0, 20), blur=20, shadow_color=(0,0,0,100))
    bg.paste(comp, ((W - comp.width)//2, (H - comp.height)//2), comp)
    bg.save(os.path.join(out_dir, "veo_shot2_page_16x9.png"))
    print("Saved veo_shot2_page_16x9.png")

