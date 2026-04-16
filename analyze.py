from PIL import Image

path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1774038290937.png"
img = Image.open(path).convert("RGBA")

pixels = img.load()
width, height = img.size
print(f"Size: {width}x{height}")

# Sample corners (usually background)
print(f"Top-Left corner: {pixels[0,0]}")
print(f"Top-Right corner: {pixels[width-1,0]}")
print(f"Bottom-Left corner: {pixels[0,height-1]}")
print(f"Bottom-Right corner: {pixels[width-1,height-1]}")

# Sample center of eagle (approx)
print(f"Center (eagle body): {pixels[width//2, height//2]}")
