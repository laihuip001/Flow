from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.infra.database import get_db, init_db, SessionLocal
from src.core.models import TextRequest, PrefetchRequest, ScanResponse, PrefetchCache
from src.core.config import settings
from src.core import processor as logic
from src.core.seasoning import SeasoningManager
import asyncio
from datetime import datetime

init_db()
app = FastAPI(
    title="Flow AI v4.0",
    description="Pre-processing × Speed - The Seasoning Update",
    version="4.0.0"
)

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
    return {"status": "running", "version": "4.0.0"}

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
        from src.infra.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {type(e).__name__}"
    
    # Gemini API設定チェック
    if settings.GEMINI_API_KEY:
        checks["gemini"] = "configured"
    else:
        checks["gemini"] = "not_configured"
    
    # 総合ステータス
    all_ok = all(v in ["ok", "configured"] for v in checks.values())
    
    return {
        "status": "running" if all_ok else "degraded",
        "version": "4.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "auth_enabled": bool(settings.API_TOKEN),
        "checks": checks
    }

@app.get("/healthz/fast", tags=["Health"])
def fast_health_check():
    """
    高速ヘルスチェック（フェイルオーバー用）
    
    DB接続やAPI設定を確認せず、即座に200を返す。
    クライアントはメインリクエスト前にこれを叩き（timeout: 500ms）、
    サーバー到達不能時は即座にフォールバック先へ切り替える。
    
    Response time target: <50ms
    """
    return {"status": "alive"}

# --- 🌶️ Seasoning Presets (v4.0) ---
@app.get("/seasoning", tags=["Core"])
def list_seasoning_presets():
    """利用可能なSeasoningプリセット一覧"""
    from src.core.seasoning import SALT_MAX, SAUCE_MAX
    return {
        "presets": [
            {"id": "salt", "level": 10, "name": "Salt", "description": "最小限の修正（誤字脱字）"},
            {"id": "sauce", "level": 50, "name": "Sauce", "description": "標準的な整形"},
            {"id": "spice", "level": 90, "name": "Spice", "description": "積極的な補完・強化"}
        ],
        "thresholds": {"salt_max": SALT_MAX, "sauce_max": SAUCE_MAX}
    }

# Legacy endpoint for backward compatibility
@app.get("/styles", tags=["Legacy", "Deprecated"])
def list_styles():
    """利用可能なスタイル一覧 (DEPRECATED - use /seasoning instead)"""
    return {
        "styles": [
            {"id": "business", "name": "ビジネス", "description": "丁寧・フォーマル"},
            {"id": "casual", "name": "カジュアル", "description": "フランク・絵文字あり"},
            {"id": "summary", "name": "要約", "description": "箇条書き・簡潔"},
            {"id": "english", "name": "英語翻訳", "description": "ビジネス英語"},
            {"id": "proofread", "name": "校正", "description": "誤字脱字修正のみ"}
        ],
        "deprecated": True,
        "migration": "Use /seasoning endpoint with 'level' parameter (0-100)"
    }

# --- ⚙️ メイン処理 (認証付き) ---
# Instantiate CoreProcessor globally
core_processor = logic.CoreProcessor()

# --- ⚙️ メイン処理 (認証付き) ---
@app.post("/process", tags=["Core"], dependencies=[Depends(verify_token)])
async def process_text(req: TextRequest, db: Session = Depends(get_db)):
    """
    メイン処理: スタイル指定でテキスト変換
    
    認証が有効な場合、Authorization: Bearer <token> ヘッダーが必要
    v3.3: オフラインフォールバック対応（キャッシュがあれば使用）
    v4.0: CoreProcessor利用
    """
    result = await core_processor.process(req, db)
    
    # エラーレスポンスの場合は適切なステータスコードを返す
    if "error" in result:
        if result["error"] == "blocked" or result["error"] == "safety_blocked":
            raise HTTPException(status_code=400, detail=result)
        elif result["error"] == "api_not_configured":
            raise HTTPException(status_code=503, detail=result)
        else:
            raise HTTPException(status_code=500, detail=result)
    
    return result

# --- 🌊 P3: Streaming Response (Refinement) ---
from fastapi.responses import StreamingResponse

@app.post("/process/stream", tags=["Core", "Titanium"], dependencies=[Depends(verify_token)])
async def process_text_stream(req: TextRequest):
    """
    リアルタイム整形（ストリーミング）
    Server-Sent Events (SSE) 形式で部分テキストを順次返却します。
    """
    # 設定取得用
    system_prompt = SeasoningManager.get_system_prompt(req.seasoning)
    config = {
        "system": system_prompt,
        "params": {"temperature": 0.3}
    }
    
    def event_generator():
        for chunk in logic.execute_gemini_stream(req.text, config):
            # SSE format: "data: <content>\n\n"
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- ⚡ Phase 1 Performance: Async Endpoint ---
# SessionLocal imported at top

async def run_async_bg_job(job_id: str):
    """Async wrapper for background job with independent DB session"""
    db = SessionLocal()
    try:
        await core_processor.process_sync_job(job_id, db)
    finally:
        db.close()

@app.post("/process/async", tags=["Performance"], dependencies=[Depends(verify_token)])
def process_text_async(req: TextRequest, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    【高速応答】非同期処理エンドポイント
    
    リクエストを即座に受け付け、Job IDを返します。
    処理はバックグラウンドで実行されます。
    
    Returns:
        job_id (str): 結果確認用のID
    """
    # 1. Create Job (uses current db session, commits immediately)
    job_id = core_processor.create_sync_job(req, db)
    
    # 2. Enqueue Background Task (uses NEW db session)
    bg_tasks.add_task(run_async_bg_job, job_id)
    
    return {
        "status": "accepted",
        "job_id": job_id,
        "message": "バックグラウンドで処理を開始しました"
    }

@app.get("/jobs/{job_id}", tags=["Performance"])
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """ジョブの状態確認"""
    from src.core.models import SyncJob
    job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "result": job.result,
        "created_at": job.created_at
    }

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
    bg_tasks.add_task(asyncio.create_task, core_processor.run_prefetch(req.text, req.target_seasoning_levels, db))
    return {"status": "accepted", "hash": logic.get_text_hash(req.text)}

@app.get("/prefetch/{text_hash}", tags=["Background"])
def get_prefetch_result(text_hash: str, db: Session = Depends(get_db)):
    """先読み結果取得（認証不要）"""
    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
    if not cache:
        return {"status": "not_found", "results": {}}
    return {"status": "found", "results": cache.results}

# --- 🔍 P2: Diff表示UI ---
from src.core.models import DiffResponse, ContextMode

@app.post("/process/diff", response_model=DiffResponse, tags=["P2 Features"], dependencies=[Depends(verify_token)])
async def process_with_diff(req: TextRequest, db: Session = Depends(get_db)):
    """
    テキスト変換 + Diff表示
    
    変換前後の差分を行単位で返す（ハルシネーション検知用）
    """
    result = await core_processor.process(req, db)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result)
    
    diff_lines = logic.generate_diff(req.text, result["result"])
    
    return DiffResponse(
        original=req.text,
        result=result["result"],
        diff_lines=diff_lines,
        seasoning=result.get("seasoning"),
        from_cache=result.get("from_cache", False)
    )

# --- 📊 P2: コンテキスト二極化（Light/Deep） ---
@app.post("/analyze", tags=["P2 Features"])
def analyze_text(req: TextRequest):
    """
    テキストを分析し、推奨モード（Light/Deep）を判定
    
    - Light: 短文、明確な意図 → 高速処理
    - Deep: 長文、複雑な構造 → 高品質処理
    """
    text_length = len(req.text)
    line_count = req.text.count('\n') + 1
    
    # ヒューリスティック判定
    if text_length < 200 and line_count < 5:
        mode = "light"
        description = "短文・シンプル: 高速処理を推奨"
        estimated_tokens = text_length * 2
        estimated_cost = estimated_tokens * 0.000075
    else:
        mode = "deep"
        description = "長文・複雑: 高品質処理を推奨"
        estimated_tokens = text_length * 3
        estimated_cost = estimated_tokens * 0.00035
    
    return ContextMode(
        mode=mode,
        description=description,
        estimated_tokens=estimated_tokens,
        estimated_cost_yen=round(estimated_cost * 150, 2)  # USD to JPY
    )

# --- 📝 P2: 文脈の継続性（クリップボード履歴） ---
# インメモリ履歴（簡易実装）
_clipboard_history: list = []
MAX_HISTORY_SIZE = 10

@app.post("/history/add", tags=["P2 Features"], dependencies=[Depends(verify_token)])
def add_to_history(req: TextRequest):
    """
    クリップボード履歴に追加（文脈の継続性）
    
    直近10件の履歴を保持し、関連するコンテキストを活用可能に
    """
    
    item = {
        "text": req.text[:500],  # 最大500文字に制限
        "timestamp": datetime.utcnow().isoformat(),
        "hash_id": logic.get_text_hash(req.text),
        "app_name": req.current_app
    }
    
    _clipboard_history.insert(0, item)
    if len(_clipboard_history) > MAX_HISTORY_SIZE:
        _clipboard_history.pop()
    
    return {"status": "added", "history_size": len(_clipboard_history)}

@app.get("/history", tags=["P2 Features"], dependencies=[Depends(verify_token)])
def get_history():
    """クリップボード履歴を取得"""
    return {"history": _clipboard_history, "size": len(_clipboard_history)}

# --- 🎯 P2: アプリ名依存排除（テキスト分析によるスタイル自動推定） ---
# suggest-style deprecated in v4.0 (Seasoning Update)
@app.post("/suggest-style", tags=["Core", "Deprecated"])
def suggest_style(req: TextRequest):
    return {"suggested_style": "default", "confidence": 0.0}

# --- 🖼️ P2: 画像認識（Gemini Vision） ---
from src.core.models import ImageProcessRequest

@app.post("/process/image", tags=["P2 Features"], dependencies=[Depends(verify_token)])
async def process_image(req: ImageProcessRequest):
    """
    画像をGemini Visionで処理
    
    - スクリーンショットのテキスト抽出
    - 手書きメモの読み取り
    - 画像からの情報抽出
    """
    import base64
    import google.generativeai as genai
    
    if not logic.is_api_configured():
        raise HTTPException(
            status_code=503,
            detail={"error": "api_not_configured", "message": "GEMINI_API_KEYが設定されていません"}
        )
    
    try:
        # Base64デコード
        image_data = base64.b64decode(req.image_base64)
        
        # Gemini Vision モデル
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # プロンプト構築
        prompt = req.prompt or "この画像に含まれるテキストを全て抽出し、整理してください。"
        # P3: Use Seasoning 30 (Salt) equivalent for image extraction
        prompt = f"Role: Optical Character Recognition.\n\n{prompt}"
        
        # API呼び出し
        response = await model.generate_content_async([
            {"mime_type": "image/png", "data": image_data},
            prompt
        ])
        
        if response.candidates and response.candidates[0].content.parts:
            result_text = response.candidates[0].content.parts[0].text.strip()
            return {
                "result": result_text,
                "style": req.style,
                "prompt_used": prompt[:100] + "..."
            }
        else:
            raise HTTPException(status_code=400, detail={"error": "blocked", "message": "画像処理がブロックされました"})
            
    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail={"error": "invalid_image", "message": "Base64エンコードが不正です"})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "api_error", "message": str(e)})

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
    print("🚀 Flow AI v4.0 - Pre-processing × Speed")
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
