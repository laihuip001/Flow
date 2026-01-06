import httpx
import asyncio
import json
import os
import sys

# Windowsでの文字化け防止
sys.stdout.reconfigure(encoding='utf-8')

SERVER_URL = "http://localhost:8000/process/stream"
API_TOKEN = os.environ.get("API_TOKEN", "")

INPUT_TEXT = """
この文章を、箇条書きで分かりやすく要約してください。
AIの進化により、私たちの生活は大きく変化しています。特に生成AIの登場は、クリエイティブな作業や事務作業の効率化に貢献しています。しかし、倫理的な問題や著作権の問題など、解決すべき課題も残されています。
"""

async def main():
    headers = {}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    
    payload = {
        "text": INPUT_TEXT,
        "style": "summary",
        "current_app": "test_script"
    }
    
    print(f"🌊 Connecting to stream: {SERVER_URL}")
    print("--- Stream Start ---")
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", SERVER_URL, json=payload, headers=headers, timeout=60.0) as response:
            if response.status_code != 200:
                print(f"\n❌ Error: {response.status_code}")
                print(await response.read())
                return
            
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[len("data: "):]
                    if data == "[DONE]":
                        print("\n--- Stream End ---")
                        break
                    
                    # リアルタイム表示（改行なしでflush）
                    print(data, end="", flush=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAborted.")
    except Exception as e:
        print(f"\nError: {e}")
