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
    print_header("Testing /suggest-style (App Name Independence)")
    
    cases = [
        {"text": "お世話になっております。よろしくお願いいたします。", "expected": "business"},
        {"text": "これめっちゃ面白いwww 笑", "expected": "casual"},
        {"text": "Summary: 1. Item 2. Item", "expected": "summary"},
        {"text": "This is an english text.", "expected": "english"}
    ]
    
    for case in cases:
        res = requests.post(f"{BASE_URL}/suggest-style", json={"text": case["text"]})
        data = res.json()
        print(f"Text: {case['text'][:20]}... -> Suggested: {data['suggested_style']}")
        if data["suggested_style"] == case["expected"]:
            print("✅ PASS")
        else:
            print(f"❌ FAIL (Expected {case['expected']})")

try:
    test_analyze()
    test_history()
    test_suggest_style()
    print("\n✅ P2 Test Suite Completed")
except Exception as e:
    print(f"\n❌ Test Suite Failed: {e}")
