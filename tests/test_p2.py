import requests
import json
import base64

BASE_URL = "http://localhost:8000"

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print(f"{'='*50}")

def test_analyze():
    print_header("Testing /analyze (Context Mode)")
    test_cases = [
        {"text": "Short text.", "expected": "light"},
        {"text": "Long text with many lines.\n" * 10, "expected": "deep"}
    ]
    
    for case in test_cases:
        try:
            res = requests.post(f"{BASE_URL}/analyze", json={"text": case["text"]})
            data = res.json()
            status = "✅ PASS" if data["mode"] == case["expected"] else "❌ FAIL"
            print(f"{status} [{len(case['text'])} chars] Expected: {case['expected']}, Got: {data['mode']}")
        except Exception as e:
            print(f"❌ FAIL Error: {e}")

def test_history():
    print_header("Testing /history (Context Continuity)")
    
    # Add items
    items = ["History Item 1", "History Item 2", "History Item 3"]
    for item in items:
        requests.post(f"{BASE_URL}/history/add", json={"text": item, "current_app": "TestApp"})
        print(f"Added: {item}")
        
    # Get history
    res = requests.get(f"{BASE_URL}/history")
    data = res.json()
    size = data["size"]
    print(f"History Size: {size}")
    
    if size >= 3 and data["history"][0]["text"] == items[-1]:
        print("✅ PASS: History added and retrieved correctly")
    else:
        print("❌ FAIL: History mismatch")

def test_suggest_style():
    """DEPRECATED: suggest-style is deprecated in v4.0"""
    print_header("Testing /suggest-style (DEPRECATED - Should return default)")
    
    res = requests.post(f"{BASE_URL}/suggest-style", json={"text": "test"})
    data = res.json()
    if data.get("suggested_style") == "default":
        print("✅ PASS: Deprecated endpoint returns default")
    else:
        print(f"❌ FAIL: Expected 'default', got {data.get('suggested_style')}")

try:
    test_analyze()
    test_history()
    test_suggest_style()
    print("\n✅ P2 Test Suite Completed (v4.0)")
except Exception as e:
    print(f"\n❌ Test Suite Failed: {e}")
