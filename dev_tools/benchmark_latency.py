import time
import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.processor import CoreProcessor, TextRequest
from src.core.config import settings

# Test payload (approx 100 chars)
TEST_TEXT_100 = "明日の会議は10時から第3会議室で行います。プロジェクトの進捗報告と、来月のスケジュール調整について話し合う予定です。資料の準備をお願いします。"

async def run_benchmark():
    print("🚀 Running Latency Benchmark (100 chars)...")
    print("-" * 50)
    
    processor = CoreProcessor()
    
    # Warmup
    print("🔥 Warming up...")
    try:
        await processor.process(TextRequest(text="warmup", seasoning=10))
    except Exception as e:
        print(f"Warmup failed (API key configured?): {e}")

    # Case 1: Salt Mode (Fastest) + Privacy OFF
    settings.PRIVACY_MODE = False
    start = time.perf_counter()
    res = await processor.process(TextRequest(text=TEST_TEXT_100, seasoning=10)) # Salt
    duration_ms = (time.perf_counter() - start) * 1000
    print(f"⚡ Salt (Privacy OFF): {duration_ms:.1f} ms")
    
    # Case 2: Sauce Mode (Standard) + Privacy OFF
    start = time.perf_counter()
    res = await processor.process(TextRequest(text=TEST_TEXT_100, seasoning=50)) # Sauce
    duration_ms = (time.perf_counter() - start) * 1000
    print(f"🍝 Sauce (Privacy OFF): {duration_ms:.1f} ms")

    # Case 3: Salt Mode + Privacy ON (Legacy)
    settings.PRIVACY_MODE = True
    start = time.perf_counter()
    res = await processor.process(TextRequest(text=TEST_TEXT_100, seasoning=10)) # Salt
    duration_ms = (time.perf_counter() - start) * 1000
    print(f"🛡️ Salt (Privacy ON ): {duration_ms:.1f} ms")

    print("-" * 50)
    print("Done.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
