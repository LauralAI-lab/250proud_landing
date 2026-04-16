from PIL import Image

def scan():
    path = "/Users/michaelprice/Library/CloudStorage/GoogleDrive-360podcast@gmail.com/My Drive/05_Production_and_Inventory/250PROUD/Print_Ready_Files/The_Blueprint_Collection/eagle_blueprint.png"
    img = Image.open(path)
    print(f"File: {path}")
    print(f"Size: {img.size}")
    print(f"Mode: {img.mode}")
    print(f"BBox: {img.getbbox()}")
    
    if img.mode == 'RGBA':
        alpha = img.split()[3]
        print(f"Alpha BBox: {alpha.getbbox()}")
        
scan()
