import os
import subprocess
import asyncio
import urllib.request
import urllib.parse
import numpy as np
import edge_tts

# -------------------------------------------------------------
# 1. 1-MINUTE URDU DOCUMENTARY SCRIPT WITH SCENE VISUALS
# -------------------------------------------------------------
DOC_SCRIPT = (
    "ہماری زمین کا ستر فیصد حصہ پانی پر مشتمل ہے، لیکن انسان نے اب تک صرف پانچ فیصد سمندر دریافت کیا ہے۔ "
    "جیسے جیسے ہم سمندر کی گہرائی میں اترتے ہیں، سورج کی روشنی غائب ہو جاتی ہے اور مکمل اندھیرا چھا جاتا ہے۔ "
    "یہاں میلوں گہرائی میں وہ پراسرار مخلوقات بستی ہیں جو اپنے جسم سے خود نیلی اور ہری روشنی پیدا کرتی ہیں۔ "
    "یہ تاریک دنیا زمین کے سب سے بڑے رازوں کو اپنے اندر چھپائے ہوئے ہے۔ "
    "سمندر صرف پانی نہیں، بلکہ نامعلوم رازوں کی ایک نہ ختم ہونے والی داستان ہے!"
)

VOICE_ACTOR = "ur-PK-AsadNeural"

# Har scene ke liye script ke mutabiq Real Photorealistic Image Prompts
SCENE_PROMPTS = [
    {
        "id": "scene1",
        "title": "Ocean Planet Earth",
        "prompt": "cinematic national geographic photography of deep blue ocean waves planet earth dramatic sunlight 4k ultra detailed"
    },
    {
        "id": "scene2",
        "title": "Descending into Deep Abyss",
        "prompt": "underwater ocean sunbeams fading into dark deep blue abyss cinematic photography national geographic 4k"
    },
    {
        "id": "scene3",
        "title": "Glowing Bioluminescent Creatures",
        "prompt": "bioluminescent glowing deep sea creature shining neon blue and green in dark ocean abyss national geographic 4k"
    },
    {
        "id": "scene4",
        "title": "Deep Sea Submarine Exploration",
        "prompt": "deep sea exploration submarine powerful searchlights illuminating ocean trench abyss cinematic photography 4k"
    },
    {
        "id": "scene5",
        "title": "Mysterious Ocean Horizon",
        "prompt": "infinite vast mysterious ocean horizon at dusk dramatic volumetric clouds cinematic 4k"
    }
]

# -------------------------------------------------------------
# 2. AUDIO & BGM GENERATION
# -------------------------------------------------------------
async def generate_voice(text: str, output_path: str):
    print("🎙️ Generating 60-Second Professional Urdu Narration...")
    comm = edge_tts.Communicate(text, VOICE_ACTOR, rate="-2%", pitch="-1Hz")
    await comm.save(output_path)

def create_documentary_bgm(duration_sec: float, sample_rate: int = 44100) -> np.ndarray:
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    drone = (
        0.26 * np.sin(2 * np.pi * 55.00 * t) +
        0.20 * np.sin(2 * np.pi * 82.41 * t) +
        0.15 * np.sin(2 * np.pi * 110.00 * t) +
        0.08 * np.sin(2 * np.pi * 164.81 * t)
    )
    swell = 0.65 + 0.35 * np.sin(2 * np.pi * 0.08 * t)
    bgm = (drone * swell)
    bgm = bgm / (np.max(np.abs(bgm)) + 1e-6) * 0.30
    return (bgm * 32767).astype(np.int16)

# -------------------------------------------------------------
# 3. FETCH REAL HIGH-DEFINITION SCENE IMAGES
# -------------------------------------------------------------
def fetch_real_scene_image(prompt_text: str, dest_path: str):
    encoded = urllib.parse.quote(prompt_text)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1920&height=1080&nologo=true&seed=42"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as response, open(dest_path, "wb") as f:
        f.write(response.read())

# -------------------------------------------------------------
# 4. MAIN BUILDER
# -------------------------------------------------------------
def build_real_documentary():
    print("=" * 60)
    print("🌍 BUILDING 100% SCRIPT-ACCURATE REAL 4K DOCUMENTARY...")
    print("=" * 60)

    work_dir = "output"
    os.makedirs(work_dir, exist_ok=True)

    # 1. Voiceover
    voice_file = os.path.join(work_dir, "doc_narration.mp3")
    asyncio.run(generate_voice(DOC_SCRIPT, voice_file))

    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", voice_file
    ]
    try:
        total_duration = float(subprocess.check_output(probe_cmd).strip())
    except Exception:
        total_duration = 58.0

    print(f"⏱️ Total Video Duration: {total_duration:.1f} seconds")

    # 2. Cinematic Soundtrack
    bgm_file = os.path.join(work_dir, "doc_bgm.wav")
    raw_pcm = os.path.join(work_dir, "bgm.raw")
    bgm_data = create_documentary_bgm(total_duration + 3.0)
    bgm_data.tofile(raw_pcm)
    subprocess.run([
        "ffmpeg", "-y", "-f", "s16le", "-ar", "44100", "-ac", "1",
        "-i", raw_pcm, bgm_file
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Generate Real Script-Matched Visual Clips (with Cinematic Ken Burns Camera Motion)
    clip_duration = total_duration / len(SCENE_PROMPTS)
    num_frames_per_clip = int(clip_duration * 30)
    clip_files = []

    for idx, sc in enumerate(SCENE_PROMPTS):
        img_path = os.path.join(work_dir, f"{sc['id']}.jpg")
        clip_path = os.path.join(work_dir, f"motion_{sc['id']}.mp4")

        print(f"📸 Generating Real Visual {idx+1}/{len(SCENE_PROMPTS)}: {sc['title']}...")
        fetch_real_scene_image(sc["prompt"], img_path)

        # Apply smooth cinematic camera zoom (Ken Burns)
        cmd_kenburns = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", img_path,
            "-t", str(clip_duration),
            "-vf", f"scale=1920:1080,zoompan=z='min(zoom+0.0008,1.20)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={num_frames_per_clip}:s=1920x1080:fps=30",
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            clip_path
        ]
        subprocess.run(cmd_kenburns, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clip_files.append(clip_path)

    # 4. Stitch All Real Visual Clips Together
    concat_list = os.path.join(work_dir, "concat.txt")
    with open(concat_list, "w") as f:
        for c in clip_files:
            f.write(f"file '{os.path.abspath(c)}'\n")

    stitched_video = os.path.join(work_dir, "stitched.mp4")
    print("🎞️ Stitching Real Documentary Scenes...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        stitched_video
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Final Audio & Video Merge
    final_video = os.path.join(work_dir, "final_video.mp4")
    print("🎬 Merging High-Def Real Visuals with Urdu Voiceover & Ambient BGM...")
    cmd_final = [
        "ffmpeg", "-y",
        "-i", stitched_video,
        "-i", voice_file,
        "-i", bgm_file,
        "-filter_complex",
        "[1:a]volume=1.0[v];[2:a]volume=0.22[b];[v][b]amix=inputs=2:duration=first[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        final_video
    ]
    subprocess.run(cmd_final, check=True)

    size_mb = os.path.getsize(final_video) / (1024 * 1024)
    print("=" * 60)
    print(f"🎉 REAL SCRIPT DOCUMENTARY READY: {final_video} ({size_mb:.2f} MB)")
    print("=" * 60)

if __name__ == "__main__":
    build_real_documentary()