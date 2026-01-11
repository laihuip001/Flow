"""
Logic Module - Core processing logic (Refactored for v4.0)

責務:
- ビジネスロジックの統合 (CoreProcessor)
- PII保護 (PrivacyScanner利用)
- コスト最適化 (CostRouter)
- ログのサニタイズ
"""
from .config import settings
import hashlib
from sqlalchemy.orm import Session
from .models import TextRequest, PrefetchCache
from datetime import datetime
import logging
from typing import List, Optional

# --- Dependencies ---
from .types import ProcessingResult, DiffLine, ScanResult, ProcessingSuccess, ProcessingError
from .privacy import PrivacyScanner, mask_pii, unmask_pii
from .gemini import (
    is_api_configured,
    execute_gemini,
    execute_gemini_stream,
)

# ロガー設定
logger = logging.getLogger("core_logic")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

from .seasoning import SeasoningManager

# --- Utilities ---
def get_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:32]

def sanitize_log(text: str) -> str:
    """ログ用にテキストをサニタイズ（PII除去）"""
    if not text:
        return "[empty]"
    # ハッシュ化して識別可能だが復元不可能にする
    text_hash = get_text_hash(text)[:8]
    return f"[text:{text_hash}...len={len(text)}]"

def generate_diff(original: str, result: str) -> List[DiffLine]:
    """元テキストと変換後テキストの差分を生成"""
    import difflib
    original_lines = original.splitlines(keepends=True)
    result_lines = result.splitlines(keepends=True)
    diff_result = []
    matcher = difflib.SequenceMatcher(None, original_lines, result_lines)
    line_num = 1
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op == "equal":
            for line in original_lines[i1:i2]:
                diff_result.append({"type": "unchanged", "content": line.rstrip("\n"), "line": line_num})
                line_num += 1
        elif op == "replace":
            for line in original_lines[i1:i2]:
                diff_result.append({"type": "removed", "content": line.rstrip("\n"), "line": line_num})
                line_num += 1
            for line in result_lines[j1:j2]:
                diff_result.append({"type": "added", "content": line.rstrip("\n"), "line": line_num})
        elif op == "delete":
            for line in original_lines[i1:i2]:
                diff_result.append({"type": "removed", "content": line.rstrip("\n"), "line": line_num})
                line_num += 1
        elif op == "insert":
            for line in result_lines[j1:j2]:
                diff_result.append({"type": "added", "content": line.rstrip("\n"), "line": line_num})
    return diff_result

# --- Core Processor (New v4.0) ---
class CoreProcessor:
    """
    AI-Clipboard-Proの中枢ロジック
    
    Features:
    - PII Masking/Unmasking
    - Cost Routing (Model Selection)
    - Offline Cache Fallback
    """
    def __init__(self):
        pass # No more StyleManager

    def _select_model(self, text: str, seasoning: int) -> str:
        """CostRouter: Speed is priority. Use Flash by default."""
        # Umami (Seasoning > 90) ALWAYS uses Smart Model for deep context
        if seasoning > 90:
            return settings.MODEL_SMART # Pro
            
        # Only use Pro model for very high seasoning (heavy reconstruction) and long text
        if len(text) > 1000 and seasoning >= 90:
            return settings.MODEL_SMART # Pro
        return settings.MODEL_FAST # Flash (Default for 99% cases)

    def create_sync_job(self, req: TextRequest, db: Session) -> str:
        """非同期ジョブを作成してIDを返す (即時応答用)"""
        import uuid  # Lightweight, kept local for minimal import overhead
        job_id = str(uuid.uuid4())
        from .models import SyncJob  # Deferred to avoid circular import
        
        job = SyncJob(
            id=job_id,
            text=req.text, # Raw text stored locally
            seasoning=req.seasoning,
            status="pending",
            created_at=datetime.utcnow()
        )
        db.add(job)
        db.commit()
        return job_id

    async def process_sync_job(self, job_id: str, db: Session) -> None:
        """バックグラウンドでSyncJobを処理"""
        from .models import SyncJob
        job = db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if not job: return

        try:
            job.status = "processing"
            db.commit()

            # Reuse process method logic but need to reconstruct Request
            req = TextRequest(text=job.text, seasoning=job.seasoning)
            
            result = await self.process(req, db)
            
            if "error" in result:
                job.status = "failed"
                job.result = result.get("message", result.get("error"))
            else:
                job.status = "completed"
                job.result = result["result"]
        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            job.status = "failed"
        finally:
            db.commit()


    async def process(self, req: TextRequest, db: Session = None) -> ProcessingResult:
        """
        メイン処理パイプライン (v4.1 速度最優先)
        1. Sanitize Log
        2. Check Cache
        3. Mask PII (PRIVACY_MODE=True時のみ)
        4. Select Model
        5. API Call
        6. Unmask PII (PRIVACY_MODE=True時のみ)
        """
        # ユーザーカスタムプロンプトを統合
        system_prompt = SeasoningManager.get_system_prompt(
            req.seasoning, 
            user_prompt=settings.USER_SYSTEM_PROMPT
        )
        config = {
            "system": system_prompt,
            "params": {"temperature": 0.3}
        }
        text_hash = get_text_hash(req.text)

        logger.info(f"📩 Processing: {sanitize_log(req.text)} seasoning={req.seasoning}")

        # --- Sub-function: Cache Fallback ---
        def try_cache_fallback() -> Optional[ProcessingSuccess]:
            if db is None:
                return None
            cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
            cache_key = f"seasoning_{req.seasoning}"
            if cache and cache.results and cache_key in cache.results:
                cached_result = cache.results[cache_key]
                if not cached_result.startswith("Error:"):
                    logger.info(f"📦 Cache Hit: {sanitize_log(cached_result)}")
                    return {
                        "result": cached_result, 
                        "seasoning": req.seasoning, 
                        "from_cache": True,
                        "model_used": None
                    }
            return None

        try:
            # 1. PII Masking (PRIVACY_MODE=False時はスキップ → 速度向上)
            if settings.PRIVACY_MODE:
                masked_text, pii_mapping = mask_pii(req.text)
            else:
                masked_text = req.text  # そのまま送信（速度最優先）
                pii_mapping = {}
            
            # 2. Model Selection
            model_name = self._select_model(masked_text, req.seasoning)
            
            # 3. API Execution
            result = await execute_gemini(masked_text, config, model=model_name)

            if result["success"]:
                # 4. PII Unmasking (PRIVACY_MODE=True時のみ)
                final_result = result["result"]
                if settings.PRIVACY_MODE and pii_mapping:
                    final_result = unmask_pii(final_result, pii_mapping)
                
                # --- TEALS Audit Logging ---
                try:
                    from src.infra.audit import get_audit_manager
                    audit = get_audit_manager()
                    # Calculate simplified processing time (can be improved)
                    # C-3: user_id is missing in Core layer request, use default for now. 
                    # Improvement: Pass user_id in TextRequest or method arg.
                    audit.log_processing(
                        user_id="anonymous", # Placeholder until C-3 fix in API layer propagation
                        input_text=masked_text, # Log masked text for strict privacy
                        output_text=final_result,
                        seasoning=req.seasoning,
                        ai_model=model_name
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Audit logging failed: {e}")
                # ---------------------------

                logger.info(f"✅ Success: {sanitize_log(final_result)}")
                return {
                    "result": final_result, 
                    "seasoning": req.seasoning, 
                    "model_used": model_name,
                    "from_cache": False
                }
            else:
                logger.warning(f"⚠️ API Failed: {result['error']}")
                # Fallback
                if result["error"] in ["api_not_configured", "api_error"]:
                    cached = try_cache_fallback()
                    if cached: return cached

                return {
                    "error": result["error"],
                    "message": result["blocked_reason"],
                    "action": "テキストを修正して再試行してください",
                }

        except Exception as e:
            logger.error(f"❌ Exception: {e}", exc_info=True)
            cached = try_cache_fallback()
            if cached: return cached
            
            return {
                "error": "internal_error",
                "message": "内部エラーが発生しました",
                "action": "しばらく待ってから再試行してください",
            }

    async def run_prefetch(self, text: str, seasoning_levels: list[int], db: Session) -> None:
        """先読み処理（バックグラウンド） - Legacy Placeholder"""
        # Prefetching for spectrum is complex. Disabled for now.
        pass

# --- Backward Capability Shortcuts ---
# main.py 等が古いままでも動くようにする (ただし main.py も更新予定)
_core = CoreProcessor()

async def process_async(req: TextRequest, db: Session = None) -> dict:
    return await _core.process(req, db)

async def run_prefetch(text: str, seasoning_levels: list[int], db: Session) -> None:
    return await _core.run_prefetch(text, seasoning_levels, db)
