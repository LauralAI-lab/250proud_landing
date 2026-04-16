import os
from PIL import Image, ImageFilter

sticker_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1774115768499.jpg"
truck_path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/silverado_window_fixed_1774116190681.png"
output_path = "/Users/michaelprice/Desktop/lauralai/250proud_landing/RAM_Sticker_Mockup.png"

print("Loading assets...")
sticker = Image.open(sticker_path).convert("RGBA")
truck = Image.open(truck_path).convert("RGBA")

# 1. Remove black background from sticker
pixels = sticker.load()
w, h = sticker.size
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if r < 20 and g < 20 and b < 20:
            pixels[x, y] = (0, 0, 0, 0)
            
# Autocrop transparent borders
bbox = sticker.getbbox()
sticker = sticker.crop(bbox)

# 2. Resize sticker for the truck window (4 inches is quite small on a large truck window)
truck_w, truck_h = truck.size
target_w = int(truck_w * 0.10) # Smaller, about 10% of truck width for a 4" sticker
ratio = target_w / sticker.width
target_h = int(sticker.height * ratio)
sticker = sticker.resize((target_w, target_h), Image.Resampling.LANCZOS)

# 3. Add a slight drop shadow to make it look real on glass (Zero rotation to keep it perfectly straight)
sticker = sticker.rotate(0, expand=True, resample=Image.Resampling.BICUBIC)

shadow = sticker.copy()
shadow_pixels = shadow.load()
for y in range(shadow.height):
    for x in range(shadow.width):
        if shadow_pixels[x,y][3] > 0:
            shadow_pixels[x,y] = (0, 0, 0, 150)
shadow = shadow.filter(ImageFilter.GaussianBlur(1.5))

composite_layer = Image.new("RGBA", truck.size, (0,0,0,0))

# Postion: Bottom left of the back window. The glass area is approx y=150 to 480.
# Bringing the sticker up (y=0.32) and in (x=0.15) guarantees it sits perfectly on the glass.
paste_x = int(truck_w * 0.18)
paste_y = int(truck_h * 0.32)

composite_layer.paste(shadow, (paste_x + 2, paste_y + 2), shadow)
composite_layer.paste(sticker, (paste_x, paste_y), sticker)

# 4. Mix the layers (multiply or alpha composite)
final = Image.alpha_composite(truck, composite_layer)

print(f"Saving mockup to {output_path}")
final.convert("RGB").save(output_path, "PNG")

