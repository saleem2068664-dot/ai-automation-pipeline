import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY nahi mili!")
    exit(1)

# Gemini prompt for daily script creation
prompt = "Generate 1 catchy YouTube Short script about AI trend or tech tip. Include Visual Ideas and Voiceover Script."

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": prompt}]}]
}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    script_content = data['candidates'][0]['content']['parts'][0]['text']
    
    # Save script to a daily file
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"daily_script_{today_date}.txt"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(script_content)
        
    print(f"✅ Successful! Daily script saved into {filename}")
else:
    print(f"❌ Error Code: {response.status_code}")
    print(response.text)