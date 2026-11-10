import os
import cv2
import numpy as np
import subprocess
import asyncio
import urllib.request
import edge_tts

# -------------------------------------------------------------
# 1. EXACT @HIDDENWHYPROJECT NARRATIVE STORYBOARD
# -------------------------------------------------------------
HIDDEN_WHY_SCENES = [
    {
        "id": "scene1_awakening",
        "title": "THE FROZEN AWAKENING",
        "sub": "TASAWWUR KAREIN AAP 20,000 SAAL PEHLE JAAGTE HAIN...",
        "text": "تصور کریں، اگر آپ اچانک بیس ہزار سال پیچھے برفانی دور میں آنکھ کھولیں! سب سے پہلی چیز جو آپ کو محسوس ہوگی وہ سردی نہیں... بلکہ ایک خوفناک خاموشی ہوگی۔",
        "image_url": "https://images.unsplash.com/photo-1517411032315-54ef2cb783bb?w=1920&q=80"  # Dramatic Ice Blizzard Mountain
    },
    {
        "id": "scene2_mammoth",
        "title": "GIANTS OF THE ICE AGE",
        "sub": "YEH DUNIYA KHOONKHAAR JANWARON KI THI",
        "text": "یہاں درجہ حرارت منفی تیس ڈگری ہے، اور افق پر آپ کو دیوہیکل میمتھ اور خطرناک شکاری جانوروں کے سائے نظر آتے ہیں۔",
        "image_url": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1920&q=80"  # Epic Cold Glacial Wilderness
    },
    {
        "id": "scene3_fire_cave",
        "title": "THE ONLY HOPE: FIRE",
        "sub": "AAG HI ZINDAGI AUR MAUT KA FAISLA THI",
        "text": "نہ کوئی موبائل، نہ ہسپتال، نہ ماڈرن کپڑے۔ آپ کی واحد امید دور کسی غار میں جلتی ہوئی وہ آگ ہے جہاں قدیم قبائلی انسان جمع ہیں۔",
        "image_url": "https://images.unsplash.com/photo-1499244571948-7ccddb3583f1?w=1920&q=80"  # Primal Campfire in Dark Cave
    },
    {
        "id": "scene4_survival",
        "title": "SURVIVING THE FIRST NIGHT",
        "sub": "AGAR AAP NE PEHLI RAAT GUZAAR LI...",
        "text": "اگر آپ ان سے دوستی کر سکے تو بچ جائیں گے، ورنہ یہ وحشی رات آپ کو ہمیشہ کے لیے جما دے گی۔",
        "image_url": "https://images.unsplash.com/photo-1509114397022-ed747cca3f65?w=1920&q=80"  # Dark Mysterious Foggy Forest
    },
    {
        "id": "scene5_stars_destiny",
        "title": "THE ROOT OF HUMANITY",
        "sub": "HUMARE BAAP DADA IS KHOFNAK DOUR SE GUZRE THAY",
        "text": "ہمارے آباؤ اجداد اس کٹھن دور میں زندہ رہے، اسی لیے آج ہم اور آپ یہاں موجود ہیں!",
        "image_url": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=1920&q=80"  # Majestic Primal Starry Cosmos
    }
]

# Deep, serious, mysterious narrator voice
VOICE_NAME = "ur-PK-AsadNeural"

# -------------------------------------------------------------
# 2. AUDIO & ATMOSPHERIC SOUND DESIGN
# -------------------------------------------------------------
async def record_narration(text: str, out_path: str):
    # -4% rate and -2Hz pitch for that deep documentary suspense
    comm = edge_tts.Communicate(text, VOICE_NAME, rate="-4%", pitch="-2Hz")
    await comm.save(out_path)

def get_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        return float(subprocess.check_output(cmd).strip())
    except Exception:
        return 11.0

def download_image(url: str, dest_path: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, "wb") as f:
        f.write(response.read())

def create_hidden_why_soundtrack(duration_sec: float, dest_path: str):
    """Deep tense sub-bass drone + howling icy wind tension"""
    sample_rate = 44100
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    
    # 1. Dark sub-drone (Low C# / G# tension)
    drone = (
        0.28 * np.sin(2 * np.pi * 48.99 * t) +
        0.22 * np.sin(2 * np.pi * 73.42 * t) +
        0.14 * np.sin(2 * np.pi * 110.0 * t)
    )
    drone *= (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t))
    
    # 2. Wind turbulence / howling noise
    np.random.seed(101)
    noise = np.random.uniform(-0.06, 0.06, size=len(t))
    wind_mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)
    wind = noise * wind_mod

    # 3. Slow dramatic heartbeat pulse every 2.4 seconds
    heartbeat = np.zeros_like(t)
    for hb in np.arange(1.0, duration_sec, 2.4):
        mask = (t >= hb) & (t < hb + 0.3)
        dt = t[mask] - hb
        heartbeat[mask] += 0.22 * np.sin(2 * np.pi * 60.0 * dt) * np.exp(-dt * 14.0)

    score = drone + wind + heartbeat
    score = score / (np.max(np.abs(score)) + 1e-6) * 0.22
    pcm = (score * 32767).astype(np.int16)

    raw_path = dest_path + ".raw"
    pcm.tofile(raw_path)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", raw_path, dest_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# -------------------------------------------------------------
# 3. @HIDDENWHY CINEMATIC VISUAL FRAME GENERATOR
# -------------------------------------------------------------
def build_hidden_why_slide(img_path: str, title: str, sub: str, duration: float, out_path: str):
    img = cv2.imread(img_path)
    if img is None:
        img = np.full((1080, 1920, 3), (25, 18, 14), dtype=np.uint8)
    else:
        h, w = img.shape[:2]
        scale = max(1920 / w, 1080 / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        start_x = (new_w - 1920) // 2
        start_y = (new_h - 1080) // 2
        img = img[start_y:start_y + 1080, start_x:start_x + 1920]

    # --- Dramatic Cinematic Color Grade (Warm Highlights, Cold Shadows) ---
    img = cv2.convertScaleAbs(img, alpha=1.08, beta=5)

    # --- Cinematic Dark Vignette & Letterbox ---
    overlay = img.copy()
    # Bottom banner for title and sub
    cv2.rectangle(overlay, (0, 890), (1920, 1080), (0, 0, 0), -1)
    # Top cinematic film bar
    cv2.rectangle(overlay, (0, 0), (1920, 75), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.72, img, 0.28, 0, img)

    # Glowing Red/Amber Accent Indicator (Hidden Why signature look)
    cv2.rectangle(img, (90, 915), (96, 1045), (0, 130, 255), -1)  # Amber-orange bar

    # Clean Typography (Modern Sans-Serif + Glowing Subtitles)
    cv2.putText(img, title, (115, 960), cv2.FONT_HERSHEY_DUPLEX, 1.25, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, sub, (115, 1015), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 215, 255), 2, cv2.LINE_AA)

    temp_slide = out_path + ".jpg"
    cv2.imwrite(temp_slide, img, [cv2.IMWRITE_JPEG_QUALITY, 96])

    # Smooth crossfade in and out (Zero Jitter, Absolute Rock Solid 1080p)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", temp_slide,
        "-t", str(duration),
        "-vf", "fade=t=in:st=0:d=0.7,fade=t=out:st=" + str(max(0.1, duration - 0.7)) + ":d=0.7",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# -------------------------------------------------------------
# 4. MASTER BUILD PIPELINE
# -------------------------------------------------------------
def build_hidden_why_video():
    print("=" * 65)
    print("🎬 MASTER PRODUCTION: @HIDDENWHYPROJECT STYLE VIDEO")
    print("=" * 65)

    work_dir = "output"
    os.makedirs(work_dir, exist_ok=True)

    rendered_scenes = []
    total_duration = 0.0

    for idx, sc in enumerate(HIDDEN_WHY_SCENES):
        print(f"\n⚡ Scene {idx+1}/{len(HIDDEN_WHY_SCENES)}: {sc['title']}")
        img_file = os.path.join(work_dir, f"{sc['id']}.jpg")
        voice_file = os.path.join(work_dir, f"{sc['id']}_voice.mp3")
        scene_video = os.path.join(work_dir, f"{sc['id']}_video.mp4")
        scene_final = os.path.join(work_dir, f"{sc['id']}_final.mp4")

        # 1. Download Epic Scene Concept Art
        print(f"📥 Downloading Cinematic Visual...")
        download_image(sc["image_url"], img_file)

        # 2. Record Narration
        print(f"🎙️ Recording Deep Dramatic Narration...")
        asyncio.run(record_narration(sc["text"], voice_file))
        dur = get_duration(voice_file) + 1.2
        total_duration += dur
        print(f"⏱️ Duration: {dur:.1f}s")

        # 3. Build Slide Video
        print(f"🎞️ Generating 1080p Film Slide with Letterbox...")
        build_hidden_why_slide(img_file, sc["title"], sc["sub"], dur, scene_video)

        # 4. Merge Scene
        cmd_merge = [
            "ffmpeg", "-y",
            "-i", scene_video,
            "-i", voice_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            scene_final
        ]
        subprocess.run(cmd_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rendered_scenes.append(scene_final)

    # 5. Stitch Scenes
    print("\n🎞️ Stitching Full 1-Minute Timeline...")
    concat_txt = os.path.join(work_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        for rf in rendered_scenes:
            f.write(f"file '{os.path.abspath(rf)}'\n")

    video_only = os.path.join(work_dir, "video_stitched.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        video_only
    ], check=True)

    # 6. Add Deep Ambient Tense Score
    bgm_path = os.path.join(work_dir, "hidden_why_bgm.wav")
    print("🎵 Mastering Deep Ambient Tension Soundtrack...")
    create_hidden_why_soundtrack(total_duration + 2.0, bgm_path)

    final_output = os.path.join(work_dir, "final_video.mp4")
    cmd_master = [
        "ffmpeg", "-y",
        "-i", video_only,
        "-i", bgm_path,
        "-filter_complex",
        "[0:a]volume=1.0[voice];[1:a]volume=0.20[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd_master, check=True)

    mb = os.path.getsize(final_output) / (1024 * 1024)
    print("=" * 65)
    print(f"🎉 @HIDDENWHY STYLE VIDEO READY: {final_output} ({mb:.2f} MB)")
    print("=" * 65)

if __name__ == "__main__":
    build_hidden_why_video()