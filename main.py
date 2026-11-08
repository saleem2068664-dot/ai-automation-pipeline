import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY environment variable not found!")
    exit(1)

# Professional Master System Prompt for Advanced Visual & Audio Production
system_prompt = """
You are an elite AI Content Director and Automation Engine for ultra-viral YouTube Shorts and Reels.
Analyze current high-performing video structures (hooks, high-retention pacing, atmospheric visual storytelling).

Generate a fully structured production payload in strictly valid JSON format without markdown code blocks.
The JSON must follow this exact structure:
{
  "project_title": "String",
  "niche": "String",
  "target_audience": "String",
  "hook_first_3_sec": "String",
  "voiceover_script": "Full script line by line with timing cues",
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "0:00-0:03",
      "voiceover": "Line spoken",
      "visual_description": "Cinematic visual description",
      "ai_video_prompt": "Ultra-detailed prompt featuring lighting, camera motion, render engine parameters",
      "audio_sfx_prompt": "Sound effect direction"
    }
  ],
  "metadata": {
    "title_options": ["Option 1", "Option 2", "Option 3"],
    "description": "Optimized description with hashtags",
    "tags": ["tag1", "tag2"]
  }
}
"""

user_topic_prompt = "Create an advanced, high-retention viral YouTube Short concept about 'Breakthrough AI Automation and Future Robotics'. Ensure cinematic visual prompts suited for AI video generation engines."

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [
        {
            "parts": [
                {"text": system_prompt + "\n\nTask: " + user_topic_prompt}
            ]
        }
    ],
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
    except Exception as e:
        print("⚠️ Warning: Output was not clean JSON, saving raw response.")
        production_data = {"raw_output": raw_json_str}

    # Timestamped folder structure for production output
    today_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("production_output", today_stamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Save Full JSON Production Bundle
    json_path = os.path.join(output_dir, "production_blueprint.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(production_data, f, indent=2, ensure_ascii=False)
        
    # 2. Save Readable Studio Script & Prompts
    script_path = os.path.join(output_dir, "studio_script.md")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(f"# Project: {production_data.get('project_title', 'Viral Short')}\n\n")
        f.write(f"**Hook (0-3s):** {production_data.get('hook_first_3_sec', '')}\n\n")
        f.write("## 🎙️ Voiceover Script\n")
        f.write(f"{production_data.get('voiceover_script', '')}\n\n")
        f.write("## 🎬 Scene Breakdown & AI Video Prompts\n")
        
        scenes = production_data.get("scenes", [])
        for sc in scenes:
            f.write(f"### Scene {sc.get('scene_number')} ({sc.get('timestamp')})\n")
            f.write(f"- **Voiceover:** {sc.get('voiceover')}\n")
            f.write(f"- **Visual:** {sc.get('visual_description')}\n")
            f.write(f"- **AI Prompt:** `{sc.get('ai_video_prompt')}`\n")
            f.write(f"- **SFX:** {sc.get('audio_sfx_prompt')}\n\n")

    print(f"✅ Extreme Production Bundle successfully generated in: {output_dir}")
else:
    print(f"❌ API Error Code: {response.status_code}")
    print(response.text)