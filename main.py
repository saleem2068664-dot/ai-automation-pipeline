import os
import cv2
import numpy as np
import math
import subprocess
import asyncio
import edge_tts

# -------------------------------------------------------------
# 1. THE ANCIENT STICKMAN SCRIPT
# -------------------------------------------------------------
DOC_SCRIPT = (
    "تصور کریں، اگر اسٹیک مین بیس ہزار سال پہلے قدیم دنیا میں جاگتا! "
    "یہ پتھر کا دور تھا، جہاں اسٹیک مین نے پہلی بار پتھر رگڑ کر آگ جلائی! "
    "پھر اس کا سامنا ایک دیوہیکل میمتھ سے ہوا، اور اسٹیک مین بھالا لے کر شکار پر نکلا! "
    "وقت بدلا اور اسٹیک مین نے مصر کے صحرا میں عظیم اہرام تعمیر کیے! "
    "اور پھر رومن میدان میں تلوار اور ڈھال لے کر بہادری سے لڑا! "
    "قدیم اسٹیک مین کی یہ کہانی بتاتی ہے کہ انسان نے کیسے تاریخ رقم کی!"
)

VOICE_NAME = "ur-PK-AsadNeural"

SCENES_DATA = [
    {
        "id": "caveman",
        "title": "THE STONE AGE AWAKENING",
        "sub": "20,000 SAAL PEHLE STICKMAN JAAGA",
        "mode": "zoom_in"
    },
    {
        "id": "fire",
        "title": "DISCOVERING THE SACRED FIRE",
        "sub": "STICKMAN NE PEHLI BAAR AAG JALAYI",
        "mode": "zoom_out"
    },
    {
        "id": "mammoth",
        "title": "HUNTING THE GIANT MAMMOTH",
        "sub": "BHALA LIYE SHIKAR PAR NIKLA",
        "mode": "zoom_in"
    },
    {
        "id": "egypt",
        "title": "ANCIENT EGYPT & PYRAMIDS",
        "sub": "SAHRA MAIN AZEEM AHRAAM KI TAAMEER",
        "mode": "zoom_out"
    },
    {
        "id": "gladiator",
        "title": "ROMAN GLADIATOR ARENA",
        "sub": "TALWAR AUR DHAAL SE JANG",
        "mode": "zoom_in"
    },
    {
        "id": "victory",
        "title": "A LEGENDARY HISTORY",
        "sub": "INSAAN NE TAAREEKH RAKAM KI",
        "mode": "zoom_out"
    }
]

# -------------------------------------------------------------
# 2. AUDIO & EPIC SOUNDTRACK GENERATOR
# -------------------------------------------------------------
async def record_full_voice(text: str, out_path: str):
    print("🎙️ Recording Ancient Stickman Epic Urdu Narration...")
    comm = edge_tts.Communicate(text, VOICE_NAME, rate="-2%", pitch="-1Hz")
    await comm.save(out_path)

def get_audio_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        return float(subprocess.check_output(cmd).strip())
    except Exception:
        return 40.0

def build_ancient_soundtrack(duration_sec: float, cut_timestamps: list, dest_path: str):
    sample_rate = 44100
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    
    # Ancient epic war drum beats (Every 1.2 seconds)
    drums = np.zeros_like(t)
    for beat_t in np.arange(0.2, duration_sec, 1.2):
        mask = (t >= beat_t) & (t < beat_t + 0.35)
        dt = t[mask] - beat_t
        drums[mask] += 0.35 * np.sin(2 * np.pi * 65.0 * dt) * np.exp(-dt * 12.0)

    # Low atmospheric drone
    drone = 0.15 * np.sin(2 * np.pi * 110.0 * t) + 0.10 * np.sin(2 * np.pi * 164.8 * t)
    total_audio = drums + drone

    # Whoosh SFX on each cut
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
# 3. PROCEDURAL ANCIENT STICKMAN DRAWING FUNCTIONS
# -------------------------------------------------------------
def get_ancient_papyrus_bg():
    """Generates a warm, authentic ancient papyrus parchment background"""
    bg = np.full((1080, 1920, 3), (210, 230, 245), dtype=np.uint8)  # Warm parchment cream
    # Subtle stone texture vignette
    grad = np.linspace(0, 1, 1080)[:, None]
    bg[:, :, 0] = np.clip(bg[:, :, 0] - grad * 35, 0, 255).astype(np.uint8)
    bg[:, :, 1] = np.clip(bg[:, :, 1] - grad * 30, 0, 255).astype(np.uint8)
    bg[:, :, 2] = np.clip(bg[:, :, 2] - grad * 20, 0, 255).astype(np.uint8)
    return bg

def draw_stickman_base(canvas, x, y, scale=1.0, pose="stand"):
    black = (20, 20, 20)
    th = max(4, int(5 * scale))
    hr = int(28 * scale)
    head_c = (int(x), int(y - 85 * scale))

    # Head
    cv2.circle(canvas, head_c, hr, black, -1)
    # Expressive White Eyes
    cv2.circle(canvas, (head_c[0] + int(6 * scale), head_c[1] - int(4 * scale)), int(4 * scale), (255, 255, 255), -1)
    cv2.circle(canvas, (head_c[0] + int(16 * scale), head_c[1] - int(4 * scale)), int(4 * scale), (255, 255, 255), -1)

    # Spine
    neck = (int(x), int(head_c[1] + hr))
    hip = (int(x), int(y))
    cv2.line(canvas, neck, hip, black, th)

    if pose == "stand":
        # Straight legs
        cv2.line(canvas, hip, (int(x - 20 * scale), int(y + 65 * scale)), black, th)
        cv2.line(canvas, hip, (int(x + 20 * scale), int(y + 65 * scale)), black, th)
        # Arms
        arm_y = int(neck[1] + 20 * scale)
        cv2.line(canvas, (int(x), arm_y), (int(x - 30 * scale), int(arm_y + 40 * scale)), black, th)
        cv2.line(canvas, (int(x), arm_y), (int(x + 30 * scale), int(arm_y + 40 * scale)), black, th)

    elif pose == "run":
        # Dynamic running legs
        cv2.line(canvas, hip, (int(x - 45 * scale), int(y + 45 * scale)), black, th)
        cv2.line(canvas, hip, (int(x + 45 * scale), int(y + 60 * scale)), black, th)
        # Dynamic running arms
        arm_y = int(neck[1] + 20 * scale)
        cv2.line(canvas, (int(x), arm_y), (int(x - 40 * scale), int(arm_y + 35 * scale)), black, th)
        cv2.line(canvas, (int(x), arm_y), (int(x + 55 * scale), int(arm_y - 20 * scale)), black, th)

    elif pose == "strike_fire":
        cv2.line(canvas, hip, (int(x - 25 * scale), int(y + 65 * scale)), black, th)
        cv2.line(canvas, hip, (int(x + 25 * scale), int(y + 65 * scale)), black, th)
        arm_y = int(neck[1] + 20 * scale)
        # Both hands forward striking stones
        cv2.line(canvas, (int(x), arm_y), (int(x + 35 * scale), int(arm_y + 25 * scale)), black, th)
        cv2.line(canvas, (int(x), arm_y), (int(x + 20 * scale), int(arm_y + 30 * scale)), black, th)

    elif pose == "pharaoh":
        cv2.line(canvas, hip, (int(x - 20 * scale), int(y + 65 * scale)), black, th)
        cv2.line(canvas, hip, (int(x + 20 * scale), int(y + 65 * scale)), black, th)
        arm_y = int(neck[1] + 20 * scale)
        # Royal arms holding scepter
        cv2.line(canvas, (int(x), arm_y), (int(x - 35 * scale), int(arm_y + 15 * scale)), black, th)
        cv2.line(canvas, (int(x), arm_y), (int(x + 45 * scale), int(arm_y - 30 * scale)), black, th)

    elif pose == "gladiator":
        # Battle stance legs
        cv2.line(canvas, hip, (int(x - 35 * scale), int(y + 65 * scale)), black, th)
        cv2.line(canvas, hip, (int(x + 35 * scale), int(y + 65 * scale)), black, th)
        arm_y = int(neck[1] + 20 * scale)
        # Left arm holding shield
        cv2.line(canvas, (int(x), arm_y), (int(x - 45 * scale), int(arm_y + 10 * scale)), black, th)
        # Right arm raising sword
        cv2.line(canvas, (int(x), arm_y), (int(x + 50 * scale), int(arm_y - 40 * scale)), black, th)

    elif pose == "victory":
        cv2.line(canvas, hip, (int(x - 25 * scale), int(y + 65 * scale)), black, th)
        cv2.line(canvas, hip, (int(x + 25 * scale), int(y + 65 * scale)), black, th)
        arm_y = int(neck[1] + 20 * scale)
        # Both hands V in the air!
        cv2.line(canvas, (int(x), arm_y), (int(x - 45 * scale), int(arm_y - 50 * scale)), black, th)
        cv2.line(canvas, (int(x), arm_y), (int(x + 45 * scale), int(arm_y - 50 * scale)), black, th)

    return head_c

# -------------------------------------------------------------
# 4. DRAW 6 INDIVIDUAL 100% SCRIPT-ACCURATE ANCIENT SCENES
# -------------------------------------------------------------
def generate_ancient_scene_image(scene_id: str, dest_path: str):
    canvas = get_ancient_papyrus_bg()
    ground_y = 780
    cv2.line(canvas, (0, ground_y), (1920, ground_y), (40, 30, 25), 4)

    # --- SCENE 1: CAVEMAN IN STONE AGE ---
    if scene_id == "caveman":
        # Cave Wall Paintings of Deer & Handprints
        cv2.putText(canvas, "(~~~)  <<-o->>", (200, 350), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.0, (70, 50, 45), 4)
        cv2.putText(canvas, "PREHISTORIC CAVE 20,000 BC", (200, 220), cv2.FONT_HERSHEY_DUPLEX, 1.1, (90, 60, 50), 2)
        # Stone Axe / Club on the ground
        cv2.line(canvas, (1150, ground_y - 20), (1220, ground_y - 20), (30, 60, 100), 8)
        cv2.circle(canvas, (1150, ground_y - 20), 25, (80, 80, 80), -1)
        # Stickman waking up
        draw_stickman_base(canvas, 960, ground_y - 65, scale=1.4, pose="stand")

    # --- SCENE 2: DISCOVERING FIRE ---
    elif scene_id == "fire":
        # Roaring Campfire
        fx, fy = 1150, ground_y - 20
        # Fire flames
        pts_flame = np.array([[fx - 50, fy], [fx, fy - 140], [fx + 50, fy]], dtype=np.int32)
        cv2.fillPoly(canvas, [pts_flame], (0, 140, 255))
        pts_flame_in = np.array([[fx - 25, fy], [fx, fy - 90], [fx + 25, fy]], dtype=np.int32)
        cv2.fillPoly(canvas, [pts_flame_in], (0, 230, 255))
        # Firewood logs
        cv2.line(canvas, (fx - 60, fy), (fx + 60, fy - 15), (20, 50, 110), 10)
        cv2.line(canvas, (fx - 50, fy - 15), (fx + 50, fy), (20, 50, 110), 10)
        # Stickman holding flint stone
        draw_stickman_base(canvas, 800, ground_y - 65, scale=1.4, pose="strike_fire")
        cv2.circle(canvas, (870, ground_y - 120), 14, (70, 70, 70), -1)  # Flint rock
        cv2.putText(canvas, "SPARKS!", (860, ground_y - 150), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 120, 255), 2)

    # --- SCENE 3: HUNTING THE GIANT MAMMOTH ---
    elif scene_id == "mammoth":
        # Giant Woolly Mammoth
        mx, my = 1350, ground_y - 120
        # Mammoth Body
        cv2.ellipse(canvas, (mx, my), (160, 120), 0, 0, 360, (30, 55, 90), -1)
        cv2.circle(canvas, (mx - 140, my - 20), 75, (25, 45, 80), -1)  # Head
        cv2.circle(canvas, (mx - 165, my - 35), 8, (255, 255, 255), -1) # Eye
        # Giant Curved Tusks
        cv2.ellipse(canvas, (mx - 210, my + 10), (70, 45), -35, 0, 180, (230, 240, 255), 14)
        # Trunk
        cv2.ellipse(canvas, (mx - 180, my + 45), (35, 65), 20, 0, 180, (25, 45, 80), 16)
        # Mammoth Legs
        for lx in [mx - 110, mx - 40, mx + 40, mx + 110]:
            cv2.line(canvas, (lx, my + 60), (lx, ground_y), (20, 40, 70), 22)
        
        # Stickman Chasing with Spear!
        draw_stickman_base(canvas, 450, ground_y - 65, scale=1.4, pose="run")
        # Long Stone Spear in Hand
        cv2.line(canvas, (430, ground_y - 120), (660, ground_y - 200), (30, 70, 130), 6)
        # Flint Spearhead
        pts_spear = np.array([[660, ground_y - 200], [690, ground_y - 212], [665, ground_y - 188]], dtype=np.int32)
        cv2.fillPoly(canvas, [pts_spear], (60, 60, 60))
        cv2.putText(canvas, "CHARGE!!", (460, ground_y - 240), cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 0, 220), 3)

    # --- SCENE 4: ANCIENT EGYPT & PYRAMIDS ---
    elif scene_id == "egypt":
        # Giant Egyptian Pyramids in Background
        p1 = np.array([[1050, ground_y], [1350, 280], [1650, ground_y]], dtype=np.int32)
        cv2.fillPoly(canvas, [p1], (110, 180, 230))  # Golden Pyramid 1
        p2 = np.array([[750, ground_y], [980, 380], [1210, ground_y]], dtype=np.int32)
        cv2.fillPoly(canvas, [p2], (85, 150, 205))   # Golden Pyramid 2
        # Blazing Desert Sun
        cv2.circle(canvas, (1650, 220), 75, (0, 200, 255), -1)

        # Stickman Pharaoh!
        hc = draw_stickman_base(canvas, 550, ground_y - 65, scale=1.4, pose="pharaoh")
        # Golden Pharaoh Nemes Crown on Head
        pts_crown = np.array([[hc[0] - 40, hc[1] - 15], [hc[0], hc[1] - 65], [hc[0] + 40, hc[1] - 15]], dtype=np.int32)
        cv2.fillPoly(canvas, [pts_crown], (0, 215, 255))
        # Royal Golden Scepter
        cv2.line(canvas, (595, ground_y - 200), (595, ground_y - 60), (0, 200, 255), 8)
        cv2.circle(canvas, (595, ground_y - 200), 16, (0, 0, 255), -1)

    # --- SCENE 5: ROMAN GLADIATOR ARENA ---
    elif scene_id == "gladiator":
        # Colosseum Arches in background
        for ax in range(250, 1800, 240):
            cv2.ellipse(canvas, (ax, ground_y - 200), (90, 180), 0, 180, 360, (130, 140, 150), 8)
            cv2.line(canvas, (ax - 90, ground_y - 200), (ax - 90, ground_y), (130, 140, 150), 8)
            cv2.line(canvas, (ax + 90, ground_y - 200), (ax + 90, ground_y), (130, 140, 150), 8)

        # Stickman Gladiator
        hc = draw_stickman_base(canvas, 960, ground_y - 65, scale=1.5, pose="gladiator")
        # Roman Helmet with Red Feather Crest!
        cv2.ellipse(canvas, (hc[0], hc[1] - 30), (32, 18), 0, 180, 360, (0, 0, 220), -1)  # Red crest
        # Golden Round Shield in Left Hand
        cv2.circle(canvas, (890, ground_y - 120), 48, (0, 215, 255), -1)
        cv2.circle(canvas, (890, ground_y - 120), 48, (0, 0, 0), 4)
        cv2.circle(canvas, (890, ground_y - 120), 15, (0, 0, 200), -1)
        # Shiny Iron Sword in Right Hand!
        cv2.line(canvas, (1020, ground_y - 160), (1090, ground_y - 260), (220, 220, 220), 8)
        cv2.line(canvas, (1005, ground_y - 170), (1035, ground_y - 150), (0, 200, 255), 8) # Sword guard
        cv2.putText(canvas, "VICTORY OR DEATH!", (760, ground_y - 320), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 200), 3)

    # --- SCENE 6: VICTORY & LEGEND OF HISTORY ---
    else:
        # Starry sky sparkles
        np.random.seed(88)
        for _ in range(50):
            sx, sy = np.random.randint(0, 1920), np.random.randint(50, 600)
            cv2.circle(canvas, (sx, sy), np.random.randint(2, 5), (0, 180, 255), -1)
        
        # Stickman Victorious Hero!
        draw_stickman_base(canvas, 960, ground_y - 65, scale=1.5, pose="victory")
        # Golden Crown on Head
        pts_win_crown = np.array([[925, ground_y - 220], [940, ground_y - 250], [960, ground_y - 230], [980, ground_y - 250], [995, ground_y - 220]], dtype=np.int32)
        cv2.fillPoly(canvas, [pts_win_crown], (0, 215, 255))
        cv2.putText(canvas, "HISTORY IS MADE!", (750, ground_y - 310), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 130, 255), 4)

    cv2.imwrite(dest_path, canvas, [cv2.IMWRITE_JPEG_QUALITY, 96])

# -------------------------------------------------------------
# 5. CINEMATIC RENDERER WITH PARTICLES & BIG IMPACT TEXT
# -------------------------------------------------------------
def render_ancient_motion_clip(img_path: str, title: str, sub: str, mode: str, duration: float, out_path: str, seed: int):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    # Pre-render Big Bold Letterbox & Signature Typography
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 880), (1920, 1080), (0, 0, 0), -1)  # Bottom banner
    cv2.rectangle(overlay, (0, 0), (1920, 75), (0, 0, 0), -1)       # Top letterbox
    cv2.addWeighted(overlay, 0.72, img, 0.28, 0, img)

    # Signature Ancient Gold Accent Bar
    cv2.rectangle(img, (75, 905), (82, 1045), (0, 190, 255), -1)

    # Big Bold Impact Captions
    cv2.putText(img, title, (108, 955), cv2.FONT_HERSHEY_DUPLEX, 1.35, (0, 0, 0), 5, cv2.LINE_AA)
    cv2.putText(img, title, (105, 952), cv2.FONT_HERSHEY_DUPLEX, 1.35, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, sub, (108, 1018), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(img, sub, (105, 1015), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 220, 255), 2, cv2.LINE_AA)

    fps = 30
    total_frames = max(1, int(duration * fps))

    # Floating Ancient Embers & Stardust Particles
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
        
        # Smooth Zoom In or Zoom Out (Sub-pixel linear)
        if mode == "zoom_in":
            zoom = 1.0 + 0.10 * p
        else:
            zoom = 1.10 - 0.10 * p

        cw = int(1920 / zoom)
        ch = int(1080 / zoom)
        cx = (1920 - cw) // 2
        cy = (1080 - ch) // 2
        
        cropped = img[cy:cy + ch, cx:cx + cw]
        frame = cv2.resize(cropped, (1920, 1080), interpolation=cv2.INTER_LINEAR)

        # Draw Dynamic Ancient Embers Particles
        for pt in particles:
            pt["y"] += pt["speed_y"]
            pt["x"] += pt["speed_x"]
            if pt["y"] > 1080: pt["y"] = 0
            if pt["x"] < 0: pt["x"] = 1920
            if pt["x"] > 1920: pt["x"] = 0
            cv2.circle(frame, (int(pt["x"]), int(pt["y"])), int(pt["radius"]), (0, 180, 255), -1)

        vw.write(frame)

    vw.release()

# -------------------------------------------------------------
# 6. MASTER PRODUCTION PIPELINE
# -------------------------------------------------------------
def build_ancient_stickman_documentary():
    print("=" * 65)
    print("🏹 PRODUCING 100% ANCIENT PERIOD STICKMAN DOCUMENTARY...")
    print("=" * 65)

    work_dir = "output"
    os.makedirs(work_dir, exist_ok=True)

    # 1. Record Urdu Voiceover
    voice_file = os.path.join(work_dir, "ancient_voice.mp3")
    asyncio.run(record_full_voice(DOC_SCRIPT, voice_file))
    total_audio_dur = get_audio_duration(voice_file)
    print(f"🎙️ Narration Recorded: {total_audio_dur:.1f}s")

    num_scenes = len(SCENES_DATA)
    clip_dur = total_audio_dur / num_scenes
    print(f"⚡ Pacing: {clip_dur:.2f}s per scene (Total {num_scenes} Cuts)!")

    # 2. Render Each Ancient Stickman Scene
    clip_files = []
    cut_timestamps = []
    current_time = 0.0

    for idx, sc in enumerate(SCENES_DATA):
        print(f"🎨 Rendering Scene {idx+1}/{num_scenes} [{sc['id']}]: {sc['title']}...")
        img_file = os.path.join(work_dir, f"scene_{idx}.jpg")
        clip_file = os.path.join(work_dir, f"clip_{idx}.mp4")

        generate_ancient_scene_image(sc["id"], img_file)
        render_ancient_motion_clip(img_file, sc["title"], sc["sub"], sc["mode"], clip_dur, clip_file, seed=idx * 21)
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
    bgm_path = os.path.join(work_dir, "ancient_soundtrack.wav")
    print(f"🔊 Synthesizing Ancient War Drums + {len(cut_timestamps)} Transition WHOOSH Effects...")
    build_ancient_soundtrack(total_audio_dur + 2.0, cut_timestamps, bgm_path)

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
    print(f"🎉 100% COMPLETE ANCIENT STICKMAN VIDEO READY: {final_output} ({size_mb:.2f} MB)")
    print("=" * 65)

if __name__ == "__main__":
    build_ancient_stickman_documentary()