import os
import numpy as np
from PIL import Image

def process_neon(in_path, out_path):
    # Pure Unmultiply math for Neon Glow Extraction on Black Backgrounds! 
    # Extracting glow: RGB = physical_color * alpha. So TrueColor = RGB / alpha.
    # The max luminance of RGB strictly mirrors the raw alpha scalar.
    img = Image.open(in_path).convert("RGB")
    arr = np.array(img).astype(float)
    
    # Isolate master luminance array
    alpha = np.max(arr, axis=2)
    
    # Division un-multiply matrix to recover true radiating pixel color geometry
    with np.errstate(divide='ignore', invalid='ignore'):
        out_r = (arr[:,:,0] / alpha) * 255
        out_g = (arr[:,:,1] / alpha) * 255
        out_b = (arr[:,:,2] / alpha) * 255
        
    out_r = np.nan_to_num(out_r)
    out_g = np.nan_to_num(out_g)
    out_b = np.nan_to_num(out_b)
    
    out_img = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
    out_img[:,:,0] = np.clip(out_r, 0, 255)
    out_img[:,:,1] = np.clip(out_g, 0, 255)
    out_img[:,:,2] = np.clip(out_b, 0, 255)
    
    # Inject slight gamma expansion to prevent structural glow collapse on dark physical ink substrates
    alpha_strong = np.clip((alpha / 255.0) ** 0.8 * 255, 0, 255)
    out_img[:,:,3] = alpha_strong.astype(np.uint8)
    
    final = Image.fromarray(out_img)
    
    # Bound structural perimeter tightly 
    final = final.crop(final.getbbox())
    
    # Size exclusively for front-panel 1200px hat frameworks
    sc = 1150 / max(final.size[0], final.size[1])
    final = final.resize((int(final.size[0]*sc), int(final.size[1]*sc)), Image.Resampling.LANCZOS)
    
    canvas = Image.new('RGBA', (1200,1200), (0,0,0,0))
    px = (1200 - final.size[0]) // 2
    py = (1200 - final.size[1]) // 2
    canvas.paste(final, (px, py), final)
    canvas.save(out_path, "PNG", dpi=(300,300))
    print(f"Neon glow structural vector isolated: {out_path}")

def process_delta(in_path, out_dir):
    img = Image.open(in_path).convert("L")
    arr = np.array(img)
    
    def save_variant(color_name, fill_rgb):
        out = np.zeros((arr.shape[0], arr.shape[1], 4), dtype=np.uint8)
        out[:,:,0] = fill_rgb[0]
        out[:,:,1] = fill_rgb[1]
        out[:,:,2] = fill_rgb[2]
        
        # Aggressive alpha clip to force crisp edge topology bypassing semi-transparent ghosting
        alpha = np.clip((arr.astype(float) - 50) / 100.0 * 255, 0, 255)
        out[:,:,3] = alpha.astype(np.uint8)
        
        final = Image.fromarray(out)
        final = final.crop(final.getbbox())
        
        sc = 1150 / max(final.size[0], final.size[1])
        final = final.resize((int(final.size[0]*sc), int(final.size[1]*sc)), Image.Resampling.LANCZOS)
        
        canvas = Image.new('RGBA', (1200,1200), (0,0,0,0))
        px = (1200 - final.size[0]) // 2
        py = (1200 - final.size[1]) // 2
        canvas.paste(final, (px, py), final)
        
        out_path = os.path.join(out_dir, f"Hat_Graphic_Delta_Dad_Hat_{color_name}_1200x1200.png")
        canvas.save(out_path, "PNG", dpi=(300,300))
        print(f"Flat minimal delta isolated natively: {out_path}")
        
    save_variant("Light", (245, 245, 245)) # Pure crisp white logic meant for dark substrates
    save_variant("Dark", (20, 25, 30))     # Technical navy drafted logic meant for light substrates

if __name__ == "__main__":
    neon_raw = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/route_66_neon_raw_1774637812305.png"
    delta_raw = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/250_delta_minimalist_raw_1774637825129.png"
    out_dir = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Brand_Assets/Headwear"
    os.makedirs(out_dir, exist_ok=True)
    
    process_neon(neon_raw, os.path.join(out_dir, "Hat_Graphic_Route_66_Neon_1200x1200.png"))
    process_delta(delta_raw, out_dir)
