from google import genai
from google.genai import types
from config import settings
import hashlib
from sqlalchemy.orm import Session
from models import TextRequest, PrefetchCache
from datetime import datetime
import asyncio
import re
import os

# API Key Setup
_api_client = None
_env_key = os.environ.get("GEMINI_API_KEY", "").strip()
_conf_key = settings.GEMINI_API_KEY.strip()

if _env_key:
    _api_client = genai.Client(api_key=_env_key)
    print(f"🔐 API Key configured from environment variable ({_env_key[:4]}...)")
elif _conf_key and _conf_key != "YOUR_API_KEY_HERE":
    _api_client = genai.Client(api_key=_conf_key)
    print(f"🔐 API Key configured from settings ({_conf_key[:4]}...)")
else:
    print("⚠️ API Key NOT configured. Please check .env file.")


def is_api_configured() -> bool:
    """APIキーが設定されているかチェック"""
    return _api_client is not None


# --- 🛡️ Safety Module ---
class PrivacyScanner:
    """個人情報検知（警告のみ・置換なし）"""

    def __init__(self):
        self.patterns = {
            # 基本PII
            "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "PHONE": r"\d{2,4}-\d{2,4}-\d{4}",
            "ZIP": r"〒?\d{3}-\d{4}",
            "MY_NUMBER": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}",
            # 拡張パターン (P0-2)
            "IP_ADDRESS": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            "API_KEY": r"(sk-|pk_|AIza|ghp_|xox[baprs]-)[a-zA-Z0-9_-]{20,}",
            "AWS_KEY": r"AKIA[0-9A-Z]{16}",
            "CREDIT_CARD": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}",
        }
        # 機密キーワード (大文字小文字無視)
        self.sensitive_keywords = [
            "CONFIDENTIAL",
            "NDA",
            "INTERNAL ONLY",
            "機密",
            "社外秘",
            "SECRET",
            "PRIVATE",
            "DO NOT SHARE",
            "取扱注意",
        ]

    def scan(self, text: str) -> dict:
        findings = {}
        # Regex パターンマッチ
        for p_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[p_type] = list(set(matches))

        # キーワードマッチ
        text_upper = text.upper()
        keyword_hits = [kw for kw in self.sensitive_keywords if kw.upper() in text_upper]
        if keyword_hits:
            findings["SENSITIVE_KEYWORD"] = keyword_hits

        count = sum(len(v) for v in findings.values())
        return {"has_risks": count > 0, "risks": findings, "risk_count": count}


# --- 🔒 PII Masking Module (P0-1) ---
def mask_pii(text: str) -> tuple[str, dict]:
    """
    PIIをプレースホルダに置換してAPIに送信可能にする。

    Returns:
        tuple: (masked_text, mapping) - マスク済テキストと復元用マッピング
    """
    scanner = PrivacyScanner()
    findings = scanner.scan(text)

    if not findings["has_risks"]:
        return text, {}

    masked_text = text
    mapping = {}
    counter = 0

    for pii_type, values in findings["risks"].items():
        for val in values:
            if val in masked_text:  # まだ置換されていない場合のみ
                placeholder = f"[PII_{counter}]"
                masked_text = masked_text.replace(val, placeholder)
                mapping[placeholder] = val
                counter += 1

    return masked_text, mapping


def unmask_pii(text: str, mapping: dict) -> str:
    """
    プレースホルダをオリジナルのPIIに復元する。
    """
    result = text
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)
    return result


# --- 🎨 Style Module ---
class StyleManager:
    """スタイル定義とプロンプト生成"""

    STYLES = {
        "business": {
            "system": "Rewrite as polite business email. Keep meaning.",
            "params": {"temperature": 0.3},
        },
        "casual": {
            "system": "Rewrite casually for chat. Add emoji.",
            "params": {"temperature": 0.7},
        },
        "summary": {"system": "Summarize in bullet points.", "params": {"temperature": 0.1}},
        "english": {"system": "Translate to professional English.", "params": {"temperature": 0.2}},
        "proofread": {
            "system": "Fix typos only. Keep original meaning.",
            "params": {"temperature": 0.0},
        },
    }

    def get_config(self, style_key: str, app_name: str = None) -> dict:
        base = self.STYLES.get(style_key, self.STYLES["proofread"]).copy()
        if app_name:
            if "slack" in app_name.lower():
                base["system"] += " (Slack向けに短く)"
            elif "mail" in app_name.lower():
                base["system"] += " (メールの件名と本文を含めて)"
        return base


# --- ⚙️ Core Logic (v3.0.1: Safety Filter対応) ---
def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


def sanitize_log(text: str, max_length: int = 20) -> str:
    """ログ用にテキストをサニタイズ（PII除去）"""
    if not text:
        return "[empty]"
    # ハッシュ化して識別可能だが復元不可能にする
    text_hash = get_text_hash(text)[:8]
    return f"[text:{text_hash}...len={len(text)}]"


# --- P2: Diff表示UI ---
def generate_diff(original: str, result: str) -> list:
    """
    元テキストと変換後テキストの差分を生成

    Returns:
        list: [{"type": "unchanged|added|removed", "content": str, "line": int}, ...]
    """
    import difflib

    original_lines = original.splitlines(keepends=True)
    result_lines = result.splitlines(keepends=True)

    diff_result = []
    matcher = difflib.SequenceMatcher(None, original_lines, result_lines)

    line_num = 1
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            for line in original_lines[i1:i2]:
                diff_result.append(
                    {"type": "unchanged", "content": line.rstrip("\n"), "line": line_num}
                )
                line_num += 1
        elif op == "replace":
            for line in original_lines[i1:i2]:
                diff_result.append(
                    {"type": "removed", "content": line.rstrip("\n"), "line": line_num}
                )
                line_num += 1
            for line in result_lines[j1:j2]:
                diff_result.append(
                    {"type": "added", "content": line.rstrip("\n"), "line": line_num}
                )
        elif op == "delete":
            for line in original_lines[i1:i2]:
                diff_result.append(
                    {"type": "removed", "content": line.rstrip("\n"), "line": line_num}
                )
                line_num += 1
        elif op == "insert":
            for line in result_lines[j1:j2]:
                diff_result.append(
                    {"type": "added", "content": line.rstrip("\n"), "line": line_num}
                )

    return diff_result


async def execute_gemini(text: str, config: dict) -> dict:
    """
    Gemini API呼び出し（New SDK v1.0 対応）

    Returns:
        dict: {"success": bool, "result": str, "error": str, "blocked_reason": str}
    """
    # APIキー未設定チェック
    if not is_api_configured():
        return {
            "success": False,
            "result": None,
            "error": "api_not_configured",
            "blocked_reason": "GEMINI_API_KEYが設定されていません。.envファイルを確認してください。",
        }

    try:
        # 新SDKでの呼び出し
        response = await _api_client.aio.models.generate_content(
            model=settings.MODEL_FAST,
            contents=f"{config['system']}\n\n【入力】\n{text}",
            config=types.GenerateContentConfig(temperature=config["params"]["temperature"]),
        )

        # レスポンス処理
        if response.text:
            return {
                "success": True,
                "result": response.text.strip(),
                "error": None,
                "blocked_reason": None,
            }

        return {
            "success": False,
            "result": None,
            "error": "empty_response",
            "blocked_reason": "空のレスポンスが返されました",
        }

    except Exception as e:
        # Pydanticのバリデーションエラーなどでブロックされた場合のハンドリング
        import traceback

        print(f"❌ API Exception: {e}")
        print(traceback.format_exc())
        return {
            "success": False,
            "result": None,
            "error": "api_error",
            "blocked_reason": f"API Error: {str(e)}",
        }


async def execute_gemini_stream(text: str, config: dict):
    """
    Gemini API ストリーミング呼び出し（SSE用）
    Yields: str (partial text)
    """
    if not is_api_configured():
        yield "Error: API Key not configured"
        return

    try:
        # 新SDKでのストリーミング呼び出し (google.genai)
        # 修正: generate_content_stream は戻り値自体が非同期イテレータのラッパー
        async for chunk in await _api_client.aio.models.generate_content_stream(
            model=settings.MODEL_FAST,
            contents=f"{config['system']}\n\n【入力】\n{text}",
            config=types.GenerateContentConfig(temperature=config["params"]["temperature"]),
        ):
            if chunk.text:
                yield chunk.text

    except Exception as e:
        import traceback

        print(f"❌ Stream Exception: {e}")
        print(traceback.format_exc())
        yield f"Error: {str(e)}"


async def process_async(req: TextRequest, db: Session = None) -> dict:
    """
    非同期処理（メイン）

    v3.3: オフラインフォールバック対応
    v4.0: PII Masking対応 - APIにPIIを送信しない
    """
    style_mgr = StyleManager()
    config = style_mgr.get_config(req.style, req.current_app)
    text_hash = get_text_hash(req.text)

    # ログはサニタイズ（PII除去）
    print(f"📩 処理開始: {sanitize_log(req.text)} style={req.style}")

    # --- キャッシュ参照（オフラインフォールバック） ---
    def try_cache_fallback() -> dict | None:
        """キャッシュから結果を取得"""
        if db is None:
            return None
        cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
        if cache and cache.results and req.style in cache.results:
            cached_result = cache.results[req.style]
            if not cached_result.startswith("Error:"):
                print(f"📦 キャッシュから取得: {sanitize_log(cached_result)}")
                return {"result": cached_result, "style": req.style, "from_cache": True}
        return None

    try:
        # PII Masking: マスクしてAPIに送信
        masked_text, pii_mapping = mask_pii(req.text)
        
        # 非同期実行 (マスク済みテキストを送信)
        result = await execute_gemini(masked_text, config)

        if result["success"]:
            # PII Unmasking: 結果内のプレースホルダを復元
            final_result = result["result"]
            if pii_mapping:
                final_result = unmask_pii(final_result, pii_mapping)
            
            print(f"✅ 処理完了: {sanitize_log(final_result)}")
            return {"result": final_result, "style": req.style}
        else:
            print(f"⚠️ API処理失敗: {result['error']}")

            # オフラインフォールバック: キャッシュを試す
            if result["error"] in ["api_not_configured", "api_error"]:
                cached = try_cache_fallback()
                if cached:
                    return cached

            return {
                "error": result["error"],
                "message": result["blocked_reason"],
                "action": "テキストを修正して再試行してください",
            }

    except Exception as e:
        print(f"❌ 例外発生: {type(e).__name__}")

        # オフラインフォールバック: キャッシュを試す
        cached = try_cache_fallback()
        if cached:
            return cached

        return {
            "error": "internal_error",
            "message": "内部エラーが発生しました",
            "action": "しばらく待ってから再試行してください",
        }


async def run_prefetch(text: str, styles: list, db: Session):
    """先読み処理（並列実行）"""
    text_hash = get_text_hash(text)

    # ログはサニタイズ
    print(f"🚀 Pre-Fetch開始: {sanitize_log(text)} styles={styles}")

    cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()

    if not cache:
        cache = PrefetchCache(hash_id=text_hash, original_text=text, results={})
        db.add(cache)
        db.commit()

    style_mgr = StyleManager()
    tasks = []
    style_names = []

    for style in styles:
        config = style_mgr.get_config(style)
        tasks.append(execute_gemini(text, config))
        style_names.append(style)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    current_results = dict(cache.results) if cache.results else {}
    for name, res in zip(style_names, results):
        if isinstance(res, Exception):
            current_results[name] = f"Error: {str(res)}"
        elif res.get("success"):
            current_results[name] = res["result"]
        else:
            current_results[name] = f"Error: {res.get('blocked_reason', 'Unknown')}"

    cache.results = current_results
    cache.created_at = datetime.utcnow()
    db.commit()
    print(f"✅ Pre-Fetch完了: {len(style_names)} styles")
