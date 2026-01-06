from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import TextRequest, PrefetchRequest, ScanResponse, PrefetchCache, ErrorResponse
from config import settings
import logic
import asyncio
from datetime import datetime
import os

init_db()
app = FastAPI(
    title="AI Clipboard Pro v3.0.1",
    description="The Unbreakable Hybrid - Production Ready",
    version="3.0.1"
)

# CORS設定（ブラウザからのアクセスを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル（GUI）をマウント
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# GUIのルートページ
@app.get("/gui", tags=["GUI"])
async def gui_page():
    """Web GUIを表示"""
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"error": "GUI not found", "hint": "Place index.html in ./static/"}

# --- 🔐 認証ミドルウェア (v3.0.1) ---
async def verify_token(authorization: str = Header(None)):
    """
    Bearer Token認証
    API_TOKENが設定されている場合のみ認証を要求
    """
    # 認証が設定されていない場合はスキップ（開発モード）
    if not settings.API_TOKEN:
        return True
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "unauthorized",
                "message": "認証が必要です",
                "action": "Authorization: Bearer <token> ヘッダーを追加してください"
            }
        )
    
    # Bearer token形式をチェック
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "invalid_auth_format",
                "message": "認証形式が不正です",
                "action": "Authorization: Bearer <token> 形式で指定してください"
            }
        )
    
    if parts[1] != settings.API_TOKEN:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "forbidden",
                "message": "トークンが無効です",
                "action": "正しいトークンを指定してください"
            }
        )
    
    return True

# --- 🏥 ヘルスチェック (v3.0.1) ---
@app.get("/", tags=["Health"])
def health_check():
    """基本的なヘルスチェック"""
    return {"status": "running", "version": "3.0.1"}

@app.get("/healthz", tags=["Health"])
def detailed_health_check():
    """
    詳細ヘルスチェック（監視ツール向け）
    
    - status: running/degraded/down
    - checks: 各コンポーネントの状態
    """
    checks = {
        "api": "ok",
        "gemini": "unknown",
        "database": "unknown"
    }
    
    # DB接続チェック
    try:
        from database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {type(e).__name__}"
    
    # Gemini API設定チェック
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        checks["gemini"] = "configured"
    else:
        checks["gemini"] = "not_configured"
    
    # 総合ステータス
    all_ok = all(v in ["ok", "configured"] for v in checks.values())
    
    return {
        "status": "running" if all_ok else "degraded",
        "version": "3.0.1",
        "timestamp": datetime.utcnow().isoformat(),
        "auth_enabled": bool(settings.API_TOKEN),
        "checks": checks
    }

# --- 🎨 スタイル一覧 ---
@app.get("/styles", tags=["Core"])
def list_styles():
    """利用可能なスタイル一覧"""
    return {
        "styles": [
            {"id": "business", "name": "ビジネス", "description": "丁寧・フォーマル"},
            {"id": "casual", "name": "カジュアル", "description": "フランク・絵文字あり"},
            {"id": "summary", "name": "要約", "description": "箇条書き・簡潔"},
            {"id": "english", "name": "英語翻訳", "description": "ビジネス英語"},
            {"id": "proofread", "name": "校正", "description": "誤字脱字修正のみ"}
        ]
    }

# --- ⚙️ メイン処理 (認証付き) ---
@app.post("/process", tags=["Core"], dependencies=[Depends(verify_token)])
def process_text(req: TextRequest):
    """
    メイン処理: スタイル指定でテキスト変換
    
    認証が有効な場合、Authorization: Bearer <token> ヘッダーが必要
    """
    result = logic.process_sync(req)
    
    # エラーレスポンスの場合は適切なステータスコードを返す
    if "error" in result:
        if result["error"] == "blocked" or result["error"] == "safety_blocked":
            raise HTTPException(status_code=400, detail=result)
        else:
            raise HTTPException(status_code=500, detail=result)
    
    return result

# --- 🛡️ 安全スキャン ---
@app.post("/scan", response_model=ScanResponse, tags=["Safety"])
def scan_text(req: TextRequest):
    """個人情報検知（認証不要）"""
    scanner = logic.PrivacyScanner()
    result = scanner.scan(req.text)
    if result["has_risks"]:
        result["message"] = f"⚠️ {result['risk_count']}件の個人情報が含まれています。送信前に確認してください。"
    else:
        result["message"] = "✅ 個人情報は検出されませんでした。"
    return result

# --- 🚀 先読み (認証付き) ---
@app.post("/prefetch", tags=["Background"], dependencies=[Depends(verify_token)])
async def trigger_prefetch(req: PrefetchRequest, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """スイッチON時のみ呼ばれる先読み"""
    bg_tasks.add_task(asyncio.create_task, logic.run_prefetch(req.text, req.target_styles, db))
    return {"status": "accepted", "hash": logic.get_text_hash(req.text)}

@app.get("/prefetch/{text_hash}", tags=["Background"])
def get_prefetch_result(text_hash: str, db: Session = Depends(get_db)):
    """先読み結果取得（認証不要）"""
    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
    if not cache:
        return {"status": "not_found", "results": {}}
    return {"status": "found", "results": cache.results}

# --- ❌ グローバルエラーハンドラ ---
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """未処理例外のキャッチ（詳細をログに、概要をクライアントに）"""
    import traceback
    print(f"❌ Unhandled Exception: {type(exc).__name__}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "予期しないエラーが発生しました",
            "action": "問題が続く場合は管理者に連絡してください"
        }
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 AI Clipboard Pro v3.0.1 - Production Ready")
    print("-" * 50)
    print("📖 API ドキュメント: http://localhost:8000/docs")
    print("🏥 ヘルスチェック: http://localhost:8000/healthz")
    print("-" * 50)
    if settings.API_TOKEN:
        print("🔐 認証: 有効 (Bearer Token)")
    else:
        print("⚠️  認証: 無効 (開発モード)")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
