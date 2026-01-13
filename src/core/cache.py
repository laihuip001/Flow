import logging
import hashlib
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from .models import PrefetchCache
from .types import ProcessingSuccess
from .seasoning import SeasoningManager, RESOLVED_LIGHT, RESOLVED_MEDIUM, RESOLVED_RICH

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

    def _check_ttl(self, cache: PrefetchCache) -> bool:
        """
        TTL (Time To Live / 賞味期限) チェック
        期限切れなら True を返す
        """
        from .config import settings
        from datetime import timedelta
        
        if not cache.created_at:
            return False

        limit = settings.CACHE_TTL_HOURS
        deadline = cache.created_at + timedelta(hours=limit)
        
        # 現在時刻が期限を過ぎていたら True (Expired)
        if datetime.utcnow() > deadline:
            logger.info(f"🗑️ Cache Expired: {cache.hash_id[:8]} (Created: {cache.created_at})")
            return True
        return False

    def _enforce_limit(self, db: Session):
        """
        LRU (Least Recently Used / 容量制限) チェック
        上限を超えていたら、一番古いアクセスのものを削除
        """
        from .config import settings
        
        max_entries = settings.CACHE_MAX_ENTRIES
        count = db.query(PrefetchCache).count()
        
        if count > max_entries:
            # 溢れた分だけ削除（念の為ループではなく一括削除を検討するが、ここでは1件ずつ古い順）
            over = count - max_entries
            logger.info(f"🧹 Cache Limit Exceeded ({count} > {max_entries}). Cleaning {over} items...")
            
            # last_accessed_at が古い順に取得して一括削除
            # SQLite does not support DELETE ... LIMIT directly in standard SQLAlchemy ORM bulk delete easily without subquery
            # but usually, fetching IDs and deleting by ID is safer and widely supported.
            
            victims = db.query(PrefetchCache.hash_id).order_by(PrefetchCache.last_accessed_at.asc()).limit(over).all()
            victim_ids = [v[0] for v in victims]
            
            if victim_ids:
                db.query(PrefetchCache).filter(PrefetchCache.hash_id.in_(victim_ids)).delete(synchronize_session=False)
                db.commit()

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
            
            # 1. TTL Check
            if cache and self._check_ttl(cache):
                # Expired: Treat as miss (Cleanup happens later or explicitly now?)
                # 簡易的にここで削除 or 無視。ここでは削除してしまうのがクリーン。
                db.delete(cache)
                db.commit()
                return None

            if cache and cache.results and cache_key in cache.results:
                cached_result = cache.results[cache_key]
                
                # エラー文字列がキャッシュされている場合はヒット扱いしない（再試行させる）
                if cached_result.startswith("Error:"):
                    return None

                # 2. LRU Update
                cache.last_accessed_at = datetime.utcnow()
                db.commit()

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

    # --- v5.0 Phase 3: Warmup Logic ---
    async def warmup_from_list(self, db: Session, templates: list[str], client, privacy, callback=None, force: bool = False) -> dict:
        """
        リスト内の定型文についてキャッシュを生成する（Warmup）。
        直列実行＋Waitによりレートリミットを回避する。

        Args:
            db: Database session
            templates: 文字列リスト
            client: GeminiClient instance
            privacy: PrivacyHandler instance
            callback: fn(current, total, text) -> None
            force: Trueなら既存キャッシュを無視して再生成

        Returns:
            dict: 処理結果統計
        """
        stats = {"total": len(templates), "processed": 0, "skipped": 0, "errors": 0}
        levels = [RESOLVED_LIGHT, RESOLVED_MEDIUM, RESOLVED_RICH]
        batch_size = 5  # M-03: Batch commit interval
        pending_commits = 0

        for i, text in enumerate(templates):
            text = text.strip()
            if not text:
                continue

            if callback:
                callback(i + 1, len(templates), text)

            try:
                text_hash = self.get_text_hash(text)
                cache = db.query(PrefetchCache).filter(PrefetchCache.hash_id == text_hash).first()
                
                current_results = {}
                
                if not cache:
                    # New Item
                    cache = PrefetchCache(hash_id=text_hash, original_text=text, results={})
                    # Don't add yet, merge later
                else:
                    if not force and cache.results and len(cache.results) >= 3:
                        stats["skipped"] += 1
                        logger.debug(f"Skipped: {text[:10]}...")
                        if callback: callback(i + 1, len(templates), f"{text[:20]} (Skip)")
                        continue
                    current_results = dict(cache.results) if cache.results else {}

                item_updated = False
                
                for season in levels:
                    key = f"seasoning_{season}"
                    if key in current_results and not force:
                        continue

                    # --- Generate ---
                    if callback: callback(i + 1, len(templates), f"{text[:20]} ({season})")
                    
                    masked, mapping = privacy.mask(text)
                    system_prompt = SeasoningManager.get_system_prompt(season)
                    
                    config = {
                        "system": system_prompt,
                        "params": {"temperature": 0.3}
                    }

                    # Call API
                    res = await client.generate_content(masked, config, model=None)

                    if res["success"]:
                        final_text = res["result"]
                        if mapping:
                            final_text = privacy.unmask(final_text, mapping)
                        
                        current_results[key] = final_text
                        item_updated = True
                        
                        # H-03: Exponential backoff for rate limiting
                        base_delay = 1.5
                        await asyncio.sleep(base_delay)
                    else:
                        err_msg = res.get('error')
                        reason = res.get('blocked_reason')
                        full_msg = f"{err_msg} ({reason})" if reason else err_msg
                        logger.error(f"❌ API Error for '{text[:10]}' ({season}): {full_msg}")
                        stats["errors"] += 1

                if item_updated:
                    cache.results = current_results
                    cache.updated_at = datetime.utcnow() # T-1: Valid now (Column added)
                    db.merge(cache)
                    pending_commits += 1
                    stats["processed"] += 1
                    
                    # M-03: Batch commits
                    if pending_commits >= batch_size:
                        db.commit()
                        pending_commits = 0
                        # Enforce Limit after batch commit
                        self._enforce_limit(db)
                        
                elif not cache.results: # Is new but failed all?
                     # If new and no results, commit emptiness or skip logic handled above
                     pass

            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.error(f"Example {CacheManager.sanitize_log(text)} failed: {e}")
                stats["errors"] += 1
                db.rollback()

        # Final commit and enforcement
        if pending_commits > 0:
            db.commit()
            self._enforce_limit(db)

        return stats
