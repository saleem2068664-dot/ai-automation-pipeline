import os
import cv2
import numpy as np
import subprocess
import asyncio
import urllib.request
import edge_tts
import replicate

# -------------------------------------------------------------
# 1. THE ICE AGE SURVIVAL SCRIPT & FLUX AI PROMPTS
# -------------------------------------------------------------
DOC_SCRIPT = (
    "تصور کریں، اگر آپ اچانک بیس ہزار سال پیچھے برفانی دور میں آنکھ کھولیں! "
    "سب سے پہلی چیز جو آپ کو محسوس ہوگی وہ شدید ٹھنڈ نہیں... بلکہ ایک پراسرار خاموشی ہوگی۔ "
    "یہاں درجہ حرارت منفی تیس ڈگری ہے، اور زمین پر میلوں دور تک صرف برف کی چادر پھیلی ہے۔ "
    "دور افق پر آپ کو دیوہیکل میمتھ اور خونخوار شکاری جانوروں کے سائے نظر آتے ہیں۔ "
    "نہ کوئی موبائل، نہ ہسپتال، نہ ماڈرن کپڑے۔ آپ کی واحد امید دور کسی غار میں جلتی ہوئی وہ آگ ہے! "
    "جہاں قدیم قبائلی انسان پتھر کے ہتھیار لیے جمع ہیں۔ "
    "اگر آپ نے ان سے دوستی کر لی تو بچ جائیں گے، ورنہ یہ وحشی رات آپ کو ہمیشہ کے لیے جما دے گی۔ "
    "ہمارے آباؤ اجداد اس کٹھن دور میں زندہ رہے، اسی لیے آج ہم اور آپ یہاں موجود ہیں!"
)

# Har scene ke liye FLUX AI 4K Photorealistic Prompts (100% Script Matched)
AI_SCENES = [
    {
        "title": "THE FROZEN AWAKENING",
        "sub": "20,000 SAAL PEHLE KI BARFANI DUNIYA",
        "mode": "zoom_in",
        "prompt": "hyper-realistic 8k cinematic concept art, lone person waking up in a massive arctic snow blizzard, frozen eyelashes, dramatic lighting, national geographic 4k"
    },
    {
        "title": "DEADLY SILENCE",
        "sub": "KHOFNAK KHAMOSHI AUR SHADEED THAND",
        "mode": "zoom_out",
        "prompt": "extreme wide shot of colossal frozen glaciers and ice mountains 20000 bc ice age, eerie atmospheric fog, volumetric winter sunlight, highly detailed 8k"
    },
    {
        "title": "SUB-ZERO REALITY",
        "sub": "DARJA-E-HARARAT MANFI 30 DEGREES",
        "mode": "zoom_in",
        "prompt": "close up of frozen frost crystals forming on ancient rocks in blizzard, sub-zero harsh winter wasteland, cinematic photography 8k"
    },
    {
        "title": "THE WOOLLY MAMMOTH",
        "sub": "DIWA-HAIKAL MAMMOTH AUR SHIKARI",
        "mode": "zoom_out",
        "prompt": "giant woolly mammoth with massive curved tusks walking through deep snow storm, hyper-realistic fur textures, epic cinematic composition 8k"
    },
    {
        "title": "TRACKS IN THE SNOW",
        "sub": "BARF MAIN GEHRE KHOJ",
        "mode": "zoom_in",
        "prompt": "deep animal and human footprints in fresh pristine white snow leading towards a dark cliff, atmospheric cold mist 8k"
    },
    {
        "title": "LOST IN PREHISTORY",
        "sub": "NA KOI MOBILE, NA KAPRE, NA MADAD",
        "mode": "zoom_out",
        "prompt": "a primitive survivalist shivering in heavy raw animal hides looking across a vast prehistoric mountain valley, hyper-realistic, dramatic moody lighting"
    },
    {
        "title": "THE CAVE ENTRANCE",
        "sub": "DOOR PAHAD KI GEHRI GHAAR",
        "mode": "zoom_in",
        "prompt": "exterior shot of an ancient stone cave entrance carved into high mountain cliff with faint warm orange glow inside, dark winter twilight 8k"
    },
    {
        "title": "THE PRIMAL FIRE",
        "sub": "ZINDAGI AUR MAUT KA FAISLA: AAG!",
        "mode": "zoom_out",
        "prompt": "close up of a roaring warm prehistoric campfire inside a dark cave, crackling amber sparks and glowing embers, hyper-realistic national geographic style 8k"
    },
    {
        "title": "ICE AGE CLAN",
        "sub": "PATTHAR KE HATHIYAR LIYE QADEEM INSAAN",
        "mode": "zoom_in",
        "prompt": "stone age paleolithic hunter gatherers holding stone spears gathered around cave fire, rugged intense faces, painted cave walls, photorealistic 8k"
    },
    {
        "title": "THE SURVIVAL NIGHT",
        "sub": "AGAR DOSTI HUI TO BACHENGE",
        "mode": "zoom_out",
        "prompt": "dramatic silhouettes of ancient hunters standing on a snowy mountain ridge under a fierce howling blizzard storm, cinematic depth of field 8k"
    },
    {
        "title": "DAWN OF HUMANITY",
        "sub": "HUMARE ABA-O-AJDAD NE YEH JANG JEETI",
        "mode": "zoom_in",
        "prompt": "majestic ancient starry cosmos and milky way sky shining bright over snow-capped mountains, dawn sun rising on the horizon, breathtaking cinematic 8k"
    }
]

VOICE_NAME = "ur-PK-AsadNeural"

# -------------------------------------------------------------
# 2. AUDIO & AUTO-WHOOSH SFX GENERATOR
# -------------------------------------------------------------
async def record_full_voice(text: str, out_path: str):
    print("🎙️ Recording Fast-Paced Suspenseful Urdu Narration...")
    comm = edge_tts.Communicate(text, VOICE_NAME, rate="-2%", pitch="-2Hz")
    await comm.save(out_path)

def get_audio_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        return float(subprocess.check_output(cmd).strip())
    except Exception:
        return 45.0

def build_pro_soundtrack(duration_sec: float, cut_timestamps: list, dest_path: str):
    sample_rate = 44100
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    
    drone = (
        0.28 * np.sin(2 * np.pi * 50.0 * t) +
        0.20 * np.sin(2 * np.pi * 75.0 * t) +
        0.14 * np.sin(2 * np.pi * 100.0 * t)
    )
    drone *= (0.7 + 0.3 * np.sin(2 * np.pi * 0.08 * t))
    np.random.seed(42)
    ambient_wind = np.random.uniform(-0.03, 0.03, size=len(t))
    total_audio = drone + ambient_wind

    whoosh_dur = 0.40
    w_len = int(sample_rate * whoosh_dur)
    w_t = np.linspace(0, whoosh_dur, w_len, endpoint=False)
    bell = (np.sin(np.pi * (w_t / whoosh_dur))) ** 2
    noise = np.random.uniform(-0.35, 0.35, size=w_len)
    sweep = np.sin(2 * np.pi * (260 - 160 * (w_t / whoosh_dur)) * w_t)
    whoosh_sfx = (noise * 0.65 + sweep * 0.35) * bell * 0.55

    for cut_t in cut_timestamps:
        start_idx = int((cut_t - 0.10) * sample_rate)
        end_idx = start_idx + w_len
        if start_idx >= 0 and end_idx < len(total_audio):
            total_audio[start_idx:end_idx] += whoosh_sfx

    total_audio = total_audio / (np.max(np.abs(total_audio)) + 1e-6) * 0.28
    pcm = (total_audio * 32767).astype(np.int16)
    
    raw_path = dest_path + ".raw"
    pcm.tofile(raw_path)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", raw_path, dest_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# -------------------------------------------------------------
# 3. REPLICATE FLUX AI IMAGE GENERATOR
# -------------------------------------------------------------
def generate_flux_image(prompt: str, dest_path: str):
    """Uses Replicate's high-speed FLUX.1-schnell model to create 100% custom 4K art"""
    try:
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "aspect_ratio": "16:9",
                "output_format": "jpg",
                "output_quality": 95
            }
        )
        # Output is a FileOutput / URL
        img_url = str(output[0])
        req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        print(f"✅ AI Image Generated Successfully: {dest_path}")
        return True
    except Exception as e:
        print(f"⚠️ Replicate error ({e}), creating atmospheric canvas...")
        canvas = np.zeros((1080, 1920, 3), dtype=np.uint8)
        grad = np.linspace(0, 1, 1080)[:, None]
        canvas[:, :, 0] = np.clip(35 + grad * 35, 0, 255).astype(np.uint8)
        canvas[:, :, 1] = np.clip(20 + grad * 25, 0, 255).astype(np.uint8)
        canvas[:, :, 2] = np.clip(15 + grad * 25, 0, 255).astype(np.uint8)
        cv2.imwrite(dest_path, canvas)
        return False

# -------------------------------------------------------------
# 4. CINEMATIC RENDERER WITH PARTICLES & BIG IMPACT TEXT
# -------------------------------------------------------------
def render_pro_scene_clip(img_path: str, title: str, sub: str, mode: str, duration: float, out_path: str, seed: int):
    img = cv2.imread(img_path)
    if img is None:
        img = np.full((1080, 1920, 3), (30, 20, 15), dtype=np.uint8)
    else:
        h, w = img.shape[:2]
        scale = max(1920 / w, 1080 / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        sx = (new_w - 1920) // 2
        sy = (new_h - 1080) // 2
        img = img[sy:sy + 1080, sx:sx + 1920]

    # Pre-render Big Bold Letterbox & Signature Typography
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 880), (1920, 1080), (0, 0, 0), -1)  # Bottom banner
    cv2.rectangle(overlay, (0, 0), (1920, 75), (0, 0, 0), -1)       # Top letterbox
    cv2.addWeighted(overlay, 0.72, img, 0.28, 0, img)

    # Signature Amber Accent Bar
    cv2.rectangle(img, (75, 905), (82, 1045), (0, 140, 255), -1)

    # Big Bold Impact Captions
    cv2.putText(img, title, (108, 955), cv2.FONT_HERSHEY_DUPLEX, 1.35, (0, 0, 0), 5, cv2.LINE_AA)
    cv2.putText(img, title, (105, 952), cv2.FONT_HERSHEY_DUPLEX, 1.35, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, sub, (108, 1018), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, sub, (105, 1015), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 215, 255), 2, cv2.LINE_AA)

    fps = 30
    total_frames = max(1, int(duration * fps))

    # Floating Snow/Embers Particles
    np.random.seed(seed)
    num_particles = 40
    particles = []
    for _ in range(num_particles):
        particles.append({
            "x": np.random.uniform(0, 1920),
            "y": np.random.uniform(0, 1080),
            "speed_y": np.random.uniform(1.2, 3.2),
            "speed_x": np.random.uniform(-1.0, 1.0),
            "radius": np.random.uniform(2, 5)
        })

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    vw = cv2.VideoWriter(out_path, fourcc, fps, (1920, 1080))

    for f in range(total_frames):
        p = f / max(1, total_frames - 1)
        
        if mode == "zoom_in":
            zoom = 1.0 + 0.12 * p
        else:
            zoom = 1.12 - 0.12 * p

        cw = int(1920 / zoom)
        ch = int(1080 / zoom)
        cx = (1920 - cw) // 2
        cy = (1080 - ch) // 2
        
        cropped = img[cy:cy + ch, cx:cx + cw]
        frame = cv2.resize(cropped, (1920, 1080), interpolation=cv2.INTER_LINEAR)

        # Draw Dynamic Atmospheric Particles
        for pt in particles:
            pt["y"] += pt["speed_y"]
            pt["x"] += pt["speed_x"]
            if pt["y"] > 1080: pt["y"] = 0
            if pt["x"] < 0: pt["x"] = 1920
            if pt["x"] > 1920: pt["x"] = 0
            cv2.circle(frame, (int(pt["x"]), int(pt["y"])), int(pt["radius"]), (240, 245, 255), -1)

        vw.write(frame)

    vw.release()

# -------------------------------------------------------------
# 5. MASTER PRODUCTION PIPELINE
# -------------------------------------------------------------
def build_pro_ai_documentary():
    print("=" * 65)
    print("🚀 PRODUCING EXTREME TIER FLUX AI DOCUMENTARY...")
    print("=" * 65)

    work_dir = "output"
    os.makedirs(work_dir, exist_ok=True)

    # 1. Record Urdu Voiceover
    voice_file = os.path.join(work_dir, "ai_narration.mp3")
    asyncio.run(record_full_voice(DOC_SCRIPT, voice_file))
    total_audio_dur = get_audio_duration(voice_file)
    print(f"🎙️ Narration Recorded: {total_audio_dur:.1f}s")

    num_scenes = len(AI_SCENES)
    clip_dur = total_audio_dur / num_scenes
    print(f"⚡ Fast Pacing: {clip_dur:.2f}s per scene (Total {num_scenes} Cuts)!")

    # 2. Generate Real FLUX AI Images & Render Motion Clips
    clip_files = []
    cut_timestamps = []
    current_time = 0.0

    for idx, sc in enumerate(AI_SCENES):
        print(f"\n🎨 [AI Generating Scene {idx+1}/{num_scenes}]: {sc['title']}...")
        img_file = os.path.join(work_dir, f"flux_{idx}.jpg")
        clip_file = os.path.join(work_dir, f"clip_{idx}.mp4")

        # Generate fresh 4K image with Replicate FLUX
        generate_flux_image(sc["prompt"], img_file)
        render_pro_scene_clip(img_file, sc["title"], sc["sub"], sc["mode"], clip_dur, clip_file, seed=idx * 19)
        clip_files.append(clip_file)

        if idx > 0:
            cut_timestamps.append(current_time)
        current_time += clip_dur

    # 3. Stitch Scenes
    concat_txt = os.path.join(work_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        for cf in clip_files:
            f.write(f"file '{os.path.abspath(cf)}'\n")

    video_only = os.path.join(work_dir, "visuals_combined.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        video_only
    ], check=True)

    # 4. Generate Soundtrack with Auto-Whoosh SFX
    bgm_path = os.path.join(work_dir, "soundtrack.wav")
    print(f"🔊 Synthesizing Soundtrack + {len(cut_timestamps)} Transition WHOOSH Effects...")
    build_pro_soundtrack(total_audio_dur + 2.0, cut_timestamps, bgm_path)

    # 5. Final Audio & Video Merge
    final_output = os.path.join(work_dir, "final_video.mp4")
    cmd_master = [
        "ffmpeg", "-y",
        "-i", video_only,
        "-i", voice_file,
        "-i", bgm_path,
        "-filter_complex",
        "[1:a]volume=1.0[voice];[2:a]volume=0.25[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd_master, check=True)

    size_mb = os.path.getsize(final_output) / (1024 * 1024)
    print("=" * 65)
    print(f"🎉 EXTREME TIER FLUX AI DOCUMENTARY READY: {final_output} ({size_mb:.2f} MB)")
    print("=" * 65)

if __name__ == "__main__":
    build_pro_ai_documentary()