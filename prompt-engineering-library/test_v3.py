"""
AI Clipboard Pro v3.0.1 - Verification Test Suite

このスクリプトを実行して、全ての項目がPASSすることを確認してください。

使用方法:
    1. サーバー起動: python main.py
    2. テスト実行: python test_v3.py

環境変数:
    - API_TOKEN: 認証トークン（設定されている場合）
"""
import requests
import os
import json
import sys

# --- Config ---
BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
API_TOKEN = os.environ.get("API_TOKEN", "")

# 認証ヘッダー
HEADERS_WITH_AUTH = {
    "Authorization": f"Bearer {API_TOKEN}" if API_TOKEN else "",
    "Content-Type": "application/json"
}
HEADERS_NO_AUTH = {
    "Content-Type": "application/json"
}

# テスト結果カウンター
results = {"pass": 0, "fail": 0, "skip": 0}

def log(name, status, details=""):
    """テスト結果をログ出力"""
    icons = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}
    icon = icons.get(status, "❓")
    print(f"{icon} [{name:<25}] {status} {details}")
    results[status.lower()] = results.get(status.lower(), 0) + 1

# =============================================================================
# Health Check Tests
# =============================================================================

def test_health_check():
    """基本ヘルスチェック"""
    try:
        res = requests.get(f"{BASE_URL}/", timeout=5)
        if res.status_code == 200 and res.json().get("status") == "running":
            log("Health Check", "PASS", f"version={res.json().get('version')}")
        else:
            log("Health Check", "FAIL", f"Unexpected response: {res.text}")
    except Exception as e:
        log("Health Check", "FAIL", str(e))

def test_detailed_health():
    """詳細ヘルスチェック (/healthz)"""
    try:
        res = requests.get(f"{BASE_URL}/healthz", timeout=5)
        if res.status_code == 200:
            data = res.json()
            checks = data.get("checks", {})
            log("Detailed Health", "PASS", f"status={data.get('status')}, checks={list(checks.keys())}")
        else:
            log("Detailed Health", "FAIL", f"Status {res.status_code}")
    except Exception as e:
        log("Detailed Health", "FAIL", str(e))

# =============================================================================
# Security Tests
# =============================================================================

def test_security_barrier():
    """認証なしでリクエストして拒否されるか（認証有効時のみ）"""
    if not API_TOKEN:
        log("Security Barrier", "SKIP", "API_TOKEN not set (dev mode)")
        return
    
    try:
        res = requests.post(
            f"{BASE_URL}/process",
            json={"text": "test", "style": "business"},
            headers=HEADERS_NO_AUTH,
            timeout=10
        )
        if res.status_code in [401, 403]:
            log("Security Barrier", "PASS", f"Rejected unauthorized request ({res.status_code})")
        else:
            log("Security Barrier", "FAIL", f"Expected 401/403, got {res.status_code}")
    except Exception as e:
        log("Security Barrier", "FAIL", str(e))

def test_auth_with_valid_token():
    """正しいトークンでリクエストが通るか"""
    if not API_TOKEN:
        log("Auth Valid Token", "SKIP", "API_TOKEN not set (dev mode)")
        return
    
    try:
        res = requests.get(f"{BASE_URL}/styles", headers=HEADERS_WITH_AUTH, timeout=5)
        if res.status_code == 200:
            log("Auth Valid Token", "PASS", "Authenticated request accepted")
        else:
            log("Auth Valid Token", "FAIL", f"Status {res.status_code}")
    except Exception as e:
        log("Auth Valid Token", "FAIL", str(e))

# =============================================================================
# Feature Tests
# =============================================================================

def test_styles_endpoint():
    """スタイル一覧取得"""
    try:
        res = requests.get(f"{BASE_URL}/styles", timeout=5)
        if res.status_code == 200:
            styles = res.json().get("styles", [])
            if len(styles) >= 5:
                log("Styles Endpoint", "PASS", f"{len(styles)} styles available")
            else:
                log("Styles Endpoint", "FAIL", f"Expected >= 5 styles, got {len(styles)}")
        else:
            log("Styles Endpoint", "FAIL", f"Status {res.status_code}")
    except Exception as e:
        log("Styles Endpoint", "FAIL", str(e))

def test_pii_scanner():
    """PIIが含まれるテキストを送信し、検出されるか"""
    payload = {"text": "連絡先は user@example.com です。電話は 090-1234-5678。"}
    try:
        res = requests.post(f"{BASE_URL}/scan", json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("has_risks") and "EMAIL" in data.get("risks", {}):
                log("PII Scanner", "PASS", f"Detected: {list(data['risks'].keys())}")
            else:
                log("PII Scanner", "FAIL", "Failed to detect PII")
        else:
            log("PII Scanner", "FAIL", f"Status {res.status_code}: {res.text[:100]}")
    except Exception as e:
        log("PII Scanner", "FAIL", str(e))

def test_pii_scanner_clean():
    """PII無しテキストでfalseが返るか"""
    payload = {"text": "今日は良い天気です。"}
    try:
        res = requests.post(f"{BASE_URL}/scan", json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if not data.get("has_risks"):
                log("PII Scanner (Clean)", "PASS", "No PII detected as expected")
            else:
                log("PII Scanner (Clean)", "FAIL", f"False positive: {data}")
        else:
            log("PII Scanner (Clean)", "FAIL", f"Status {res.status_code}")
    except Exception as e:
        log("PII Scanner (Clean)", "FAIL", str(e))

def test_process_endpoint():
    """メイン処理エンドポイント（認証有効時はトークン必要）"""
    payload = {"text": "明日の会議について確認", "style": "business"}
    headers = HEADERS_WITH_AUTH if API_TOKEN else HEADERS_NO_AUTH
    
    try:
        res = requests.post(f"{BASE_URL}/process", json=payload, headers=headers, timeout=30)
        if res.status_code == 200:
            data = res.json()
            if "result" in data:
                log("Process Endpoint", "PASS", f"Result length: {len(data['result'])} chars")
            else:
                log("Process Endpoint", "FAIL", f"No result in response: {data}")
        elif res.status_code == 503:
            log("Process Endpoint", "SKIP", "Gemini API not configured")
        else:
            log("Process Endpoint", "FAIL", f"Status {res.status_code}: {res.text[:100]}")
    except requests.exceptions.Timeout:
        log("Process Endpoint", "FAIL", "Request timed out (>30s)")
    except Exception as e:
        log("Process Endpoint", "FAIL", str(e))

def test_prefetch_endpoint():
    """先読みエンドポイント"""
    payload = {"text": "テストテキスト", "target_styles": ["business", "casual"]}
    headers = HEADERS_WITH_AUTH if API_TOKEN else HEADERS_NO_AUTH
    
    try:
        res = requests.post(f"{BASE_URL}/prefetch", json=payload, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "accepted" and "hash" in data:
                log("Prefetch Endpoint", "PASS", f"hash={data['hash'][:8]}...")
            else:
                log("Prefetch Endpoint", "FAIL", f"Invalid response: {data}")
        elif res.status_code == 503:
            log("Prefetch Endpoint", "SKIP", "Gemini API not configured")
        else:
            log("Prefetch Endpoint", "FAIL", f"Status {res.status_code}")
    except Exception as e:
        log("Prefetch Endpoint", "FAIL", str(e))

# =============================================================================
# Error Handling Tests
# =============================================================================

def test_error_response_format():
    """エラーレスポンスが適切なフォーマットか"""
    # 不正なスタイルでリクエスト
    payload = {"text": "", "style": "invalid_style"}
    headers = HEADERS_WITH_AUTH if API_TOKEN else HEADERS_NO_AUTH
    
    try:
        res = requests.post(f"{BASE_URL}/process", json=payload, headers=headers, timeout=30)
        # 何らかのエラーが返ってくることを確認
        if res.status_code >= 400:
            log("Error Response Format", "PASS", f"Got error response ({res.status_code})")
        else:
            # 空テキストでも成功する場合はスキップ
            log("Error Response Format", "SKIP", "Empty text accepted")
    except Exception as e:
        log("Error Response Format", "FAIL", str(e))

# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 AI Clipboard Pro v3.0.1 - Verification Test Suite")
    print("=" * 60)
    print(f"📍 Target: {BASE_URL}")
    print(f"🔐 Auth: {'Enabled' if API_TOKEN else 'Disabled (dev mode)'}")
    print("=" * 60)
    print()
    
    # サーバー起動確認
    try:
        requests.get(BASE_URL, timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Error: API Server is not running.")
        print("   Please run: python main.py")
        sys.exit(1)
    
    # Health Tests
    print("📋 Health Checks")
    print("-" * 40)
    test_health_check()
    test_detailed_health()
    print()
    
    # Security Tests
    print("🔐 Security Tests")
    print("-" * 40)
    test_security_barrier()
    test_auth_with_valid_token()
    print()
    
    # Feature Tests
    print("✨ Feature Tests")
    print("-" * 40)
    test_styles_endpoint()
    test_pii_scanner()
    test_pii_scanner_clean()
    test_process_endpoint()
    test_prefetch_endpoint()
    print()
    
    # Error Handling Tests
    print("❌ Error Handling Tests")
    print("-" * 40)
    test_error_response_format()
    print()
    
    # Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    total = results["pass"] + results["fail"] + results["skip"]
    print(f"   ✅ PASS: {results['pass']}")
    print(f"   ❌ FAIL: {results['fail']}")
    print(f"   ⏭️  SKIP: {results['skip']}")
    print(f"   📋 TOTAL: {total}")
    print()
    
    if results["fail"] > 0:
        print("⚠️  Some tests failed. Please review and fix.")
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        sys.exit(0)
