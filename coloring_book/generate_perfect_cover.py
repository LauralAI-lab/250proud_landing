import os
import math
from PIL import Image, ImageDraw

script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "video_renders")

# 8.5 x 11 ratio
PW, PH = 1700, 2200
NAVY = (10, 25, 49) # #0A1931
GOLD = (201, 168, 76)

def draw_star(draw, cx, cy, size, color):
    # Port of the PDF star drawer
    outer_r = size
    inner_r = size * 0.382
    start_angle = math.pi / 2
    
    pts = []
    for i in range(5):
        angle = start_angle + i * (2 * math.pi / 5)
        angle_inner = angle + (math.pi / 5)
        # Invert Y for PIL vs ReportLab
        pts.append((cx + inner_r * math.cos(angle_inner), cy - inner_r * math.sin(angle_inner)))
        
        angle_next = start_angle + (i + 1) * (2 * math.pi / 5)
        pts.append((cx + outer_r * math.cos(angle_next), cy - outer_r * math.sin(angle_next)))
        
    draw.polygon(pts, fill=color)

# Create 8.5x11 base cover
cover = Image.new('RGBA', (PW, PH), NAVY)

# Paste the square graphic in the center
graphic_path = os.path.join(script_dir, "epic_cover_final.png")
if os.path.exists(graphic_path):
    g_img = Image.open(graphic_path).convert("RGBA")
    # scale graphic to width
    g_w = PW
    g_h = int(g_img.height * (PW / g_img.width))
    g_img = g_img.resize((g_w, g_h), Image.Resampling.LANCZOS)
    
    y_center = (PH - g_h) // 2
    cover.paste(g_img, (0, y_center), g_img)

# Draw stars at top and bottom margins
draw = ImageDraw.Draw(cover)
num_stars = 7
star_size = 28 # scaled up for 1700px width
margin_top_y = 120
margin_bottom_y = PH - 120
spacing = PW // (num_stars + 1)

for i in range(1, num_stars + 1):
    cx = i * spacing
    draw_star(draw, cx, margin_top_y, star_size, GOLD)
    draw_star(draw, cx, margin_bottom_y, star_size, GOLD)

# Now drop this perfect cover onto the 16:9 Veo backdrop
W, H = 1920, 1080
bg = Image.new('RGB', (W, H), (20, 22, 25))

# Scale cover to fit inside 1080p with padding
target_h = int(H * 0.8)
target_w = int(target_h * (PW / PH))
cover_resized = cover.resize((target_w, target_h), Image.Resampling.LANCZOS)

from PIL import ImageFilter
def create_shadow(img, offset=(0,40), blur=50, shadow_color=(0,0,0,250)):
    shadow = Image.new('RGBA', img.size, shadow_color)
    shadow_mask = img.split()[3] if img.mode == 'RGBA' else Image.new('L', img.size, 255)
    shadow.putalpha(shadow_mask)
    canvas = Image.new('RGBA', (img.width + abs(offset[0]) + blur*2, img.height + abs(offset[1]) + blur*2), (0,0,0,0))
    canvas.paste(shadow, (blur + offset[0], blur + offset[1]))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(img, (blur, blur), img if img.mode == 'RGBA' else None)
    return canvas

composite = create_shadow(cover_resized)
bg.paste(composite, ((W - composite.width)//2, (H - composite.height)//2), composite)

bg.save(os.path.join(out_dir, "veo_shot1_cover_16x9_perfect.png"))
print("Done saving perfect cover!")
