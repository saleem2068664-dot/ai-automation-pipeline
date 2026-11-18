import os
import cv2
import numpy as np
import math
import subprocess
import asyncio
import edge_tts

# -------------------------------------------------------------
# 1. MASTER DNA-1 NOIR STICKMAN STORYBOARD (SCENE-BY-SCENE SYNC)
# -------------------------------------------------------------
# BGR Color Palette Locked to Master Prompt DNA-1:
C_VOID       = (0, 0, 0)         # #000000 Pitch Black Void
C_BODY_NEAR  = (231, 228, 228)   # #E4E4E7 Matte Near-Limb
C_BODY_FAR   = (122, 113, 113)   # #71717A Depth Far-Limb
C_OUTLINE    = (91, 82, 82)      # #52525B Silhouette Rim
C_FLOOR      = (42, 39, 39)      # #27272A Floor Horizon
C_WHITE      = (255, 255, 255)   # #FFFFFF Glowing Eyes / Core
C_GOLD       = (11, 158, 245)    # #F59E0B Selective Gold Accent
C_CRIMSON    = (68, 68, 239)     # #EF4444 Selective Crimson Wall
C_CYAN       = (212, 182, 6)     # #06B6D4 Selective Cyan Droplets
C_PORTAL     = (129, 185, 16)    # #10B981 Emerald Portal

VOICE_NAME = "ur-PK-AsadNeural"

NOIR_SCENES = [
    {
        "id": "scene1_spotlight",
        "title": "THE SILENT TRAP",
        "voice": "زیادہ تر لوگ ناکامی سے نہیں... بلکہ ایک ان دیکھے خوف سے ہار جاتے ہیں۔"
    },
    {
        "id": "scene2_crimson_wall",
        "title": "THE WALL OF FEAR",
        "voice": "جب بھی آپ آگے بڑھنے کی کوشش کرتے ہیں، تو خوف کی ایک سرخ دیوار آپ کا راستہ روک لیتی ہے۔"
    },
    {
        "id": "scene3_overthinking",
        "title": "WEIGHT OF DOUBT",
        "voice": "شک اور مایوسی کی بارش انسان کو اندر سے توڑ دیتی ہے، اور قدم رک جاتے ہیں۔"
    },
    {
        "id": "scene4_portal_leap",
        "title": "CHOOSE COURAGE",
        "voice": "لیکن جس لمحے آپ ہمت کر کے ایک قدم آگے بڑھاتے ہیں، کامیابی کا دروازہ خود کھل جاتا ہے!"
    },
    {
        "id": "scene5_gold_victory",
        "title": "BEYOND THE SHADOW",
        "voice": "کیونکہ آپ کی اصل طاقت اس خوف کے بالکل پار چھپی ہوتی ہے!"
    }
]

# -------------------------------------------------------------
# 2. AUDIO & FOLEY SFX SYNTHESIS
# -------------------------------------------------------------
async def record_voice(text: str, out_path: str):
    comm = edge_tts.Communicate(text, VOICE_NAME, rate="-3%", pitch="-2Hz")
    await comm.save(out_path)

def get_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        return float(subprocess.check_output(cmd).strip())
    except Exception:
        return 5.0

def build_noir_soundtrack(total_dur: float, scene_starts: list, dest_path: str):
    """Deep noir sub-bass hum + Whoosh transitions + Impact & Chime cues"""
    sr = 44100
    t = np.linspace(0, total_dur, int(sr * total_dur), endpoint=False)

    # Low cinematic ambient noir drone
    drone = (
        0.24 * np.sin(2 * np.pi * 55.0 * t) +
        0.16 * np.sin(2 * np.pi * 82.4 * t) +
        0.10 * np.sin(2 * np.pi * 110.0 * t)
    ) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.1 * t))

    audio = drone.copy()

    # Whoosh at every scene transition
    w_dur = 0.38
    w_len = int(sr * w_dur)
    w_t = np.linspace(0, w_dur, w_len, endpoint=False)
    bell = np.sin(np.pi * (w_t / w_dur)) ** 2
    np.random.seed(7)
    whoosh = (np.random.uniform(-0.3, 0.3, w_len) * 0.65 + np.sin(2 * np.pi * (240 - 140 * (w_t / w_dur)) * w_t) * 0.35) * bell * 0.45

    for st in scene_starts[1:]:
        idx = int(max(0, st - 0.1) * sr)
        if idx + w_len < len(audio):
            audio[idx:idx + w_len] += whoosh

    # Resonant Golden Chime on Scene 4 & 5
    for ct in [scene_starts[3] + 0.6, scene_starts[4] + 0.2]:
        c_dur = 1.4
        c_len = int(sr * c_dur)
        c_t = np.linspace(0, c_dur, c_len, endpoint=False)
        chime = (0.3 * np.sin(2 * np.pi * 523.25 * c_t) + 0.15 * np.sin(2 * np.pi * 1046.5 * c_t)) * np.exp(-c_t * 2.8)
        idx = int(ct * sr)
        if idx + c_len < len(audio):
            audio[idx:idx + c_len] += chime

    audio = audio / (np.max(np.abs(audio)) + 1e-6) * 0.28
    pcm = (audio * 32767).astype(np.int16)
    raw = dest_path + ".raw"
    pcm.tofile(raw)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", raw, dest_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# -------------------------------------------------------------
# 3. DNA-1 NOIR STAGE & STICKMAN RIG RENDERER
# -------------------------------------------------------------
def draw_spotlight_stage(frame, spot_x, floor_y, beam_color=C_WHITE, beam_opacity=0.11, pool_rx=95):
    h, w = frame.shape[:2]
    overlay = frame.copy()

    # 25-degree conical overhead spotlight beam
    beam_pts = np.array([
        [int(spot_x - 35), 0],
        [int(spot_x + 35), 0],
        [int(spot_x + pool_rx * 1.4), floor_y],
        [int(spot_x - pool_rx * 1.4), floor_y]
    ], dtype=np.int32)
    cv2.fillPoly(overlay, [beam_pts], beam_color)
    cv2.addWeighted(overlay, beam_opacity, frame, 1.0 - beam_opacity, 0, frame)

    # Radial ground light pool (60x18 ratio scaled for 720p)
    pool_overlay = frame.copy()
    cv2.ellipse(pool_overlay, (int(spot_x), floor_y), (pool_rx, 16), 0, 0, 360, beam_color, -1)
    cv2.addWeighted(pool_overlay, 0.25, frame, 0.75, 0, frame)
    cv2.ellipse(frame, (int(spot_x), floor_y), (int(pool_rx * 0.55), 8), 0, 0, 360, beam_color, -1)

    # Razor-thin 1.5px horizon floor line (#27272A) at Y=74%
    cv2.line(frame, (0, floor_y), (w, floor_y), C_FLOOR, 2)

def draw_noir_stickman(frame, x, y, scale=1.0, walk_phase=0.0, crouch=0.0, bow_deg=0.0,
                       arm_raise=0.0, silhouette=False, eye_scale=1.0, alpha=1.0):
    """Draws the exact DNA-1 Stickman with near/far limb depth & glowing oval eyes"""
    target = frame if alpha >= 0.99 else frame.copy()
    th = max(4, int(6 * scale))
    near_col = C_VOID if silhouette else C_BODY_NEAR
    far_col  = C_VOID if silhouette else C_BODY_FAR

    crouch_px = int(28 * scale * crouch)
    bow_rad = math.radians(bow_deg)

    hip = (int(x), int(y - 72 * scale + crouch_px))
    torso_len = 66 * scale
    neck = (
        int(hip[0] + math.sin(bow_rad) * torso_len),
        int(hip[1] - math.cos(bow_rad) * torso_len)
    )
    head_r = int(23 * scale)
    head_c = (
        int(neck[0] + math.sin(bow_rad) * (head_r + 4)),
        int(neck[1] - math.cos(bow_rad) * (head_r + 4))
    )

    # Walking stride math
    stride = math.sin(walk_phase) * 34 * scale
    lift1 = max(0.0, math.cos(walk_phase)) * 14 * scale
    lift2 = max(0.0, -math.cos(walk_phase)) * 14 * scale

    foot_far  = (int(x - stride), int(y - lift2))
    foot_near = (int(x + stride), int(y - lift1))

    knee_far  = (int((hip[0] + foot_far[0]) / 2 + 8 * crouch), int((hip[1] + foot_far[1]) / 2 - 6 * crouch))
    knee_near = (int((hip[0] + foot_near[0]) / 2 + 12 * crouch), int((hip[1] + foot_near[1]) / 2 - 6 * crouch))

    # Far arm & far leg (#71717A depth)
    sh = (int(neck[0] - math.sin(bow_rad) * 8), int(neck[1] + 10 * scale))
    hand_far = (
        int(sh[0] + math.sin(walk_phase) * 26 * scale + arm_raise * 20),
        int(sh[1] + 46 * scale - arm_raise * 70 * scale)
    )
    hand_near = (
        int(sh[0] - math.sin(walk_phase) * 26 * scale + arm_raise * 35),
        int(sh[1] + 46 * scale - arm_raise * 85 * scale)
    )

    if silhouette:
        # 1px outline rim (#52525B)
        for p1, p2 in [(hip, knee_far), (knee_far, foot_far), (hip, neck), (sh, hand_far),
                       (hip, knee_near), (knee_near, foot_near), (sh, hand_near)]:
            cv2.line(target, p1, p2, C_OUTLINE, th + 3, cv2.LINE_AA)
        cv2.circle(target, head_c, head_r + 2, C_OUTLINE, -1, cv2.LINE_AA)

    # Far limbs
    cv2.line(target, hip, knee_far, far_col, th, cv2.LINE_AA)
    cv2.line(target, knee_far, foot_far, far_col, th, cv2.LINE_AA)
    cv2.line(target, sh, hand_far, far_col, th - 1, cv2.LINE_AA)

    # Torso + Head
    cv2.line(target, hip, neck, near_col, th + 1, cv2.LINE_AA)
    cv2.circle(target, head_c, head_r, near_col, -1, cv2.LINE_AA)

    # Near limbs
    cv2.line(target, hip, knee_near, near_col, th, cv2.LINE_AA)
    cv2.line(target, knee_near, foot_near, near_col, th, cv2.LINE_AA)
    cv2.line(target, sh, hand_near, near_col, th - 1, cv2.LINE_AA)

    # Two glowing #FFFFFF oval eyes
    eye_col = C_VOID if not silhouette else C_WHITE
    eye_h = max(2, int(6 * scale * eye_scale))
    eye_w = max(2, int(4 * scale))
    cv2.ellipse(target, (head_c[0] + int(5 * scale), head_c[1] - int(3 * scale)), (eye_w, eye_h), 0, 0, 360, eye_col, -1)
    cv2.ellipse(target, (head_c[0] + int(14 * scale), head_c[1] - int(3 * scale)), (eye_w, eye_h), 0, 0, 360, eye_col, -1)

    if alpha < 0.99:
        cv2.addWeighted(target, alpha, frame, 1.0 - alpha, 0, frame)

def draw_floor_reflection(frame, x, floor_y):
    """14% subtle vertical reflection under the character on the dark floor"""
    refl = frame.copy()
    cv2.ellipse(refl, (int(x), floor_y + 24), (16, 22), 0, 0, 360, C_BODY_FAR, -1)
    cv2.addWeighted(refl, 0.14, frame, 0.86, 0, frame)

def draw_upper_title(frame, title, y_pos=140):
    """Upper-third tracked bold title (Y=16%-32%)"""
    font = cv2.FONT_HERSHEY_DUPLEX
    size = cv2.getTextSize(title, font, 1.45, 3)[0]
    tx = (frame.shape[1] - size[0]) // 2
    cv2.putText(frame, title, (tx + 3, y_pos + 3), font, 1.45, (20, 20, 20), 4, cv2.LINE_AA)
    cv2.putText(frame, title, (tx, y_pos), font, 1.45, C_WHITE, 3, cv2.LINE_AA)

# -------------------------------------------------------------
# 4. FRAME-BY-FRAME ANIMATED SCENES (100% DNA-1 LOCKED)
# -------------------------------------------------------------
def render_noir_scene(scene_id: str, title: str, duration: float, out_path: str):
    w, h, fps = 1280, 720, 30
    floor_y = int(h * 0.74)  # Y=74% locked horizon
    total_frames = max(1, int(duration * fps))

    vw = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    np.random.seed(42)
    droplets = [{"x": np.random.randint(150, w - 150), "y": np.random.randint(0, floor_y), "sp": np.random.uniform(7, 11)} for _ in range(40)]

    for f in range(total_frames):
        t = f / fps
        p = f / max(1, total_frames - 1)
        frame = np.zeros((h, w, 3), dtype=np.uint8)  # Pure #000000 void

        # --- SCENE 1: THE SILENT TRAP (Spotlight, blinking, golden spark) ---
        if scene_id == "scene1_spotlight":
            sx = int(w * 0.5)
            draw_spotlight_stage(frame, sx, floor_y, C_WHITE, 0.12)
            draw_floor_reflection(frame, sx, floor_y)
            blink = 0.15 if (f % 75) < 4 else 1.0
            # Golden spark orbiting softly
            gx = int(sx + 95 * math.cos(t * 2.2))
            gy = int(floor_y - 110 + 18 * math.sin(t * 3.0))
            cv2.circle(frame, (gx, gy), 14, (5, 70, 110), -1)
            cv2.circle(frame, (gx, gy), 6, C_GOLD, -1)
            draw_noir_stickman(frame, sx, floor_y, scale=1.15, bow_deg=3 * math.sin(t * 2), eye_scale=blink)
            draw_upper_title(frame, title, y_pos=155)

        # --- SCENE 2: WALL OF FEAR (Walk + Crimson Barrier + Recoil) ---
        elif scene_id == "scene2_crimson_wall":
            wall_x = int(w * 0.62)
            sx = int(w * 0.25 + min(1.0, p * 1.4) * (wall_x - w * 0.25 - 65))
            draw_spotlight_stage(frame, sx, floor_y, C_WHITE, 0.10)
            draw_floor_reflection(frame, sx, floor_y)

            # Glowing Crimson Barrier Wall (#EF4444)
            glow = frame.copy()
            cv2.rectangle(glow, (wall_x - 16, 160), (wall_x + 16, floor_y), C_CRIMSON, -1)
            cv2.addWeighted(glow, 0.35, frame, 0.65, 0, frame)
            cv2.rectangle(frame, (wall_x - 4, 160), (wall_x + 4, floor_y), C_CRIMSON, -1)

            walking = p < 0.7
            phase = t * 11.0 if walking else 0.0
            crouch = 0.55 if not walking else 0.0
            draw_noir_stickman(frame, sx, floor_y, scale=1.15, walk_phase=phase, crouch=crouch, arm_raise=0.3 if not walking else 0.0)
            draw_upper_title(frame, title, y_pos=155)

        # --- SCENE 3: WEIGHT OF DOUBT (14 deg Forward Bow + Cyan Rain 18px) ---
        elif scene_id == "scene3_overthinking":
            sx = int(w * 0.45)
            draw_spotlight_stage(frame, sx, floor_y, C_CYAN, 0.10)
            draw_floor_reflection(frame, sx, floor_y)

            # 14-degree ease-in-out forward bow
            bow = 14.0 + 4.0 * math.sin(t * 2.5)
            draw_noir_stickman(frame, sx, floor_y, scale=1.15, crouch=0.35, bow_deg=bow)

            # Discrete Cyan Droplets (#06B6D4)
            for d in droplets:
                d["y"] += d["sp"]
                if d["y"] > floor_y:
                    d["y"] = 0
                cv2.line(frame, (d["x"], int(d["y"])), (d["x"], int(d["y"]) + 18), C_CYAN, 2)

            # Floating distant Gold Key / Spark (#F59E0B)
            cv2.circle(frame, (int(w * 0.78), floor_y - 120), 10, C_GOLD, -1)
            draw_upper_title(frame, title, y_pos=155)

        # --- SCENE 4: CHOOSE COURAGE (6f Anticipation + 3-Ghost Trails + Emerald Portal) ---
        elif scene_id == "scene4_portal_leap":
            portal_x = int(w * 0.76)
            # Glowing Emerald/Cyan Portal (#10B981)
            p_glow = frame.copy()
            cv2.ellipse(p_glow, (portal_x, floor_y - 110), (55, 110), 0, 0, 360, C_PORTAL, -1)
            cv2.addWeighted(p_glow, 0.30, frame, 0.70, 0, frame)
            cv2.ellipse(frame, (portal_x, floor_y - 110), (38, 95), 0, 0, 360, C_PORTAL, 5)
            cv2.ellipse(frame, (portal_x, floor_y - 110), (26, 75), 0, 0, 360, C_CYAN, 2)

            if p < 0.20:
                # 6-frame deep anticipation crouch
                sx = int(w * 0.25)
                draw_spotlight_stage(frame, sx, floor_y, C_WHITE, 0.12)
                draw_noir_stickman(frame, sx, floor_y, scale=1.15, crouch=0.85, bow_deg=18.0)
            else:
                # High-speed dash with 3-ghost trails (30%, 18%, 8%)
                dp = min(1.0, (p - 0.20) / 0.70)
                sx = int(w * 0.25 + dp * (portal_x - w * 0.25))
                draw_spotlight_stage(frame, sx, floor_y, C_PORTAL, 0.12)
                draw_floor_reflection(frame, sx, floor_y)

                for g_idx, g_alpha in [(3, 0.08), (2, 0.18), (1, 0.30)]:
                    gx = sx - g_idx * 42
                    draw_noir_stickman(frame, gx, floor_y - 18, scale=1.15, walk_phase=t * 18 - g_idx, bow_deg=15.0, alpha=g_alpha)

                draw_noir_stickman(frame, sx, floor_y - 18, scale=1.15, walk_phase=t * 18, bow_deg=15.0, arm_raise=0.5)

            draw_upper_title(frame, title, y_pos=155)

        # --- SCENE 5: BEYOND THE SHADOW (Silhouette Rim + Glowing Oval Eyes + Gold Rays) ---
        else:
            sx = int(w * 0.5)
            draw_spotlight_stage(frame, sx, floor_y, C_GOLD, 0.14, pool_rx=130)
            draw_floor_reflection(frame, sx, floor_y)
            # Iconic rim-lit silhouette (#000000 + 1px #52525B + 2 glowing #FFFFFF oval eyes)
            arm_up = min(1.0, p * 2.5)
            draw_noir_stickman(frame, sx, floor_y, scale=1.22, arm_raise=arm_up, silhouette=True, eye_scale=1.15)
            draw_upper_title(frame, title, y_pos=155)

        vw.write(frame)

    vw.release()

# -------------------------------------------------------------
# 5. MASTER PIPELINE
# -------------------------------------------------------------
def build_noir_stickman_video():
    print("=" * 65)
    print("🎬 RENDERING DNA-1 NOIR STICKMAN ANIMATED MASTERPIECE...")
    print("=" * 65)

    work_dir = "output"
    os.makedirs(work_dir, exist_ok=True)

    scene_videos = []
    voice_files = []
    scene_starts = []
    cur_t = 0.0

    for idx, sc in enumerate(NOIR_SCENES):
        print(f"⚡ Scene {idx+1}/{len(NOIR_SCENES)}: {sc['title']}...")
        v_path = os.path.join(work_dir, f"vo_{idx}.mp3")
        c_path = os.path.join(work_dir, f"raw_{idx}.mp4")
        m_path = os.path.join(work_dir, f"merged_{idx}.mp4")

        asyncio.run(record_voice(sc["voice"], v_path))
        dur = get_duration(v_path) + 0.6
        scene_starts.append(cur_t)
        cur_t += dur

        render_noir_scene(sc["id"], sc["title"], dur, c_path)

        subprocess.run([
            "ffmpeg", "-y", "-i", c_path, "-i", v_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest", m_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        scene_videos.append(m_path)

    concat_txt = os.path.join(work_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        for sv in scene_videos:
            f.write(f"file '{os.path.abspath(sv)}'\n")

    stitched = os.path.join(work_dir, "stitched_noir.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", stitched
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    bgm_path = os.path.join(work_dir, "noir_bgm.wav")
    build_noir_soundtrack(cur_t + 1.5, scene_starts, bgm_path)

    final_video = os.path.join(work_dir, "final_video.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", stitched, "-i", bgm_path,
        "-filter_complex", "[0:a]volume=1.0[vo];[1:a]volume=0.22[bgm];[vo][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
        final_video
    ], check=True)

    print(f"🎉 DNA-1 NOIR STICKMAN READY: {final_video} ({os.path.getsize(final_video) // 1024} KB)")

if __name__ == "__main__":
    build_noir_stickman_video()