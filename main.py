import os
import subprocess
import cohere

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
                "content": "Give a 2-word title about AI automation.",
            }
        ],
    )
    script_text = response.message.content[0].text.strip()
except Exception as e:
    print(f"Using default text: {e}")

print(f"Blender Scene Text: {script_text}")

# 2. Create a temporary Blender Python automation script (blender_script.py)
blender_code = f"""
import bpy

# Clear existing objects
bpy.ops.wm.read_factory_settings(use_empty=True)

# Add Camera
bpy.ops.object.camera_add(location=(0, -7, 0), rotation=(1.57, 0, 0))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# Add Light
bpy.ops.object.light_add(type='POINT', location=(0, -5, 5))

# Add 3D Text Object
bpy.ops.font.text_add(location=(-2, 0, 0))
text_obj = bpy.context.active_object
text_obj.data.body = "{script_text}"
text_obj.data.size = 1.0
text_obj.scale = (1.5, 1.5, 1.5)

# Render Settings for Video Output
scene = bpy.context.scene
scene.render.engine = 'CYCLES'  # or BLENDER_EEVEE
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.resolution_percentage = 100
scene.frame_end = 60  # 2 seconds at 30fps

output_path = "{os.path.abspath('production_output/short_10sec_video.mp4')}"
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'

# Execute Render
bpy.ops.render.render(animation=True)
print("Blender 3D Render Complete!")
"""

with open("blender_script.py", "w", encoding="utf-8") as f:
    f.write(blender_code)

# 3. Ensure Output Directory Exists
os.makedirs("production_output", exist_ok=True)

# 4. Run Blender in Headless Mode via Terminal Command
print("🎬 Running Blender Headless 3D Render...")
subprocess.run(["blender", "-b", "-P", "blender_script.py"], check=True)

print("✅ Blender 3D video generation finished successfully!")