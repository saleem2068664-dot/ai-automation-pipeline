import os
import subprocess
import glob

def create_ancient_audio():
    os.makedirs("output", exist_ok=True)
    audio_path = "output/audio.mp3"
    print("Generating 60-Second Ancient Atmosphere Audio Bed...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anoisesrc=d=60:c=pink:r=44100:a=0.03",
        "-f", "lavfi", "-i", "sine=frequency=110:duration=60",
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[a]",
        "-map", "[a]",
        "-t", "60",
        audio_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print("Ancient audio created successfully.")
    except Exception as e:
        print(f"Audio creation fallback: {e}")

def run_ancient_stickman_render():
    os.makedirs("output/frames", exist_ok=True)
    
    # Pehle 60s ka audio banate hain
    create_ancient_audio()
    
    blender_script = """
import bpy
import math
import os

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 1800 # 60 Seconds @ 30 FPS
scene.render.fps = 30

# 1. Noir Deep Ancient World Void (#000000)
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.01, 0.01, 0.02, 1.0)
bg.inputs['Strength'].default_value = 0.5

# Ancient 25° Conical Spotlight
bpy.ops.object.light_add(type='SPOT', location=(0, -2, 8))
spot = bpy.context.active_object
spot.data.energy = 1200.0
spot.data.spot_size = math.radians(35)
spot.data.spot_blend = 0.4
spot.data.color = (1.0, 0.85, 0.4)

# 2. Horizon Ground Plane
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -1.2))
ground = bpy.context.active_object
mat_ground = bpy.data.materials.new(name="GroundMat")
mat_ground.use_nodes = True
mat_ground.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
ground.data.materials.append(mat_ground)

# 3. Ancient Pyramid Silhouette
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=4.5, depth=4.0, location=(6, 8, 0.8))
pyramid = bpy.context.active_object
mat_pyr = bpy.data.materials.new(name="PyrMat")
mat_pyr.use_nodes = True
mat_pyr.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.08, 0.06, 0.03, 1.0)
pyramid.data.materials.append(mat_pyr)

# 4. Matte Off-White Stickman Hero (#E4E4E7)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(0, 0, 1.4))
head = bpy.context.active_object
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=1.2, location=(0, 0, 0.6))
torso = bpy.context.active_object

mat_stick = bpy.data.materials.new(name="StickMat")
mat_stick.use_nodes = True
mat_stick.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.89, 0.89, 0.91, 1.0)
head.data.materials.append(mat_stick)
torso.data.materials.append(mat_stick)

# Ancient Fire Torch (#F59E0B Gold Spark)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0.7, -0.2, 1.1))
torch_flame = bpy.context.active_object
mat_torch = bpy.data.materials.new(name="TorchMat")
mat_torch.use_nodes = True
mat_torch.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.96, 0.62, 0.04, 1.0)
torch_flame.data.materials.append(mat_torch)

# 5. On-Screen Kinetic Title
bpy.ops.object.text_add(location=(-3.4, -2.5, 2.4))
title_txt = bpy.context.active_object
title_txt.data.body = "ANCIENT STICKMAN QUEST"
title_txt.data.size = 0.55
title_txt.data.extrude = 0.12
title_txt.rotation_euler = (math.radians(75), 0, 0)
mat_txt = bpy.data.materials.new(name="TitleMat")
mat_txt.use_nodes = True
mat_txt.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.98, 0.8, 0.08, 1.0)
title_txt.data.materials.append(mat_txt)

# 6. Animation (1800 Frames)
head.animation_data_create()
torso.animation_data_create()
torch_flame.animation_data_create()

for f in range(1, 1801, 10):
    t = f * 0.1
    bounce = 0.3 * abs(math.sin(t))
    squash_stretch = 1.0 + 0.15 * math.sin(t * 2)
    x_pos = -3.5 + (f / 1800.0) * 7.0
    
    head.location.x = x_pos
    head.location.z = 1.4 + bounce
    head.scale.z = squash_stretch
    head.keyframe_insert(data_path="location", frame=f)
    head.keyframe_insert(data_path="scale", frame=f)
    
    torso.location.x = x_pos
    torso.location.z = 0.6 + bounce
    torso.rotation_euler.y = math.radians(math.sin(t) * 12)
    torso.keyframe_insert(data_path="location", frame=f)
    torso.keyframe_insert(data_path="rotation_euler", frame=f)
    
    torch_flame.location.x = x_pos + 0.6
    torch_flame.location.z = 1.1 + bounce + 0.08 * math.sin(f * 0.5)
    torch_flame.keyframe_insert(data_path="location", frame=f)

# Camera (35mm)
bpy.ops.object.camera_add(location=(0, -7.5, 1.8), rotation=(math.radians(80), 0, 0))
scene.camera = bpy.context.active_object
scene.camera.data.lens = 35

# Fast Workbench Mode
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.light = 'STUDIO'

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.abspath("output/frames/frame_")

print("Rendering 60-Second Ancient Stickman (1800 frames)...")
bpy.ops.render.render(animation=True)
print("Frames rendered.")
"""

    with open("render_script.py", "w") as f:
        f.write(blender_script)
        
    print("Launching Blender Engine...")
    subprocess.run(["blender", "-b", "-P", "render_script.py"], check=True)
    
    png_files = sorted(glob.glob("output/frames/frame_*.png"))
    print(f"Total Frames Rendered: {len(png_files)}")
    
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
        print(f"SUCCESS! 60s Video Created: {final_video} (Size: {os.path.getsize(final_video)} bytes)")

if __name__ == "__main__":
    run_ancient_stickman_render()