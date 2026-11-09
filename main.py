import os
import math
import subprocess
import asyncio
import cv2
import numpy as np

# 1. Real Natural Urdu Voiceover (Edge-TTS)
async def generate_firefly_urdu_voice():
    os.makedirs("output", exist_ok=True)
    voice_path = "output/urdu_voice.mp3"
    
    urdu_text = "جب جنگل میں اندھیرا چھا گیا، تو ننھے جگنو نے اپنی جادوئی روشنی سے پوری وادی کو چمکا دیا!"
    
    print("Generating Natural Urdu Voiceover via Edge-TTS...")
    import edge_tts
    communicate = edge_tts.Communicate(urdu_text, "ur-PK-AsadNeural", rate="+4%")
    await communicate.save(voice_path)
    print("Urdu Voiceover ready at output/urdu_voice.mp3")

def render_firefly_animation():
    os.makedirs("output", exist_ok=True)
    
    # Generate Voiceover
    asyncio.run(generate_firefly_urdu_voice())
    
    width, height = 1280, 720
    fps = 30
    total_frames = 300 # 10 Seconds
    
    temp_video = "output/temp_visuals.mp4"
    final_video = "output/final_video.mp4"
    voice_path = "output/urdu_voice.mp3"
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    print(f"Rendering {total_frames} Frames of Magic Night Forest Animation...")
    
    for f in range(total_frames):
        # 1. Midnight Magic Night Forest Void (#0A0F1D)
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = (29, 15, 10) # BGR: Deep Midnight Blue
        
        # Distant Pine Tree Silhouettes
        for tree_x in [120, 260, 420, 850, 1020, 1180]:
            pts = np.array([[tree_x, 560], [tree_x - 50, 560], [tree_x, 320], [tree_x + 50, 560]])
            cv2.fillPoly(img, [pts], (42, 25, 18))
        
        # Ground Moss Grass (#052e16)
        cv2.rectangle(img, (0, 540), (width, height), (22, 46, 5), -1)
        cv2.line(img, (0, 540), (width, 540), (10, 10, 10), 3)
        
        # Glowing Crescent Moon in Sky
        cv2.circle(img, (1050, 140), 50, (180, 240, 255), -1)
        cv2.circle(img, (1030, 130), 45, (29, 15, 10), -1) # Moon crescent shadow
        
        # 2. Cute Baby Firefly Motion Physics
        t = f * 0.14
        # Flying figure-8 hover path
        fly_x = 640 + int(140 * math.sin(t * 0.8))
        fly_y = 360 + int(50 * math.cos(t * 1.6))
        
        # Firefly Wing Flutter (Rapid 4-frame wing flap)
        wing_flap = int(35 * math.sin(f * 1.2))
        cv2.ellipse(img, (fly_x - 35, fly_y - 25), (40, abs(wing_flap) + 8), -25, 0, 360, (240, 240, 240), -1)
        cv2.ellipse(img, (fly_x + 35, fly_y - 25), (40, abs(wing_flap) + 8), 25, 0, 360, (240, 240, 240), -1)
        cv2.ellipse(img, (fly_x - 35, fly_y - 25), (40, abs(wing_flap) + 8), -25, 0, 360, (10, 10, 10), 2)
        cv2.ellipse(img, (fly_x + 35, fly_y - 25), (40, abs(wing_flap) + 8), 25, 0, 360, (10, 10, 10), 2)
        
        # Glowing Abdomen Tail (The Magic Light Bulb!)
        # Light grows from soft to ultra-bright
        glow_radius = 50 + int(20 * math.sin(f * 0.2))
        if f > 75:
            # Huge radial bloom glow on dark forest
            cv2.circle(img, (fly_x, fly_y + 35), glow_radius + 40, (50, 180, 140), 2)
            cv2.circle(img, (fly_x, fly_y + 35), glow_radius + 20, (100, 230, 180), -1) # Soft green-cyan halo
        
        # Inner Gold/Neon Bulb
        cv2.circle(img, (fly_x, fly_y + 35), 32, (8, 214, 6), -1) # #06D6A0 Emerald Glow
        cv2.circle(img, (fly_x, fly_y + 35), 18, (200, 255, 240), -1) # White-hot core
        cv2.circle(img, (fly_x, fly_y + 35), 32, (10, 10, 10), 3) # Outline
        
        # Firefly Cute Body Torso (#18181B Glossy Charcoal)
        cv2.ellipse(img, (fly_x, fly_y - 10), (36, 45), 0, 0, 360, (24, 24, 27), -1)
        cv2.ellipse(img, (fly_x, fly_y - 10), (36, 45), 0, 0, 360, (10, 10, 10), 3)
        
        # Firefly Head
        head_y = fly_y - 65
        cv2.circle(img, (fly_x, head_y), 34, (35, 35, 38), -1)
        cv2.circle(img, (fly_x, head_y), 34, (10, 10, 10), 3)
        
        # Antennae with glowing yellow tips
        cv2.line(img, (fly_x - 15, head_y - 20), (fly_x - 35, head_y - 50), (10, 10, 10), 3)
        cv2.line(img, (fly_x + 15, head_y - 20), (fly_x + 35, head_y - 50), (10, 10, 10), 3)
        cv2.circle(img, (fly_x - 35, head_y - 50), 7, (8, 204, 250), -1) # Gold tip
        cv2.circle(img, (fly_x + 35, head_y - 50), 7, (8, 204, 250), -1)
        
        # Big Glossy Pixar Eyes
        cv2.circle(img, (fly_x - 14, head_y - 4), 14, (255, 255, 255), -1)
        cv2.circle(img, (fly_x + 14, head_y - 4), 14, (255, 255, 255), -1)
        cv2.circle(img, (fly_x - 14, head_y - 4), 8, (10, 10, 10), -1)
        cv2.circle(img, (fly_x + 14, head_y - 4), 8, (10, 10, 10), -1)
        # Eye Highlights
        cv2.circle(img, (fly_x - 17, head_y - 7), 4, (255, 255, 255), -1)
        cv2.circle(img, (fly_x + 11, head_y - 7), 4, (255, 255, 255), -1)
        # Smile
        cv2.ellipse(img, (fly_x, head_y + 14), (12, 8), 0, 0, 180, (10, 10, 10), 3)
        
        # 3. Floating Golden Star Particles (#FACC15)
        for i in range(12):
            star_seed = (f * 3 + i * 95) % 1280
            star_y = (180 + int(i * 35) + int(15 * math.sin(f * 0.1 + i))) % 520
            cv2.circle(img, (star_seed, star_y), 4, (8, 204, 250), -1)
        
        # 4. On-Screen Kinetic Title
        cv2.putText(img, "LITTLE FIREFLY MAGIC GLOW!", (220, 80), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.3, (10, 10, 10), 7, cv2.LINE_AA)
        cv2.putText(img, "LITTLE FIREFLY MAGIC GLOW!", (220, 80), 
                    cv2.FONT_HERSHEY_DUPLEX, 1.3, (8, 204, 250), 3, cv2.LINE_AA)
        
        out.write(img)

    out.release()
    print("Visuals rendering completed.")
    
    # 5. Merge HD Visuals with Crystal-Clear Urdu Voiceover
    print("Merging Visuals with Urdu Voiceover...")
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", voice_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_video
    ]
    subprocess.run(cmd, check=True)
    size_mb = os.path.getsize(final_video) / (1024 * 1024)
    print(f"SUCCESS! Baby Firefly Urdu Video Ready: {final_video} (Size: {size_mb:.2f} MB)")

if __name__ == "__main__":
    render_firefly_animation()if __name__ == "__main__":
    render_firefly_animation()
git commit -m "Generate 10s Baby Firefly cartoon with Urdu voiceover and magic glow"
git push origin main --force