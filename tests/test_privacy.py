
import pytest
from src.core.privacy import PrivacyScanner, mask_pii, unmask_pii, PrivacyScanner

class TestPrivacyScanner:
    """Zero-Trust Privacy Scanner Tests"""

    @pytest.fixture
    def scanner(self):
        return PrivacyScanner()

    def test_email_masking(self):
        text = "Contact me at test.user@example.com immediately."
        masked, mapping = mask_pii(text)
        assert "test.user@example.com" not in masked
        assert "[PII_" in masked
        assert unmask_pii(masked, mapping) == text
        
    def test_phone_jp(self):
        phones = ["090-1234-5678", "03-1234-5678", "0120-123-456"]
        for p in phones:
            masked, mapping = mask_pii(f"Call {p}")
            assert p not in masked
            assert_restored = unmask_pii(masked, mapping)
            assert p in assert_restored

    def test_credit_card(self):
        # Fake numbers but matching pattern
        cc = "4532-1234-5678-9012"
        masked, _ = mask_pii(f"Pay with {cc}")
        assert cc not in masked
        assert "PII" in masked

    def test_api_keys(self):
        keys = [
            "sk-1234567890abcdef1234567890abcdef",
            "xoxb-123456789012-1234567890123-abcdef123",
            "AIzaSyD-1234567890abcdef1234567890ab"
        ]
        for k in keys:
            masked, _ = mask_pii(f"Key is {k}")
            assert k not in masked

    def test_my_number(self):
        mn = "1234-5678-9012"
        masked, _ = mask_pii(f"My number is {mn}")
        assert mn not in masked

    def test_ip_address(self):
        ip = "192.168.1.1"
        masked, _ = mask_pii(f"Server at {ip}")
        assert ip not in masked

    def test_sensitive_keywords(self):
        # Keywords are detected but NOT masked by default in current logic? 
        # Check logic.py: It scans keywords but mask_pii only loops over `findings["risks"]`.
        # logic.py Line 81: findings["SENSITIVE_KEYWORD"] = ...
        # logic.py Line 105: for pii_type, values in findings["risks"].items():
        # So it DOES mask them if they are in 'risks'.
        text = "This is CONFIDENTIAL data."
        # However, logic.py PrivacyScanner.scan returns {"risks": findings}.
        # So YES, it should mask keywords.
        masked, _ = mask_pii(text)
        assert "CONFIDENTIAL" not in masked

    def test_multiple_pii(self):
        text = "Email: foo@bar.com, Phone: 090-0000-0000"
        masked, mapping = mask_pii(text)
        assert "foo@bar.com" not in masked
        assert "090-0000-0000" not in masked
        assert len(mapping) == 2
        assert unmask_pii(masked, mapping) == text

    def test_no_pii(self):
        text = "Hello world safe text."
        masked, mapping = mask_pii(text)
        assert masked == text
        assert mapping == {}

    def test_fail_safe_pattern(self):
        """Ensure no partial leaks"""
        text = "sk-too-short"
        masked, _ = mask_pii(text)
        # Should NOT mask (too short)
        assert text == masked

    def test_japanese_address_zip(self):
        text = "〒100-0001 東京都千代田区"
        masked, _ = mask_pii(text)
        assert "100-0001" not in masked

    # v4.1 新パターンテスト
    def test_new_api_key_patterns(self):
        """gsk_, glpat-, Bearer トークンの検出"""
        keys = [
            "gsk_1234567890abcdef1234567890abcdef",
            "glpat-1234567890abcdef1234567890",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6",
        ]
        for k in keys:
            masked, _ = mask_pii(f"Token: {k}")
            assert k not in masked, f"Failed to mask: {k}"

    def test_aws_key_pattern(self):
        """AWS Access Key ID の検出 (AKIA...)"""
        keys = [
            "AKIAIOSFODNN7EXAMPLE",
            "AKIA0123456789ABCDEF",
        ]
        for k in keys:
            masked, _ = mask_pii(f"AWS Key: {k}")
            assert k not in masked, f"Failed to mask: {k}"
            assert "[PII_" in masked

    def test_password_pattern(self):
        """password=, secret: 形式の検出"""
        patterns = [
            "password=mysecretpass123",
            "secret: my_api_secret_key",
            "TOKEN=abcdefgh12345678",
        ]
        for p in patterns:
            masked, _ = mask_pii(f"Config: {p}")
            # パスワード値がマスクされているか確認
            assert "[PII_" in masked, f"Failed to mask: {p}"

    def test_japanese_address_full(self):
        """日本住所パターンの検出"""
        addresses = [
            "東京都渋谷区",
            "大阪府大阪市",
            "北海道札幌市",
            "神奈川県横浜市",
        ]
        for addr in addresses:
            masked, _ = mask_pii(f"住所: {addr}")
            assert addr not in masked, f"Failed to mask: {addr}"

    # check_deny_list テスト
    def test_deny_list_blocks_confidential(self, scanner):
        """機密キーワードでブロックされることを確認"""
        is_blocked, keyword = scanner.check_deny_list("This is CONFIDENTIAL data")
        assert is_blocked is True
        assert keyword == "CONFIDENTIAL"

    def test_deny_list_blocks_japanese(self, scanner):
        """日本語機密キーワードでブロックされることを確認"""
        is_blocked, keyword = scanner.check_deny_list("この文書は社外秘です")
        assert is_blocked is True
        assert keyword == "社外秘"

    def test_deny_list_case_insensitive(self, scanner):
        """大文字小文字を無視してブロックすることを確認"""
        is_blocked, keyword = scanner.check_deny_list("this is secret info")
        assert is_blocked is True
        assert keyword == "SECRET"

    def test_deny_list_allows_safe_text(self, scanner):
        """安全なテキストはブロックされないことを確認"""
        is_blocked, keyword = scanner.check_deny_list("Hello, this is a normal message.")
        assert is_blocked is False
        assert keyword is None


