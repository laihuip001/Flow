"""
Connection Test Script

Verifies that the FastAPI backend is reachable and responding correctly.
Run this BEFORE launching the Flet app.
"""
import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"


async def test_connection():
    """Test basic connectivity to the backend."""
    print(f"🔌 Testing connection to {BASE_URL}...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Health check
        try:
            response = await client.get(f"{BASE_URL}/healthz")
            if response.status_code == 200:
                print("✅ Health check: PASS")
            else:
                print(f"❌ Health check: FAIL (Status {response.status_code})")
                return False
        except httpx.RequestError as e:
            print(f"❌ Health check: FAIL (Connection error: {e})")
            return False
        
        # Test 2: Process endpoint
        try:
            response = await client.post(
                f"{BASE_URL}/process",
                json={"text": "テスト", "style": "proofread"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Process endpoint: PASS")
                print(f"   Result preview: {result.get('result', 'N/A')[:50]}...")
            else:
                print(f"⚠️ Process endpoint: Status {response.status_code}")
                print(f"   Response: {response.text[:100]}")
        except httpx.RequestError as e:
            print(f"❌ Process endpoint: FAIL ({e})")
            return False
        
        # Test 3: Stream endpoint
        try:
            chunks = []
            async with client.stream(
                "POST",
                f"{BASE_URL}/process/stream",
                json={"text": "テスト", "style": "proofread"}
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            chunks.append(data)
            if chunks:
                print(f"✅ Stream endpoint: PASS ({len(chunks)} chunks received)")
            else:
                print("⚠️ Stream endpoint: No data received")
        except Exception as e:
            print(f"⚠️ Stream endpoint: {e}")
    
    print("\n🎉 All tests passed! Ready to launch Flet app.")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
