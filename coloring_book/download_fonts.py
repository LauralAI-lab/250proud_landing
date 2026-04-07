import os
import urllib.request

font_urls = {
    "OpenSans-Regular.ttf": "https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-Regular.ttf",
    "OpenSans-Bold.ttf": "https://github.com/googlefonts/opensans/raw/main/fonts/ttf/OpenSans-Bold.ttf",
    "RobotoSlab-Regular.ttf": "https://github.com/googlefonts/robotoslab/raw/main/fonts/ttf/RobotoSlab-Regular.ttf",
    "RobotoSlab-Bold.ttf": "https://github.com/googlefonts/robotoslab/raw/main/fonts/ttf/RobotoSlab-Bold.ttf"
}

os.makedirs("fonts", exist_ok=True)

for name, url in font_urls.items():
    dest = os.path.join("fonts", name)
    if not os.path.exists(dest):
        print(f"Downloading {name}...")
        try:
            urllib.request.urlretrieve(url, dest)
            print(f"Saved {dest}")
        except Exception as e:
            print(f"Failed to download {name}: {e}")
    else:
        print(f"{name} already exists.")
