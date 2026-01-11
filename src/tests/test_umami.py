import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.seasoning import SeasoningManager
from core.processor import CoreProcessor
from core.config import settings
from core.models import TextRequest

class TestUmamiSeasoning(unittest.TestCase):
    def test_seasoning_constants(self):
        """Verify Umami threshold constants are effectively working"""
        # Testing behavior via public API since constants might be internal
        self.assertEqual(SeasoningManager.get_level_label(80), "Spice (Rich)")
        self.assertEqual(SeasoningManager.get_level_label(95), "Umami (Deep Context)")

    def test_seasoning_prompt(self):
        """Verify Umami prompt generation"""
        prompt = SeasoningManager.get_system_prompt(95)
        self.assertIn("Context Architect", prompt)
        self.assertIn("Deep Context", prompt) # Or whatever key phrase we decide on

    def test_processor_model_selection(self):
        """Verify CoreProcessor selects SMART model for Umami"""
        processor = CoreProcessor()
        
        # Helper to expose the private method for testing, 
        # or we verify by mocking settings and checking behavior if possible.
        # Since _select_model is protected, we can access it for testing purposes in Python.
        
        # Case 1: Low seasoning, short text -> FAST model
        model = processor._select_model("short text", 50)
        self.assertEqual(model, settings.MODEL_FAST)
        
        # Case 2: High seasoning (Spice), short text -> FAST model (as per original logic)
        model = processor._select_model("short text", 80)
        self.assertEqual(model, settings.MODEL_FAST)

        # Case 3: High seasoning (Spice), long text -> SMART model (original logic condition)
        # Original logic: len > 1000 and seasoning >= 90 (Wait, existing was >=90 for smart?)
        # Let's check the existing code again. 
        # "len(text) > 1000 and seasoning >= 90" was the condition for SMART.
        # If we change seasoning >= 90 to be Umami, then Umami should ALWAYS use SMART?
        # The plan says: "Umami always uses the high-intelligence model (Gemini Pro 1.5) regardless of text length."
        
        # So for Umami (95), even short text should use SMART.
        model = processor._select_model("short text", 95)
        self.assertEqual(model, settings.MODEL_SMART)

if __name__ == '__main__':
    unittest.main()
