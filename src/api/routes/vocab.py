"""
Vocabulary API Router - カスタム語彙管理
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.core.vocab_store import get_vocab_store

router = APIRouter(prefix="/vocab", tags=["vocabulary"])


# --- Request/Response Models ---
class VocabAddRequest(BaseModel):
    term: str
    category: str = "custom"


class VocabResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# --- Endpoints ---
@router.get("")
async def list_vocab():
    """
    登録済み語彙一覧を取得
    """
    store = get_vocab_store()
    items = store.list_all()
    return {
        "count": len(items),
        "items": items
    }


@router.post("")
async def add_vocab(req: VocabAddRequest):
    """
    機密語彙を追加
    
    追加された語彙はmask_pii()で自動検出される
    """
    store = get_vocab_store()
    success = store.add_term(req.term, req.category)
    
    if success:
        return VocabResponse(
            success=True,
            message=f"語彙 '{req.term}' を追加しました",
            data={"term": req.term, "category": req.category}
        )
    else:
        raise HTTPException(
            status_code=409,
            detail={"error": "duplicate", "message": f"語彙 '{req.term}' は既に登録済みです"}
        )


@router.delete("/{term}")
async def remove_vocab(term: str):
    """
    語彙を削除
    """
    store = get_vocab_store()
    success = store.remove_term(term)
    
    if success:
        return VocabResponse(
            success=True,
            message=f"語彙 '{term}' を削除しました"
        )
    else:
        raise HTTPException(
            status_code=404,
            detail={"error": "not_found", "message": f"語彙 '{term}' が見つかりません"}
        )


@router.get("/search")
async def search_vocab(q: str, limit: int = 10):
    """
    語彙を検索（部分一致）
    """
    store = get_vocab_store()
    results = store.search(q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "items": results
    }


@router.post("/check")
async def check_text(text: str):
    """
    テキスト内のカスタム語彙を検出
    """
    store = get_vocab_store()
    found = store.find_in_text(text)
    return {
        "found": found,
        "count": len(found)
    }
