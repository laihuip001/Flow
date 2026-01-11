"""
Health Check Routes
"""
from fastapi import APIRouter
from sqlalchemy import text
from datetime import datetime
from src.core.config import settings

router = APIRouter(tags=["Health"])


@router.get("/")
def health_check():
    """基本的なヘルスチェック"""
    return {"status": "running", "version": "4.0.0"}


@router.get("/healthz")
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


@router.get("/healthz/fast")
def fast_health_check():
    """
    高速ヘルスチェック（フェイルオーバー用）
    
    DB接続やAPI設定を確認せず、即座に200を返す。
    Response time target: <50ms
    """
    return {"status": "alive"}
