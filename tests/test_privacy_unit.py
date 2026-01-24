
import unittest
from src.core.privacy import PrivacyScanner

class TestPrivacyScannerCorrectness(unittest.TestCase):
    def setUp(self):
        self.scanner = PrivacyScanner()

    def test_scan_email(self):
        text = "Contact me at test@example.com"
        result = self.scanner.scan(text)
        self.assertTrue(result["has_risks"])
        self.assertIn("EMAIL", result["risks"])
        self.assertIn("test@example.com", result["risks"]["EMAIL"])

    def test_scan_phone(self):
        text = "Call 090-1234-5678"
        result = self.scanner.scan(text)
        self.assertTrue(result["has_risks"])
        self.assertIn("PHONE", result["risks"])
        self.assertIn("090-1234-5678", result["risks"]["PHONE"])

    def test_scan_keyword(self):
        text = "This is CONFIDENTIAL information."
        result = self.scanner.scan(text)
        self.assertTrue(result["has_risks"])
        self.assertIn("SENSITIVE_KEYWORD", result["risks"])
        self.assertIn("CONFIDENTIAL", result["risks"]["SENSITIVE_KEYWORD"])

    def test_scan_keyword_case_insensitive(self):
        text = "This is confidential information."
        result = self.scanner.scan(text)
        self.assertTrue(result["has_risks"])
        self.assertIn("SENSITIVE_KEYWORD", result["risks"])
        # The scanner returns the keyword from its list (uppercase)
        self.assertIn("CONFIDENTIAL", result["risks"]["SENSITIVE_KEYWORD"])

    def test_scan_multiple(self):
        text = "Email: test@example.com, Phone: 090-1234-5678"
        result = self.scanner.scan(text)
        self.assertTrue(result["has_risks"])
        self.assertIn("EMAIL", result["risks"])
        self.assertIn("PHONE", result["risks"])

    def test_no_risks(self):
        text = "Hello world. This is safe text."
        result = self.scanner.scan(text)
        self.assertFalse(result["has_risks"])
        self.assertEqual(result["risk_count"], 0)

    def test_check_deny_list(self):
        text = "This is CONFIDENTIAL"
        is_blocked, kw = self.scanner.check_deny_list(text)
        self.assertTrue(is_blocked)
        self.assertEqual(kw, "CONFIDENTIAL")

    def test_check_deny_list_case_insensitive(self):
        text = "This is confidential"
        is_blocked, kw = self.scanner.check_deny_list(text)
        self.assertTrue(is_blocked)
        self.assertEqual(kw, "CONFIDENTIAL")

    def test_check_deny_list_safe(self):
        text = "This is safe"
        is_blocked, kw = self.scanner.check_deny_list(text)
        self.assertFalse(is_blocked)
        self.assertIsNone(kw)

if __name__ == "__main__":
    unittest.main()
