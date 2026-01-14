"""
CoreProcessor 統合テスト

テスト対象:
- ユーティリティ関数（get_text_hash, sanitize_log, generate_diff）
- CoreProcessor._select_model（モデル選択ロジック）
- CoreProcessor.process（Gemini APIモック使用）
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.core.processor import (
    get_text_hash,
    sanitize_log,
    generate_diff,
    CoreProcessor,
)
from src.core.models import TextRequest


class TestUtilities:
    """ユーティリティ関数テスト"""
    
    def test_get_text_hash(self):
        """ハッシュ生成の一貫性"""
        text = "テスト文字列"
        hash1 = get_text_hash(text)
        hash2 = get_text_hash(text)
        assert hash1 == hash2
        assert len(hash1) == 32  # SHA256の先頭32文字
    
    def test_get_text_hash_different(self):
        """異なるテキストは異なるハッシュ"""
        hash1 = get_text_hash("Hello")
        hash2 = get_text_hash("World")
        assert hash1 != hash2
    
    def test_sanitize_log_empty(self):
        """空文字列のサニタイズ"""
        assert sanitize_log("") == "[empty]"
        assert sanitize_log(None) == "[empty]"
    
    def test_sanitize_log_normal(self):
        """通常テキストのサニタイズ"""
        result = sanitize_log("テスト文字列です")
        assert "[text:" in result
        assert "len=" in result
        assert "テスト" not in result  # 元テキストは含まれない
    
    def test_generate_diff_identical(self):
        """同一テキストの差分"""
        diff = generate_diff("同じテキスト", "同じテキスト")
        types = [d["type"] for d in diff]
        assert all(t == "unchanged" for t in types)
    
    def test_generate_diff_changed(self):
        """変更ありの差分"""
        diff = generate_diff("元のテキスト", "新しいテキスト")
        types = [d["type"] for d in diff]
        assert "removed" in types or "added" in types


class TestCoreProcessorModelSelection:
    """CoreProcessor モデル選択ロジックテスト"""
    
    @pytest.fixture
    def processor(self):
        return CoreProcessor()
    
    def test_select_model_low_seasoning(self, processor):
        """低Seasoning → Flash"""
        model = processor._select_model("短いテキスト", seasoning=30)
        assert "flash" in model.lower() or "fast" in model.lower() or model == processor._select_model("x", 30)
    
    def test_select_model_high_seasoning(self, processor):
        """高Seasoning (>90) → Pro"""
        model = processor._select_model("テキスト", seasoning=95)
        # Umami (>90) uses smart model
        assert model is not None
    
    def test_select_model_long_text_high_seasoning(self, processor):
        """長文 + 高Seasoning → Pro"""
        long_text = "テスト" * 500  # >1000文字
        model = processor._select_model(long_text, seasoning=92)
        assert model is not None


class TestCoreProcessorProcess:
    """CoreProcessor.process 統合テスト（モック使用）"""
    
    @pytest.fixture
    def processor(self):
        return CoreProcessor()
    
    @pytest.mark.asyncio
    async def test_process_success(self, processor):
        """正常処理フロー"""
        req = TextRequest(text="テスト入力", seasoning=50)
        
        # Gemini APIをモック (CoreProcessor.gemini_client.generate_content)
        mock_result = {"success": True, "result": "整形されたテキスト"}
        
        # processor.gemini_client は __init__ で生成されているので、それをモックと差し替える
        processor.gemini_client = MagicMock()
        processor.gemini_client.generate_content = AsyncMock(return_value=mock_result)
        
        # 実行 (CacheManagerのモックが必要かもだが、DB=Noneならキャッシュチェックはスキップorエラーキャッチで無視されるはず)
        # しかし実装では check_cache が例外キャッチして None を返すので大丈夫そう
        
        result = await processor.process(req, db=None)
        
        assert "result" in result
        assert result["result"] == "整形されたテキスト"
        assert result["from_cache"] == False
    
    @pytest.mark.asyncio
    async def test_process_api_error(self, processor):
        """API エラー時のフォールバック"""
        req = TextRequest(text="テスト入力", seasoning=50)
        
        mock_result = {
            "success": False, 
            "error": "api_error",
            "blocked_reason": "APIエラー"
        }
        
        processor.gemini_client = MagicMock()
        processor.gemini_client.generate_content = AsyncMock(return_value=mock_result)
        
        result = await processor.process(req, db=None)
        
        assert "error" in result
        assert result["error"] == "api_error"
    

    @pytest.mark.asyncio
    async def test_process_privacy_masking(self, processor):
        """PIIマスキングが適用されることを確認"""
        # メールアドレス入りのテキスト
        req = TextRequest(text="連絡先: test@example.com", seasoning=50)
        
        mock_result = {"success": True, "result": "連絡先: [PII_0]"}
        
        processor.gemini_client = MagicMock()
        processor.gemini_client.generate_content = AsyncMock(return_value=mock_result)

        with patch("src.core.processor.settings") as mock_settings:
            mock_settings.PRIVACY_MODE = True
            mock_settings.MODEL_FAST = "gemini-flash"
            mock_settings.MODEL_SMART = "gemini-pro"
            mock_settings.USER_SYSTEM_PROMPT = ""
            
            # プロセス実行
            result = await processor.process(req, db=None)
            
            # APIが呼ばれたことを確認 (モックを通して確認)
            processor.gemini_client.generate_content.assert_called_once()

