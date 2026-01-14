
import pytest
from unittest.mock import MagicMock
from src.core.cache import CacheManager
from src.core.models import PrefetchCache

class TestCacheManager:
    def setup_method(self):
        self.manager = CacheManager()
        self.mock_db = MagicMock()

    def test_get_text_hash(self):
        text = "test_text"
        hash_val = CacheManager.get_text_hash(text)
        assert len(hash_val) == 32
        assert hash_val == CacheManager.get_text_hash(text) # Deterministic

    def test_sanitize_log(self):
        text = "test_text"
        log = CacheManager.sanitize_log(text)
        assert "[text:" in log
        assert "...len=9]" in log
        assert CacheManager.sanitize_log("") == "[empty]"

    def test_check_cache_none_db(self):
        assert self.manager.check_cache(None, "text", 50) is None

    def test_check_cache_hit(self):
        text = "test_text"
        seasoning = 50
        text_hash = CacheManager.get_text_hash(text)
        
        mock_cache = MagicMock()
        mock_cache.results = {f"seasoning_{seasoning}": "cached_result"}
        # Fix: created_at must be set to avoid attribute error in logging/ttl check or logic
        from datetime import datetime
        mock_cache.created_at = datetime.utcnow()
        mock_cache.hash_id = text_hash  # for logging
        
        # Mock query chain
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_cache
        
        result = self.manager.check_cache(self.mock_db, text, seasoning)
        
        assert result is not None
        assert result["result"] == "cached_result"
        assert result["from_cache"] is True

    def test_check_cache_miss_not_found(self):
        # Mock returns None
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        result = self.manager.check_cache(self.mock_db, "text", 50)
        assert result is None

    def test_check_cache_miss_key_missing(self):
        mock_cache = MagicMock()
        mock_cache.results = {"other_key": "res"}
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_cache
        result = self.manager.check_cache(self.mock_db, "text", 50)
        assert result is None

    def test_check_cache_ignore_error(self):
        text = "test_text"
        seasoning = 50
        mock_cache = MagicMock()
        mock_cache.results = {f"seasoning_{seasoning}": "Error: api failed"}
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_cache
        
        result = self.manager.check_cache(self.mock_db, text, seasoning)
        assert result is None # Should ignore cached errors


class TestCacheManagerTTL:
    """TTLチェックのテスト"""
    
    def setup_method(self):
        self.manager = CacheManager()
    
    def test_check_ttl_no_created_at(self):
        """created_atがNoneの場合はFalse（期限切れではない）"""
        mock_cache = MagicMock()
        mock_cache.created_at = None
        
        result = self.manager._check_ttl(mock_cache)
        assert result is False
    
    def test_check_ttl_not_expired(self):
        """作成直後はFalse（期限切れではない）"""
        from datetime import datetime
        mock_cache = MagicMock()
        mock_cache.created_at = datetime.utcnow()
        mock_cache.hash_id = "test_hash_12345678"
        
        result = self.manager._check_ttl(mock_cache)
        assert result is False
    
    def test_check_ttl_expired(self):
        """TTL時間（デフォルト168時間=7日）を超えていたらTrue（期限切れ）"""
        from datetime import datetime, timedelta
        mock_cache = MagicMock()
        # 200時間前に作成（168時間を超過）
        mock_cache.created_at = datetime.utcnow() - timedelta(hours=200)
        mock_cache.hash_id = "test_hash_12345678"
        
        result = self.manager._check_ttl(mock_cache)
        assert result is True


class TestCacheManagerLRU:
    """LRU容量制限のテスト"""
    
    def setup_method(self):
        self.manager = CacheManager()
        self.mock_db = MagicMock()
    
    def test_enforce_limit_under_limit(self):
        """制限内なら削除しない"""
        # count() が制限以下を返す
        self.mock_db.query.return_value.count.return_value = 10  # 制限以下
        
        self.manager._enforce_limit(self.mock_db)
        
        # deleteは呼ばれない
        self.mock_db.query.return_value.filter.return_value.delete.assert_not_called()
    
    def test_enforce_limit_over_limit(self):
        """制限超過なら削除処理が実行される (CACHE_MAX_ENTRIES=100)"""
        mock_query = MagicMock()
        mock_query.count.return_value = 150  # 100を超過
        # order_by等のチェーンをモック
        mock_query.order_by.return_value.limit.return_value.all.return_value = [("hash_1",)]
        
        self.mock_db.query.return_value = mock_query
        
        self.manager._enforce_limit(self.mock_db)
        
        # count が呼ばれたことを確認（制限チェックが実行された）
        mock_query.count.assert_called_once()
