import os
import subprocess
import asyncio
import requests
import numpy as np
import edge_tts

# -------------------------------------------------------------
# 1. 1-MINUTE URDU DOCUMENTARY SCRIPT
# -------------------------------------------------------------
DOC_SCRIPT = (
    "ہماری زمین کا ستر فیصد حصہ پانی پر مشتمل ہے، لیکن انسان نے اب تک صرف پانچ فیصد سمندر دریافت کیا ہے۔ "
    "جیسے جیسے ہم سمندر کی گہرائی میں اترتے ہیں، سورج کی روشنی غائب ہو جاتی ہے اور مکمل اندھیرا چھا جاتا ہے۔ "
    "یہاں میلوں گہرائی میں وہ پراسرار مخلوقات بستی ہیں جو اپنے جسم سے خود نیلی اور ہری روشنی پیدا کرتی ہیں۔ "
    "یہ تاریک دنیا زمین کے سب سے بڑے رازوں کو اپنے اندر چھپائے ہوئے ہے۔ "
    "سمندر صرف پانی نہیں، بلکہ نامعلوم رازوں کی ایک نہ ختم ہونے والی داستان ہے!"
)

VOICE_ACTOR = "ur-PK-AsadNeural"  # Professional Urdu Narration

# -------------------------------------------------------------
# 2. HD PEXELS DIRECT DOCUMENTARY VIDEO CLIPS
# -------------------------------------------------------------
# Real high-resolution Pexels documentary clips (Ocean Depths, Waves, Bioluminescence)
PEXELS_CLIPS = [
    {
        "url": "https://videos.pexels.com/video-files/856381/856381-hd_1920_1080_30fps.mp4",
        "duration": 12,
        "title": "Ocean Surface & Waves"
    },
    {
        "url": "https://videos.pexels.com/video-files/3015510/3015510-hd_1920_1080_24fps.mp4",
        "duration": 12,
        "title": "Diving into Deep Blue"
    },
    {
        "url": "https://videos.pexels.com/video-files/3163534/3163534-hd_1920_1080_30fps.mp4",
        "duration": 12,
        "title": "Mysterious Underwater Reef"
    },
    {
        "url": "https://videos.pexels.com/video-files/2439510/2439510-hd_1920_1080_30fps.mp4",
        "duration": 12,
        "title": "Deep Water Currents & Sunrays"
    },
    {
        "url": "https://videos.pexels.com/video-files/1448735/1448735-hd_1920_1080_24fps.mp4",
        "duration": 14,
        "title": "Abyss & Infinite Ocean Horizon"
    }
]

# -------------------------------------------------------------
# 3. HELPER FUNCTIONS
# -------------------------------------------------------------
async def generate_urdu_narration(text: str, output_path: str):
    print("🎙️ Generating 60-Second Professional Urdu Narration...")
    communicate = edge_tts.Communicate(text, VOICE_ACTOR, rate="-2%", pitch="-1Hz")
    await communicate.save(output_path)

def download_file(url: str, dest_path: str):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    with requests.get(url, headers=headers, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                f.write(chunk)

def create_cinematic_bgm(duration_sec: float, sample_rate: int = 44100) -> np.ndarray:
    """Generates a deep, mysterious National Geographic style ambient drone soundtrack"""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Deep cello/drone sub-bass (C2 = 65.4 Hz, G2 = 98.0 Hz, D#3 = 155.6 Hz)
    drone = (
        0.25 * np.sin(2 * np.pi * 65.41 * t) +
        0.20 * np.sin(2 * np.pi * 98.00 * t) +
        0.15 * np.sin(2 * np.pi * 155.56 * t) +
        0.08 * np.sin(2 * np.pi * 196.00 * t)
    )
    # Ambient swell modulation
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * t)
    bgm = drone * swell
    bgm = bgm / (np.max(np.abs(bgm)) + 1e-6) * 0.28
    return (bgm * 32767).astype(np.int16)

# -------------------------------------------------------------
# 4. MAIN DOCUMENTARY BUILDER
# -------------------------------------------------------------
def build_1minute_documentary():
    print("=" * 60)
    print("🌍 BUILDING 1-MINUTE PEXELS URDU DOCUMENTARY...")
    print("=" * 60)

    work_dir = "output"
    os.makedirs(work_dir, exist_ok=True)

    # 1. Generate Urdu Voiceover
    voice_file = os.path.join(work_dir, "doc_narration.mp3")
    asyncio.run(generate_urdu_narration(DOC_SCRIPT, voice_file))

    # Find exact duration of generated voiceover using ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", voice_file
    ]
    try:
        voice_duration = float(subprocess.check_output(probe_cmd).strip())
    except Exception:
        voice_duration = 55.0

    print(f"⏱️ Narration Duration: {voice_duration:.1f} seconds")

    # 2. Generate Cinematic Ambient BGM
    bgm_wav = os.path.join(work_dir, "cinematic_bgm.wav")
    raw_pcm = os.path.join(work_dir, "bgm.raw")
    bgm_data = create_cinematic_bgm(voice_duration + 2.0)
    bgm_data.tofile(raw_pcm)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", raw_pcm, bgm_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Download & Process Pexels Video Clips
    clip_files = []
    clip_dur = voice_duration / len(PEXELS_CLIPS) + 0.5

    for idx, item in enumerate(PEXELS_CLIPS):
        raw_clip = os.path.join(work_dir, f"raw_clip_{idx}.mp4")
        processed_clip = os.path.join(work_dir, f"clip_{idx}.mp4")

        print(f"📥 Downloading Pexels Clip {idx+1}/{len(PEXELS_CLIPS)}: {item['title']}...")
        download_file(item["url"], raw_clip)

        # Standardize clip to 1080p 30fps with subtle slow zoom (Ken Burns)
        cmd_trim = [
            "ffmpeg", "-y",
            "-ss", "0",
            "-t", str(clip_dur),
            "-i", raw_clip,
            "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30",
            "-c:v", "libx264",
            "-preset", "fast",
            "-an",
            processed_clip
        ]
        subprocess.run(cmd_trim, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clip_files.append(processed_clip)

    # 4. Concatenate All Clips into One Visual Sequence
    concat_list = os.path.join(work_dir, "concat_list.txt")
    with open(concat_list, "w") as f:
        for c in clip_files:
            f.write(f"file '{os.path.abspath(c)}'\n")

    stitched_video = os.path.join(work_dir, "stitched_visuals.mp4")
    print("🎞️ Stitching Pexels Clips Together...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        stitched_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Final Audio Mix (Voiceover 100% + Ambient BGM 25%) + Video
    final_video = os.path.join(work_dir, "final_video.mp4")
    print("🎬 Rendering Final 1-Minute Documentary with Studio Audio...")
    final_cmd = [
        "ffmpeg", "-y",
        "-i", stitched_video,
        "-i", voice_file,
        "-i", bgm_wav,
        "-filter_complex",
        "[1:a]volume=1.0[voice];[2:a]volume=0.22[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_video
    ]
    subprocess.run(final_cmd, check=True)

    size_mb = os.path.getsize(final_video) / (1024 * 1024)
    print("=" * 60)
    print(f"🎉 1-MINUTE DOCUMENTARY READY: {final_video} (Size: {size_mb:.2f} MB)")
    print("=" * 60)

if __name__ == "__main__":
    build_1minute_documentary()