import cv2
import numpy as np
from PIL import Image

def fix_kerning(input_path, output_path):
    print(f"Fixing Kerning on {input_path}")
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    
    # We know the image is 4500x5400
    h, w = img.shape[:2]
    mid_x = w // 2
    
    # We want to isolate the text. The text is at the top.
    # Let's find the bottom of the text by scanning from the top down.
    # Actually, we can just grab the top ~900 pixels.
    # To be perfectly safe and not cut the rope, let's find the bounding box of the top text.
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV) # Dark pixels are 255
    
    # Find all connected components
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Collect all contours that form the top wordmark.
    # The text is roughly in the top 20% of the image.
    text_contours = []
    max_y_of_text = 0
    
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if y < h * 0.22: # Top 22%
            # Check if it's a large enough shape to be a letter (avoid random noise)
            if cw > 20 and ch > 20: 
                # If it's part of the text, let's track the maximum Y
                # Wait, the rope itself might reach into the top 20% in the exact center!
                pass
                
    # A much simpler and safer approach: The user wants to close the gap.
    # The gap is perfectly in the center (mid_x).
    # Since it's a white background, we can literally copy the bounding box of "250" and move it right.
    # Let's define the region: x from 0 to mid_x-50, y from 0 to 1000.
    # And right region: x from mid_x+50 to w, y from 0 to 1000.
    # We will shift the left region RIGHT by 120 pixels, and the right region LEFT by 120 pixels.
    
    # We must ensure we don't accidentally grab the rope. Let's trace carefully.
    # From the screenshot, the text is clearly separated by a large white space above the rope.
    # We will just shift the pixels that are above the rope.
    # How to find the rope top edge? Scanning down the exact center column (mid_x).
    rope_top_y = 0
    for y_coord in range(100, h):
        if gray[y_coord, mid_x] < 200: # Found a dark pixel
            rope_top_y = y_coord
            break
            
    print(f"Detected rope top at Y={rope_top_y}")
    
    # The text must be strictly above the rope.
    # The gap between '0' and 'P' is right at the middle.
    shift_amount = 140 # pixels to shift inwards
    
    # Create a mask of the text we want to shift.
    # Left text: everything dark above rope_top_y - 50, and left of mid_x
    # Right text: everything dark above rope_top_y - 50, and right of mid_x
    
    y_cut = rope_top_y - 30 # Safe buffer above the rope
    
    # We don't want to just shift the whole rectangle, because it's an arch.
    # If we shift horizontally, it might look slightly wider. That's fine.
    
    new_img = img.copy()
    
    # Erase the current text area with pure white
    new_img[0:y_cut, 0:w] = [255, 255, 255, 255] if img.shape[2] == 4 else [255, 255, 255]
    
    # Grab the left text pixels
    left_chunk = img[0:y_cut, 0:mid_x]
    # Paste to new image, shifted right
    new_img[0:y_cut, shift_amount:mid_x+shift_amount] = np.where(left_chunk < 240, left_chunk, new_img[0:y_cut, shift_amount:mid_x+shift_amount])
    
    # Grab the right text pixels
    right_chunk = img[0:y_cut, mid_x:w]
    # Paste to new image, shifted left
    new_img[0:y_cut, mid_x-shift_amount:w-shift_amount] = np.where(right_chunk < 240, right_chunk, new_img[0:y_cut, mid_x-shift_amount:w-shift_amount])
    
    cv2.imwrite(output_path, new_img)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    tee_input = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America/GulfOfAmerica_Tee_v2_CorrectText_RAW_WHITE_4500x5400.png"
    
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/Regional_Collection/Gulf_Of_America"
    
    fix_kerning(tee_input, f"{out_dir}/GulfOfAmerica_Tee_v2_CorrectedKerning_RAW_WHITE_4500x5400.png")

