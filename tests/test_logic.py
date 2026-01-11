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
    """SeasoningManager テスト (v4.1 日本語版)"""
    
    def test_light_prompt(self):
        """Light (0-40) プロンプト取得"""
        prompt = SeasoningManager.get_system_prompt(10)
        
        # 日本語プロンプトに変更: 誤字脱字修正、元の意図を維持
        assert "入力文を整形" in prompt
        assert "誤字脱字" in prompt
    
    def test_medium_prompt(self):
        """Medium (41-70) プロンプト取得"""
        prompt = SeasoningManager.get_system_prompt(50)
        
        # プロンプトとして整形、構造を整理
        assert "プロンプトとして整形" in prompt
        assert "構造を整理" in prompt
    
    def test_rich_prompt(self):
        """Rich (71-90) プロンプト取得"""
        prompt = SeasoningManager.get_system_prompt(80)
        
        # 入力文を強化、不足している情報を補完
        assert "強化" in prompt
        assert "補完" in prompt
    
    def test_level_label(self):
        """レベルラベル取得 (日本語版)"""
        assert SeasoningManager.get_level_label(10) == "Light（軽め）"
        assert SeasoningManager.get_level_label(50) == "Medium（標準）"
        assert SeasoningManager.get_level_label(80) == "Rich（濃いめ）"
        assert SeasoningManager.get_level_label(95) == "Deep（深い）"
