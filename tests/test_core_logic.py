"""
Unit Tests for Core Logic (Flow v4.0)
Testing CoreProcessor with mocked DB and External API
"""
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.core.processor import CoreProcessor, generate_diff
from src.core.models import TextRequest
from src.core.types import ProcessingResult

class TestCoreProcessor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.processor = CoreProcessor()
        self.mock_db = MagicMock()

    def test_diff_generation(self):
        """Diff生成ロジックのテスト"""
        original = "Hello World"
        result = "Hello Python"
        diff = generate_diff(original, result)
        
        # Check structure
        self.assertIsInstance(diff, list)
        self.assertTrue(all("type" in d for d in diff))
        self.assertTrue(all("content" in d for d in diff))
        
        # Check logic
        # Expect: "Hello " (unchanged), "World" (removed), "Python" (added) or line based
        # generate_diff is line-based.
        # Line 1: "Hello World" -> "Hello Python" (replace)
        self.assertEqual(len(diff), 2) # removed, added
        self.assertEqual(diff[0]["type"], "removed")
        self.assertEqual(diff[1]["type"], "added")

    async def test_process_success(self):
        """正常系プロセスのテスト"""
        # Setup mocks
        self.processor.privacy_handler = MagicMock()
        self.processor.privacy_handler.mask.return_value = ("masked_text", {})
        self.processor.privacy_handler.unmask.return_value = "processed_text"

        self.processor.gemini_client = AsyncMock()
        self.processor.gemini_client.generate_content.return_value = {"success": True, "result": "processed_text"}
        
        req = TextRequest(text="input", seasoning=30)
        
        # Execute
        result = await self.processor.process(req, self.mock_db)
        
        # Assertions
        self.assertIn("result", result)
        self.assertEqual(result["result"], "processed_text")
        self.assertEqual(result["seasoning"], 30)
        self.assertIn("model_used", result)
        self.assertFalse(result.get("from_cache", True)) # Should be False

    async def test_process_api_failure(self):
        """APIエラー時のテスト"""
        self.processor.gemini_client = AsyncMock()
        self.processor.gemini_client.generate_content.return_value = {
            "success": False, 
            "error": "api_error", 
            "blocked_reason": "Limit exceeded"
        }
        
        req = TextRequest(text="input", seasoning=30)
        
        # Execute
        result = await self.processor.process(req, self.mock_db)
        
        # Assertions
        self.assertIn("error", result)
        self.assertEqual(result["error"], "api_error")
        # Cache fallback logic might trigger, but mock_db returns None for cache, so error returns.

if __name__ == "__main__":
    unittest.main()
