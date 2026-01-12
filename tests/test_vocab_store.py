"""
VocabularyStore テスト
"""
import pytest
import tempfile
import os
from pathlib import Path
from src.core.vocab_store import VocabularyStore


class TestVocabularyStore:
    """語彙ストア基本機能テスト"""
    
    @pytest.fixture
    def store(self, tmp_path):
        """テスト用の一時DBを使用"""
        db_path = tmp_path / "test_vocab.db"
        store = VocabularyStore(db_path=db_path)
        yield store
        # 明示的クリーンアップ不要（tmp_pathがpytestで管理）
    
    def test_add_and_list(self, store):
        """語彙追加と一覧取得"""
        assert store.add_term("プロジェクトX", "project")
        assert store.add_term("山田部長", "person")
        
        all_vocab = store.list_all()
        assert len(all_vocab) == 2
        terms = [v["term"] for v in all_vocab]
        assert "プロジェクトX" in terms
        assert "山田部長" in terms
    
    def test_duplicate_prevention(self, store):
        """重複登録防止"""
        assert store.add_term("機密情報", "custom")
        assert not store.add_term("機密情報", "custom")  # 重複はFalse
        assert store.count() == 1
    
    def test_remove(self, store):
        """語彙削除"""
        store.add_term("削除対象", "test")
        assert store.count() == 1
        store.remove_term("削除対象")
        assert store.count() == 0
    
    def test_find_in_text(self, store):
        """テキスト内の語彙検出"""
        store.add_term("プロジェクトX", "project")
        store.add_term("極秘計画", "secret")
        
        text = "プロジェクトXの進捗報告です。"
        found = store.find_in_text(text)
        assert "プロジェクトX" in found
        assert "極秘計画" not in found
    
    def test_search(self, store):
        """部分一致検索"""
        store.add_term("開発チームA", "team")
        store.add_term("開発チームB", "team")
        store.add_term("営業部門", "dept")
        
        results = store.search("開発")
        assert len(results) == 2
    
    def test_empty_store(self, store):
        """空ストアの動作"""
        assert store.count() == 0
        assert store.list_all() == []
        assert store.find_in_text("テスト") == []
