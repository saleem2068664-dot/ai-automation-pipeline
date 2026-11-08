import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
pixabay_key = os.getenv("PIXABAY_API_KEY")

if not gemini_key:
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
      "search_keyword": "single concise english keyword for video search (e.g. robot, futuristic, space)",
      "voiceover": "Line spoken",
      "visual_description": "Cinematic visual description",
      "ai_video_prompt": "Ultra-detailed prompt featuring lighting, camera motion"
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

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"

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
    videos_dir = os.path.join(output_dir, "scene_videos")
    os.makedirs(videos_dir, exist_ok=True)
    
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
    if voiceover_text:
        print("🔊 Generating voiceover audio file (.mp3)...")
        tts = gTTS(text=voiceover_text, lang='en', slow=False)
        audio_path = os.path.join(output_dir, "voiceover_audio.mp3")
        tts.save(audio_path)
        print(f"✅ Voiceover audio successfully saved: {audio_path}")

    # 4. Fetch HD Stock Video Clips via Pixabay API
    scenes = production_data.get('scenes', [])
    if pixabay_key and scenes:
        print("🎬 Fetching HD stock video clips from Pixabay API...")
        for scene in scenes:
            scene_num = scene.get('scene_number', 1)
            query = scene.get('search_keyword', 'technology')
            print(f"🔍 Searching video for Scene {scene_num} (Query: '{query}')...")
            
            pixabay_url = f"https://pixabay.com/api/videos/?key={pixabay_key}&q={query}&video_type=film&per_page=3"
            res = requests.get(pixabay_url)
            
            if res.status_code == 200:
                pix_data = res.json()
                hits = pix_data.get('hits', [])
                if hits:
                    video_files = hits[0].get('videos', {})
                    video_download_url = video_files.get('medium', {}).get('url') or video_files.get('small', {}).get('url')
                    
                    if video_download_url:
                        v_res = requests.get(video_download_url)
                        v_filename = os.path.join(videos_dir, f"scene_{scene_num}.mp4")
                        with open(v_filename, "wb") as vf:
                            vf.write(v_res.content)
                        print(f"✅ Saved video for Scene {scene_num}: {v_filename}")
                else:
                    print(f"⚠️ No videos found for query '{query}'")

    print(f"✅ Extreme Production Bundle successfully compiled in: {output_dir}")
else:
    print(f"❌ API Error Code: {response.status_code}")
    print(response.text)