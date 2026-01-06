"""
Gemini Client Module - Gemini API呼び出し

責務: API設定、呼び出し、レスポンス処理
"""
import os
from google import genai
from google.genai import types
from .config import settings


# --- API Client Setup ---
_api_client = None
_env_key = os.environ.get("GEMINI_API_KEY", "").strip()
_conf_key = settings.GEMINI_API_KEY.strip()

if _env_key:
    _api_client = genai.Client(api_key=_env_key)
    print(f"🔐 API Key configured from environment variable ({_env_key[:4]}...)")
elif _conf_key:
    _api_client = genai.Client(api_key=_conf_key)
    print(f"🔐 API Key configured from settings ({_conf_key[:4]}...)")
else:
    print("⚠️ API Key NOT configured. Please check .env file.")


def is_api_configured() -> bool:
    """APIキーが設定されているかチェック"""
    return _api_client is not None


async def execute_gemini(text: str, config: dict, model: str = None) -> dict:
    """
    Gemini API呼び出し（New SDK v1.0 対応）

    Returns:
        dict: {"success": bool, "result": str, "error": str, "blocked_reason": str}
    """
    if not is_api_configured():
        return {
            "success": False,
            "result": "",
            "error": "api_not_configured",
            "blocked_reason": "APIキーが設定されていません",
        }

    try:
        target_model = model or settings.MODEL_FAST
        prompt = f"{config['system']}\n\n[Input]\n{text}"

        response = await _api_client.aio.models.generate_content(
            model=target_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=config["params"].get("temperature", 0.3)
            ),
        )

        # Safety Filter チェック
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, "finish_reason"):
                if candidate.finish_reason == "SAFETY":
                    blocked_categories = []
                    if hasattr(candidate, "safety_ratings"):
                        for rating in candidate.safety_ratings:
                            if rating.blocked:
                                blocked_categories.append(rating.category)
                    return {
                        "success": False,
                        "result": "",
                        "error": "safety_blocked",
                        "blocked_reason": f"Safety filter: {blocked_categories}",
                    }

        result_text = response.text.strip() if response.text else ""
        return {"success": True, "result": result_text, "error": None, "blocked_reason": None}

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Gemini API Error: {error_msg}")
        return {
            "success": False,
            "result": "",
            "error": "api_error",
            "blocked_reason": error_msg,
        }


def execute_gemini_stream(text: str, config: dict):
    """
    Gemini API ストリーミング呼び出し（SSE用）
    Yields: str (partial text)
    """
    if not is_api_configured():
        yield "Error: APIキーが設定されていません"
        return

    try:
        model = settings.MODEL_FAST
        prompt = f"{config['system']}\n\n[Input]\n{text}"

        # ストリーミングレスポンス
        for chunk in _api_client.models.generate_content_stream(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=config["params"].get("temperature", 0.3)
            ),
        ):
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"Error: {str(e)}"
