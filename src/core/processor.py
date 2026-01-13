"""
Logic Module - Core processing logic (Refactored for v5.0 Phase 1)

責務:
- ビジネスロジックの統合 (CoreProcessor)
- PII保護 (PrivacyScanner利用)
- コスト最適化 (CostRouter)
- ログのサニタイズ
"""
from .config import settings
import uuid
from sqlalchemy.orm import Session
from .models import TextRequest, PrefetchCache, SyncJob
from datetime import datetime
import logging
from typing import List, Optional

# --- Constants (C-4-5 Refactored) ---
UMAMI_THRESHOLD = 90  # Seasoning > 90 uses Smart Model
LONG_TEXT_THRESHOLD = 1000  # Characters threshold for model selection

# --- Dependencies ---
from .types import ProcessingResult, DiffLine, ScanResult, ProcessingSuccess, ProcessingError
from .privacy import PrivacyHandler
from .gemini import GeminiClient, execute_gemini, execute_gemini_stream
from .audit_logger import AuditLogger

# ロガー設定
logger = logging.getLogger("core_logic")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

from .seasoning import SeasoningManager
from .cache import CacheManager

# --- Utilities ---
# get_text_hash, sanitize_log are delegated to CacheManager


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

# --- Core Processor (New v5.0) ---
class CoreProcessor:
    """
    AI-Clipboard-Proの中枢ロジック
    
    Features:
    - PII Masking/Unmasking
    - Cost Routing (Model Selection)
    - Offline Cache Fallback
    """
    def __init__(self):
        self.cache_manager = CacheManager()
        self.privacy_handler = PrivacyHandler()
        self.gemini_client = GeminiClient()
        self.audit_logger = AuditLogger()

    def _select_model(self, text: str, seasoning: int) -> str:
        """CostRouter: Speed is priority. Use Flash by default."""
        # Umami (Seasoning > threshold) ALWAYS uses Smart Model for deep context
        if seasoning > UMAMI_THRESHOLD:
            return settings.MODEL_SMART
            
        # Pro model for high seasoning + long text
        if len(text) > LONG_TEXT_THRESHOLD:
            return settings.MODEL_SMART
        return settings.MODEL_FAST

    def create_sync_job(self, req: TextRequest, db: Session) -> str:
        """非同期ジョブを作成してIDを返す (即時応答用)"""
        job_id = str(uuid.uuid4())
        
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
        logger.info(f"📩 Processing: {CacheManager.sanitize_log(req.text)} seasoning={req.seasoning}")

        # --- Sub-function: Cache Fallback ---
        try_cache_fallback = lambda: self.cache_manager.check_cache(db, req.text, req.seasoning)

        try:
            # 1. PII Masking (PRIVACY_MODE=False時はスキップ → 速度向上)
            if settings.PRIVACY_MODE:
                masked_text, pii_mapping = self.privacy_handler.mask(req.text)
            else:
                masked_text = req.text  # そのまま送信（速度最優先）
                pii_mapping = {}
                # v4.1: 開発者向け警告
                logger.warning("⚠️ PRIVACY_MODE=False: PIIマスキング無効。本番環境では有効化推奨。")
            
            # 2. Model Selection
            model_name = self._select_model(masked_text, req.seasoning)
            
            # 3. API Execution
            result = await self.gemini_client.generate_content(masked_text, config, model=model_name)

            if result["success"]:
                # 4. PII Unmasking (PRIVACY_MODE=True時のみ)
                final_result = result["result"]
                if settings.PRIVACY_MODE and pii_mapping:
                    final_result = self.privacy_handler.unmask(final_result, pii_mapping)
                
                # --- TEALS Audit Logging ---
                self.audit_logger.log_processing(
                    user_id="anonymous",
                    input_text=masked_text,
                    output_text=final_result,
                    seasoning=req.seasoning,
                    ai_model=model_name
                )
                # ---------------------------

                logger.info(f"✅ Success: {CacheManager.sanitize_log(final_result)}")
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
