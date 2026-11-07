import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: GEMINI_API_KEY nahi mili!")
    exit(1)

print("✅ GEMINI_API_KEY successfully load ho gayi hai!")

# Simple test prompt sending to Gemini
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
payload = {
    "contents": [{"parts": [{"text": "Hello Gemini! Say 'AI Agent Connected Successfully'"}]}]
}
headers = {'Content-Type': 'application/json'}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    data = response.json()
    reply = data['candidates'][0]['content']['parts'][0]['text']
    print(f"🤖 Gemini ka Reply: {reply}")
else:
    print(f"❌ Error Code: {response.status_code}")
    print(response.text)