import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env読み込み
load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    # .envから読めない場合のフォールバック（configも確認する簡易実装）
    from config import settings
    api_key = settings.GEMINI_API_KEY

print(f"Checking models with API Key: {api_key[:5]}...")

genai.configure(api_key=api_key)

try:
    print("\n📋 Available Models for 'generateContent':")
    print("-" * 50)
    
    count = 0
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            print(f"  Version: {m.version}")
            print(f"  Description: {m.description[:50]}...")
            count += 1
            
    if count == 0:
        print("❌ No models capability found.")
    else:
        print("-" * 50)
        print(f"Total {count} models found.")

except Exception as e:
    print(f"❌ Error fetching models: {e}")
