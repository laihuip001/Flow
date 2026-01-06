"""
Benchmark: AI-Clipboard-Pro Latency Test

Gemini API呼び出しのレイテンシを測定し、README記載の「90秒→5秒」を裏付ける。
"""
import time
import os
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from google import genai
from google.genai import types


def benchmark_gemini_direct(model: str = "models/gemini-3-flash-preview", iterations: int = 3) -> dict:
    """
    Gemini API直接呼び出しのレイテンシを測定
    
    Returns:
        dict: {model, iterations, avg_latency_seconds, timings}
    """
    # .env読み込み
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"error": "GEMINI_API_KEY not found in .env"}
    
    client = genai.Client(api_key=api_key)
    
    test_text = "これはベンチマーク用のテストテキストです。日本語の文章を英語に翻訳してください。"
    prompt = f"Translate to professional English. Keep meaning.\n\n[Input]\n{test_text}"
    
    timings = []
    
    for i in range(iterations):
        start = time.time()
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3)
            )
            elapsed = time.time() - start
            timings.append(elapsed)
            print(f"  Iteration {i+1}: {elapsed:.2f}s - {response.text[:50]}...")
        except Exception as e:
            print(f"  Iteration {i+1}: ERROR - {str(e)}")
            timings.append(-1)
    
    valid_timings = [t for t in timings if t > 0]
    avg = sum(valid_timings) / len(valid_timings) if valid_timings else -1
    
    return {
        "model": model,
        "iterations": iterations,
        "avg_latency_seconds": round(avg, 2),
        "timings": timings,
        "success_rate": f"{len(valid_timings)}/{iterations}"
    }


def main():
    print("=" * 60)
    print("AI-Clipboard-Pro Latency Benchmark")
    print("=" * 60)
    
    models = [
        "models/gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
    ]
    
    results = []
    
    for model in models:
        print(f"\n📊 Testing: {model}")
        print("-" * 40)
        result = benchmark_gemini_direct(model, iterations=3)
        results.append(result)
        
        if "error" not in result:
            print(f"  ⏱️ Average: {result['avg_latency_seconds']}s")
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for r in results:
        if "error" in r:
            print(f"  {r.get('model', 'unknown')}: ERROR - {r['error']}")
        else:
            print(f"  {r['model']}: {r['avg_latency_seconds']}s avg ({r['success_rate']})")


if __name__ == "__main__":
    main()
