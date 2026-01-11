"""
P2 Features Routes - Analysis, History, Diff
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.infra.database import get_db
from src.core.models import TextRequest, DiffResponse, ContextMode
from src.core import processor as logic
from typing import List, Dict, Any, Optional

router = APIRouter(tags=["P2 Features"])

# Constants
MAX_HISTORY_SIZE = 10
MAX_TEXT_LENGTH_HISTORY = 500

# Reference to core processor
core_processor: Optional[logic.CoreProcessor] = None


def set_processor(processor: logic.CoreProcessor):
    global core_processor
    core_processor = processor


# --- 🔍 Diff表示 ---
@router.post("/process/diff", response_model=DiffResponse)
async def process_with_diff(req: TextRequest, db: Session = Depends(get_db)):
    """テキスト変換 + Diff表示"""
    if not core_processor:
        raise HTTPException(status_code=500, detail="Processor not initialized")
    
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


# --- 📊 コンテキスト分析 ---
@router.post("/analyze")
def analyze_text(req: TextRequest):
    """テキストを分析し、推奨モード（Light/Deep）を判定"""
    text_length = len(req.text)
    line_count = req.text.count('\n') + 1
    
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
        estimated_cost_yen=round(estimated_cost * 150, 2)
    )


# --- 📝 クリップボード履歴 ---
_clipboard_history: List[Dict[str, Any]] = []


@router.post("/history/add")
def add_to_history(req: TextRequest):
    """クリップボード履歴に追加"""
    item = {
        "text": req.text[:MAX_TEXT_LENGTH_HISTORY],
        "timestamp": datetime.utcnow().isoformat(),
        "hash_id": logic.get_text_hash(req.text),
        "app_name": req.current_app
    }
    
    _clipboard_history.insert(0, item)
    if len(_clipboard_history) > MAX_HISTORY_SIZE:
        _clipboard_history.pop()
    
    return {"status": "added", "history_size": len(_clipboard_history)}


@router.get("/history")
def get_history():
    """クリップボード履歴を取得"""
    return {"history": _clipboard_history, "size": len(_clipboard_history)}
