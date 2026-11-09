import os
import cv2
import numpy as np
import math
import subprocess
import asyncio
import edge_tts

# -------------------------------------------------------------
# 1. URDU VOICE & MAGICAL BGM SYNTHESIS
# -------------------------------------------------------------
URDU_SCRIPT = "جب گھنے جنگل میں تاریکی چھا گئی، تو ننھے جگنو نے اپنی جادوئی روشنی سے پوری وادی کو ستاروں کی طرح چمکا دیا!"
AUDIO_VOICE = "ur-PK-AsadNeural"

async def generate_voice(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, AUDIO_VOICE, rate="+0%", pitch="+2Hz")
    await communicate.save(output_path)

def create_magical_soundtrack(duration_sec: float, sample_rate: int = 44100) -> np.ndarray:
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Dreamy magical ambient pad chords (D major 9th / F# minor ethereal harmonics)
    pad = (
        0.18 * np.sin(2 * np.pi * 146.83 * t) +   # D3
        0.15 * np.sin(2 * np.pi * 220.00 * t) +   # A3
        0.14 * np.sin(2 * np.pi * 277.18 * t) +   # C#4
        0.12 * np.sin(2 * np.pi * 329.63 * t) +   # E4
        0.10 * np.sin(2 * np.pi * 440.00 * t)     # A4
    )
    # Slow breathing volume modulation
    pad *= (0.7 + 0.3 * np.sin(2 * np.pi * 0.25 * t))
    
    # Twinkling fairy dust sparkle chimes
    chimes = np.zeros_like(t)
    np.random.seed(42)
    chime_times = np.linspace(0.8, duration_sec - 0.8, 14) + np.random.uniform(-0.3, 0.3, 14)
    for ct in chime_times:
        freq = np.random.choice([1046.5, 1318.5, 1567.98, 2093.0, 2637.0])
        mask = (t >= ct) & (t < ct + 0.9)
        dt = t[mask] - ct
        envelope = np.exp(-dt * 5.0) * np.sin(2 * np.pi * freq * dt)
        chimes[mask] += 0.22 * envelope

    soundtrack = pad + chimes
    soundtrack = soundtrack / (np.max(np.abs(soundtrack)) + 1e-6) * 0.4
    return (soundtrack * 32767).astype(np.int16)

# -------------------------------------------------------------
# 2. CINEMATIC DRAWING UTILITIES
# -------------------------------------------------------------
def draw_sparkle(img, center, size, color, alpha=1.0):
    cx, cy = int(center[0]), int(center[1])
    overlay = img.copy()
    cv2.circle(overlay, (cx, cy), max(2, int(size * 0.3)), color, -1)
    # 4-point star flare
    pts1 = np.array([[cx - size, cy], [cx, cy - 2], [cx + size, cy], [cx, cy + 2]])
    pts2 = np.array([[cx, cy - size], [cx + 2, cy], [cx, cy + size], [cx - 2, cy]])
    cv2.fillPoly(overlay, [pts1], color)
    cv2.fillPoly(overlay, [pts2], color)
    cv2.addWeighted(overlay, alpha, img, 1.0 - alpha, 0, img)

def draw_bloom_glow(img, center, radius, color_bgr, intensity=0.7):
    cx, cy = int(center[0]), int(center[1])
    h, w = img.shape[:2]
    # multi-layered radial bloom
    for r_factor, alpha_factor in [(3.2, 0.08), (2.2, 0.16), (1.4, 0.30), (0.7, 0.60)]:
        r = int(radius * r_factor)
        if r <= 0: continue
        glow_layer = img.copy()
        cv2.circle(glow_layer, (cx, cy), r, color_bgr, -1)
        cv2.addWeighted(glow_layer, alpha_factor * intensity, img, 1.0 - (alpha_factor * intensity), 0, img)

# -------------------------------------------------------------
# 3. EXTREME TIER CARTOON ENGINE
# -------------------------------------------------------------
def render_extreme_cartoon():
    print("=" * 60)
    print("🎬 STARTING EXTREME TIER 2.5D CARTOON ENGINE...")
    print("=" * 60)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    fps = 30
    total_duration = 10.0
    total_frames = int(fps * total_duration)
    width, height = 1280, 720

    # 1. Voiceover
    urdu_audio_path = os.path.join(output_dir, "urdu_voice.mp3")
    print("🎙️ Generating Crystal Clear Urdu Narration...")
    asyncio.run(generate_voice(URDU_SCRIPT, urdu_audio_path))

    # 2. Ambient BGM Soundtrack
    bgm_wav_path = os.path.join(output_dir, "ambient_bgm.wav")
    bgm_pcm = create_magical_soundtrack(total_duration)
    # Write PCM to WAV using ffmpeg
    pcm_raw_path = os.path.join(output_dir, "bgm.raw")
    bgm_pcm.tofile(pcm_raw_path)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", pcm_raw_path, bgm_wav_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Particle System (Fairy Dust)
    np.random.seed(99)
    num_particles = 65
    particles = []
    for _ in range(num_particles):
        particles.append({
            "x": np.random.uniform(0, width),
            "y": np.random.uniform(0, height),
            "vx": np.random.uniform(-0.5, 0.5),
            "vy": np.random.uniform(-0.8, -0.2),
            "radius": np.random.uniform(2, 6),
            "phase": np.random.uniform(0, 2 * math.pi),
            "color": [
                int(np.random.uniform(140, 255)),  # B
                int(np.random.uniform(210, 255)),  # G
                int(np.random.uniform(120, 220))   # R (Golden-Cyan fairy sparkles)
            ]
        })

    # 4. Video Writer Setup
    temp_video = os.path.join(output_dir, "temp_render.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

    print(f"🎨 Rendering {total_frames} Cinematic Frames with Baby Firefly & Fairy Dust...")

    for f in range(total_frames):
        t = f / fps
        progress = f / total_frames

        # --- A. BASE SKY GRADIENT (Midnight Deep Navy to Magical Violet) ---
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        sky_gradient = np.linspace(0, 1, height)[:, None]
        # Top color: Deep Midnight Navy (35, 12, 10), Bottom color: Magical Violet (85, 30, 48)
        frame[:, :, 0] = (25 + sky_gradient * 50).astype(np.uint8)   # Blue
        frame[:, :, 1] = (10 + sky_gradient * 25).astype(np.uint8)   # Green
        frame[:, :, 2] = (15 + sky_gradient * 35).astype(np.uint8)   # Red

        # --- B. CINEMATIC MOON & VOLUMETRIC HALO ---
        # Slow camera drift zoom effect on moon
        moon_center = (int(width * 0.78 - progress * 20), int(height * 0.28))
        draw_bloom_glow(frame, moon_center, 90, (180, 240, 255), intensity=0.35)
        # Crescent Moon
        cv2.circle(frame, moon_center, 48, (210, 245, 255), -1)
        shadow_center = (moon_center[0] - 14, moon_center[1] - 8)
        cv2.circle(frame, shadow_center, 44, (35, 15, 20), -1)

        # --- C. ANCIENT ENCHANTED FOREST SILHOUETTES ---
        # Distant background hills & mist
        hills = np.array([
            [0, height],
            [0, int(height * 0.62)],
            [int(width * 0.25), int(height * 0.55)],
            [int(width * 0.55), int(height * 0.60)],
            [int(width * 0.85), int(height * 0.53)],
            [width, int(height * 0.58)],
            [width, height]
        ], dtype=np.int32)
        cv2.fillPoly(frame, [hills], (40, 20, 25))

        # Big Majestic Tree on Left
        tree_left = np.array([
            [0, height],
            [int(width * 0.12), height],
            [int(width * 0.16), int(height * 0.50)],
            [int(width * 0.28), int(height * 0.30)],
            [int(width * 0.20), int(height * 0.28)],
            [int(width * 0.14), int(height * 0.38)],
            [int(width * 0.12), 0],
            [0, 0]
        ], dtype=np.int32)
        cv2.fillPoly(frame, [tree_left], (18, 8, 12))

        # Big Majestic Tree on Right
        tree_right = np.array([
            [width, height],
            [int(width * 0.88), height],
            [int(width * 0.84), int(height * 0.45)],
            [int(width * 0.72), int(height * 0.25)],
            [int(width * 0.80), int(height * 0.22)],
            [int(width * 0.86), int(height * 0.32)],
            [int(width * 0.88), 0],
            [width, 0]
        ], dtype=np.int32)
        cv2.fillPoly(frame, [tree_right], (18, 8, 12))

        # Glowing Magic Mushrooms on Tree Bark
        mushrooms = [
            (int(width * 0.14), int(height * 0.62), (255, 180, 50)),
            (int(width * 0.15), int(height * 0.70), (220, 255, 100)),
            (int(width * 0.86), int(height * 0.58), (255, 140, 200)),
        ]
        for mx, my, m_col in mushrooms:
            m_glow = 0.5 + 0.5 * math.sin(t * 3.0 + mx)
            draw_bloom_glow(frame, (mx, my), int(16 * m_glow), m_col, intensity=0.4)
            cv2.ellipse(frame, (mx, my), (14, 8), 0, 0, 180, m_col, -1)

        # --- D. DYNAMIC FAIRY DUST PARTICLES ---
        for p in particles:
            p["x"] += p["vx"] + 0.25 * math.sin(t * 1.5 + p["phase"])
            p["y"] += p["vy"]
            if p["y"] < 0:
                p["y"] = height + 10
                p["x"] = np.random.uniform(0, width)
            if p["x"] < 0: p["x"] = width
            if p["x"] > width: p["x"] = 0
            
            p_twinkle = 0.4 + 0.6 * math.sin(t * 4.0 + p["phase"])
            p_size = int(p["radius"] * (0.8 + 0.3 * math.sin(t * 2.0)))
            draw_sparkle(frame, (p["x"], p["y"]), p_size, p["color"], alpha=p_twinkle)

        # --- E. CUTE CARTOON BABY FIREFLY ("NOORI") ---
        # Organic, curved 3D-like flight path across the screen
        base_fx = width * (0.18 + 0.64 * (t / total_duration))
        fly_x = int(base_fx + 40 * math.sin(t * 1.6))
        fly_y = int(height * 0.50 + 65 * math.sin(t * 2.2) + 25 * math.cos(t * 1.1))
        
        # Scale grows slightly as he flies closer to the camera!
        char_scale = 1.0 + 0.35 * (t / total_duration)
        
        # 1. Massive Lantern Tail Glow (Pulsing Heartbeat of Magic)
        glow_pulse = 0.8 + 0.25 * math.sin(t * 6.0)
        tail_x = int(fly_x - 38 * char_scale)
        tail_y = int(fly_y + 14 * char_scale)
        draw_bloom_glow(frame, (tail_x, tail_y), int(120 * char_scale * glow_pulse), (80, 255, 170), intensity=0.85)
        draw_bloom_glow(frame, (tail_x, tail_y), int(55 * char_scale), (180, 255, 240), intensity=0.95)

        # Tail Lantern (Translucent bulb)
        cv2.circle(frame, (tail_x, tail_y), int(22 * char_scale), (140, 255, 200), -1)
        cv2.circle(frame, (tail_x, tail_y), int(12 * char_scale), (255, 255, 255), -1)

        # 2. Chubby Cute Body (Warm cartoon amber with dark stripes)
        body_center = (int(fly_x - 10 * char_scale), int(fly_y + 6 * char_scale))
        cv2.ellipse(frame, body_center, (int(26 * char_scale), int(20 * char_scale)), 12, 0, 360, (30, 110, 190), -1)
        # Cute cartoon stripes
        cv2.ellipse(frame, body_center, (int(16 * char_scale), int(19 * char_scale)), 12, 0, 360, (20, 55, 95), 3)

        # 3. Flapping Translucent Fairy Wings (High-Speed Flutter)
        wing_flutter = math.sin(t * 32.0)
        wing_h = int(32 * char_scale * abs(wing_flutter)) + 6
        wing_w = int(24 * char_scale)
        wing_y = int(fly_y - 18 * char_scale)
        
        wing_layer = frame.copy()
        # Back wing
        cv2.ellipse(wing_layer, (int(fly_x - 12 * char_scale), wing_y), (wing_w, wing_h), -35, 0, 360, (255, 240, 220), -1)
        # Front wing
        cv2.ellipse(wing_layer, (int(fly_x - 2 * char_scale), wing_y), (int(wing_w * 1.1), wing_h), -20, 0, 360, (255, 255, 240), -1)
        cv2.addWeighted(wing_layer, 0.65, frame, 0.35, 0, frame)

        # 4. Cute Big Head
        head_center = (int(fly_x + 18 * char_scale), int(fly_y - 2 * char_scale))
        cv2.circle(frame, head_center, int(22 * char_scale), (50, 150, 230), -1)

        # 5. Kawaii Expressive Cartoon Eyes
        # Blinking logic (every 2.8 seconds, eye closes for 4 frames)
        is_blinking = (f % int(fps * 2.8)) < 4
        eye1_x = int(head_center[0] + 6 * char_scale)
        eye1_y = int(head_center[1] - 4 * char_scale)
        eye_r = int(7 * char_scale)

        if not is_blinking:
            # Big adorable eye pupil
            cv2.circle(frame, (eye1_x, eye1_y), eye_r, (25, 20, 20), -1)
            # Sparkling white highlight reflection
            cv2.circle(frame, (eye1_x + 2, eye1_y - 2), max(2, int(eye_r * 0.45)), (255, 255, 255), -1)
            cv2.circle(frame, (eye1_x - 2, eye1_y + 2), max(1, int(eye_r * 0.2)), (255, 255, 255), -1)
        else:
            # Cute happy curved closed eyelid ^
            cv2.ellipse(frame, (eye1_x, eye1_y), (eye_r, 4), 0, 180, 360, (20, 20, 20), 2)

        # Rosy Blush Cheek
        cv2.circle(frame, (int(head_center[0] + 4 * char_scale), int(head_center[1] + 8 * char_scale)), int(5 * char_scale), (80, 80, 240), -1)

        # Cute Bouncy Antennae with Glowing Bulbs
        antenna_tip = (int(head_center[0] + 16 * char_scale), int(head_center[1] - 24 * char_scale + 4 * math.sin(t * 8)))
        cv2.line(frame, head_center, antenna_tip, (30, 80, 140), max(2, int(2 * char_scale)))
        cv2.circle(frame, antenna_tip, max(3, int(4 * char_scale)), (100, 255, 220), -1)

        # --- F. CINEMATIC VIGNETTE (Darkened Curved Film Corners) ---
        vignette_mask = np.zeros((height, width), dtype=np.float32)
        cv2.circle(vignette_mask, (width // 2, height // 2), int(width * 0.68), 1.0, -1)
        vignette_mask = cv2.GaussianBlur(vignette_mask, (101, 101), 0)
        for c in range(3):
            frame[:, :, c] = np.clip(frame[:, :, c] * (0.55 + 0.45 * vignette_mask), 0, 255).astype(np.uint8)

        out.write(frame)

    out.release()
    print("✅ Visual Animation Frames Successfully Rendered!")

    # 4. FINAL STUDIO AUDIO-VIDEO MULTIPLEXING
    final_video = os.path.join(output_dir, "final_video.mp4")
    print("🎵 Merging Urdu Voiceover + Magical Sound Effects with Video...")
    
    # Complex FFmpeg Filter: Voiceover at 100% volume, magical ambient BGM at 35% background volume
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", urdu_audio_path,
        "-i", bgm_wav_path,
        "-filter_complex",
        "[1:a]volume=1.0[voice];[2:a]volume=0.35[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_video
    ]
    subprocess.run(cmd, check=True)

    size_mb = os.path.getsize(final_video) / (1024 * 1024)
    print("=" * 60)
    print(f"🎉 EXTREME TIER CARTOON READY: {final_video} (Size: {size_mb:.2f} MB)")
    print("=" * 60)

if __name__ == "__main__":
    render_extreme_cartoon()