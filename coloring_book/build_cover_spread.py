import os
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color, CMYKColor, HexColor
from reportlab.lib.units import inch

# Print Dimensions
TRIM_W = 8.5 * inch
TRIM_H = 11.0 * inch
BLEED = 0.125 * inch
SPINE = 0.1 * inch # 44 pages approx.

SPREAD_WIDTH = (2 * TRIM_W) + SPINE + (2 * BLEED)
SPREAD_HEIGHT = TRIM_H + (2 * BLEED)

FRONT_X = BLEED + TRIM_W + SPINE
BACK_X = BLEED

# Colors
C_NAVY = HexColor("#0A1931")
C_GOLD = HexColor("#C9A84C")

def register_fonts():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        landing_dir = os.path.dirname(script_dir)
        base = os.path.join(landing_dir, "fonts")
        if not os.path.exists(base):
            base = os.path.join(script_dir, "fonts")
            
        pdfmetrics.registerFont(TTFont("OpenSans", os.path.join(base, "OpenSans-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("OpenSans-Bold", os.path.join(base, "OpenSans-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoSlab", os.path.join(base, "RobotoSlab-Regular.ttf")))
        pdfmetrics.registerFont(TTFont("RobotoSlab-Bold", os.path.join(base, "RobotoSlab-Bold.ttf")))
    except Exception as e:
        print("Warning: Could not register fonts.")

def draw_wrapped_text(c, text, x_center, y, width, font_name, font_size, line_height_mult=1.3):
    c.setFont(font_name, font_size)
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if c.stringWidth(test_line, font_name, font_size) < width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    
    current_y = y
    for line in lines:
        c.drawCentredString(x_center, current_y, line.strip())
        current_y -= font_size * line_height_mult
    return current_y

def draw_star(c, cx, cy, size, color):
    c.setFillColor(color)
    p = c.beginPath()
    outer_r = size
    inner_r = size * 0.382
    start_angle = math.pi / 2
    
    p.moveTo(cx + outer_r * math.cos(start_angle), cy + outer_r * math.sin(start_angle))
    for i in range(5):
        angle = start_angle + i * (2 * math.pi / 5)
        angle_inner = angle + (math.pi / 5)
        p.lineTo(cx + inner_r * math.cos(angle_inner), cy + inner_r * math.sin(angle_inner))
        
        angle_next = start_angle + (i + 1) * (2 * math.pi / 5)
        p.lineTo(cx + outer_r * math.cos(angle_next), cy + outer_r * math.sin(angle_next))
    p.close()
    c.drawPath(p, fill=1, stroke=0)

def draw_spread(c):
    # Full bleed background Navy across entire canvas
    c.setFillColor(C_NAVY)
    c.rect(0, 0, SPREAD_WIDTH, SPREAD_HEIGHT, fill=1, stroke=0)
    
    # ---------------- FRONT COVER ----------------
    # Background Image 
    bg_img = "epic_cover_final.png" # usually US Letter aspect ratio
    if os.path.exists(bg_img):
        # Extend the image to cover the front trim + its 3 bleed edges + half spine
        # Width: 8.5 + 0.125 (right) + (half spine 0.05) = 8.675
        # We can just center it on the front cover area. It might stretch slightly, so preserveAspect
        fw = TRIM_W + 2*BLEED
        fh = TRIM_H + 2*BLEED
        c.drawImage(bg_img, FRONT_X - BLEED, 0, width=fw, height=fh, preserveAspectRatio=True, anchor='c')
    
    # Draw Stars safely inside front cover
    # Front cover boundaries (Local to trim): 0 to TRIM_W
    num_stars = 7
    star_size = 14
    margin_top_local_y = TRIM_H - 45 # 747
    margin_bottom_local_y = 45
    spacing = TRIM_W / (num_stars + 1)
    for i in range(1, num_stars + 1):
        cx = FRONT_X + (i * spacing)
        # Shift Y to global canvas by adding bottom BLEED
        draw_star(c, cx, margin_top_local_y + BLEED, star_size, C_GOLD)
        draw_star(c, cx, margin_bottom_local_y + BLEED, star_size, C_GOLD)

    # ---------------- BACK COVER ----------------
    bc_center = BACK_X + (TRIM_W / 2)
    
    c.setFillColor(C_GOLD)
    c.setFont("RobotoSlab-Bold", 36)
    c.drawCentredString(bc_center, SPREAD_HEIGHT - 2 * inch, "250Proud\u2122 \u00B7 1776\u20132026")
    
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("RobotoSlab", 22)
    c.drawCentredString(bc_center, SPREAD_HEIGHT - 3 * inch, "Proud of where we've been. Ready for what's next.")
    
    c.setFont("OpenSans", 14)
    top_promo_text = ("Find a complete selection of all-original patriotic merchandise at 250Proud\u2122.Net. "
                      "Upload your colored American Flag Page to 250Proud.Net. "
                      "We'll include it in our gallery and enter you into a drawing to have it printed on your very own t-shirt!")
    
    # Safe margins: 0.5 inside trim
    safe_width = TRIM_W - (1.0 * inch)
    draw_wrapped_text(c, top_promo_text, bc_center, SPREAD_HEIGHT - 3.8 * inch, safe_width, "OpenSans", 13, line_height_mult=1.3)
    
    # Mockup Products
    mockup_y = SPREAD_HEIGHT / 2 - 1.7 * inch
    mockup_size = 2.0 * inch
    m_spacing = (TRIM_W - (3 * mockup_size)) / 4
    
    m1 = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/mockup_snapback.png"
    m2 = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/eagle_blueprint_tee_live.jpg"
    m3 = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/mockup_mug.jpg"
    
    for i, m_path in enumerate([m1, m2, m3]):
        x = BACK_X + m_spacing + i * (mockup_size + m_spacing) + (mockup_size/2)
        if os.path.exists(m_path):
            c.drawImage(m_path, x - (mockup_size/2), mockup_y, width=mockup_size, height=mockup_size, preserveAspectRatio=True, anchor='c')

    # Logo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "illustrations", "white_250proud_logo.png")
    logo_w = 2.0 * inch
    logo_h = 1.0 * inch
    if os.path.exists(logo_path):
        c.drawImage(logo_path, bc_center - (logo_w/2), BLEED + 1.8 * inch, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')

    # B2B Pitch
    c.setFillColor(HexColor("#FFFFFF"))
    b2b_text = ("Find out how to get your very own white-labeled version of this book to use as a promotional item. "
                "Use it as a download or have it printed. Set your business apart and show your patriotism to your customers. "
                "Visit 250Proud.net for details or email info@250Proud.net")
    draw_wrapped_text(c, b2b_text, bc_center, BLEED + 1.5 * inch, safe_width, "OpenSans-Bold", 12, line_height_mult=1.3)
    
    c.setFont("OpenSans", 10)
    c.drawCentredString(bc_center, BLEED + 0.5 * inch, "\u00A9 2026 LauralAI LLC. All Rights Reserved. | 250Proud.net")
    c.showPage()

def build_pdf():
    output_path = "250Proud_ColoringBook_CoverSpread.pdf"
    register_fonts()
    c = canvas.Canvas(output_path, pagesize=(SPREAD_WIDTH, SPREAD_HEIGHT))
    draw_spread(c)
    c.save()
    print(f"✅ Successfully built {output_path} (Size: {SPREAD_WIDTH/inch}\" x {SPREAD_HEIGHT/inch}\")")

if __name__ == "__main__":
    if not os.path.exists("fonts"):
        os.chdir("/Users/michaelprice/Desktop/lauralai/250proud_landing/coloring_book")
    build_pdf()
