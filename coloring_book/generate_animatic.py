import os
from dotenv import load_dotenv
from elevenlabs import generate, set_api_key, save
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, ColorClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import numpy as np

load_dotenv('../.env')
api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    print("Warning: ELEVENLABS_API_KEY not found in ../.env")

# Paths
script_dir = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(script_dir, "video_renders")
os.makedirs(out_dir, exist_ok=True)

ILLUST = os.path.join(script_dir, "illustrations")
logo_path = os.path.join(script_dir, "../nc_assets/img/logo.png")
cover_path = os.path.join(script_dir, "epic_cover_final.png")
pano_path = os.path.join(script_dir, "american_journey_v2.png")

vo_30s_script = """Two hundred and fifty years ago, they started something.
Rebels. Inventors. Soldiers. Everyday people who did extraordinary things.
We put the best of their stories in a coloring book. For all ages.
Download it free. We'll mail you a sticker just for signing up.
250Proud.net — the story isn't finished."""

# 1. Synthesize Audio
vo_30s_path = os.path.join(out_dir, "vo_30s.mp3")

if api_key and not os.path.exists(vo_30s_path):
    print("Synthesizing 30s VoiceOver...")
    try:
        set_api_key(api_key)
        audio = generate(
            text=vo_30s_script,
            voice="pNInz6obpgDQGcFmaJgB",
            model="eleven_multilingual_v2"
        )
        save(audio, vo_30s_path)
    except Exception as e:
        print(f"ElevenLabs error: {e}")

# PIL Helpers to bypass ImageMagick dependency in MoviePy
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
        except Exception as e:
            pass # fallback if logo fails
    else:
        # Multiline text block
        lines = text.split('\n')
        y_text = size[1]/2 - (len(lines)*font_size)/2
        for line in lines:
            bbox = d.textbbox((0,0), line, font=font)
            line_w = bbox[2]-bbox[0]
            d.text(((size[0]-line_w)/2, y_text), line, font=font, fill=color)
            y_text += font_size * 1.2
            
    # Paste onto a solid frame so ImageClip reads properly
    solid = Image.new('RGB', size, (10, 15, 30)) if not text.startswith("FREE") else Image.new('RGB', size, (0,0,0))
    if not is_logo and "FREE" not in text:
        return np.array(img)
    else:
        solid.paste(img, (0,0), img)
        return np.array(solid)

print("Assembling 30s Video...")
W, H = 1920, 1080

# 0:00 - 0:03 Logo String (Black)
logo_img = create_text_image("", size=(W,H), is_logo=True)
logo_clip = ImageClip(logo_img).set_duration(3).crossfadein(1).set_start(0)

# 0:03 - 0:10 Book Reveal (Cover)
try:
    c_img = Image.open(cover_path).resize((800, 800), Image.Resampling.LANCZOS)
    base_book = Image.new('RGB', (W, H), (10, 15, 30))
    base_book.paste(c_img, ((W-800)//2, (H-800)//2))
except:
    base_book = Image.new('RGB', (W, H), (10, 15, 30))

book_clip = ImageClip(np.array(base_book)).set_duration(7).set_start(3).crossfadein(1)

# 0:10 - 0:20 Paging Loop
pages = [
    os.path.join(ILLUST, "page_03.png"),
    os.path.join(ILLUST, "page_04.png"),
    os.path.join(ILLUST, "page_08.png"),
    os.path.join(ILLUST, "page_12.png"),
    os.path.join(ILLUST, "page_14.png"),
    os.path.join(ILLUST, "page_17.png"),
    pano_path
]
page_clips = []
start_t = 10.0
dur = 1.5
for idx, p in enumerate(pages):
    try:
        p_img = Image.open(p).convert("RGBA")
        if p_img.width > p_img.height:
            new_w = min(W, int(H * p_img.width / p_img.height))
            p_img = p_img.resize((new_w, H))
        else:
            p_img = p_img.resize((int(H * p_img.width / p_img.height), H))
        bg = Image.new('RGB', (W,H), (10, 15, 30))
        bg.paste(p_img, ((W-p_img.width)//2, (H-p_img.height)//2), mask=p_img if p_img.mode=="RGBA" else None)
        pc = ImageClip(np.array(bg)).set_duration(dur).set_start(start_t)
        if idx > 0:
            pc = pc.crossfadein(0.2)
        page_clips.append(pc)
    except:
        pass
    start_t += dur

# 0:20 - 0:30 CTA
cta_text = "FREE Download\n250 Strong — Built By Hand\nPlus a FREE 250Proud Sticker\n250Proud.net"
cta_img = create_text_image(cta_text, color=(201,168,76))
cta_clip = ImageClip(cta_img).set_duration(10).set_start(20).crossfadein(1)

# Compile Video
final_video = CompositeVideoClip([logo_clip, book_clip] + page_clips + [cta_clip], size=(W,H)).set_duration(30)

# Attach Audio if exists
if os.path.exists(vo_30s_path):
    audio = AudioFileClip(vo_30s_path)
    final_video = final_video.set_audio(audio)

final_video.write_videofile(os.path.join(out_dir, "250proud_coloring_30s_animatic.mp4"), fps=24, logger=None)
print("✅ Done rendering 30s Animatic.")
