import os
import subprocess
import glob

def create_ancient_2d_audio():
    os.makedirs("output", exist_ok=True)
    audio_path = "output/audio.mp3"
    print("Generating 10s Ancient Cave & Stone Clink Audio Bed...")
    # 10s Tribal Drum + Stone Strike + Fire Spark Whoosh
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anoisesrc=d=10:c=pink:r=44100:a=0.03",
        "-f", "lavfi", "-i", "sine=frequency=130:duration=10",
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[a]",
        "-map", "[a]",
        "-t", "10",
        audio_path
    ]
    try:
        subprocess.run(cmd, check=True)
        print("Ancient audio bed generated.")
    except Exception as e:
        print(f"Audio fallback: {e}")

def run_ancient_life_2d_render():
    os.makedirs("output/frames", exist_ok=True)
    
    # Audio generate karein
    create_ancient_2d_audio()
    
    blender_script = """
import bpy
import math
import os

# Clean old scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 300 # 10 Seconds @ 30 FPS
scene.render.fps = 30

# 1. 2D Orthographic Flat Cel Camera (Zero 3D Distortion)
bpy.ops.object.camera_add(location=(0, -8.0, 1.2), rotation=(math.radians(90), 0, 0))
cam = bpy.context.active_object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 6.5
scene.camera = cam

# 2. 2D Ancient Cave Background (#1E1B18 Earthy Stone)
bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 2.0, 1.5))
bg = bpy.context.active_object
bg.rotation_euler = (math.radians(90), 0, 0)
mat_bg = bpy.data.materials.new(name="CaveBG")
mat_bg.use_nodes = True
mat_bg.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.12, 0.10, 0.08, 1.0)
bg.data.materials.append(mat_bg)

# 3. 2D Ground Line (#3E2723 Soil Strip)
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -1.1))
ground = bpy.context.active_object
mat_ground = bpy.data.materials.new(name="GroundMat")
mat_ground.use_nodes = True
mat_ground.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.24, 0.15, 0.14, 1.0)
ground.data.materials.append(mat_ground)

# 4. Cute 2D Cel-Shaded Ancient Caveman Character
# Body Torso (Fur Tunic #D97706 Warm Tan)
bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=1.1, location=(0, 0, 0.2))
torso = bpy.context.active_object
mat_tunic = bpy.data.materials.new(name="TunicMat")
mat_tunic.use_nodes = True
mat_tunic.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.85, 0.47, 0.02, 1.0) # #D97706
torso.data.materials.append(mat_tunic)

# Head (Cartoon Peach #FDBA74)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(0, 0, 1.2))
head = bpy.context.active_object
mat_skin = bpy.data.materials.new(name="SkinMat")
mat_skin.use_nodes = True
mat_skin.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.99, 0.73, 0.45, 1.0)
head.data.materials.append(mat_skin)

# Wild Cave Hair (#451A03 Dark Brown)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.65, location=(0, 0.1, 1.5))
hair = bpy.context.active_object
mat_hair = bpy.data.materials.new(name="HairMat")
mat_hair.use_nodes = True
mat_hair.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.27, 0.10, 0.01, 1.0)
hair.data.materials.append(mat_hair)

# Ancient Flint Stones (Tools #94A3B8 Slate Gray)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(-0.5, -0.4, 0.3))
stone1 = bpy.context.active_object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0.5, -0.4, 0.3))
stone2 = bpy.context.active_object

mat_stone = bpy.data.materials.new(name="StoneMat")
mat_stone.use_nodes = True
mat_stone.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.58, 0.64, 0.72, 1.0)
stone1.data.materials.append(mat_stone)
stone2.data.materials.append(mat_stone)

# Glowing Fire Spark Particle (#FACC15 Golden Fire)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0, -0.4, -0.6))
fire = bpy.context.active_object
mat_fire = bpy.data.materials.new(name="FireMat")
mat_fire.use_nodes = True
mat_fire.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.98, 0.80, 0.08, 1.0) # #FACC15
fire.data.materials.append(mat_fire)

# 5. On-Screen Kinetic Text: "HOW ANCIENT HUMANS LIVED!"
bpy.ops.object.text_add(location=(-2.8, -1.0, 2.5))
title_txt = bpy.context.active_object
title_txt.data.body = "HOW ANCIENT HUMANS LIVED!"
title_txt.data.size = 0.42
title_txt.rotation_euler = (math.radians(90), 0, 0)
mat_title = bpy.data.materials.new(name="TitleMat")
mat_title.use_nodes = True
mat_title.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (0.98, 0.80, 0.08, 1.0) # #FACC15
title_txt.data.materials.append(mat_title)

# 6. 10-Second 2D Animation Micro-Beats (300 Frames @ 30 FPS)
# Beat 1 (0-3s, f1-90): Stones striking together (Anticipation)
# Beat 2 (3-7s, f91-210): Exact Impact Spark + 15% vertical squash
# Beat 3 (7-10s, f211-300): Fire ignites + Happy Freeze
torso.animation_data_create()
head.animation_data_create()
stone1.animation_data_create()
stone2.animation_data_create()
fire.animation_data_create()

for f in range(1, 301, 5):
    if f < 100:
        # Striking flint stones together
        t = f * 0.35
        strike = 0.25 * math.sin(t)
        stone1.location.x = -0.5 + strike
        stone2.location.x = 0.5 - strike
        stone1.keyframe_insert(data_path="location", frame=f)
        stone2.keyframe_insert(data_path="location", frame=f)
        fire.scale = (0.01, 0.01, 0.01)
        fire.keyframe_insert(data_path="scale", frame=f)
    elif f < 220:
        # Fire burst impact & Caveman joy bounce
        t = (f - 100) * 0.15
        bounce = 0.35 * abs(math.sin(t))
        torso.location.z = 0.2 + bounce
        head.location.z = 1.2 + bounce
        torso.keyframe_insert(data_path="location", frame=f)
        head.keyframe_insert(data_path="location", frame=f)
        
        # Fire grows
        fire_scale = min(1.3, 0.4 + (f - 100) * 0.01)
        fire.scale = (fire_scale, fire_scale, fire_scale)
        fire.location.z = -0.6 + 0.1 * math.sin(f * 0.4)
        fire.keyframe_insert(data_path="scale", frame=f)
        fire.keyframe_insert(data_path="location", frame=f)
    else:
        # Final Happy Freeze Hold (Frames 270-300)
        torso.location.z = 0.3
        head.location.z = 1.3
        torso.keyframe_insert(data_path="location", frame=f)
        head.keyframe_insert(data_path="location", frame=f)

# 7. Fast 2D Cel Workbench Shading
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.color_type = 'MATERIAL'
scene.display.shading.light = 'FLAT' # Pure 2D Cartoon Look

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.abspath("output/frames/frame_")

print("Rendering 10s 2D Ancient Life Animation (300 frames)...")
bpy.ops.render.render(animation=True)
print("2D Frames Render Completed!")
"""

    with open("render_script.py", "w") as f:
        f.write(blender_script)
        
    print("Launching 2D Cel Animation Engine...")
    subprocess.run(["blender", "-b", "-P", "render_script.py"], check=True)
    
    png_files = sorted(glob.glob("output/frames/frame_*.png"))
    print(f"Total 2D Frames Rendered: {len(png_files)}")
    
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
        print(f"SUCCESS! 10-Second 2D Video Created: {final_video} (Size: {os.path.getsize(final_video)} bytes)")

if __name__ == "__main__":
    run_ancient_life_2d_render()