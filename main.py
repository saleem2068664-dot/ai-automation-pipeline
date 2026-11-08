import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from gtts import gTTS
from moviepy.editor import AudioFileClip, ColorClip

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not found!")
    exit(1)

system_prompt = """
You are an elite AI Content Director and Automation Engine for ultra-viral YouTube Shorts and Reels.
Generate a fully structured production payload in strictly valid JSON format without markdown code blocks.
The JSON must follow this exact structure:
{
  "project_title": "String",
  "niche": "String",
  "target_audience": "String",
  "hook_first_3_sec": "String",
  "voiceover_script": "Full script line by line for the voiceover",
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "0:00-0:03",
      "voiceover": "Line spoken",
      "visual_description": "Cinematic visual description",
      "ai_video_prompt": "Ultra-detailed prompt featuring lighting, camera motion",
      "audio_sfx_prompt": "Sound effect direction"
    }
  ],
  "metadata": {
    "title_options": ["Option 1", "Option 2"],
    "description": "Optimized description with hashtags",
    "tags": ["tag1", "tag2"]
  }
}
"""

user_topic_prompt = "Create an advanced, high-retention viral YouTube Short concept about 'Breakthrough AI Automation and Future Robotics'."

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [{"parts": [{"text": system_prompt + "\n\nTask: " + user_topic_prompt}]}],
    "generationConfig": {
        "response_mime_type": "application/json",
        "temperature": 0.7
    }
}

headers = {'Content-Type': 'application/json'}

print("🚀 Requesting production payload from Gemini API...")
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    res_data = response.json()
    raw_json_str = res_data['candidates'][0]['content']['parts'][0]['text']
    
    try:
        production_data = json.loads(raw_json_str)
    except:
        production_data = {"raw_output": raw_json_str}

    today_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("production_output", today_stamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Save JSON Blueprint
    json_path = os.path.join(output_dir, "production_blueprint.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(production_data, f, indent=2, ensure_ascii=False)
        
    # 2. Save Markdown Studio Script
    script_path = os.path.join(output_dir, "studio_script.md")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(f"# Project: {production_data.get('project_title', 'Viral Short')}\n\n")
        f.write(f"**Hook (0-3s):** {production_data.get('hook_first_3_sec', '')}\n\n")
        f.write("## 🎙️ Voiceover Script\n")
        f.write(f"{production_data.get('voiceover_script', '')}\n\n")

    # 3. Generate Text-to-Speech Voiceover Audio (.mp3)
    voiceover_text = production_data.get('voiceover_script', '')
    audio_path = None
    if voiceover_text:
        print("🔊 Generating voiceover audio file (.mp3)...")
        tts = gTTS(text=voiceover_text, lang='en', slow=False)
        audio_path = os.path.join(output_dir, "voiceover_audio.mp3")
        tts.save(audio_path)
        print(f"✅ Voiceover audio saved: {audio_path}")

    # 4. Render Final HD Video Short (.mp4) using MoviePy
    if audio_path and os.path.exists(audio_path):
        print("🎬 Rendering final HD video short (.mp4)...")
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Create vertical 1080x1920 cinematic background canvas
            video_clip = ColorClip(size=(1080, 1920), color=(15, 15, 22), duration=duration)
            video_clip = video_clip.set_audio(audio_clip)
            
            final_video_path = os.path.join(output_dir, "final_short.mp4")
            video_clip.write_videofile(
                final_video_path, 
                fps=24, 
                codec="libx264", 
                audio_codec="aac",
                logger=None
            )
            print(f"✅ Final Video Short successfully rendered: {final_video_path}")
        except Exception as e:
            print(f"⚠️ Video rendering warning/error: {e}")

    print(f"✅ Extreme Production Bundle fully compiled in: {output_dir}")
else:
    print(f"❌ API Error Code: {response.status_code}")
    print(response.text)