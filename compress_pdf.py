import fitz
import os

input_file = "250Proud_ColoringBook_2026_v1.pdf"
output_file = "250Proud_ColoringBook_Web.pdf"

print(f"Compressing {input_file}...")
doc = fitz.open(input_file)

# Basic optimization: clean metadata, deflate streams, garbage collection
doc.save(
    output_file,
    garbage=4,        # Maximum garbage collection
    deflate=True,     # Compress streams
    clean=True        # Clean and sanitize content streams
)

if os.path.exists(output_file):
    curr_size = os.path.getsize(input_file) / (1024*1024)
    new_size = os.path.getsize(output_file) / (1024*1024)
    print(f"Original: {curr_size:.2f} MB")
    print(f"Compressed: {new_size:.2f} MB")
else:
    print("Failed to save.")
