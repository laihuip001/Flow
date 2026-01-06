import google.generativeai as genai
import os

# APIキー設定
api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyCYehgUDkUliA9h50Ic--SXSZHyUOvZtqs")
genai.configure(api_key=api_key)

print("Testing Gemini API...")
model = genai.GenerativeModel("models/gemini-flash-latest")

try:
    response = model.generate_content("Hello, say hi in Japanese")
    print("Success!")
    print(response.text)
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")

print("Done.")
