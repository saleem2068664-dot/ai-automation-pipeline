import os
import math
import subprocess
import cv2
import numpy as np

def generate_ancient_audio(output_audio="output/audio.mp3"):
    os.makedirs("output", exist_ok=True)
    print("Generating Real Ancient Tribal Drum & Atmospheric Audio (No Beep!)...")
    # Real multi-layered ambient percussion + warm low bass (NO ELECTRONIC SINE BEEP)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anoisesrc=d=10:c=pink:r=44100:a=0.04", # Ambient cave wind
        "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*55*t)*exp(-3*mod(t,1.0)):d=10", # Rhythmic tribal drum kick
        "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*220*t)*exp(-8*mod(t,0.5)):d=10", # Stone clink strike
        "-filter_complex", "[0:a][1:a][2:a]amix=inputs=3:duration=first[a]",
        "-map", "[a]",
        "-t", "10",
        output_audio
    ]
    try:
        subprocess.run(cmd, check=True)
        print("Real Ancient Soundtrack created successfully.")
    except Exception as e:
        print(f"Audio fallback: {e}")

def render_ancient_2d_animation():
    os.makedirs("output/frames", exist_ok=True)
    generate_ancient_audio()
    
    width, height = 1280, 720
    fps = 30
    total_frames = 300 # 10 Seconds
    
    print(f"Direct Rendering {total_frames} Frames of 2D Ancient Life Animation...")
    
    for f in range(total_frames):
        # 1. Dark Ancient Cave Background (#1E1B18)
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = (24, 27, 30) # BGR: Dark Stone Cave
        
        # Cave Wall Texture & Stones
        cv2.circle(img, (200, 150), 120, (35, 38, 42), -1)
        cv2.circle(img, (1100, 200), 160, (35, 38, 42), -1)
        
        # 2. Ground Soil (#3E2723)
        cv2.rectangle(img, (0, 560), (width, height), (35, 39, 62), -1)
        cv2.line(img, (0, 560), (width, 560), (10, 10, 10), 3) # 3px ink line
        
        # 3. Caveman Animation Physics (Bounce & Walk)
        t = f * 0.15
        bounce = int(25 * abs(math.sin(t)))
        c_x = 450 + int((f / total_frames) * 150) # Moving slowly forward
        c_y = 480 - bounce
        
        # Caveman Torso (Fur Tunic #D97706)
        cv2.ellipse(img, (c_x, c_y), (45, 65), 0, 0, 360, (2, 119, 217), -1) # Orange Tunic
        cv2.ellipse(img, (c_x, c_y), (45, 65), 0, 0, 360, (10, 10, 10), 3)  # Ink outline
        
        # Caveman Head (Skin #FDBA74)
        head_y = c_y - 85
        cv2.circle(img, (c_x, head_y), 42, (116, 186, 253), -1) # Peach Skin
        cv2.circle(img, (c_x, head_y), 42, (10, 10, 10), 3)     # Ink outline
        
        # Caveman Wild Hair (#451A03)
        cv2.circle(img, (c_x, head_y - 20), 45, (1, 26, 69), -1)
        
        # Eyes (>< anticipation if f < 100, else big happy eyes)
        if f < 100:
            # Squeezed '><' eyes striking stones
            cv2.line(img, (c_x - 18, head_y - 5), (c_x - 8, head_y), (10, 10, 10), 3)
            cv2.line(img, (c_x - 18, head_y + 5), (c_x - 8, head_y), (10, 10, 10), 3)
            cv2.line(img, (c_x + 18, head_y - 5), (c_x + 8, head_y), (10, 10, 10), 3)
            cv2.line(img, (c_x + 18, head_y + 5), (c_x + 8, head_y), (10, 10, 10), 3)
        else:
            # Big open happy eyes with glossy highlights
            cv2.circle(img, (c_x - 12, head_y - 5), 8, (255, 255, 255), -1)
            cv2.circle(img, (c_x + 12, head_y - 5), 8, (255, 255, 255), -1)
            cv2.circle(img, (c_x - 12, head_y - 5), 4, (10, 10, 10), -1)
            cv2.circle(img, (c_x + 12, head_y - 5), 4, (10, 10, 10), -1)
            # Big smile
            cv2.ellipse(img, (c_x, head_y + 16), (15, 10), 0, 0, 180, (10, 10, 10), 3)
        
        # 4. Flint Stones & Fire Mechanism
        fire_x = 750
        fire_y = 550
        
        if f < 100:
            # Striking stones together
            strike_offset = int(25 * math.sin(f * 0.4))
            cv2.circle(img, (c_x + 50 + strike_offset, c_y + 10), 16, (140, 140, 140), -1)
            cv2.circle(img, (c_x + 90 - strike_offset, c_y + 10), 16, (180, 180, 180), -1)
            # Sparks
            if abs(strike_offset) < 5:
                cv2.circle(img, (c_x + 70, c_y + 10), 12, (8, 204, 250), -1) # Gold spark
        else:
            # Fire Ignites! (#FACC15 & #FF4500)
            fire_height = min(120, 20 + int((f - 100) * 1.2))
            flame_pts = np.array([
                [fire_x - 40, fire_y],
                [fire_x, fire_y - fire_height + int(10 * math.sin(f * 0.5))],
                [fire_x + 40, fire_y]
            ])
            cv2.drawContours(img, [flame_pts], 0, (8, 204, 250), -1) # Outer Gold
            cv2.drawContours(img, [flame_pts], 0, (10, 10, 10), 3)
            # Inner bright yellow core
            inner_flame = np.array([
                [fire_x - 20, fire_y],
                [fire_x, fire_y - int(fire_height * 0.6)],
                [fire_x + 20, fire_y]
            ])
            cv2.drawContours(img, [inner_flame], 0, (200, 255, 255), -1)
            
            # Fire logs underneath
            cv2.line(img, (fire_x - 45, fire_y + 8), (fire_x + 45, fire_y - 8), (19, 69, 139), 8)
            cv2.line(img, (fire_x - 45, fire_y - 8), (fire_x + 45, fire_y + 8), (19, 69, 139), 8)
        
        # 5. On-Screen Kinetic Title ("HOW ANCIENT HUMANS LIVED!")
        cv2.putText(img, "HOW ANCIENT HUMANS LIVED!", (240, 90), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (10, 10, 10), 8, cv2.LINE_AA) # Black outline
        cv2.putText(img, "HOW ANCIENT HUMANS LIVED!", (240, 90), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (8, 204, 250), 3, cv2.LINE_AA) # Gold text
        
        if f > 120:
            # Subtitle
            cv2.putText(img, "DISCOVERY OF FIRE", (420, 145), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Frame save karein
        frame_path = f"output/frames/frame_{f:04d}.png"
        cv2.imwrite(frame_path, img)

    print("All 300 visual frames drawn successfully!")
    
    # 6. FFmpeg Video Assembly
    final_video = "output/final_video.mp4"
    audio_path = "output/audio.mp3"
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", "output/frames/frame_%04d.png",
        "-i", audio_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        final_video
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    size_mb = os.path.getsize(final_video) / (1024 * 1024)
    print(f"SUCCESS! Final Animated Video Ready: {final_video} (Size: {size_mb:.2f} MB)")

if __name__ == "__main__":
    render_ancient_2d_animation()