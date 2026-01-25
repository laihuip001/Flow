"""
Flow AI v4.0 - API Server
=========================

Pre-processing × Speed - The Seasoning Update

This is the main entry point for the FastAPI application.
All route handlers are organized in the routes/ package.
"""
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.infra.database import init_db
from src.core.config import settings
from src.core import processor as logic
from src.api.auth import verify_token

# Static files directory
STATIC_DIR = Path(__file__).parent.parent / "static"

# --- Initialize Database ---
init_db()

# --- Create FastAPI App ---
app = FastAPI(
    title="Flow AI v4.0",
    description="Pre-processing × Speed - The Seasoning Update",
    version="4.0.0"
)


# --- Initialize Processor ---
core_processor = logic.CoreProcessor()

# --- Import and Configure Routers ---
from src.api.routes import (
    health_router,
    core_router,
    safety_router,
    features_router,
    vision_router,
    legacy_router,
    set_core_processor,
    set_safety_processor,
    set_features_processor,
    audit_router,
    vocab_router,
    sync_router,
    set_sync_processor,
)

# Inject processor instances
set_core_processor(core_processor)
set_safety_processor(core_processor)
set_features_processor(core_processor)
set_sync_processor(core_processor)

# --- Include Routers ---
app.include_router(health_router)
app.include_router(core_router, dependencies=[Depends(verify_token)])
app.include_router(safety_router)  # No auth for scan
app.include_router(features_router, dependencies=[Depends(verify_token)])
app.include_router(vision_router, dependencies=[Depends(verify_token)])
app.include_router(audit_router, dependencies=[Depends(verify_token)])
app.include_router(vocab_router, dependencies=[Depends(verify_token)])  # v4.1
app.include_router(sync_router, dependencies=[Depends(verify_token)])  # v5.0 Phase 4
app.include_router(legacy_router)

# --- 📁 Static Files (Web UI) ---
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    
    @app.get("/", include_in_schema=False)
    async def serve_ui():
        """Serve the Web UI at root"""
        return FileResponse(STATIC_DIR / "index.html")


# --- ❌ グローバルエラーハンドラ ---
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """未処理例外のキャッチ"""
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


# --- Main Entry Point ---
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
