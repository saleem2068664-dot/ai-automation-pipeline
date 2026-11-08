import os
from google import genai

# Automatically picks up GEMINI_API_KEY from environment variables
client = genai.Client()

print("🚀 Requesting production payload using Google GenAI SDK...")

raw_json_str = None
for attempt in range(4):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Generate a viral YouTube Short concept about AI automation.",
        )
        raw_json_str = response.text
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")

if raw_json_str:
    print("Successfully generated response!")
    print(raw_json_str)
else:
    raise Exception("Critical Pipeline Error: SDK failed to generate response after retries.")