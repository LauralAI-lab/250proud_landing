import os
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color, CMYKColor, HexColor
from reportlab.lib.units import inch

# Import the data
try:
    from book_data import PAGES
except ImportError:
    from coloring_book.book_data import PAGES

PAGE_WIDTH = 8.75 * inch
PAGE_HEIGHT = 11.25 * inch

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
        print("Warning: Could not register fonts.")

def draw_wrapped_text(c, text, x, y, width, font_name, font_size, line_height_mult=1.3):
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

def draw_footer(c, page_num):
    c.setFillColor(C_DARK_GRAY)
    c.setFont("OpenSans", 9)
    # Move footer up slightly to stay clear of bleed
    c.drawCentredString(PAGE_WIDTH / 2, 0.625 * inch, f"\u00A9 2026 LauralAI LLC. All Rights Reserved. | 250Proud.net | Page {page_num}")

def draw_blank_page(c):
    # Simply render a blank page
    c.showPage()

def draw_intro(c):
    c.setFillColor(C_DARK_GRAY)
    
    safe_margin_x = 0.625 * inch
    inner_width = PAGE_WIDTH - 2 * safe_margin_x
    
    c.setFont("RobotoSlab-Bold", 32)
    c.drawString(safe_margin_x, PAGE_HEIGHT - 2 * inch, "This Book Belongs To:")
    c.drawString(safe_margin_x, PAGE_HEIGHT - 2.8 * inch, "_____________________")
    
    intro_text = ("America turns 250 in 2026. That's two and a half centuries of inventors, rebels, explorers, and everyday people "
                 "who did extraordinary things (most of them without a smartphone or a GPS). This coloring book isn't a history "
                 "test. It's a tour. We picked 20 moments, people, and places across 250 years that we think are genuinely worth "
                 "knowing, including a few you've probably never heard of. Grab your colored pencils. Or don't. Either way, the "
                 "stories are worth reading. \n\nThe 250Proud Team")
    
    y = PAGE_HEIGHT - 4.2 * inch
    c.setFont("OpenSans", 16)
    
    for param_text in intro_text.split("\n"):
        if param_text.strip():
            y = draw_wrapped_text(c, param_text, safe_margin_x, y, inner_width, "OpenSans", 16, 1.5)
        else:
            y -= 16 * 1.5
                
    draw_footer(c, 1)
    c.showPage()

def draw_content_page(c, page_data, real_page_num, display_page_num):
    margin_x = 0.625 * inch
    margin_y = 0.625 * inch
    inner_width = PAGE_WIDTH - 2 * margin_x
    
    c.setFillColor(C_DARK_GRAY)
    c.setFont("OpenSans-Bold", 10)
    c.drawString(margin_x, PAGE_HEIGHT - margin_y - 10, page_data["era"].upper())
    
    c.setFont("RobotoSlab-Bold", 20)
    y_after_head = draw_wrapped_text(c, page_data["headline"], margin_x, PAGE_HEIGHT - margin_y - 35, inner_width, "RobotoSlab-Bold", 22)
    
    ph_height = PAGE_HEIGHT * 0.53 # slightly smaller due to larger document
    ph_y = y_after_head - ph_height - 10
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "illustrations", f"page_{display_page_num:02d}.png")
    if os.path.exists(img_path):
        c.drawImage(img_path, margin_x, ph_y, width=inner_width, height=ph_height, preserveAspectRatio=True, anchor='c')
        c.setStrokeColor(HexColor("#111111"))
        c.setLineWidth(1.5)
        c.rect(margin_x, ph_y, inner_width, ph_height, fill=0, stroke=1)
    else:
        c.setFillColor(C_GRAY_PLACEHOLDER)
        c.setStrokeColor(HexColor("#AAAAAA"))
        c.rect(margin_x, ph_y, inner_width, ph_height, fill=1, stroke=1)
        
        c.setFillColor(C_DARK_GRAY)
        c.setFont("OpenSans-Bold", 18)
        c.drawCentredString(PAGE_WIDTH / 2, ph_y + (ph_height / 2), f"[ART PLACEHOLDER: Illustration {display_page_num}]")
    
    c.setFillColor(C_DARK_GRAY)
    start_text_y = ph_y - 25
    
    c.setFont("OpenSans-Bold", 11)
    lkf_y = draw_wrapped_text(c, "LITTLE-KNOWN FACT:", margin_x, start_text_y, inner_width, "OpenSans-Bold", 11)
    c.setFont("OpenSans", 11)
    y_after_lkf = draw_wrapped_text(c, page_data["little_known"], margin_x, lkf_y, inner_width, "OpenSans", 11, line_height_mult=1.2)
    
    c.setLineWidth(1.0)
    c.line(margin_x, y_after_lkf - 10, margin_x + inner_width, y_after_lkf - 10)
    
    c.setFont("OpenSans", 12)
    draw_wrapped_text(c, page_data["fact"], margin_x, y_after_lkf - 30, inner_width, "OpenSans", 12, line_height_mult=1.3)
    
    draw_footer(c, real_page_num)
    c.showPage()

def draw_bonus_page(c, real_page_num):
    margin_x = 0.625 * inch
    inner_width = PAGE_WIDTH - 2 * margin_x
    
    c.setFillColor(C_DARK_GRAY)
    c.setFont("RobotoSlab-Bold", 24)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 1.0 * inch, "The Flag Has Changed 27 Times.")
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 1.4 * inch, "Here's Your Version.")
    
    c.setFont("OpenSans", 14)
    text = ("The American flag has had 27 official versions since 1777. The current 50-star design was created by a "
            "17-year-old named Robert Heft for a high school project. He got a B-. His teacher changed the grade to an A "
            "after Congress adopted the design in 1960.")
    draw_wrapped_text(c, text, margin_x, PAGE_HEIGHT - 1.9 * inch, inner_width, "OpenSans", 14)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(script_dir, "illustrations", "page_23.png") # Legacy index 23
    if os.path.exists(img_path):
        c.drawImage(img_path, margin_x, 2 * inch, width=inner_width, height=PAGE_HEIGHT - 5 * inch, preserveAspectRatio=True, anchor='c')
        c.setStrokeColor(HexColor("#111111"))
        c.setLineWidth(1.5)
        c.rect(margin_x, 2 * inch, inner_width, PAGE_HEIGHT - 5 * inch, fill=0, stroke=1)
    else:
        c.setFillColor(C_GRAY_PLACEHOLDER)
        c.setStrokeColor(HexColor("#AAAAAA"))
        c.rect(margin_x, 2 * inch, inner_width, PAGE_HEIGHT - 5 * inch, fill=1, stroke=1)
        
        c.setFillColor(C_DARK_GRAY)
        c.setFont("OpenSans-Bold", 18)
        c.drawCentredString(PAGE_WIDTH / 2, (PAGE_HEIGHT + 2 * inch - 5 * inch) / 2 + inch, "[ART PLACEHOLDER: Uncolored American Flag]")
    
    draw_footer(c, real_page_num)
    c.showPage()

def build_pdf():
    output_path = "250Proud_ColoringBook_POD_Interior.pdf"
    register_fonts()
    c = canvas.Canvas(output_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
    
    # Page 1: Intro
    draw_intro(c)
    # Page 2: Blank (Back of intro)
    draw_blank_page(c)
    
    real_page = 3
    # Content Pages
    for i, page_data in enumerate(PAGES):
        # Illustration mapping: data index 0 was page 3 in old book, so display_page_num = i+3
        draw_content_page(c, page_data, real_page_num=real_page, display_page_num=i+3)
        real_page += 1
        draw_blank_page(c) # Back side is blank to prevent marker bleed
        real_page += 1
        
    # Bonus Flag
    draw_bonus_page(c, real_page_num=real_page)
    real_page += 1
    # Final Blank page
    draw_blank_page(c)
    
    c.save()
    print(f"✅ Successfully built {output_path} (Pages: {real_page})")

if __name__ == "__main__":
    if not os.path.exists("fonts"):
        os.chdir("/Users/michaelprice/Desktop/lauralai/250proud_landing/coloring_book")
    build_pdf()
