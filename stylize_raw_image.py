import cv2
import numpy as np
import os

def process_raw_stylize():
    raw_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1774374574741.png"
    img = cv2.imread(raw_path, cv2.IMREAD_COLOR)
    
    if img is None:
        print("Error reading the image.")
        return
        
    rows, cols = img.shape[:2]
    
    # 1. Cinematic Radial Vignette (Heavy studio spotlight effect)
    # This functionally solves the "cut off edges" by plunging the left and right borders deeply into studio shadow
    kernel_x = cv2.getGaussianKernel(cols, cols / 2.5) # Wider beam
    kernel_y = cv2.getGaussianKernel(rows, rows / 2.5)
    kernel = kernel_y * kernel_x.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    
    vignetted = np.copy(img)
    for i in range(3):
        vignetted[:,:,i] = vignetted[:,:,i] * mask * 1.5 # Boost center brightness to compensate
        
    # Cap values strictly to visual constraints 
    vignetted = np.clip(vignetted, 0, 255).astype(np.uint8)
    
    # 2. Organic Streetwear Film Grain (Adding physical luxury texture)
    noise = np.random.normal(0, 10, img.shape).astype(np.float32)
    noisy_img = cv2.addWeighted(vignetted.astype(np.float32), 0.95, noise, 0.05, 0)
    
    # 3. High-End Brutalist Color Grade (Cool shadows, high contrast)
    b, g, r = cv2.split(noisy_img)
    
    r = cv2.add(r, -15) # Pull heat out of shadows
    b = cv2.add(b, 10)  # Inject cool studio slate tones 
    
    graded = cv2.merge((b, g, r))
    graded = np.clip(graded, 0, 255).astype(np.uint8)
    
    # Export permanently to the Master Render line
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Mockups/Editorial_Hero_Mockups"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Cinematic_Supplier_Apollo_Eagle.jpg")
    
    cv2.imwrite(out_path, graded)
    print(f"Brutalist Color Grading Process strictly mapping to native bounds finished: {out_path}")

if __name__ == "__main__":
    process_raw_stylize()
