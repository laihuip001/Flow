"""
Direct Gemini API Speed Test
No FastAPI, No Flet - Just pure API call
"""
import time
import os

# Load API key from .env
api_key = None
if os.path.exists(".env"):
    with open(".env", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env")
    exit(1)

print(f"🔑 API Key: {api_key[:8]}...")

from google import genai

client = genai.Client(api_key=api_key)

test_text = "これはテスト文章です。誤字脱字があれば修正してください。"

print("\n" + "="*50)
print("Testing gemini-1.5-flash...")
print("="*50)

start = time.time()
try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=f"Fix typos only:\n\n{test_text}"
    )
    elapsed = time.time() - start
    print(f"✅ Response in {elapsed:.2f}s:")
    print(response.text[:200] if response.text else "Empty")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Error after {elapsed:.2f}s: {e}")

print("\n" + "="*50)
print("Testing gemini-2.0-flash-lite (fastest)...")
print("="*50)

start = time.time()
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=f"Fix typos only:\n\n{test_text}"
    )
    elapsed = time.time() - start
    print(f"✅ Response in {elapsed:.2f}s:")
    print(response.text[:200] if response.text else "Empty")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Error after {elapsed:.2f}s: {e}")

print("\n" + "="*50)
print("Testing gemini-2.0-flash...")
print("="*50)

start = time.time()
try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Fix typos only:\n\n{test_text}"
    )
    elapsed = time.time() - start
    print(f"✅ Response in {elapsed:.2f}s:")
    print(response.text[:200] if response.text else "Empty")
except Exception as e:
    elapsed = time.time() - start
    print(f"❌ Error after {elapsed:.2f}s: {e}")

print("\n✅ Test complete!")
input("Press Enter to close...")
