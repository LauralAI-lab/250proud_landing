import sys
from rembg import remove
from PIL import Image

def create_premium_mockup():
    print("Loading Original CFK Mockup and AI Background...")
    input_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1774045560273.png"
    bg_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/premium_podium_bg_1774045826921.png"
    output_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/nc_assets/img/mockup_snapback.png"

    # Remove the generic white background from CFK mockup
    raw_hat = Image.open(input_path).convert("RGBA")
    print("Running neural background removal...")
    transparent_hat = remove(raw_hat)

    # Automatically crop the transparent hat to its bounding box
    bbox = transparent_hat.getbbox()
    transparent_hat = transparent_hat.crop(bbox)
    
    # Load premium dark background
    bg = Image.open(bg_path).convert("RGBA")
    bg_w, bg_h = bg.size
    
    # Resize hat to fit well on the pedestal (make it take up ~60% of the background width)
    target_width = int(bg_w * 0.6)
    ratio = target_width / transparent_hat.width
    target_height = int(transparent_hat.height * ratio)
    hat_resized = transparent_hat.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Coordinates to center the hat over the pedestal
    # The podium is approximately in the bottom 40-70% of the image. 
    # Center X:
    paste_x = (bg_w - target_width) // 2
    # Paste Y: center vertically but drop it down a bit to sit on the pedestal
    paste_y = (bg_h - target_height) // 2 + int(bg_h * 0.05)
    
    print("Compositing...")
    bg.paste(hat_resized, (paste_x, paste_y), hat_resized)
    
    # Save the new professional mockup in the assets folder directly
    # Replacing the old placeholder snapback so the website updates instantly.
    bg.convert("RGB").save(output_path, "PNG")
    print(f"Premium mockup saved to {output_path}")

if __name__ == "__main__":
    create_premium_mockup()
