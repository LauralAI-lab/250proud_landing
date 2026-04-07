import os
from dotenv import load_dotenv
from elevenlabs import generate, set_api_key, save
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np

load_dotenv('../.env')
api_key = os.getenv("ELEVENLABS_API_KEY")

script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "video_renders")
os.makedirs(out_dir, exist_ok=True)

ILLUST = os.path.join(script_dir, "illustrations")
logo_path = os.path.join(script_dir, "../nc_assets/img/logo.png")
cover_path = os.path.join(script_dir, "epic_cover_final.png")
pano_path = os.path.join(script_dir, "american_journey_v2.png")

vo_15s_script = """A coloring book full of ordinary people who built America.
Free to download. Free sticker when you join.
Get yours now at 250Proud.net."""

vo_15s_path = os.path.join(out_dir, "vo_15s.mp3")

if api_key and not os.path.exists(vo_15s_path):
    try:
        set_api_key(api_key)
        audio = generate(text=vo_15s_script, voice="pNInz6obpgDQGcFmaJgB", model="eleven_multilingual_v2")
        save(audio, vo_15s_path)
    except Exception as e:
        pass

def create_text_image(text, size=(1920, 1080), font_size=80, color=(255, 255, 255), is_logo=False):
    img = Image.new('RGBA', size, (0,0,0,0))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", font_size)
    except:
        font = ImageFont.load_default()
    if is_logo:
        try:
            L = Image.open(logo_path).convert("RGBA")
            lw = int(size[0]*0.4)
            lh = int(lw * L.height / L.width)
            L = L.resize((lw, lh), Image.Resampling.LANCZOS)
            img.paste(L, ((size[0]-lw)//2, (size[1]-lh)//2), L)
        except Exception:
            pass
    else:
        lines = text.split('\n')
        y_text = size[1]/2 - (len(lines)*font_size)/2
        for line in lines:
            bbox = d.textbbox((0,0), line, font=font)
            line_w = bbox[2]-bbox[0]
            d.text(((size[0]-line_w)/2, y_text), line, font=font, fill=color)
            y_text += font_size * 1.2
            
    solid = Image.new('RGB', size, (10, 15, 30)) if not text.startswith("FREE") else Image.new('RGB', size, (0,0,0))
    if not is_logo and "FREE" not in text:
        return np.array(img)
    else:
        solid.paste(img, (0,0), img)
        return np.array(solid)

W, H = 1920, 1080
logo_img = create_text_image("", size=(W,H), is_logo=True)
logo_clip = ImageClip(logo_img).set_duration(1.5).crossfadein(0.5).set_start(0)

try:
    c_img = Image.open(cover_path).resize((800, 800), Image.Resampling.LANCZOS)
    base_book = Image.new('RGB', (W, H), (10, 15, 30))
    base_book.paste(c_img, ((W-800)//2, (H-800)//2))
except:
    base_book = Image.new('RGB', (W, H), (10, 15, 30))

book_clip = ImageClip(np.array(base_book)).set_duration(3.5).set_start(1.5).crossfadein(0.5)

pages = [
    os.path.join(ILLUST, "page_03.png"),
    os.path.join(ILLUST, "page_04.png"),
    os.path.join(ILLUST, "page_12.png"),
    os.path.join(ILLUST, "page_17.png")
]
page_clips = []
start_t = 5.0
dur = 1.0
for idx, p in enumerate(pages):
    try:
        p_img = Image.open(p).convert("RGBA")
        new_w = min(W, int(H * p_img.width / p_img.height)) if p_img.width > p_img.height else int(H * p_img.width / p_img.height)
        p_img = p_img.resize((new_w, H))
        bg = Image.new('RGB', (W,H), (10, 15, 30))
        bg.paste(p_img, ((W-p_img.width)//2, (H-p_img.height)//2), mask=p_img if p_img.mode=="RGBA" else None)
        pc = ImageClip(np.array(bg)).set_duration(dur).set_start(start_t)
        if idx > 0:
            pc = pc.crossfadein(0.2)
        page_clips.append(pc)
    except:
        pass
    start_t += dur

cta_text = "FREE Download\n250 Strong — Built By Hand\n250Proud.net"
cta_img = create_text_image(cta_text, color=(201,168,76))
cta_clip = ImageClip(cta_img).set_duration(6).set_start(9).crossfadein(0.5)

final_video = CompositeVideoClip([logo_clip, book_clip] + page_clips + [cta_clip], size=(W,H)).set_duration(15)

if os.path.exists(vo_15s_path):
    audio = AudioFileClip(vo_15s_path)
    final_video = final_video.set_audio(audio)

final_video.write_videofile(os.path.join(out_dir, "250proud_coloring_15s_animatic.mp4"), fps=24, logger=None)
print("✅ Done rendering 15s Animatic.")
