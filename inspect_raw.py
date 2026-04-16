import cv2

path = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/media__1774374574741.png"
img = cv2.imread(path)

print(f"Scanning geometry for: {path}")
if img is not None:
    print(f"Raw Physical Array Size: {img.shape}")
else:
    print("Failed to read image")
