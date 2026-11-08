import os
import cohere

# Configure Cohere Client using GitHub Secret
api_key = os.environ.get("COHERE_API_KEY")
co = cohere.ClientV2(api_key=api_key)

print("🚀 Requesting production payload using Cohere API...")

raw_json_str = None
for attempt in range(4):
    try:
        response = co.chat(
            model="command-r-08-2024",
            messages=[
                {
                    "role": "user",
                    "content": "Generate a viral YouTube Short concept about AI automation.",
                }
            ],
        )
        raw_json_str = response.message.content[0].text
        break
    except Exception as e:
        print(f"Attempt {attempt+1} failed: {e}")

if raw_json_str:
    print("Successfully generated response!")
    print(raw_json_str)
else:
    raise Exception("Critical Pipeline Error: Cohere API failed to generate response after retries.")