import os
import cv2
import numpy as np
import math
import subprocess
import asyncio
import edge_tts

# -------------------------------------------------------------
# 1. URDU VOICE & CARTOON SOUND EFFECTS
# -------------------------------------------------------------
URDU_STORY = "ایک دن اسٹیک مین کو راستے میں ایک عجیب لال بٹن ملا... اس نے بنا سوچے بٹن دبا دیا، اور پھر زووووم! وہ سیدھا چاند پر پہنچ گیا!"
VOICE_NAME = "ur-PK-AsadNeural"

async def generate_voice(text: str, output_path: str):
    communicate = edge_tts.Communicate(text, VOICE_NAME, rate="+5%", pitch="+3Hz")
    await communicate.save(output_path)

def create_cartoon_audio(duration_sec: float, sample_rate: int = 44100) -> np.ndarray:
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    audio = np.zeros_like(t)

    # 1. Bouncy Fun Cartoon Background Beat
    beat = 0.08 * np.sin(2 * np.pi * 330 * t) * (np.sin(2 * np.pi * 2.5 * t) > 0.3)
    audio += beat

    # 2. Click Sound at 4.2 seconds (Button Press)
    click_mask = (t >= 4.2) & (t < 4.35)
    dt_c = t[click_mask] - 4.2
    audio[click_mask] += 0.5 * np.sin(2 * np.pi * 1200 * dt_c) * np.exp(-dt_c * 40.0)

    # 3. Rocket Whoosh Blast from 6.0 to 9.5 seconds
    rocket_mask = (t >= 6.0) & (t < 9.5)
    dt_r = t[rocket_mask] - 6.0
    # Rising frequency slide + noise roar
    freq = 150 + dt_r * 250
    noise = np.random.uniform(-0.15, 0.15, size=len(dt_r))
    audio[rocket_mask] += 0.25 * np.sin(2 * np.pi * freq * dt_r) + noise

    audio = audio / (np.max(np.abs(audio)) + 1e-6) * 0.35
    return (audio * 32767).astype(np.int16)

# -------------------------------------------------------------
# 2. 2D STICKMAN DRAWING FUNCTIONS
# -------------------------------------------------------------
def draw_stickman(img, x, y, scale=1.0, pose="walk", walk_phase=0.0, emotion="normal"):
    """Draws a clean, dynamic, expressive 2D cartoon stickman"""
    c_black = (25, 25, 25)
    c_white = (255, 255, 255)
    th = max(3, int(4 * scale))
    
    head_r = int(22 * scale)
    head_center = (int(x), int(y - 70 * scale))
    
    # 1. Head
    cv2.circle(img, head_center, head_r, c_black, -1)
    
    # 2. Expressive Face
    if emotion == "normal":
        # Two cute eyes looking forward
        cv2.circle(img, (head_center[0] + int(6 * scale), head_center[1] - int(4 * scale)), int(3 * scale), c_white, -1)
        cv2.circle(img, (head_center[0] + int(14 * scale), head_center[1] - int(4 * scale)), int(3 * scale), c_white, -1)
    elif emotion == "curious":
        # One big eye, one small eye
        cv2.circle(img, (head_center[0] + int(8 * scale), head_center[1] - int(4 * scale)), int(5 * scale), c_white, -1)
        cv2.circle(img, (head_center[0] + int(14 * scale), head_center[1] - int(4 * scale)), int(2 * scale), c_white, -1)
    elif emotion == "shocked":
        # Huge comic shock eyes (O_O)
        cv2.circle(img, (head_center[0] - int(6 * scale), head_center[1] - int(5 * scale)), int(7 * scale), c_white, -1)
        cv2.circle(img, (head_center[0] + int(8 * scale), head_center[1] - int(5 * scale)), int(7 * scale), c_white, -1)
        cv2.circle(img, (head_center[0] - int(6 * scale), head_center[1] - int(5 * scale)), int(2 * scale), c_black, -1)
        cv2.circle(img, (head_center[0] + int(8 * scale), head_center[1] - int(5 * scale)), int(2 * scale), c_black, -1)
        # Open screaming mouth
        cv2.ellipse(img, (head_center[0] + int(1 * scale), head_center[1] + int(8 * scale)), (int(6 * scale), int(8 * scale)), 0, 0, 360, c_white, -1)

    # 3. Body Spine
    neck = (int(x), int(head_center[1] + head_r))
    hip = (int(x), int(y))
    cv2.line(img, neck, hip, c_black, th)

    # 4. Arms & Legs based on Pose
    if pose == "walk":
        # Walking legs cycle
        leg1_x = int(x + math.sin(walk_phase) * 25 * scale)
        leg2_x = int(x - math.sin(walk_phase) * 25 * scale)
        cv2.line(img, hip, (leg1_x, int(y + 50 * scale)), c_black, th)
        cv2.line(img, hip, (leg2_x, int(y + 50 * scale)), c_black, th)
        # Walking arms cycle
        arm_y = int(neck[1] + 15 * scale)
        arm1_x = int(x - math.sin(walk_phase) * 20 * scale)
        arm2_x = int(x + math.sin(walk_phase) * 20 * scale)
        cv2.line(img, (int(x), arm_y), (arm1_x, int(arm_y + 35 * scale)), c_black, th)
        cv2.line(img, (int(x), arm_y), (arm2_x, int(arm_y + 35 * scale)), c_black, th)

    elif pose == "push":
        # Standing firm legs
        cv2.line(img, hip, (int(x - 20 * scale), int(y + 50 * scale)), c_black, th)
        cv2.line(img, hip, (int(x + 10 * scale), int(y + 50 * scale)), c_black, th)
        # Reaching arm pointing to the button
        arm_y = int(neck[1] + 15 * scale)
        cv2.line(img, (int(x), arm_y), (int(x + 45 * scale), int(arm_y + 25 * scale)), c_black, th)
        cv2.line(img, (int(x), arm_y), (int(x - 15 * scale), int(arm_y + 30 * scale)), c_black, th)

    elif pose == "rocket":
        # Legs flailing in panic
        leg1_x = int(x - 15 * scale + math.sin(walk_phase * 2) * 10 * scale)
        leg2_x = int(x + 15 * scale - math.sin(walk_phase * 2) * 10 * scale)
        cv2.line(img, hip, (leg1_x, int(y + 45 * scale)), c_black, th)
        cv2.line(img, hip, (leg2_x, int(y + 45 * scale)), c_black, th)
        # Arms flailing up in the air
        arm_y = int(neck[1] + 10 * scale)
        cv2.line(img, (int(x), arm_y), (int(x - 35 * scale), int(arm_y - 35 * scale)), c_black, th)
        cv2.line(img, (int(x), arm_y), (int(x + 35 * scale), int(arm_y - 35 * scale)), c_black, th)

# -------------------------------------------------------------
# 3. VIDEO RENDER MAIN PIPELINE
# -------------------------------------------------------------
def render_stickman_story():
    print("🎬 STARTING 2D STICKMAN ANIMATION ENGINE...")
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    fps = 30
    total_sec = 10.0
    total_frames = int(fps * total_sec)
    w, h = 1280, 720

    # 1. Audio Generation
    urdu_audio = os.path.join(output_dir, "stickman_urdu.mp3")
    print("🎙️ Generating Urdu Narration...")
    asyncio.run(generate_voice(URDU_STORY, urdu_audio))

    bgm_wav = os.path.join(output_dir, "stickman_sfx.wav")
    sfx_data = create_cartoon_audio(total_sec)
    sfx_raw = os.path.join(output_dir, "sfx.raw")
    sfx_data.tofile(sfx_raw)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", sfx_raw, bgm_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Video Render
    temp_video = os.path.join(output_dir, "stickman_temp.mp4")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (w, h))

    ground_y = int(h * 0.75)
    btn_x = int(w * 0.65)

    print(f"🎨 Rendering {total_frames} Frames of 2D Stickman Cartoon...")

    for f in range(total_frames):
        t = f / fps

        # Background: Clean stylized comic / notebook background
        frame = np.full((h, w, 3), 246, dtype=np.uint8)  # Soft cream paper white
        
        # Ground Line
        cv2.line(frame, (0, ground_y), (w, ground_y), (40, 40, 40), 4)

        # --------------------------------------------------
        # SCENE 1: WALKING & SPOTTING BUTTON (0.0 to 3.5s)
        # --------------------------------------------------
        if t < 3.5:
            # Stickman walks from left towards center
            walk_progress = min(1.0, t / 3.0)
            sm_x = int(w * 0.15 + (btn_x - w * 0.28) * walk_progress)
            sm_y = ground_y - 50
            
            is_walking = t < 2.5
            pose = "walk" if is_walking else "push"
            emotion = "normal" if t < 2.0 else "curious"
            phase = t * 12.0 if is_walking else 0.0

            # Draw Question Mark "?" over head when curious
            if t >= 2.0:
                cv2.putText(frame, "?", (sm_x + 15, sm_y - 120), cv2.FONT_HERSHEY_DUPLEX, 1.6, (0, 0, 220), 4)

            # Draw Red Button Pedestal
            cv2.rectangle(frame, (btn_x - 30, ground_y - 35), (btn_x + 30, ground_y), (60, 60, 60), -1)
            # Big Red Dome
            cv2.ellipse(frame, (btn_x, ground_y - 35), (28, 20), 0, 180, 360, (40, 40, 230), -1)
            # Signboard: "DO NOT TOUCH!"
            cv2.rectangle(frame, (btn_x - 70, ground_y - 110), (btn_x + 70, ground_y - 65), (255, 255, 255), -1)
            cv2.rectangle(frame, (btn_x - 70, ground_y - 110), (btn_x + 70, ground_y - 65), (30, 30, 30), 3)
            cv2.putText(frame, "DO NOT TOUCH!", (btn_x - 62, ground_y - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2)

            draw_stickman(frame, sm_x, sm_y, scale=1.0, pose=pose, walk_phase=phase, emotion=emotion)

        # --------------------------------------------------
        # SCENE 2: PRESSING THE BUTTON (3.5 to 5.8s)
        # --------------------------------------------------
        elif t < 5.8:
            sm_x = btn_x - 45
            sm_y = ground_y - 50
            
            # Button pressed down!
            btn_h = 10 if t >= 4.2 else 20
            cv2.rectangle(frame, (btn_x - 30, ground_y - 35), (btn_x + 30, ground_y), (60, 60, 60), -1)
            cv2.ellipse(frame, (btn_x, ground_y - 35), (28, btn_h), 0, 180, 360, (40, 40, 230), -1)

            # Shockwave circle when pressed at 4.2s
            if 4.2 <= t < 4.9:
                ring_r = int((t - 4.2) * 220)
                cv2.circle(frame, (btn_x, ground_y - 35), ring_r, (0, 0, 255), 3)
                cv2.putText(frame, "CLICK!!", (btn_x - 40, ground_y - 90), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 220), 3)

            emotion = "shocked" if t >= 4.2 else "curious"
            draw_stickman(frame, sm_x, sm_y, scale=1.0, pose="push", walk_phase=0, emotion=emotion)

        # --------------------------------------------------
        # SCENE 3: ROCKET BLAST OFF TO SPACE! (5.8 to 10.0s)
        # --------------------------------------------------
        else:
            rocket_t = t - 5.8
            # Stickman shoots straight into the sky!
            sm_x = btn_x
            sm_y = int((ground_y - 50) - (rocket_t ** 2.2) * 90)

            # Draw Rocket on Stickman's Back
            cv2.rectangle(frame, (sm_x - 16, sm_y - 50), (sm_x - 4, sm_y + 10), (180, 50, 40), -1)
            cv2.rectangle(frame, (sm_x + 4, sm_y - 50), (sm_x + 16, sm_y + 10), (180, 50, 40), -1)
            
            # Roaring Fire Flames!
            flame_h = int(35 + 20 * math.sin(t * 30))
            pts_flame = np.array([
                [sm_x - 14, sm_y + 10], [sm_x - 6, sm_y + 10], [sm_x - 10, sm_y + 10 + flame_h],
                [sm_x + 6, sm_y + 10], [sm_x + 14, sm_y + 10], [sm_x + 10, sm_y + 10 + flame_h]
            ], dtype=np.int32)
            cv2.fillPoly(frame, [pts_flame[:3]], (0, 140, 255))
            cv2.fillPoly(frame, [pts_flame[3:]], (0, 220, 255))

            # Comic Action Speed Lines (WHOOSH!)
            for lx in [sm_x - 60, sm_x - 30, sm_x + 30, sm_x + 60]:
                cv2.line(frame, (lx, sm_y + 40), (lx, sm_y + 140), (120, 120, 120), 2)
            
            # Big Comic Text
            cv2.putText(frame, "ZOOM!!!", (sm_x + 50, sm_y - 40), cv2.FONT_HERSHEY_DUPLEX, 1.8, (0, 100, 255), 4)

            draw_stickman(frame, sm_x, sm_y, scale=1.0, pose="rocket", walk_phase=t * 10, emotion="shocked")

        out.write(frame)

    out.release()
    print("✅ Visual Animation Complete!")

    # 3. Merge Video with Voice + SFX
    final_video = os.path.join(output_dir, "final_video.mp4")
    print("🎵 Merging Urdu Voiceover and Cartoon SFX...")
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", urdu_audio,
        "-i", bgm_wav,
        "-filter_complex",
        "[1:a]volume=1.0[voice];[2:a]volume=0.4[sfx];[voice][sfx]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_video
    ]
    subprocess.run(cmd, check=True)
    print("🎉 STICKMAN 2D ANIMATION READY:", final_video)

if __name__ == "__main__":
    render_stickman_story()