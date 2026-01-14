"""
Direct test with the EXACT user text
"""
import time, os

api_key = None
for path in [".env", "../.env"]:
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
        if api_key: break

print(f"🔑 API Key: {api_key[:8] if api_key else 'NOT FOUND'}...")

from google import genai

client = genai.Client(api_key=api_key)

# The exact user text
user_text = """PrivacyScannerの不完全性:** 「検知して警告する」方式に変更されたが、検知パターンが正規表現（Regex）に依存している。文脈的な機密情報（プロジェクト名、社内用語等）が漏洩するリスクをどう評価し、Gemini Nano等を用いたオンデバイスでのセマンティック・スキャンへどう移行すべきか。"""

print(f"\n📝 Input length: {len(user_text)} chars")
print("="*50)

start = time.time()
try:
    response = client.models.generate_content(
        model="models/gemini-3-flash-preview",
        contents=f"Summarize in bullet points:\n\n{user_text}"
    )
    elapsed = time.time() - start
    print(f"✅ Response in {elapsed:.2f}s:")
    print(response.text[:300] if response.text else "Empty")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Error after {elapsed:.2f}s: {e}")

input("\nPress Enter...")
