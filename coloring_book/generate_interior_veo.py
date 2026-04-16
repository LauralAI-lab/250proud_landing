import os
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFilter

script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "video_renders")
pdf_path = os.path.join(script_dir, "250Proud_ColoringBook_2026_v1.pdf")

# Veo background dimensions
W, H = 1920, 1080
NAVY = (20, 22, 25)

def create_shadow(img, offset=(0,40), blur=50, shadow_color=(0,0,0,250)):
    shadow = Image.new('RGBA', img.size, shadow_color)
    shadow_mask = img.split()[3] if img.mode == 'RGBA' else Image.new('L', img.size, 255)
    shadow.putalpha(shadow_mask)
    canvas = Image.new('RGBA', (img.width + abs(offset[0]) + blur*2, img.height + abs(offset[1]) + blur*2), (0,0,0,0))
    canvas.paste(shadow, (blur + offset[0], blur + offset[1]))
    canvas = canvas.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(img, (blur, blur), img if img.mode == 'RGBA' else None)
    return canvas

def extract_and_compose(pdf_doc, page_num, out_filename):
    print(f"Extracting page {page_num}...")
    page = pdf_doc.load_page(page_num)
    # Render at 2x dpi for high quality
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    
    # Save temp and open w/ PIL
    temp_path = os.path.join(out_dir, "temp.png")
    pix.save(temp_path)
    
    p_img = Image.open(temp_path).convert("RGBA")
    
    # Drop onto Veo 16:9 canvas
    target_h = int(H * 0.8) # Keep some breathing room top/bottom
    target_w = int(target_h * (p_img.width / p_img.height))
    p_img_resized = p_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    bg = Image.new('RGB', (W, H), NAVY)
    composite = create_shadow(p_img_resized)
    
    bg.paste(composite, ((W - composite.width)//2, (H - composite.height)//2), composite)
    final_out = os.path.join(out_dir, out_filename)
    bg.save(final_out)
    print(f"Saved {final_out}")
    os.remove(temp_path)

if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    print(f"PDF loaded with {doc.page_count} pages.")
    
    # Select our pages to extract
    # The pdf consists of:
    # 0 = Cover
    # 1 = Blank inside front cover
    # 2 = This Book Belongs to intro page
    # 3 = Title / Back of intro 
    # 4,5,6,7... interior illustration pages (illustrations are typically on even indices or odd indices depending on the build logic)
    
    # Let's extract specific nice pages (e.g. Page 4, Page 12, Page 22) to avoid blank backsides
    # We will extract pages without human subjects to bypass Veo safety filters:
    # PDF Index 9 (Railroad), 15 (Highway), 20 (Webb Telescope)
    extract_and_compose(doc, 9, "veo_shot_safe_interior_page9_railroad.png")
    extract_and_compose(doc, 15, "veo_shot_safe_interior_page15_highway.png")
    extract_and_compose(doc, 20, "veo_shot_safe_interior_page20_telescope.png")
    
    # The Back Cover is the very last page
    back_idx = doc.page_count - 1
    extract_and_compose(doc, back_idx, "veo_shot_back_cover.png")
else:
    print("Cannot find the PDF file!")
