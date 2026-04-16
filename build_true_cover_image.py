from PIL import Image, ImageDraw
import math

def draw_star(draw, cx, cy, size, color):
    points = []
    outer_r = size
    inner_r = size * 0.382
    start_angle = math.pi / 2
    for i in range(5):
        angle = start_angle + i * (2 * math.pi / 5)
        angle_inner = angle + (math.pi / 5)
        # Invert Y for Pillow
        points.append((cx + outer_r * math.cos(angle), cy - outer_r * math.sin(angle)))
        points.append((cx + inner_r * math.cos(angle_inner), cy - inner_r * math.sin(angle_inner)))
    draw.polygon(points, fill=color)

def make_cover():
    width = 1750
    height = 2250 # Approx 8.5x11 ratio
    cover = Image.new('RGB', (width, height), '#0A1931')
    
    try:
        epic = Image.open('epic_cover_final.png').convert("RGBA")
        ew, eh = epic.size
        # Try to fit it beautifully
        target_eh = int((width / ew) * eh)
        if target_eh > height:
            # Scale by height instead
            target_eh = height
            width_scaled = int((height / eh) * ew)
            epic = epic.resize((width_scaled, target_eh), Image.LANCZOS)
            x_offset = (width - width_scaled) // 2
            y_offset = 0
            cover.paste(epic, (x_offset, y_offset), epic)
        else:
            epic = epic.resize((width, target_eh), Image.LANCZOS)
            x_offset = 0
            y_offset = (height - target_eh) // 2
            cover.paste(epic, (x_offset, y_offset), epic)
    except Exception as e:
        print("Epic cover error:", e)
    
    draw = ImageDraw.Draw(cover)
    gold = (201, 168, 76)
    
    # Draw Stars
    num_stars = 7
    star_size = 35
    spacing = width / (num_stars + 1)
    
    y_top = int(height * 0.05)
    y_bot = int(height * 0.95)
    
    for i in range(1, num_stars + 1):
        cx = i * spacing
        draw_star(draw, cx, y_top, star_size, gold)
        draw_star(draw, cx, y_bot, star_size, gold)
        
    cover.save("nc_assets/img/generated_true_cover.png", "PNG")
    print("Saved generated_true_cover.png!")

if __name__ == "__main__":
    make_cover()
