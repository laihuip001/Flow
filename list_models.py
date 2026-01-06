"""
List all available Gemini models
"""
import os

api_key = None
if os.path.exists(".env"):
    with open(".env", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    print("❌ GEMINI_API_KEY not found")
    exit(1)

from google import genai
client = genai.Client(api_key=api_key)

print("📋 Available Models:")
print("="*60)

for model in client.models.list():
    name = model.name
    # Only show generative models
    if "generate" in str(model.supported_actions).lower():
        print(f"  {name}")

print("\n" + "="*60)
print("Done!")
input("Press Enter...")
