"""
Legacy Routes - Deprecated Endpoints
"""
from fastapi import APIRouter
from src.core.models import TextRequest

router = APIRouter(tags=["Legacy", "Deprecated"])


@router.get("/styles")
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


@router.post("/suggest-style")
def suggest_style(req: TextRequest):
    """スタイル推奨 (DEPRECATED)"""
    return {"suggested_style": "default", "confidence": 0.0}
