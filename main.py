import os
import subprocess
import glob

def run_blender_render():
    os.makedirs("output/frames", exist_ok=True)
    
    # 1. Blender Internal Python Script
    blender_script = """
import bpy
import math

# Puranay objects saaf karein
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Bright Background & Lighting
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.08, 0.08, 0.12, 1.0) # Cartoon Slate Dark
bg.inputs['Strength'].default_value = 1.5

# Bright Sun Light
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object.data
sun.energy = 5.0
sun.color = (1.0, 0.95, 0.85)

# Colorful Rim Light (Cyber Yellow)
bpy.ops.object.light_add(type='POINT', location=(-3, 3, 4))
rim = bpy.context.active_object.data
rim.energy = 800.0
rim.color = (0.98, 0.8, 0.08)

# 3D Ground Stage
bpy.ops.mesh.primitive_cylinder_add(radius=4, depth=0.2, location=(0, 0, -1))
stage = bpy.context.active_object
mat_stage = bpy.data.materials.new(name="StageMat")
mat_stage.use_nodes = True
mat_stage.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.5, 0.4, 1.0)
stage.data.materials.append(mat_stage)

# 3D Cartoon Hero (Bouncy Gold Mascot)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.3, location=(0, 0, 0.6))
hero = bpy.context.active_object
hero.name = "CartoonHero"

mat_hero = bpy.data.materials.new(name="HeroMat")
mat_hero.use_nodes = True
bsdf = mat_hero.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.98, 0.8, 0.08, 1.0) # #FACC15 Gold
bsdf.inputs['Roughness'].default_value = 0.2
hero.data.materials.append(mat_hero)

# 3D Floating Bold Text
bpy.ops.object.text_add(location=(-2.8, -1.8, 2.3))
txt = bpy.context.active_object
txt.data.body = "CORVO 3D PIPELINE"
txt.data.extrude = 0.15
txt.data.size = 0.65
txt.rotation_euler = (math.radians(75), 0, 0)

mat_txt = bpy.data.materials.new(name="TextMat")
mat_txt.use_nodes = True
mat_txt.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.84, 0.63, 1.0)
txt.data.materials.append(mat_txt)

# 90 Frames Animation (3 Seconds Ultra-Smooth @ 30 FPS)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 90
scene.render.fps = 30

hero.animation_data_create()
for f in range(1, 91):
    # Bounce and Spin
    hero.location.z = 0.6 + 0.6 * abs(math.sin(f * 0.15))
    hero.rotation_euler.z = math.radians(f * 4.0)
    hero.keyframe_insert(data_path="location", frame=f)
    hero.keyframe_insert(data_path="rotation_euler", frame=f)

# Camera Setup (Locked pointing at Hero)
bpy.ops.object.camera_add(location=(0, -6.5, 2.5), rotation=(math.radians(75), 0, 0))
cam = bpy.context.active_object
cam.data.lens = 35
scene.camera = cam

# PNG Frames Output (Cloud par 100% crash-proof)
scene.render.engine = 'BLENDER_EEVEE'
try:
    scene.eevee.taa_render_samples = 4
except:
    pass

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.abspath("output/frames/frame_")

bpy.ops.render.render(animation=True)
print("All 3D Cartoon Frames Rendered Successfully!")
"""

    with open("render_script.py", "w") as f:
        f.write(blender_script)
        
    print("Executing Blender Headless Engine...")
    cmd_blender = ["blender", "-b", "-P", "render_script.py"]
    subprocess.run(cmd_blender, check=True)
    
    # Check karein frames bane hain ya nahi
    png_files = glob.glob("output/frames/frame_*.png")
    print(f"Total Rendered Frames Found: {len(png_files)}")
    
    final_output = "output/final_video.mp4"
    audio_path = "output/audio.mp3"
    
    if len(png_files) > 0:
        print("Stitching PNG frames into HD MP4 Video with FFmpeg...")
        # FFmpeg frames ko video mein convert karega
        if os.path.exists(audio_path):
            cmd_ffmpeg = [
                "ffmpeg", "-y",
                "-framerate", "30",
                "-i", "output/frames/frame_%04d.png",
                "-i", audio_path,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-shortest",
                final_output
            ]
        else:
            cmd_ffmpeg = [
                "ffmpeg", "-y",
                "-framerate", "30",
                "-i", "output/frames/frame_%04d.png",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                final_output
            ]
        subprocess.run(cmd_ffmpeg, check=True)
        print(f"SUCCESS: Video Generated: {final_output} (Size: {os.path.getsize(final_output)} bytes)")
    else:
        print("ERROR: No PNG frames were found!")

if __name__ == "__main__":
    run_blender_render()