"""
Gemini Client Module - Gemini API呼び出し

責務: API設定、呼び出し、レスポンス処理
"""
import os
from google import genai
from google.genai import types
from .config import settings


class GeminiClient:
    """
    Gemini API Client Wrapper (v5.0 Phase 1)
    """
    def __init__(self):
        self.client = None
        self._configure()

    def _configure(self):
        env_key = os.environ.get("GEMINI_API_KEY", "").strip()
        conf_key = settings.GEMINI_API_KEY.strip()

        if env_key:
            self.client = genai.Client(api_key=env_key)
            print("🔐 API Key configured from environment variable (***...)")
        elif conf_key:
            self.client = genai.Client(api_key=conf_key)
            print("🔐 API Key configured from settings (***...)")
        else:
            print("⚠️ API Key NOT configured. Please check .env file.")

    @property
    def is_configured(self) -> bool:
        return self.client is not None

    async def generate_content(self, text: str, config: dict, model: str = None) -> dict:
        if not self.is_configured:
            return {
                "success": False,
                "result": "",
                "error": "api_not_configured",
                "blocked_reason": "APIキーが設定されていません",
            }

        try:
            target_model = model or settings.MODEL_FAST
            prompt = f"{config['system']}\n\n[Input]\n{text}"

            response = await self.client.aio.models.generate_content(
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

    def generate_content_stream(self, text: str, config: dict):
        if not self.is_configured:
            yield "Error: APIキーが設定されていません"
            return

        try:
            model = settings.MODEL_FAST
            prompt = f"{config['system']}\n\n[Input]\n{text}"

            for chunk in self.client.models.generate_content_stream(
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


# --- Backward Compatibility ---
_default_client = GeminiClient()

def is_api_configured() -> bool:
    return _default_client.is_configured

async def execute_gemini(text: str, config: dict, model: str = None) -> dict:
    return await _default_client.generate_content(text, config, model)

def execute_gemini_stream(text: str, config: dict):
    return _default_client.generate_content_stream(text, config)
