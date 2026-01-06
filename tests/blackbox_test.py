import requests
import time
import sys
import json

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "your_secret_token_here"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def test_health():
    try:
        resp = requests.get(f"{BASE_URL}/healthz")
        if resp.status_code == 200:
            log("Health check passed", "SUCCESS")
            return True
        else:
            log(f"Health check failed: {resp.status_code}", "FAIL")
            return False
    except Exception as e:
        log(f"Connection failed: {e}", "FAIL")
        return False

def test_normal_business():
    log("Testing Normal Case: Business Style...")
    payload = {
        "text": "やあ、元気？これやっといて。",
        "seasoning": 50,
        "acknowledge_risks": True
    }
    try:
        resp = requests.post(f"{BASE_URL}/process", json=payload, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if "converted" in data:
                log(f"Response: {data['converted'][:50]}...", "SUCCESS")
            else:
                log(f"Unexpected response format: {data}", "FAIL")
        else:
            log(f"Request failed: {resp.status_code} - {resp.text}", "FAIL")
    except Exception as e:
        log(f"Exception: {e}", "FAIL")

def test_error_invalid_seasoning():
    log("Testing Error Case: Invalid Seasoning Value...")
    payload = {
        "text": "test",
        "seasoning": 999,  # Invalid but should still process
        "acknowledge_risks": True
    }
    try:
        resp = requests.post(f"{BASE_URL}/process", json=payload, headers=HEADERS)
        
        log(f"Status Code: {resp.status_code}", "INFO")
        if resp.status_code != 200:
             log("Got non-200 response as expected (or handled error)", "SUCCESS")
             log(f"Response: {resp.text}", "INFO")
        else:
             log("Got 200 response - API might be permissive (Defaulting?)", "WARNING")
    except Exception as e:
        log(f"Exception: {e}", "FAIL")

def test_security_pii():
    log("Testing Security Case: PII Detection...")
    payload = {
        "text": "My email is test_user@example.com and phone is 090-1234-5678"
    }
    try:
        # PII scan might not need auth, or maybe it does. Let's send it to be safe.
        resp = requests.post(f"{BASE_URL}/scan", json=payload, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("has_risks") is True:
                log(f"PII Detected: {data.get('risks')}", "SUCCESS")
            else:
                log(f"PII NOT Detected (Unexpected): {data}", "FAIL")
        elif resp.status_code == 404:
             log("/scan endpoint not found. Trying /privacy_check...", "WARNING")
             resp = requests.post(f"{BASE_URL}/privacy_check", json=payload, headers=HEADERS)
             if resp.status_code == 200:
                data = resp.json()
                if data.get("has_risks") is True:
                    log(f"PII Detected: {data.get('risks')}", "SUCCESS")
                else:
                    log(f"PII NOT Detected: {data}", "FAIL")
             else:
                log(f"Failed to find privacy endpoint: {resp.status_code}", "FAIL")
        else:
            log(f"Request failed: {resp.status_code}", "FAIL")
    except Exception as e:
        log(f"Exception: {e}", "FAIL")

if __name__ == "__main__":
    # Wait for server to start
    for _ in range(10):
        if test_health():
            break
        time.sleep(1)
    
    test_normal_business()
    test_error_invalid_seasoning()
    test_security_pii()
