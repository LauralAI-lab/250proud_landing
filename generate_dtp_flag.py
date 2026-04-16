import os
import math

output_dir = "/Users/michaelprice/Desktop/lauralai/250proud_landing/DirectPrint"
os.makedirs(output_dir, exist_ok=True)
svg_path = os.path.join(output_dir, "born_1776_still_standing.svg")

width = 4500
height = 5400

# Patriotic Colors
red = "#B31942"
white = "#FFFFFF" 
blue = "#0A3161"
gold = "#B8922A"
dark_grey = "#222222"

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .retro-text {{
        font-family: 'Impact', 'Arial Black', sans-serif;
        font-weight: 900;
        text-anchor: middle;
      }}
      .stripe-red {{ fill: {red}; }}
      .stripe-white {{ fill: {white}; }}
      .union {{ fill: {blue}; }}
      .star {{ fill: {white}; }}
      /* Mask for the distressed look */
      .scratch {{ fill: none; stroke: {dark_grey}; stroke-linecap: round; }}
    </style>
    
    <mask id="distressMask">
      <rect width="100%" height="100%" fill="white"/>
      <!-- Procedurally generated scratches will go here -->
"""

# Generate some random looking scratches for the mask to give it a distressed/apparel feel
import random
random.seed(1776)
for _ in range(300):
    x1 = random.randint(0, width)
    y1 = random.randint(0, height)
    length = random.randint(50, 400)
    angle = random.uniform(0, math.pi * 2)
    x2 = x1 + length * math.cos(angle)
    y2 = y1 + length * math.sin(angle)
    stroke_w = random.randint(3, 15)
    svg_content += f'      <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" stroke-width="{stroke_w}" opacity="{random.uniform(0.3, 0.9)}" />\n'

for _ in range(800):
    cx = random.randint(0, width)
    cy = random.randint(0, height)
    r = random.randint(2, 25)
    svg_content += f'      <circle cx="{cx}" cy="{cy}" r="{r}" fill="black" opacity="{random.uniform(0.2, 0.8)}" />\n'

svg_content += """
    </mask>
  </defs>

  <!-- Apply the mask to everything -->
  <g mask="url(#distressMask)">
"""

# FLAG DIMENSIONS
# Let's make the flag centered, about 3800px wide, and 2000px high
flag_w = 3800
flag_h = 2200
flag_x = (width - flag_w) // 2
flag_y = 1200

# 13 Stripes
stripe_h = flag_h / 13
for i in range(13):
    color_class = "stripe-red" if i % 2 == 0 else "stripe-white"
    sy = flag_y + i * stripe_h
    # Make them slightly uneven for a hand-painted/tattered look
    svg_content += f'    <rect x="{flag_x}" y="{sy}" width="{flag_w}" height="{stripe_h + 2}" class="{color_class}" />\n'

# Union (Canton)
union_h = stripe_h * 7
union_w = flag_w * 0.4
svg_content += f'    <rect x="{flag_x}" y="{flag_y}" width="{union_w}" height="{union_h}" class="union" />\n'

# Stars inside the union (Betsey Ross circle of 13)
def create_star(cx, cy, r, points=5, inner_ratio=0.382):
    path = "M "
    for i in range(points * 2):
        angle = i * math.pi / points - math.pi / 2
        radius = r if i % 2 == 0 else r * inner_ratio
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        path += f"{x:.1f},{y:.1f} "
    return path + "Z"

center_x = flag_x + (union_w / 2)
center_y = flag_y + (union_h / 2)
radius = union_h * 0.35

for i in range(13):
    angle = i * 2 * math.pi / 13 - math.pi / 2
    cx = center_x + radius * math.cos(angle)
    cy = center_y + radius * math.sin(angle)
    svg_content += f'    <path d="{create_star(cx, cy, 50)}" class="star" />\n'


# Add the typography
svg_content += f"""
    <!-- Text Drop Shadows -->
    <text x="{width//2 + 25}" y="{flag_y - 120 + 25}" class="retro-text" font-size="800px" fill="{dark_grey}">BORN 1776.</text>
    <text x="{width//2 + 20}" y="{flag_y + flag_h + 600 + 20}" class="retro-text" font-size="600px" fill="{dark_grey}">STILL STANDING.</text>

    <!-- Main Text -->
    <text x="{width//2}" y="{flag_y - 120}" class="retro-text" font-size="800px" fill="{white}" stroke="{red}" stroke-width="25">BORN 1776.</text>
    <text x="{width//2}" y="{flag_y + flag_h + 600}" class="retro-text" font-size="600px" fill="{gold}" stroke="{blue}" stroke-width="15">STILL STANDING.</text>
  </g>
</svg>
"""

with open(svg_path, "w") as f:
    f.write(svg_content)

print(f"✅ Generated incredibly clean, perfectly masked Distressed Flag SVG at: {svg_path}")
