import os
import cv2
import numpy as np
import subprocess
import asyncio
import urllib.request
import edge_tts

# -------------------------------------------------------------
# 1. SCENE-BY-SCENE SYNCED SCRIPT & REAL 1080P PHOTOGRAPHS
# -------------------------------------------------------------
DOCUMENTARY_SCENES = [
    {
        "id": "scene1",
        "title": "THE OCEAN PLANET",
        "urdu_sub": "ہماری زمین کا 70 فیصد حصہ پانی پر مشتمل ہے",
        "voice_text": "ہماری زمین کا ستر فیصد حصہ پانی پر مشتمل ہے، لیکن انسان نے اب تک صرف پانچ فیصد سمندر دریافت کیا ہے۔",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1920&q=80"
    },
    {
        "id": "scene2",
        "title": "DESCENDING INTO DARKNESS",
        "urdu_sub": "گہرائی میں سورج کی روشنی غائب ہو جاتی ہے",
        "voice_text": "جیسے جیسے ہم سمندر کی گہرائی میں اترتے ہیں، سورج کی روشنی غائب ہو جاتی ہے اور مکمل اندھیرا چھا جاتا ہے۔",
        "image_url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=1920&q=80"
    },
    {
        "id": "scene3",
        "title": "BIOLUMINESCENT CREATURES",
        "urdu_sub": "پراسرار مخلوقات جو خود روشنی پیدا کرتی ہیں",
        "voice_text": "یہاں میلوں گہرائی میں وہ پراسرar مخلوقات بستی ہیں جو اپنے جسم سے خود نیلی اور ہری روشنی پیدا کرتی ہیں۔",
        "image_url": "https://images.unsplash.com/photo-1548263594-a71ea65a8598?w=1920&q=80"
    },
    {
        "id": "scene4",
        "title": "SECRETS OF THE ABYSS",
        "urdu_sub": "یہ دنیا زمین کے سب سے بڑے رازوں کو چھپائے ہوئے ہے",
        "voice_text": "یہ تاریک دنیا زمین کے سب سے بڑے رازوں کو اپنے اندر چھپائے ہوئے ہے۔",
        "image_url": "https://images.unsplash.com/photo-1582967788606-a171c1080cb0?w=1920&q=80"
    },
    {
        "id": "scene5",
        "title": "AN INFINITE MYSTERY",
        "urdu_sub": "سمندر نامعلوم رازوں کی نہ ختم ہونے والی داستان ہے",
        "voice_text": "سمندر صرف پانی نہیں، بلکہ نامعلوم رازوں کی ایک نہ ختم ہونے والی داستان ہے!",
        "image_url": "https://images.unsplash.com/photo-1498084393753-b411b2d26b34?w=1920&q=80"
    }
]

VOICE_ACTOR = "ur-PK-AsadNeural"

# -------------------------------------------------------------
# 2. AUDIO & DOWNLOAD UTILITIES
# -------------------------------------------------------------
async def generate_scene_voice(text: str, output_path: str):
    comm = edge_tts.Communicate(text, VOICE_ACTOR, rate="-2%", pitch="-1Hz")
    await comm.save(output_path)

def get_audio_duration(file_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        return float(subprocess.check_output(cmd).strip())
    except Exception:
        return 10.0

def download_image(url: str, dest_path: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as response, open(dest_path, "wb") as f:
        f.write(response.read())

def create_subtle_ambient_bgm(total_duration: float, dest_path: str):
    sample_rate = 44100
    t = np.linspace(0, total_duration, int(sample_rate * total_duration), endpoint=False)
    drone = (
        0.25 * np.sin(2 * np.pi * 55.0 * t) +
        0.18 * np.sin(2 * np.pi * 82.4 * t) +
        0.12 * np.sin(2 * np.pi * 110.0 * t)
    )
    swell = 0.7 + 0.3 * np.sin(2 * np.pi * 0.08 * t)
    bgm = (drone * swell)
    bgm = bgm / (np.max(np.abs(bgm)) + 1e-6) * 0.18
    pcm = (bgm * 32767).astype(np.int16)
    
    raw_path = dest_path + ".raw"
    pcm.tofile(raw_path)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", raw_path, dest_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# -------------------------------------------------------------
# 3. HIGH-RESOLUTION CINEMATIC SCENE GENERATOR (ZERO JITTER)
# -------------------------------------------------------------
def build_cinematic_scene_video(img_path: str, title: str, sub: str, duration: float, out_path: str):
    """Creates a rock-solid, crystal-clear 1080p scene with elegant documentary typography"""
    img = cv2.imread(img_path)
    if img is None:
        # Fallback dark ocean canvas
        img = np.full((1080, 1920, 3), (45, 20, 12), dtype=np.uint8)
    else:
        # Scale to fit 1920x1080 perfectly
        h, w = img.shape[:2]
        scale = max(1920 / w, 1080 / h)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        # Crop center
        start_x = (new_w - 1920) // 2
        start_y = (new_h - 1080) // 2
        img = img[start_y:start_y + 1080, start_x:start_x + 1920]

    # Add Cinematic Letterbox Vignette (Darkened edges for dramatic TV documentary look)
    overlay = img.copy()
    # Bottom documentary title banner
    cv2.rectangle(overlay, (0, 920), (1920, 1080), (0, 0, 0), -1)
    # Subtle top letterbox
    cv2.rectangle(overlay, (0, 0), (1920, 70), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.65, img, 0.35, 0, img)

    # Gold accent line
    cv2.line(img, (100, 930), (1820, 930), (0, 200, 255), 2)

    # Elegant Documentary Typography
    cv2.putText(img, title, (100, 980), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 225, 255), 2, cv2.LINE_AA)
    cv2.putText(img, sub, (100, 1030), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)

    # Save prepared slide image
    temp_slide = out_path + ".jpg"
    cv2.imwrite(temp_slide, img, [cv2.IMWRITE_JPEG_QUALITY, 95])

    # Convert to video with smooth 1-second fade-in (NO JITTER, PURE CRISP 1080p)
    fps = 30
    frames = int(duration * fps)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", temp_slide,
        "-t", str(duration),
        "-vf", "fade=t=in:st=0:d=0.8,fade=t=out:st=" + str(max(0.1, duration - 0.8)) + ":d=0.8",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# -------------------------------------------------------------
# 4. MASTER COMPOSITION PIPELINE
# -------------------------------------------------------------
def build_master_documentary():
    print("=" * 65)
    print("🎬 MASTER PRODUCTION: PROFESSIONAL URDU DOCUMENTARY")
    print("=" * 65)

    work_dir = "output"
    os.makedirs(work_dir, exist_ok=True)

    rendered_scenes = []
    total_doc_duration = 0.0

    for idx, sc in enumerate(DOCUMENTARY_SCENES):
        print(f"\n--- [Scene {idx+1}/{len(DOCUMENTARY_SCENES)}: {sc['title']}] ---")
        img_file = os.path.join(work_dir, f"{sc['id']}.jpg")
        voice_file = os.path.join(work_dir, f"{sc['id']}_voice.mp3")
        scene_video = os.path.join(work_dir, f"{sc['id']}_video.mp4")
        scene_final = os.path.join(work_dir, f"{sc['id']}_merged.mp4")

        # 1. Download Photo
        print(f"📥 Fetching HD Photograph...")
        download_image(sc["image_url"], img_file)

        # 2. Generate Sentence Voiceover
        print(f"🎙️ Recording Urdu Voiceover for this scene...")
        asyncio.run(generate_scene_voice(sc["voice_text"], voice_file))
        scene_dur = get_audio_duration(voice_file) + 1.2  # 1.2s breathing room
        total_doc_duration += scene_dur
        print(f"⏱️ Scene Duration: {scene_dur:.1f}s")

        # 3. Create Smooth 1080p Scene Video (Zero Jitter)
        print(f"🎞️ Rendering Clean 1080p Visual Slide with Fade In/Out...")
        build_cinematic_scene_video(img_file, sc["title"], sc["urdu_sub"], scene_dur, scene_video)

        # 4. Merge Scene Video + Scene Voice
        cmd_merge_scene = [
            "ffmpeg", "-y",
            "-i", scene_video,
            "-i", voice_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            scene_final
        ]
        subprocess.run(cmd_merge_scene, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rendered_scenes.append(scene_final)

    # 5. Concatenate All Scenes Seamlessly
    print("\n🎞️ Stitching All Scenes into Final 1-Minute Documentary...")
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

    # 6. Add Background Documentary Music (Balanced Audio Mix)
    bgm_path = os.path.join(work_dir, "documentary_bgm.wav")
    print("🎵 Adding Subtle Cinematic Ambient Soundtrack...")
    create_subtle_ambient_bgm(total_doc_duration + 2.0, bgm_path)

    final_output = os.path.join(work_dir, "final_video.mp4")
    cmd_master = [
        "ffmpeg", "-y",
        "-i", video_only,
        "-i", bgm_path,
        "-filter_complex",
        "[0:a]volume=1.0[voice];[1:a]volume=0.18[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
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
    print(f"🎉 100% PROFESSIONAL DOCUMENTARY READY: {final_output} ({mb:.2f} MB)")
    print("=" * 65)

if __name__ == "__main__":
    build_master_documentary()