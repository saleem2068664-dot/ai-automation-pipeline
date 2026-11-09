import os
import subprocess
import cohere
import asyncio
import edge_tts

# 1. Fetch AI Script Hook using Cohere
api_key = os.environ.get("COHERE_API_KEY")
co = cohere.ClientV2(api_key=api_key)

print("🚀 Requesting script from Cohere...")
script_text = "AI Automation 3D"
try:
    response = co.chat(
        model="command-r-08-2024",
        messages=[
            {
                "role": "user",
                "content": "Give a short 2-word title about AI automation.",
            }
        ],
    )
    script_text = response.message.content[0].text.strip()
except Exception as e:
    print(f"Using default text: {e}")

print(f"Blender Scene Text: {script_text}")

# 2. Generate Microsoft TTS Voiceover
voiceover_path = "voiceover.mp3"

async def generate_tts(text, output_file):
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    await communicate.save(output_file)

print("🎙️ Generating Microsoft TTS Voiceover...")
asyncio.run(generate_tts(script_text, voiceover_path))

# 3. Create Blender Python automation script
blender_code = f"""
import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)

# Add Camera & Studio Lights
bpy.ops.object.camera_add(location=(0, -8, 1.5), rotation=(1.4, 0, 0))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

bpy.ops.object.light_add(type='POINT', location=(5, -5, 5))
light1 = bpy.context.active_object
light1.data.energy = 1500.0

bpy.ops.object.light_add(type='POINT', location=(-5, -5, -2))
light2 = bpy.context.active_object
light2.data.energy = 800.0

# Add 3D Text Object
bpy.ops.font.text_add(location=(-2.2, 0, 0))
text_obj = bpy.context.active_object
text_obj.data.body = "{script_text}"
text_obj.data.size = 1.1
text_obj.scale = (1.5, 1.5, 1.5)
text_obj.rotation_euler = (1.57, 0, 0)

# Animate 3D Text Rotation across 300 Frames (10 Seconds)
text_obj.rotation_euler[2] = 0.0
text_obj.keyframe_insert(data_path="rotation_euler", frame=1)
text_obj.rotation_euler[2] = math.radians(360)
text_obj.keyframe_insert(data_path="rotation_euler", frame=300)

# Render Settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.frame_start = 1
scene.frame_end = 300

bpy.ops.wm.save_as_mainfile(filepath="scene.blend")
print(".blend project file generated successfully!")
"""

with open("generate_scene.py", "w", encoding="utf-8") as f:
    f.write(blender_code)

print("🎬 Generating Blender .blend file...")
subprocess.run(["blender", "-b", "-P", "generate_scene.py"], check=True)

# 4. Merge Voiceover with Video via FFmpeg
os.makedirs("production_output", exist_ok=True)
raw_video_path = "temp_video.mp4"
final_video_path = "production_output/short_10sec_video.mp4"

# Render raw video from Blender
subprocess.run(["blender", "-b", "scene.blend", "-o", os.path.abspath(raw_video_path), "-F", "MPEG4", "-x", "1", "-a"], check=True)

# Combine TTS Voiceover Audio with Rendered Video using FFmpeg
if os.path.exists(voiceover_path) and os.path.exists(raw_video_path):
    print("🔊 Merging Microsoft TTS Audio with 3D Video...")
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", raw_video_path,
        "-i", voiceover_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        final_video_path
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print("✅ Final 3D Video with Audio output generated!")