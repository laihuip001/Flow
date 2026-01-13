"""
Sync API Router (遅延同期 API)
v5.0 Phase 4

/sync/* エンドポイントを提供します。
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from src.infra.database import get_db
from src.core.sync import SyncManager
from sqlalchemy.orm import Session

router = APIRouter(prefix="/sync", tags=["Sync (遅延同期)"])

# --- Dependency Injection ---
_sync_manager: Optional[SyncManager] = None
_core_processor = None

def set_sync_processor(processor):
    """CoreProcessor を設定する（main.py から呼び出される）"""
    global _core_processor
    _core_processor = processor

def get_sync_manager() -> SyncManager:
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = SyncManager()
    return _sync_manager


# --- Request/Response Models ---
class EnqueueRequest(BaseModel):
    text: str = Field(..., description="処理対象テキスト")
    seasoning: int = Field(30, description="処理レベル 0-100")

class EnqueueResponse(BaseModel):
    job_id: str
    status: str = "pending"
    message: str = "ジョブをキューに登録しました"

class ProcessResponse(BaseModel):
    processed: int
    failed: int
    total: int

class JobStatusResponse(BaseModel):
    id: str
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# --- Endpoints ---
@router.post("/enqueue", response_model=EnqueueResponse)
async def enqueue_job(
    req: EnqueueRequest,
    db: Session = Depends(get_db),
    mgr: SyncManager = Depends(get_sync_manager)
):
    """
    ジョブをキューに登録する
    (オフライン時にリクエストを保存しておくために使用)
    """
    job_id = mgr.enqueue(db, req.text, req.seasoning)
    return EnqueueResponse(job_id=job_id)


@router.post("/process", response_model=ProcessResponse)
async def process_pending_jobs(
    limit: int = 10,
    db: Session = Depends(get_db),
    mgr: SyncManager = Depends(get_sync_manager)
):
    """
    未処理 (pending) のジョブをまとめて処理する
    クライアントがネットワーク復帰時に呼び出す想定
    """
    if _core_processor is None:
        raise HTTPException(status_code=500, detail="CoreProcessor is not initialized")
    
    stats = mgr.process_pending(db, _core_processor, limit)
    return ProcessResponse(**stats)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_db),
    mgr: SyncManager = Depends(get_sync_manager)
):
    """
    ジョブIDからステータスと結果を取得する (Polling用)
    """
    result = mgr.get_result(db, job_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(**result)
