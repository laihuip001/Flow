"""
Safety & Background Routes - PII Scan, Prefetch
"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from src.infra.database import get_db
from src.core.models import TextRequest, PrefetchRequest, ScanResponse, PrefetchCache
from src.core import processor as logic
from src.core.privacy import PrivacyScanner
import asyncio
from typing import Optional

router = APIRouter()

# Reference to core processor (will be set by main.py)
core_processor: Optional[logic.CoreProcessor] = None


def set_processor(processor: logic.CoreProcessor):
    global core_processor
    core_processor = processor


# --- 🛡️ 安全スキャン ---
@router.post("/scan", response_model=ScanResponse, tags=["Safety"])
def scan_text(req: TextRequest):
    """個人情報検知（認証不要）"""
    scanner = PrivacyScanner()
    result = scanner.scan(req.text)
    if result["has_risks"]:
        result["message"] = f"⚠️ {result['risk_count']}件の個人情報が含まれています。送信前に確認してください。"
    else:
        result["message"] = "✅ 個人情報は検出されませんでした。"
    return result


# --- 🚀 先読み ---
@router.post("/prefetch", tags=["Background"])
async def trigger_prefetch(req: PrefetchRequest, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """スイッチON時のみ呼ばれる先読み"""
    if core_processor:
        bg_tasks.add_task(asyncio.create_task, core_processor.run_prefetch(req.text, req.target_seasoning_levels, db))
    return {"status": "accepted", "hash": logic.CacheManager.get_text_hash(req.text)}


@router.get("/prefetch/{text_hash}", tags=["Background"])
def get_prefetch_result(text_hash: str, db: Session = Depends(get_db)):
    """先読み結果取得（認証不要）"""
    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
    if not cache:
        return {"status": "not_found", "results": {}}
    return {"status": "found", "results": cache.results}
