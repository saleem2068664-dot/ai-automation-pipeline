import os
import subprocess
import glob

def create_cyber_audio():
    os.makedirs("output", exist_ok=True)
    audio_path = "output/audio.mp3"
    print("Generating 60-Second Cyber Rhythm & Foley Audio Bed...")
    # 60s Upbeat Cyber Rhythm Bed (No Spoken Voiceover)
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anoisesrc=d=60:c=pink:r=44100:a=0.02",
        "-f", "lavfi", "-i", "sine=frequency=140:duration=60",
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[a]",
        "-map", "[a]",
        "-t", "60",
        audio_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print("Cyber audio bed ready.")
    except Exception as e:
        print(f"Audio fallback: {e}")

def run_cyber_fox_render():
    os.makedirs("output/frames", exist_ok=True)
    
    # Audio generate karein
    create_cyber_audio()
    
    blender_script = """
import bpy
import math
import os

# Clean old scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 1800 # 60 Seconds @ 30 FPS
scene.render.fps = 30

# 1. Cyber Dark Grid Void (#05050A)
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.02, 0.02, 0.04, 1.0)
bg.inputs['Strength'].default_value = 0.8

# Overhead Cyber Spotlight (Cyan Beam #06B6D4)
bpy.ops.object.light_add(type='SPOT', location=(0, -2, 9))
spot = bpy.context.active_object
spot.data.energy = 1500.0
spot.data.spot_size = math.radians(40)
spot.data.color = (0.02, 0.71, 0.83) # Neon Cyan

# 2. Reflective Neon Stage Floor
bpy.ops.mesh.primitive_cylinder_add(radius=6, depth=0.3, location=(0, 0, -1.2))
floor = bpy.context.active_object
mat_floor = bpy.data.materials.new(name="CyberFloor")
mat_floor.use_nodes = True
mat_floor.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.04, 0.05, 0.08, 1.0)
floor.data.materials.append(mat_floor)

# 3. 3D Cyber Fox Mascot Hero (#F97316 Electric Orange)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(0, 0, 0.5))
hero = bpy.context.active_object
hero.name = "CyberFox"

mat_hero = bpy.data.materials.new(name="FoxMat")
mat_hero.use_nodes = True
bsdf = mat_hero.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.97, 0.45, 0.08, 1.0) # Vibrant Orange
bsdf.inputs['Roughness'].default_value = 0.2
hero.data.materials.append(mat_hero)

# Fox Ears (Cute 3D Low-Poly Cones)
for side in [-0.6, 0.6]:
    bpy.ops.mesh.primitive_cone_add(radius1=0.35, depth=0.7, location=(side, 0, 1.6))
    ear = bpy.context.active_object
    ear.parent = hero
    ear.data.materials.append(mat_hero)

# 4. Animated Kinetic 3D Title (Cyan Glow)
bpy.ops.object.text_add(location=(-3.0, -2.0, 2.5))
txt = bpy.context.active_object
txt.data.body = "CYBER FOX ESCAPE!"
txt.data.size = 0.6
txt.data.extrude = 0.15
txt.rotation_euler = (math.radians(75), 0, 0)

mat_txt = bpy.data.materials.new(name="TxtMat")
mat_txt.use_nodes = True
mat_txt.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.71, 0.83, 1.0)
txt.data.materials.append(mat_txt)

# 5. Full 60s Animation: High-Speed Jump & Spin Loop
hero.animation_data_create()
txt.animation_data_create()

for f in range(1, 1801, 10):
    t = f * 0.12
    # 6-frame anticipation crouch & 15% squash-stretch bounce
    bounce = 0.45 * abs(math.sin(t))
    squash = 1.0 + 0.15 * math.sin(t * 2)
    
    hero.location.z = 0.5 + bounce
    hero.scale.z = squash
    hero.rotation_euler.z = math.radians(f * 4.5) # 360° dynamic spin
    hero.keyframe_insert(data_path="location", frame=f)
    hero.keyframe_insert(data_path="scale", frame=f)
    hero.keyframe_insert(data_path="rotation_euler", frame=f)
    
    # Text gentle floating wave
    txt.location.z = 2.5 + 0.1 * math.sin(t * 0.5)
    txt.keyframe_insert(data_path="location", frame=f)

# Final 30-Frame Happy Freeze (Frames 1770-1800)
for f_hold in [1770, 1800]:
    hero.location.z = 0.5
    hero.keyframe_insert(data_path="location", frame=f_hold)

# 6. Camera Setup (35mm Wide Action Tracking)
bpy.ops.object.camera_add(location=(0, -7.0, 2.2), rotation=(math.radians(78), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 35

# Fast CPU Workbench Mode
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.light = 'STUDIO'

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.abspath("output/frames/frame_")

print("Rendering 60s Cyber Fox Animation...")
bpy.ops.render.render(animation=True)
print("Frames finished.")
"""

    with open("render_script.py", "w") as f:
        f.write(blender_script)
        
    print("Executing Blender Engine for Cyber Fox...")
    subprocess.run(["blender", "-b", "-P", "render_script.py"], check=True)
    
    png_files = sorted(glob.glob("output/frames/frame_*.png"))
    print(f"Total Cyber Fox Frames: {len(png_files)}")
    
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
        print(f"60-SECOND CYBER FOX VIDEO GENERATED: {final_video} (Size: {os.path.getsize(final_video)} bytes)")

if __name__ == "__main__":
    run_cyber_fox_render()