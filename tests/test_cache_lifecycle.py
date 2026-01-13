import sys
import os
import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.models import Base, PrefetchCache
from src.core.cache import CacheManager
from src.core.config import settings

class TestCacheLifecycle(unittest.TestCase):
    def setUp(self):
        # Use simple in-memory DB for testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.mgr = CacheManager()

    def tearDown(self):
        self.db.close()

    def test_ttl_expiry(self):
        """賞味期限 (TTL) のテスト"""
        # 1. 期限切れのデータを作成 (作成日を8日前に設定: TTLはデフォルト168h=7日)
        old_date = datetime.utcnow() - timedelta(days=8)
        text = "old_onigiri"
        text_hash = self.mgr.get_text_hash(text)
        
        item = PrefetchCache(
            hash_id=text_hash,
            original_text=text,
            results={"seasoning_30": "stale data"},
            created_at=old_date,
            last_accessed_at=old_date
        )
        self.db.add(item)
        self.db.commit()

        # 2. Check Cache
        # ヒットしない（期限切れで削除される）はず
        result = self.mgr.check_cache(self.db, text, 30)
        self.assertIsNone(result, "期限切れデータはNoneを返すべき")
        
        # DBからも消えているか確認
        check = self.db.query(PrefetchCache).filter_by(hash_id=text_hash).first()
        self.assertIsNone(check, "期限切れデータは削除されるべき")

    def test_lru_limit(self):
        """容量制限 (LRU) のテスト"""
        # 設定を一時的に変更 (最大2件)
        from unittest.mock import patch
        
        # Safe patching of settings
        with patch("src.core.config.settings.CACHE_MAX_ENTRIES", 2):
            # 1. 2件追加
            items = []
            for i in range(2):
                t = f"item_{i}"
                h = self.mgr.get_text_hash(t)
                # last_accessed_at をずらす (item_0 が一番古い)
                acc = datetime.utcnow() - timedelta(minutes=10 - i)
                item = PrefetchCache(
                    hash_id=h, original_text=t, results={}, 
                    created_at=datetime.utcnow(), last_accessed_at=acc
                )
                self.db.add(item)
                items.append(h)
            self.db.commit()
            
            # Count check
            count = self.db.query(PrefetchCache).count()
            self.assertEqual(count, 2)
            
            # 2. 3件目を追加 (制限発動)
            
            # 3件目を追加
            t3 = "item_new"
            h3 = self.mgr.get_text_hash(t3)
            item3 = PrefetchCache(
                hash_id=h3, original_text=t3, results={},
                created_at=datetime.utcnow(), last_accessed_at=datetime.utcnow()
            )
            self.db.add(item3)
            self.db.commit()
            
            # Limit発動
            self.mgr._enforce_limit(self.db)
            
            # 残りは2件のはず
            count = self.db.query(PrefetchCache).count()
            self.assertEqual(count, 2, "3件追加後は2件に削減されるべき")
            
            # 一番古かった item_0 (items[0]) が消えているはず
            check_old = self.db.query(PrefetchCache).filter_by(hash_id=items[0]).first()
            self.assertIsNone(check_old, "一番古いデータが削除されるべき")
            
            # item_1 と item_new は残っているはず
            check_1 = self.db.query(PrefetchCache).filter_by(hash_id=items[1]).first()
            check_new = self.db.query(PrefetchCache).filter_by(hash_id=h3).first()
            self.assertIsNotNone(check_1)
            self.assertIsNotNone(check_new)

if __name__ == "__main__":
    unittest.main()
