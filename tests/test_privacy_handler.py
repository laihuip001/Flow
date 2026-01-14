import pytest
from unittest.mock import MagicMock, patch
from src.core.privacy import PrivacyHandler

class TestPrivacyHandler:
    @pytest.fixture
    def handler(self):
        return PrivacyHandler()

    @patch("src.core.vocab_store.get_vocab_store")
    def test_mask_with_custom_vocab(self, mock_get_store, handler):
        """カスタム語彙ストアを使用したマスク処理のテスト"""
        # Mockのセットアップ
        mock_store = MagicMock()
        mock_store.find_in_text.return_value = ["Project Titan"]
        mock_get_store.return_value = mock_store

        text = "Meeting regarding Project Titan."
        masked, mapping = handler.mask(text, use_custom_vocab=True)

        assert "Project Titan" not in masked
        assert "[VOCAB_" in masked
        assert "Project Titan" in mapping.values()
        
        # 復元テスト
        restored = handler.unmask(masked, mapping)
        assert restored == text

    @patch("src.core.vocab_store.get_vocab_store")
    def test_mask_vocab_error_fallback(self, mock_get_store, handler):
        """VocabStoreがエラーを返してもプロセスが落ちないことを確認"""
        mock_get_store.side_effect = Exception("Database connection failed")

        text = "Hello world."
        # エラーが発生しても例外はキャッチされてマスク処理自体は成功すべき（PIIマスクのみ） (Falseにならないか確認)
        masked, mapping = handler.mask(text, use_custom_vocab=True)
        
        assert masked == text
        assert mapping == {}

    def test_handler_initialization(self, handler):
        assert handler.scanner is not None
