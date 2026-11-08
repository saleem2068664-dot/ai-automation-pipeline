import os
import cohere
from gtts import gTTS
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip

# 1. Generate Short Prompt using Cohere API
api_key = os.environ.get("COHERE_API_KEY")
co = cohere.ClientV2(api_key=api_key)

print("🚀 Requesting Short Concept from Cohere...")

response = co.chat(
    model="command-r-08-2024",
    messages=[
        {
            "role": "user",
            "content": "Write a 1-sentence catchy hook about AI Automation (under 15 words).",
        }
    ],
)
text_content = response.message.content[0].text.strip()
print(f"Generated Hook: {text_content}")

# 2. Setup Production Directory
os.makedirs("production_output", exist_ok=True)

# 3. Create 10-Second Video Clip (1080x1920 Shorts Format)
duration = 10
bg_clip = ColorClip(size=(1080, 1920), color=(15, 23, 42), duration=duration)

# Create Text Overlay
txt_clip = TextClip(
    text_content,
    fontsize=50,
    color='white',
    font='Arial',
    method='caption',
    size=(900, None)
).set_position('center').set_duration(duration)

# Combine Background and Text
final_video = CompositeVideoClip([bg_clip, txt_clip])

# Export MP4 Video File
output_video_path = "production_output/short_10sec_video.mp4"
final_video.write_videofile(
    output_video_path,
    fps=24,
    codec="libx264",
    audio=False
)

print(f"✅ 10-second video rendered and saved to {output_video_path}")