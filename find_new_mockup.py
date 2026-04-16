import os
import glob

def find_newest():
    print("Scanning for newest media artifacts...")
    brain_dir = "/Users/michaelprice/.gemini/antigravity/brain/16710064-4f21-4c93-a195-f96bfd146cc3/*"
    files = glob.glob(brain_dir)
    # Filter for png and jpg
    img_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    img_files.sort(key=os.path.getmtime, reverse=True)
    
    for f in img_files[:5]:
        print(f"Found artifact: {f} (Time: {os.path.getmtime(f)})")

if __name__ == "__main__":
    find_newest()
