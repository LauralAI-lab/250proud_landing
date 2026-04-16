import os
import math

output_dir = "/Users/michaelprice/Desktop/lauralai/250proud_landing/DirectPrint"
os.makedirs(output_dir, exist_ok=True)
svg_path = os.path.join(output_dir, "born_1776_still_standing.svg")

# 4500x5400 is perfectly sized for 15x18 inch DTG printing at 300 DPI
width = 4500
height = 5400

def create_star(cx, cy, r, points=5, inner_ratio=0.382):
    path = "M "
    for i in range(points * 2):
        angle = i * math.pi / points - math.pi / 2
        radius = r if i % 2 == 0 else r * inner_ratio
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        path += f"{x:.1f},{y:.1f} "
    return path + "Z"

# Build the 13 stars
star_paths = ""
for i in range(13):
    angle = i * 2 * math.pi / 13 - math.pi / 2
    r_circle = 800
    cx = r_circle * math.cos(angle)
    cy = r_circle * math.sin(angle)
    star_paths += f'      <path d="{create_star(cx, cy, 120)}" class="star" />\n'

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <!-- Muted Gold Gradient -->
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#cfb53b"/>
      <stop offset="100%" stop-color="#8a7314"/>
    </linearGradient>
    
    <!-- Warm Grey Gradient -->
    <linearGradient id="greyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#e0e0e0"/>
      <stop offset="100%" stop-color="#a0a0a0"/>
    </linearGradient>

    <!-- Darker Grey Gradient for contrast -->
    <linearGradient id="darkGreyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#888888"/>
      <stop offset="100%" stop-color="#444444"/>
    </linearGradient>
    
    <style>
      .bg-stripes {{ fill: none; stroke: url(#darkGreyGrad); stroke-width: 150; stroke-linecap: round; opacity: 0.8; }}
      .bg-stripes-gold {{ fill: none; stroke: url(#goldGrad); stroke-width: 120; stroke-linecap: round; opacity: 0.9; }}
      .star {{ fill: url(#greyGrad); opacity: 0.9; }}
      .text-large {{ font-family: 'Impact', 'Arial Black', sans-serif; font-size: 850px; font-weight: 900; fill: url(#greyGrad); text-anchor: middle; letter-spacing: -10px; }}
      .text-medium {{ font-family: 'Impact', 'Arial Black', sans-serif; font-size: 550px; font-weight: 900; fill: url(#goldGrad); text-anchor: middle; letter-spacing: 5px; }}
    </style>
  </defs>

  <!-- Transparent background by default. No rect drawn for background! -->

  <g transform="translate({width//2}, {height//2 - 600})">
    <!-- Star Circle behind text -->
{star_paths}
  </g>

  <!-- Stylized Flag Stripes -->
  <!-- Top stripes behind BORN 1776 -->
  <path d="M 600 1200 L 3900 1200" class="bg-stripes" />
  <path d="M 800 1450 L 3700 1450" class="bg-stripes-gold" />
  <path d="M 500 1700 L 4000 1700" class="bg-stripes" />
  
  <!-- Middle stripes cutting behind -->
  <path d="M 700 2800 L 3800 2800" class="bg-stripes" />
  <path d="M 900 3050 L 3600 3050" class="bg-stripes-gold" />
  
  <!-- Bottom stripes behind STILL STANDING -->
  <path d="M 600 4000 L 3900 4000" class="bg-stripes" />
  <path d="M 800 4250 L 3700 4250" class="bg-stripes-gold" />

  <!-- Main Typography -->
  <g transform="translate({width//2}, 2300)">
    <!-- Slight drop shadow for text pop -->
    <text x="20" y="20" class="text-large" fill="#000000" opacity="0.4">BORN 1776.</text>
    <text x="0" y="0" class="text-large">BORN 1776.</text>
  </g>

  <g transform="translate({width//2}, 3700)">
    <text x="15" y="15" class="text-medium" fill="#000000" opacity="0.4">STILL STANDING.</text>
    <text x="0" y="0" class="text-medium">STILL STANDING.</text>
  </g>

</svg>
"""

with open(svg_path, "w") as f:
    f.write(svg_content)

print(f"✅ Successfully generated high-resolution SVG at: {svg_path}")

try:
    png_path = svg_path.replace(".svg", ".png")
    # Quick attempt to generate PNG using macOS native sips or standard tool if ImageMagick is installed
    # sips doesn't support SVG natively, we will try rsvg-convert or magick
    if os.system(f"magick -density 300 -background none {svg_path} {png_path} 2>/dev/null") == 0:
        print(f"✅ Successfully generated 300 DPI Transparent PNG at: {png_path}")
    elif os.system(f"rsvg-convert -h {height} -a {svg_path} -o {png_path} 2>/dev/null") == 0:
        print(f"✅ Successfully generated Transparent PNG at: {png_path}")
except Exception as e:
    pass
