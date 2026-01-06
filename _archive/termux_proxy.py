"""
AI Clipboard Pro - Termux Lightweight Proxy (v3.0.2)

軽量プロキシモード: requestsパッケージのみを使用し、重い依存関係を回避。
Termux環境での起動が高速化され、メモリ使用量も削減される。

このスクリプトは、実際の処理をPC/VPS/Cloudサーバーに委譲する。
Termuxでは最小限のHTTPプロキシとして機能する。

使用方法:
    pip install requests flask  # 軽量な依存のみ
    python termux_proxy.py

環境変数:
    - BACKEND_URL: プロキシ先のサーバーURL (例: https://your-pc.ngrok.io)
    - PROXY_PORT: このプロキシのポート (デフォルト: 8000)
    - API_TOKEN: 認証トークン（オプション）
"""

import os
import sys

# 依存ライブラリチェック
try:
    import requests
except ImportError:
    print("❌ Error: requests ライブラリが必要です")
    print("   pip install requests")
    sys.exit(1)

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("❌ Error: Flask ライブラリが必要です")
    print("   pip install flask")
    sys.exit(1)

# --- 設定 ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8080")
PROXY_PORT = int(os.environ.get("PROXY_PORT", "8000"))
API_TOKEN = os.environ.get("API_TOKEN", "")
TIMEOUT = 60  # バックエンドへのタイムアウト（秒）

app = Flask(__name__)

def get_headers():
    """認証ヘッダーを生成"""
    headers = {"Content-Type": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return headers

def proxy_request(method, path, json_body=None):
    """バックエンドへリクエストをプロキシ"""
    url = f"{BACKEND_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, headers=get_headers(), timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, json=json_body, headers=get_headers(), timeout=TIMEOUT)
        else:
            return jsonify({"error": "unsupported_method"}), 405
        
        return response.json(), response.status_code
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "backend_timeout",
            "message": f"バックエンドサーバー ({BACKEND_URL}) がタイムアウトしました",
            "action": "バックエンドサーバーの状態を確認してください"
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "backend_unreachable",
            "message": f"バックエンドサーバー ({BACKEND_URL}) に接続できません",
            "action": "BACKEND_URL環境変数を確認してください"
        }), 502
    except Exception as e:
        return jsonify({
            "error": "proxy_error",
            "message": str(e)
        }), 500

# --- ヘルスチェック ---
@app.route("/", methods=["GET"])
def health_check():
    """ローカルプロキシのヘルスチェック"""
    return jsonify({
        "status": "running",
        "mode": "proxy",
        "version": "3.0.2",
        "backend": BACKEND_URL
    })

@app.route("/healthz", methods=["GET"])
def detailed_health():
    """詳細ヘルスチェック（バックエンド疎通確認含む）"""
    checks = {
        "proxy": "ok",
        "backend": "unknown"
    }
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if response.status_code == 200:
            checks["backend"] = "ok"
        else:
            checks["backend"] = f"error: status {response.status_code}"
    except Exception as e:
        checks["backend"] = f"error: {type(e).__name__}"
    
    all_ok = all(v == "ok" for v in checks.values())
    
    return jsonify({
        "status": "running" if all_ok else "degraded",
        "mode": "proxy",
        "version": "3.0.2",
        "backend_url": BACKEND_URL,
        "checks": checks
    })

# --- プロキシエンドポイント ---
@app.route("/styles", methods=["GET"])
def styles():
    return proxy_request("GET", "/styles")

@app.route("/scan", methods=["POST"])
def scan():
    return proxy_request("POST", "/scan", request.get_json())

@app.route("/process", methods=["POST"])
def process():
    return proxy_request("POST", "/process", request.get_json())

@app.route("/prefetch", methods=["POST"])
def prefetch():
    return proxy_request("POST", "/prefetch", request.get_json())

@app.route("/prefetch/<text_hash>", methods=["GET"])
def get_prefetch(text_hash):
    return proxy_request("GET", f"/prefetch/{text_hash}")

@app.route("/log_correction", methods=["POST"])
def log_correction():
    return proxy_request("POST", "/log_correction", request.get_json())

# --- 起動 ---
if __name__ == "__main__":
    print("=" * 50)
    print("🌐 AI Clipboard Pro - Termux Lightweight Proxy")
    print("=" * 50)
    print(f"📍 Proxy Port: {PROXY_PORT}")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"🔐 Auth: {'Enabled' if API_TOKEN else 'Disabled'}")
    print("=" * 50)
    print()
    
    if BACKEND_URL == "http://localhost:8080":
        print("⚠️  警告: BACKEND_URL がデフォルト値です")
        print("   実際のバックエンドURLを環境変数で設定してください:")
        print("   export BACKEND_URL=https://your-server.ngrok.io")
        print()
    
    app.run(host="0.0.0.0", port=PROXY_PORT, debug=False)
