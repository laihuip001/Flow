"""
Vision Routes - Image Processing with Gemini
"""
from fastapi import APIRouter, HTTPException
import base64
import os
from google import genai
from google.genai import types
from src.core.models import ImageProcessRequest
from src.core.config import settings
from src.core import processor as logic

router = APIRouter(tags=["Vision"])


@router.post("/process/image")
async def process_image(req: ImageProcessRequest):
    """
    画像をGemini Visionで処理
    
    - スクリーンショットのテキスト抽出
    - 手書きメモの読み取り
    - 画像からの情報抽出
    """
    if not logic.is_api_configured():
        raise HTTPException(
            status_code=503,
            detail={"error": "api_not_configured", "message": "GEMINI_API_KEYが設定されていません"}
        )
    
    try:
        # Base64デコード
        image_data = base64.b64decode(req.image_base64)
        
        # API Client
        api_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        client = genai.Client(api_key=api_key)
        
        # プロンプト構築
        prompt = req.prompt or "この画像に含まれるテキストを全て抽出し、整理してください。"
        prompt = f"Role: Optical Character Recognition.\n\n{prompt}"
        
        # API呼び出し
        response = await client.aio.models.generate_content(
            model="models/gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=image_data, mime_type="image/png"),
                prompt
            ]
        )
        
        if response.text:
            return {
                "result": response.text.strip(),
                "style": req.style,
                "prompt_used": prompt[:100] + "..."
            }
        else:
            raise HTTPException(status_code=400, detail={"error": "blocked", "message": "画像処理がブロックされました"})
            
    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail={"error": "invalid_image", "message": "Base64エンコードが不正です"})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "api_error", "message": str(e)})
