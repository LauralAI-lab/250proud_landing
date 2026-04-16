import os
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color, CMYKColor, HexColor
from reportlab.lib.units import inch
from PIL import Image

# Import the data we scraped
try:
    from book_data import PAGES
except ImportError:
    # Fallback to local copy if run in weird environment
    from coloring_book.book_data import PAGES

# Dimensions
PAGE_WIDTH, PAGE_HEIGHT = letter

# Colors (as requested)
C_NAVY = HexColor("#0A1931")
C_GOLD = HexColor("#C9A84C")
C_RED = HexColor("#B22234")
C_OFFWHITE = HexColor("#F5F0E8")
C_GRAY_PLACEHOLDER = HexColor("#DDDDDD")
C_DARK_GRAY = HexColor("#333333")

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
        print("Warning: Could not register fonts. Make sure download_fonts.py was run.")
        raise e

def draw_wrapped_text(c, text, x, y, width, font_name, font_size, line_height_mult=1.3):
    """Draw text bounded by width."""
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
        c.drawString(x, current_y, line.strip())
        current_y -= font_size * line_height_mult
    return current_y

def draw_centered_wrapped_text(c, text, x_center, y, width, font_name, font_size, line_height_mult=1.3):
    """Draw text bounded by width, but cleanly centered."""
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

def draw_star_pdf(c, cx, cy, size, color):
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

def draw_cover(c):
    # Place the fully composited epic cover
    bg_img = "epic_cover_final.png"
    if os.path.exists(bg_img):
        # We fill the page with the image, maintaining aspect to cover
        c.drawImage(bg_img, 0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT, preserveAspectRatio=True, anchor='c')
    else:
        # Fallback navy
        c.setFillColor(C_NAVY)
        c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)

    # Draw explicit vector stars in the vertical PDF page margins
    num_stars = 7
    star_size = 14
    margin_top_y = PAGE_HEIGHT - 45 # 747
    margin_bottom_y = 45
    spacing = PAGE_WIDTH / (num_stars + 1)
    for i in range(1, num_stars + 1):
        cx = i * spacing
        draw_star_pdf(c, cx, margin_top_y, star_size, C_GOLD)
        draw_star_pdf(c, cx, margin_bottom_y, star_size, C_GOLD)

    c.showPage()

def draw_intro(c):
    c.setFillColor(C_DARK_GRAY)
    
    # Needs to belong to
    c.setFont("RobotoSlab-Bold", 32)
    c.drawString(inch, PAGE_HEIGHT - 2 * inch, "This Book Belongs To:")
    c.drawString(inch, PAGE_HEIGHT - 2.8 * inch, "_____________________")
    
    intro_text = ("America turns 250 in 2026. That's two and a half centuries of inventors, rebels, explorers, and everyday people "
                 "who did extraordinary things (most of them without a smartphone or a GPS). This coloring book isn't a history "
                 "test. It's a tour. We picked 20 moments, people, and places across 250 years that we think are genuinely worth "
                 "knowing, including a few you've probably never heard of. Grab your colored pencils. Or don't. Either way, the "
                 "stories are worth reading. \n\nThe 250Proud Team")
    
    y = PAGE_HEIGHT - 4.2 * inch
    c.setFont("OpenSans", 16)
    
    # Manually split explicit newlines
    for param_text in intro_text.split("\n"):
        if param_text.strip():
            y = draw_wrapped_text(c, param_text, inch, y, PAGE_WIDTH - 2 * inch, "OpenSans", 16, 1.5)
        else:
            y -= 16 * 1.5 # blank line
                
    draw_footer(c, 2)
    c.showPage()

def draw_footer(c, page_num):
    c.setFillColor(C_DARK_GRAY)
    c.setFont("OpenSans", 9)
    c.drawCentredString(PAGE_WIDTH / 2, 0.5 * inch, f"\u00A9 2026 LauralAI LLC. All Rights Reserved. | 250Proud.net | Page {page_num}")

def draw_content_page(c, page_data, page_num):
    # Safe Margins
    margin_x = 0.5 * inch
    margin_y = 0.5 * inch
    inner_width = PAGE_WIDTH - 2 * margin_x
    
    # Era Label
    c.setFillColor(C_DARK_GRAY)
    c.setFont("OpenSans-Bold", 10)
    c.drawString(margin_x, PAGE_HEIGHT - margin_y - 10, page_data["era"].upper())
    
    # Headline
    c.setFont("RobotoSlab-Bold", 20)
    y_after_head = draw_wrapped_text(c, page_data["headline"], margin_x, PAGE_HEIGHT - margin_y - 35, inner_width, "RobotoSlab-Bold", 22)
    
    # Art Placeholder / Final Image
    ph_height = PAGE_HEIGHT * 0.55
    ph_y = y_after_head - ph_height - 10
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "illustrations", f"page_{page_num:02d}.png")
    if os.path.exists(img_path):
        c.drawImage(img_path, margin_x, ph_y, width=inner_width, height=ph_height, preserveAspectRatio=True, anchor='c')
        
        # Add a crisp border framing
        c.setStrokeColor(HexColor("#111111"))
        c.setLineWidth(1.5)
        c.rect(margin_x, ph_y, inner_width, ph_height, fill=0, stroke=1)
    else:
        c.setFillColor(C_GRAY_PLACEHOLDER)
        c.setStrokeColor(HexColor("#AAAAAA"))
        c.rect(margin_x, ph_y, inner_width, ph_height, fill=1, stroke=1)
        
        c.setFillColor(C_DARK_GRAY)
        c.setFont("OpenSans-Bold", 18)
        c.drawCentredString(PAGE_WIDTH / 2, ph_y + (ph_height / 2), f"[ART PLACEHOLDER: Page {page_num}]")
    
    c.setFillColor(C_DARK_GRAY)
    
    start_text_y = ph_y - 25
    
    # Little-Known Fact Callout
    c.setFont("OpenSans-Bold", 11)
    lkf_y = draw_wrapped_text(c, "LITTLE-KNOWN FACT:", margin_x, start_text_y, inner_width, "OpenSans-Bold", 11)
    c.setFont("OpenSans", 11)
    y_after_lkf = draw_wrapped_text(c, page_data["little_known"], margin_x, lkf_y, inner_width, "OpenSans", 11, line_height_mult=1.2)
    
    # Separator
    c.setLineWidth(1.0)
    c.line(margin_x, y_after_lkf - 10, margin_x + inner_width, y_after_lkf - 10)
    
    # Main Fact
    c.setFont("OpenSans", 12)
    draw_wrapped_text(c, page_data["fact"], margin_x, y_after_lkf - 30, inner_width, "OpenSans", 12, line_height_mult=1.3)
    
    draw_footer(c, page_num)
    c.showPage()

def draw_bonus_page(c):
    # Page 23
    margin_x = 0.5 * inch
    inner_width = PAGE_WIDTH - 2 * margin_x
    
    c.setFillColor(C_DARK_GRAY)
    c.setFont("RobotoSlab-Bold", 24)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 0.9 * inch, "The Flag Has Changed 27 Times.")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 1.3 * inch, "Here's Your Version.")
    
    c.setFont("OpenSans", 14)
    text = ("The American flag has had 27 official versions since 1777. The current 50-star design was created by a "
            "17-year-old named Robert Heft for a high school project. He got a B-. His teacher changed the grade to an A "
            "after Congress adopted the design in 1960.")
    draw_wrapped_text(c, text, margin_x, PAGE_HEIGHT - 1.8 * inch, inner_width, "OpenSans", 14)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "illustrations", "page_23.png")
    if os.path.exists(img_path):
        c.drawImage(img_path, margin_x, 2 * inch, width=inner_width, height=PAGE_HEIGHT - 5 * inch, preserveAspectRatio=True, anchor='c')
        c.setStrokeColor(HexColor("#111111"))
        c.setLineWidth(1.5)
        c.rect(margin_x, 2 * inch, inner_width, PAGE_HEIGHT - 5 * inch, fill=0, stroke=1)
    else:
        # Placeholder for the flag to color
        c.setFillColor(C_GRAY_PLACEHOLDER)
        c.setStrokeColor(HexColor("#AAAAAA"))
        c.rect(margin_x, 2 * inch, inner_width, PAGE_HEIGHT - 5 * inch, fill=1, stroke=1)
        
        c.setFillColor(C_DARK_GRAY)
        c.setFont("OpenSans-Bold", 18)
        c.drawCentredString(PAGE_WIDTH / 2, (PAGE_HEIGHT + 2 * inch - 5 * inch) / 2 + inch, "[ART PLACEHOLDER: Uncolored American Flag]")
    
    draw_footer(c, 23)
    c.showPage()

def draw_back_cover(c):
    # Navy background
    c.setFillColor(C_NAVY)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    
    c.setFillColor(C_GOLD)
    c.setFont("RobotoSlab-Bold", 36)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 2 * inch, "250Proud\u2122 \u00B7 1776\u20132026")
    
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("RobotoSlab", 22)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 3 * inch, "Proud of where we've been. Ready for what's next.")
    
    c.setFont("OpenSans", 14)
    # The new text block
    top_promo_text = ("Find a complete selection of all-original patriotic merchandise at 250Proud\u2122.Net. "
                      "Upload your colored American Flag Page to 250Proud.Net. "
                      "We'll include it in our gallery and enter you into a drawing to have it printed on your very own t-shirt!")
    top_promo_margin = 1.0 * inch
    top_promo_width = PAGE_WIDTH - 2 * top_promo_margin
    draw_centered_wrapped_text(c, top_promo_text, PAGE_WIDTH / 2, PAGE_HEIGHT - 3.8 * inch, top_promo_width, "OpenSans", 13, line_height_mult=1.3)
    
    # 3 Mockup Product Images
    mockup_y = PAGE_HEIGHT / 2 - 1.7 * inch
    mockup_size = 2.0 * inch
    spacing = (PAGE_WIDTH - (3 * mockup_size)) / 4
    
    m1 = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/mockup_snapback.png"
    m2 = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/eagle_blueprint_tee_live.jpg"
    m3 = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/mockup_mug.jpg"
    
    for i, m_path in enumerate([m1, m2, m3]):
        x = spacing + i * (mockup_size + spacing)
        if os.path.exists(m_path):
            c.drawImage(m_path, x, mockup_y, width=mockup_size, height=mockup_size, preserveAspectRatio=True, anchor='c')
            
    # 250Proud Logo at the bottom
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "illustrations", "white_250proud_logo.png")
    logo_w = 2.0 * inch
    logo_h = 1.0 * inch
    if os.path.exists(logo_path):
        c.drawImage(logo_path, (PAGE_WIDTH - logo_w) / 2, 1.8 * inch, width=logo_w, height=logo_h, preserveAspectRatio=True, anchor='c', mask='auto')
        
    # B2B Promotional Pitch
    c.setFillColor(HexColor("#FFFFFF"))
    b2b_text = ("Find out how to get your very own white-labeled version of this book to use as a promotional item. "
                "Use it as a download or have it printed. Set your business apart and show your patriotism to your customers. "
                "Visit 250Proud.net for details or email info@250Proud.net")
    b2b_margin = 0.8 * inch
    b2b_width = PAGE_WIDTH - 2 * b2b_margin
    draw_centered_wrapped_text(c, b2b_text, PAGE_WIDTH / 2, 1.5 * inch, b2b_width, "OpenSans-Bold", 12, line_height_mult=1.3)
    
    c.setFont("OpenSans", 10)
    c.drawCentredString(PAGE_WIDTH / 2, 0.5 * inch, "\u00A9 2026 LauralAI LLC. All Rights Reserved. | 250Proud.net")
    
    c.showPage()

def build_pdf():
    # Make sure we run from correct working directory context or handle nested calls
    output_path = "250Proud_ColoringBook_Digital_Edition.pdf"
    
    register_fonts()
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Page 1: Cover
    draw_cover(c)
    
    # Page 2: Intro
    draw_intro(c)
    
    # Pages 3-22: Content
    for i, page_data in enumerate(PAGES):
        draw_content_page(c, page_data, page_num=i+3)
        
    # Page 23: Bonus Flag
    draw_bonus_page(c)
    
    # Page 24: Back Cover
    draw_back_cover(c)
    
    c.save()
    print(f"✅ Successfully built {output_path}")

if __name__ == "__main__":
    # Ensure current directory has fonts folder (either run from coloring_book or script handles it)
    if not os.path.exists("fonts"):
        os.chdir("/Users/michaelprice/Desktop/lauralai/250proud_landing/coloring_book")
    build_pdf()
