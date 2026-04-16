import cv2
import numpy as np
import os
import glob

def simplify_coloring_book_image(input_path, output_path):
    # Read in grayscale to remove ALL color fill
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Failed to read {input_path}")
        return
    
    # 1. Blur to eliminate fine details and shading (adjust kernel size to control detail reduction)
    # A bilateral filter preserves strong edges while aggressively blurring out textures/shading inside areas
    blurred = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
    
    # Additional median blur to wipe out small noisy details
    blurred = cv2.medianBlur(blurred, 7)
    
    # 2. Adaptive thresholding extracts the bold outlines while ignoring gradient shading
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=21, C=10
    )
    
    # 3. Morphological operations to clean up remaining noise and make the lines bold
    kernel_clean = np.ones((2, 2), np.uint8)
    
    # Removing small black dots (noise) in the white white areas
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_clean, iterations=1)
    
    # Thicken the main black outlines (since black is 0, eroding the white dilates the black)
    thick_kernel = np.ones((2, 2), np.uint8)
    final_img = cv2.erode(cleaned, thick_kernel, iterations=1)
    
    cv2.imwrite(output_path, final_img)
    print(f"Processed into low-detail line art: {output_path}")

def main():
    # Looks for any RAW images in the current directory and processes them
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, "Simplified_LineArt")
    os.makedirs(out_dir, exist_ok=True)
    
    # Process anything matching standard extensions we want to convert
    images = glob.glob(os.path.join(script_dir, "*.png"))
    
    if not images:
        print("No PNG images found to process.")
        return
        
    for file in images:
        filename = os.path.basename(file)
        # Skip previously processed files if they exist in the same directory pattern
        if "simplified" in filename.lower():
            continue
            
        out_path = os.path.join(out_dir, filename.replace(".png", "_simplified.png"))
        simplify_coloring_book_image(file, out_path)

if __name__ == "__main__":
    main()
