import os
import google.generativeai as genai

# Configure Gemini API Key
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("🚀 Requesting production payload using Gemini 1.5 Flash...")

# Explicit model name set as requested
model = genai.GenerativeModel("gemini-1.5-flash-latest")

raw_json_str = None
for attempt in range(4):
    try:
        response = model.generate_content("Generate a viral YouTube Short concept about AI automation.")
        raw_json_str = response.text
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")

if raw_json_str:
    print("Successfully generated response!")
    print(raw_json_str)
else:
    raise Exception("Critical Pipeline Error: Gemini SDK failed to generate response after retries.")