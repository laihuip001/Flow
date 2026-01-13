
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
