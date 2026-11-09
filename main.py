import os
import subprocess
import glob

def run_blender_render():
    os.makedirs("output/frames", exist_ok=True)
    
    blender_script = """
import bpy
import math
import os

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Sun Light
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object.data
sun.energy = 4.0

# 3D Colorful Mascot Sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, 0.5))
hero = bpy.context.active_object
mat = bpy.data.materials.new(name="GoldMat")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.98, 0.8, 0.08, 1.0) # #FACC15
hero.data.materials.append(mat)

# 3D Ground
bpy.ops.mesh.primitive_plane_add(size=15, location=(0, 0, -0.7))

# 3D Text
bpy.ops.object.text_add(location=(-2.2, -1.5, 1.8))
txt = bpy.context.active_object
txt.data.body = "CORVO 3D"
txt.data.extrude = 0.1
txt.rotation_euler = (math.radians(75), 0, 0)

# Animation (60 frames = 2 seconds test @ 30 FPS)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 60
scene.render.fps = 30

for f in range(1, 61):
    hero.location.z = 0.5 + 0.5 * abs(math.sin(f * 0.2))
    hero.rotation_euler.z = math.radians(f * 6.0)
    hero.keyframe_insert(data_path="location", frame=f)
    hero.keyframe_insert(data_path="rotation_euler", frame=f)

# Camera
bpy.ops.object.camera_add(location=(0, -6, 2), rotation=(math.radians(75), 0, 0))
scene.camera = bpy.context.active_object

# Render Settings: CPU Workbench/Cycles (Zero OpenGL Crash Risk)
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.light = 'STUDIO'

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.abspath("output/frames/frame_")

print("Rendering frames via Blender...")
bpy.ops.render.render(animation=True)
print("Rendering finished!")
"""

    with open("render_script.py", "w") as f:
        f.write(blender_script)
        
    print("Launching Blender with Software Virtual Buffer...")
    subprocess.run(["blender", "-b", "-P", "render_script.py"], check=True)
    
    png_files = sorted(glob.glob("output/frames/frame_*.png"))
    print(f"Total Rendered Frames: {len(png_files)}")
    
    if png_files:
        final_video = "output/final_video.mp4"
        audio_path = "output/audio.mp3"
        
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-framerate", "30",
            "-pattern_type", "glob",
            "-i", "output/frames/frame_*.png",
            "-i", audio_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            final_video
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"SUCCESS! Video created at: {final_video} (Size: {os.path.getsize(final_video)} bytes)")
    else:
        print("ERROR: No frames were rendered by Blender.")

if __name__ == "__main__":
    run_blender_render()