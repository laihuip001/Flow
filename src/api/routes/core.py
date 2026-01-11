"""
Core Processing Routes - Main text processing endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.infra.database import get_db, SessionLocal
from src.core.models import TextRequest
from src.core.config import settings
from src.core import processor as logic
from src.core.seasoning import SeasoningManager
from typing import Optional

router = APIRouter(tags=["Core"])

# Reference to core processor (will be set by main.py)
core_processor: Optional[logic.CoreProcessor] = None


def set_processor(processor: logic.CoreProcessor):
    global core_processor
    core_processor = processor


# --- 🌶️ Seasoning Presets ---
@router.get("/seasoning")
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


# --- ⚙️ メイン処理 ---
@router.post("/process")
async def process_text(req: TextRequest, db: Session = Depends(get_db)):
    """メイン処理: Seasoningレベル指定でテキスト変換"""
    if not core_processor:
        raise HTTPException(status_code=500, detail="Processor not initialized")
    
    result = await core_processor.process(req, db)
    
    if "error" in result:
        if result["error"] in ["blocked", "safety_blocked"]:
            raise HTTPException(status_code=400, detail=result)
        elif result["error"] == "api_not_configured":
            raise HTTPException(status_code=503, detail=result)
        else:
            raise HTTPException(status_code=500, detail=result)
    
    return result


# --- 🌊 ストリーミング ---
@router.post("/process/stream")
async def process_text_stream(req: TextRequest):
    """リアルタイム整形（ストリーミング）"""
    system_prompt = SeasoningManager.get_system_prompt(req.seasoning)
    config = {"system": system_prompt, "params": {"temperature": 0.3}}
    
    def event_generator():
        for chunk in logic.execute_gemini_stream(req.text, config):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# --- ⚡ 非同期処理 ---
async def run_async_bg_job(job_id: str):
    """Background job wrapper"""
    db = SessionLocal()
    try:
        if core_processor:
            await core_processor.process_sync_job(job_id, db)
    finally:
        db.close()


@router.post("/process/async", tags=["Performance"])
def process_text_async(req: TextRequest, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """非同期処理エンドポイント"""
    if not core_processor:
        raise HTTPException(status_code=500, detail="Processor not initialized")
    
    job_id = core_processor.create_sync_job(req, db)
    bg_tasks.add_task(run_async_bg_job, job_id)
    
    return {
        "status": "accepted",
        "job_id": job_id,
        "message": "バックグラウンドで処理を開始しました"
    }


@router.get("/jobs/{job_id}", tags=["Performance"])
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
