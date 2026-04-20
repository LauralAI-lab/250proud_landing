import fitz
import os

input_file = "250Proud_ColoringBook_2026_v1.pdf"
output_file = "250Proud_ColoringBook_Web.pdf"

print("Rasterizing and compressing the PDF...")

doc = fitz.open(input_file)
new_doc = fitz.open()

for i in range(len(doc)):
    page = doc[i]
    
    # 150 DPI for fast web download but perfectly usable line-art at home
    zoom = 150 / 72.0
    mat = fitz.Matrix(zoom, zoom)
    
    # Use RGB for the cover (page 0), Grayscale for the interior coloring pages
    cspace = fitz.csRGB if i == 0 else fitz.csGRAY
    
    pix = page.get_pixmap(matrix=mat, alpha=False, colorspace=cspace)
    
    # Save as highly compressed JPEG stream (75%)
    img_bytes = pix.tobytes("jpeg", 75)
    
    # Embed back into new PDF page with identical rect geometry
    new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
    new_page.insert_image(page.rect, stream=img_bytes)

new_doc.save(output_file, garbage=4, deflate=True)

if os.path.exists(output_file):
    curr_size = os.path.getsize(input_file) / (1024*1024)
    new_size = os.path.getsize(output_file) / (1024*1024)
    print(f"Original: {curr_size:.2f} MB")
    print(f"Compressed: {new_size:.2f} MB")
    print("Done!")
else:
    print("Failed to save.")
