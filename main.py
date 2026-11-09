import os
import math
import subprocess
import cv2
import numpy as np

def render_ancient_2d_animation():
    os.makedirs("output/frames", exist_ok=True)
    
    width, height = 1280, 720
    fps = 30
    total_frames = 300 # 10 Seconds
    
    print(f"Direct Rendering {total_frames} Frames of 2D Ancient Life Animation...")
    
    for f in range(total_frames):
        # 1. Dark Ancient Cave Background
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = (24, 27, 30) # Dark Stone Cave
        
        # Cave Walls
        cv2.circle(img, (200, 150), 120, (35, 38, 42), -1)
        cv2.circle(img, (1100, 200), 160, (35, 38, 42), -1)
        
        # 2. Ground Soil
        cv2.rectangle(img, (0, 560), (width, height), (35, 39, 62), -1)
        cv2.line(img, (0, 560), (width, 560), (10, 10, 10), 3)
        
        # 3. Caveman Motion Physics
        t = f * 0.15
        bounce = int(25 * abs(math.sin(t)))
        c_x = 450 + int((f / total_frames) * 150)
        c_y = 480 - bounce
        
        # Caveman Torso (Fur Tunic #D97706)
        cv2.ellipse(img, (c_x, c_y), (45, 65), 0, 0, 360, (2, 119, 217), -1)
        cv2.ellipse(img, (c_x, c_y), (45, 65), 0, 0, 360, (10, 10, 10), 3)
        
        # Head (Peach Skin #FDBA74)
        head_y = c_y - 85
        cv2.circle(img, (c_x, head_y), 42, (116, 186, 253), -1)
        cv2.circle(img, (c_x, head_y), 42, (10, 10, 10), 3)
        
        # Wild Hair (#451A03)
        cv2.circle(img, (c_x, head_y - 20), 45, (1, 26, 69), -1)
        
        # Eyes
        if f < 100:
            cv2.line(img, (c_x - 18, head_y - 5), (c_x - 8, head_y), (10, 10, 10), 3)
            cv2.line(img, (c_x - 18, head_y + 5), (c_x - 8, head_y), (10, 10, 10), 3)
            cv2.line(img, (c_x + 18, head_y - 5), (c_x + 8, head_y), (10, 10, 10), 3)
            cv2.line(img, (c_x + 18, head_y + 5), (c_x + 8, head_y), (10, 10, 10), 3)
        else:
            cv2.circle(img, (c_x - 12, head_y - 5), 8, (255, 255, 255), -1)
            cv2.circle(img, (c_x + 12, head_y - 5), 8, (255, 255, 255), -1)
            cv2.circle(img, (c_x - 12, head_y - 5), 4, (10, 10, 10), -1)
            cv2.circle(img, (c_x + 12, head_y - 5), 4, (10, 10, 10), -1)
            cv2.ellipse(img, (c_x, head_y + 16), (15, 10), 0, 0, 180, (10, 10, 10), 3)
        
        # 4. Flint Stones & Fire
        fire_x, fire_y = 750, 550
        if f < 100:
            strike_offset = int(25 * math.sin(f * 0.4))
            cv2.circle(img, (c_x + 50 + strike_offset, c_y + 10), 16, (140, 140, 140), -1)
            cv2.circle(img, (c_x + 90 - strike_offset, c_y + 10), 16, (180, 180, 180), -1)
            if abs(strike_offset) < 5:
                cv2.circle(img, (c_x + 70, c_y + 10), 14, (8, 204, 250), -1) # Spark
        else:
            fire_height = min(120, 20 + int((f - 100) * 1.2))
            flame_pts = np.array([
                [fire_x - 40, fire_y],
                [fire_x, fire_y - fire_height + int(10 * math.sin(f * 0.5))],
                [fire_x + 40, fire_y]
            ])
            cv2.drawContours(img, [flame_pts], 0, (8, 204, 250), -1)
            cv2.drawContours(img, [flame_pts], 0, (10, 10, 10), 3)
            cv2.line(img, (fire_x - 45, fire_y + 8), (fire_x + 45, fire_y - 8), (19, 69, 139), 8)
            cv2.line(img, (fire_x - 45, fire_y - 8), (fire_x + 45, fire_y + 8), (19, 69, 139), 8)
        
        # 5. On-Screen Title
        cv2.putText(img, "HOW ANCIENT HUMANS LIVED!", (240, 90), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (10, 10, 10), 8, cv2.LINE_AA)
        cv2.putText(img, "HOW ANCIENT HUMANS LIVED!", (240, 90), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (8, 204, 250), 3, cv2.LINE_AA)
        
        if f > 120:
            cv2.putText(img, "DISCOVERY OF FIRE", (420, 145), 
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        
        # Frame save
        cv2.imwrite(f"output/frames/frame_{f:04d}.png", img)

    print("All 300 visual frames saved!")
    
    final_video = "output/final_video.mp4"
    
    # 6. Crash-Proof FFmpeg: Real Audio Built-in Directly!
    # Generates warm rhythmic tribal ambient track inside FFmpeg without needing external file!
    print("Stitching 300 Frames with Built-in Ancient Soundscape...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", "output/frames/frame_%04d.png",
        "-f", "lavfi", "-i", "anoisesrc=d=10:c=pink:r=44100:a=0.03", # Ancient cave wind
        "-f", "lavfi", "-i", "aevalsrc=sin(2*PI*55*t)*exp(-3*mod(t,1.0)):d=10", # Tribal drum beat
        "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        final_video
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    
    size_mb = os.path.getsize(final_video) / (1024 * 1024)
    print(f"SUCCESS! 100% Real Video Ready: {final_video} (Size: {size_mb:.2f} MB)")

if __name__ == "__main__":
    render_ancient_2d_animation()