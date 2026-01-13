import logging
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from .models import PrefetchCache
from .types import ProcessingSuccess

logger = logging.getLogger("core_cache")

class CacheManager:
    """
    キャッシュ管理・Prefetchロジックの責務を持つクラス (v5.0 Phase 1)
    """

    @staticmethod
    def get_text_hash(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:32]

    @staticmethod
    def sanitize_log(text: str) -> str:
        """ログ用にテキストをサニタイズ（ハッシュ化）"""
        if not text:
            return "[empty]"
        text_hash = CacheManager.get_text_hash(text)[:8]
        return f"[text:{text_hash}...len={len(text)}]"

    def check_cache(self, db: Session, text: str, seasoning: int) -> Optional[ProcessingSuccess]:
        """
        キャッシュを検索し、ヒットすれば結果を返す。
        ヒットしない場合はNoneを返す。
        """
        if db is None:
            return None

        text_hash = self.get_text_hash(text)
        cache_key = f"seasoning_{seasoning}"

        try:
            cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
            if cache and cache.results and cache_key in cache.results:
                cached_result = cache.results[cache_key]
                
                # エラー文字列がキャッシュされている場合はヒット扱いしない（再試行させる）
                if cached_result.startswith("Error:"):
                    return None

                logger.info(f"📦 Cache Hit: {CacheManager.sanitize_log(cached_result)}")
                return {
                    "result": cached_result,
                    "seasoning": seasoning,
                    "from_cache": True,
                    "model_used": None
                }
        except Exception as e:
            logger.warning(f"⚠️ Cache check failed: {e}")
            return None
        
        return None
