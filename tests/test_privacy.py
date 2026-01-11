
import pytest
from src.core.privacy import PrivacyScanner, mask_pii, unmask_pii

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

    def test_overlap_credit_card_my_number(self):
        """
        Verify that a Credit Card (16 digits) is not partially masked as My Number (12 digits).
        Prior to optimization, My Number (12) would match the first 12 digits of CC (16), leaving 4 digits exposed.
        """
        cc = "1234-5678-9012-3456"
        masked, mapping = mask_pii(f"Payment: {cc}")

        # Should be masked as one PII entity
        assert cc not in masked
        assert "[PII_0]-3456" not in masked
        # The whole CC number should be in the mapping
        assert list(mapping.values())[0] == cc

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
        # Not masking address text yet, only ZIP
