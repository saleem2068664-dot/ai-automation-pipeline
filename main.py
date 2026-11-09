import os
import subprocess

def run_blender_render():
    os.makedirs("output", exist_ok=True)
    
    # 1. Blender Internal Python Script Tayar Karte Hain
    blender_script = """
import bpy
import math

# Puranay objects delete karein
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 1. Vibrant World Background & Lighting
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.05, 0.05, 0.08, 1.0) # Deep Cartoon Night Void
bg.inputs['Strength'].default_value = 1.0

# Key Light
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object.data
sun.energy = 4.0
sun.color = (1.0, 0.95, 0.8)

# Colorful Rim Light (Cyber Yellow / Gold)
bpy.ops.object.light_add(type='POINT', location=(-3, 3, 4))
rim = bpy.context.active_object.data
rim.energy = 500.0
rim.color = (0.98, 0.8, 0.08)

# 2. Floor Plane (1.5px horizon ground stage)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -1))
floor = bpy.context.active_object
mat_floor = bpy.data.materials.new(name="FloorMat")
mat_floor.use_nodes = True
mat_floor.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1.0)
floor.data.materials.append(mat_floor)

# 3. Cute Cartoon 3D Hero Mesh (Character Mascot)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, 0.6))
hero = bpy.context.active_object
hero.name = "CartoonHero"

# Vibrant Yellow/Gold Material
mat_hero = bpy.data.materials.new(name="HeroMat")
mat_hero.use_nodes = True
bsdf = mat_hero.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.98, 0.8, 0.08, 1.0) # #FACC15 Gold
bsdf.inputs['Roughness'].default_value = 0.2
bsdf.inputs['Specular IOR Level'].default_value = 0.5
hero.data.materials.append(mat_hero)

# 4. Animated 3D Floating Kinetic Text
bpy.ops.object.text_add(location=(-2.8, -1.8, 2.2))
txt = bpy.context.active_object
txt.data.body = "CORVO 3D PIPELINE"
txt.data.extrude = 0.15
txt.data.size = 0.65
txt.rotation_euler = (math.radians(75), 0, 0)

mat_txt = bpy.data.materials.new(name="TextMat")
mat_txt.use_nodes = True
mat_txt.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.02, 0.84, 0.63, 1.0) # #06D6A0
txt.data.materials.append(mat_txt)

# 5. Animation Keyframes (10 Seconds = 300 Frames @ 30 FPS)
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 150 # 5 Seconds super-fast render test (150 frames)
scene.render.fps = 30

# Hero Bouncing & Rotating Animation
hero.animation_data_create()
for f in range(1, 151, 15):
    hero.location.z = 0.6 + 0.5 * abs(math.sin(f * 0.15))
    hero.rotation_euler.z = math.radians(f * 3.6)
    hero.keyframe_insert(data_path="location", frame=f)
    hero.keyframe_insert(data_path="rotation_euler", frame=f)

# 6. Camera Setup
bpy.ops.object.camera_add(location=(0, -6.5, 2.5), rotation=(math.radians(75), 0, 0))
cam = bpy.context.active_object
cam.data.lens = 35
scene.camera = cam

# 7. Render Engine: Ultra-Fast EEVEE (Only 4 samples for speed!)
scene.render.engine = 'BLENDER_EEVEE'
try:
    scene.eevee.taa_render_samples = 4
except:
    pass

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = "/tmp/raw_render.mp4"

bpy.ops.render.render(animation=True)
print("Blender 3D Animation Render Completed Successfully!")
"""

    with open("render_script.py", "w") as f:
        f.write(blender_script)
        
    print("Starting Headless Blender 3D Render Engine...")
    cmd_blender = ["blender", "-b", "-P", "render_script.py"]
    subprocess.run(cmd_blender, check=True)
    
    # Audio aur Video ko merge karke final_video.mp4 banate hain
    raw_video = "/tmp/raw_render.mp4"
    audio_path = "output/audio.mp3"
    final_output = "output/final_video.mp4"
    
    if os.path.exists(raw_video) and os.path.exists(audio_path):
        print("Merging Audio & 3D Video with FFmpeg...")
        cmd_ffmpeg = [
            "ffmpeg", "-y",
            "-i", raw_video,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            final_output
        ]
        subprocess.run(cmd_ffmpeg, check=True)
        print(f"Final 3D Video Generated at: {final_output}")
    elif os.path.exists(raw_video):
        os.rename(raw_video, final_output)
        print("Final Video Generated without Audio.")

if __name__ == "__main__":
    run_blender_render()