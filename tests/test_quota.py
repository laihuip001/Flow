"""
Test available models for quota
"""
import time, os

api_key = None
if os.path.exists(".env"):
    with open(".env", encoding="utf-8") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break

from google import genai
client = genai.Client(api_key=api_key)

test_text = "これはテスト文章です"

models_to_test = [
    "models/gemini-3-flash-preview",
    "models/gemini-flash-latest",
    "models/gemini-flash-lite-latest",
    "models/gemini-2.5-flash",
]

for model in models_to_test:
    print(f"\n{'='*50}")
    print(f"Testing {model}...")
    print("="*50)
    
    start = time.time()
    try:
        response = client.models.generate_content(
            model=model,
            contents=f"Fix typos:\n{test_text}"
        )
        elapsed = time.time() - start
        print(f"✅ SUCCESS in {elapsed:.2f}s")
        print(f"   Response: {response.text[:100] if response.text else 'Empty'}")
    except Exception as e:
        elapsed = time.time() - start
        err_str = str(e)
        if "429" in err_str:
            print(f"❌ QUOTA EXHAUSTED ({elapsed:.2f}s)")
        elif "404" in err_str:
            print(f"❌ MODEL NOT FOUND ({elapsed:.2f}s)")
        else:
            print(f"❌ ERROR ({elapsed:.2f}s): {err_str[:80]}")

print("\n✅ Test complete!")
input("Press Enter...")
