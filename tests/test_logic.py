"""
AI-Clipboard-Pro: Unit Tests

pytest tests/ で実行
"""
import pytest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.privacy import PrivacyScanner, mask_pii, unmask_pii
from src.core.seasoning import SeasoningManager


class TestPrivacyScanner:
    """PrivacyScanner テスト"""
    
    def test_email_detection(self):
        """メールアドレス検知"""
        scanner = PrivacyScanner()
        result = scanner.scan("連絡先: test@example.com です")
        
        assert result["has_risks"] == True
        assert "EMAIL" in result["risks"]
        assert "test@example.com" in result["risks"]["EMAIL"]
    
    def test_phone_detection(self):
        """電話番号検知"""
        scanner = PrivacyScanner()
        result = scanner.scan("電話: 03-1234-5678")
        
        assert result["has_risks"] == True
        assert "PHONE" in result["risks"]
    
    def test_api_key_detection(self):
        """APIキー検知（拡張パターン）"""
        scanner = PrivacyScanner()
        result = scanner.scan("key: sk-1234567890abcdefghij1234")
        
        assert result["has_risks"] == True
        assert "API_KEY" in result["risks"]
    
    def test_sensitive_keyword_detection(self):
        """機密キーワード検知"""
        scanner = PrivacyScanner()
        result = scanner.scan("この資料は社外秘です")
        
        assert result["has_risks"] == True
        assert "SENSITIVE_KEYWORD" in result["risks"]
        assert "社外秘" in result["risks"]["SENSITIVE_KEYWORD"]
    
    def test_no_pii(self):
        """PII無しの場合"""
        scanner = PrivacyScanner()
        result = scanner.scan("今日は良い天気です")
        
        assert result["has_risks"] == False
        assert result["risk_count"] == 0


class TestPIIMasking:
    """PII Masking テスト"""
    
    def test_mask_and_unmask(self):
        """マスク→アンマスクの往復"""
        original = "連絡先: test@example.com, 電話: 03-1234-5678"
        
        masked, mapping = mask_pii(original)
        
        # マスクされていることを確認
        assert "test@example.com" not in masked
        assert "[PII_" in masked
        
        # アンマスクで復元
        restored = unmask_pii(masked, mapping)
        assert restored == original
    
    def test_no_pii_passthrough(self):
        """PII無しはそのまま通過"""
        original = "Hello World"
        masked, mapping = mask_pii(original)
        
        assert masked == original
        assert mapping == {}


class TestSeasoningManager:
    """SeasoningManager テスト (v4.0)"""
    
    def test_salt_prompt(self):
        """Salt (0-30) プロンプト取得"""
        prompt = SeasoningManager.get_system_prompt(10)
        
        assert "Text Cleaner" in prompt
        assert "Fix typos" in prompt
    
    def test_sauce_prompt(self):
        """Sauce (31-70) プロンプト取得"""
        prompt = SeasoningManager.get_system_prompt(50)
        
        assert "Text Editor" in prompt
        assert "Clarify" in prompt
    
    def test_spice_prompt(self):
        """Spice (71-100) プロンプト取得"""
        prompt = SeasoningManager.get_system_prompt(90)
        
        assert "Text Enhancer" in prompt
        assert "Elaborate" in prompt
    
    def test_level_label(self):
        """レベルラベル取得"""
        assert SeasoningManager.get_level_label(10) == "Salt (Minimal)"
        assert SeasoningManager.get_level_label(50) == "Sauce (Standard)"
        assert SeasoningManager.get_level_label(90) == "Spice (Rich)"
