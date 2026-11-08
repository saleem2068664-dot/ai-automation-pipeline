import os
import cv2
import numpy as np
import cohere

# 1. Fetch AI Text Hook using Cohere API
api_key = os.environ.get("COHERE_API_KEY")
co = cohere.ClientV2(api_key=api_key)

print("🚀 Requesting viral hook from Cohere...")

text_content = "AI Automation: Save 10+ Hours Every Week!"
try:
    response = co.chat(
        model="command-r-08-2024",
        messages=[
            {
                "role": "user",
                "content": "Write a 1-sentence catchy hook about AI Automation (under 10 words).",
            }
        ],
    )
    text_content = response.message.content[0].text.strip()
except Exception as e:
    print(f"Fallback to default text due to API notice: {e}")

print(f"Video Hook Text: {text_content}")

# 2. Setup Production Output Folder
output_dir = "production_output"
os.makedirs(output_dir, exist_ok=True)
video_path = os.path.join(output_dir, "short_10sec_video.mp4")

# 3. Create 10-Second 1080x1920 (Shorts Format) Video Frame-by-Frame
width, height = 1080, 1920
fps = 30
duration_sec = 10
total_frames = fps * duration_sec

# Video Writer setup using MP4V codec
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1.6
font_color = (255, 255, 255) # White text
thickness = 4

# Wrap text into lines for Vertical Shorts display
words = text_content.split()
lines = []
current_line = []

for word in words:
    current_line.append(word)
    test_str = " ".join(current_line)
    (w, _), _ = cv2.getTextSize(test_str, font, font_scale, thickness)
    if w > width - 150:
        current_line.pop()
        lines.append(" ".join(current_line))
        current_line = [word]
lines.append(" ".join(current_line))

# Render Frames
for frame_idx in range(total_frames):
    # Dark modern gradient-like background
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:, :] = [30, 20, 15] # Dark Blue/Slate base color
    
    # Calculate centered vertical position for wrapped lines
    line_height = 80
    start_y = (height - (len(lines) * line_height)) // 2
    
    for i, line in enumerate(lines):
        (text_w, text_h), _ = cv2.getTextSize(line, font, font_scale, thickness)
        text_x = (width - text_w) // 2
        text_y = start_y + (i * line_height)
        
        # Draw background shadow for readability
        cv2.putText(frame, line, (text_x + 3, text_y + 3), font, font_scale, (0, 0, 0), thickness + 2)
        # Draw main text
        cv2.putText(frame, line, (text_x, text_y), font, font_scale, font_color, thickness)
    
    out.write(frame)

out.release()
print(f"✅ 10-Second MP4 Video successfully generated at: {video_path}")