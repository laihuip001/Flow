"""
Unit Tests for SeasoningManager
v5.0
"""
import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.seasoning import (
    SeasoningManager,
    RESOLVED_LIGHT,
    RESOLVED_MEDIUM,
    RESOLVED_RICH,
    LIGHT_MAX,
    MEDIUM_MAX,
    RICH_MAX
)


class TestSeasoningManager(unittest.TestCase):

    def test_resolve_level_light(self):
        """resolve_level: 0-45 → RESOLVED_LIGHT (30)"""
        self.assertEqual(SeasoningManager.resolve_level(0), RESOLVED_LIGHT)
        self.assertEqual(SeasoningManager.resolve_level(30), RESOLVED_LIGHT)
        self.assertEqual(SeasoningManager.resolve_level(45), RESOLVED_LIGHT)

    def test_resolve_level_medium(self):
        """resolve_level: 46-75 → RESOLVED_MEDIUM (60)"""
        self.assertEqual(SeasoningManager.resolve_level(46), RESOLVED_MEDIUM)
        self.assertEqual(SeasoningManager.resolve_level(60), RESOLVED_MEDIUM)
        self.assertEqual(SeasoningManager.resolve_level(75), RESOLVED_MEDIUM)

    def test_resolve_level_rich(self):
        """resolve_level: 76-100 → RESOLVED_RICH (100)"""
        self.assertEqual(SeasoningManager.resolve_level(76), RESOLVED_RICH)
        self.assertEqual(SeasoningManager.resolve_level(100), RESOLVED_RICH)

    def test_get_level_label(self):
        """get_level_label: 各レベルで正しいラベルを返す"""
        self.assertEqual(SeasoningManager.get_level_label(30), "Light（軽め）")
        self.assertEqual(SeasoningManager.get_level_label(50), "Medium（標準）")
        self.assertEqual(SeasoningManager.get_level_label(80), "Rich（濃いめ）")
        self.assertEqual(SeasoningManager.get_level_label(95), "Deep（深い）")

    def test_get_system_prompt_light(self):
        """get_system_prompt: Light レベルで正しいプロンプトを返す"""
        prompt = SeasoningManager.get_system_prompt(30)
        self.assertIn("誤字脱字", prompt)
        self.assertIn("元の意図", prompt)

    def test_get_system_prompt_medium(self):
        """get_system_prompt: Medium レベルで正しいプロンプトを返す"""
        prompt = SeasoningManager.get_system_prompt(60)
        self.assertIn("プロンプトとして整形", prompt)
        self.assertIn("箇条書き", prompt)

    def test_get_system_prompt_rich(self):
        """get_system_prompt: Rich レベルで正しいプロンプトを返す"""
        prompt = SeasoningManager.get_system_prompt(85)
        self.assertIn("強化", prompt)
        self.assertIn("補完", prompt)

    def test_get_system_prompt_deep(self):
        """get_system_prompt: Deep レベルで正しいプロンプトを返す"""
        prompt = SeasoningManager.get_system_prompt(95)
        self.assertIn("深く解釈", prompt)
        self.assertIn("昇華", prompt)

    def test_get_system_prompt_with_user_prompt(self):
        """get_system_prompt: ユーザープロンプトが追加されること"""
        prompt = SeasoningManager.get_system_prompt(30, "追加の指示です")
        self.assertIn("追加指示:", prompt)
        self.assertIn("追加の指示です", prompt)

    def test_get_system_prompt_clamping(self):
        """get_system_prompt: 範囲外の値がクランプされること"""
        # -10 → 0 (Light)
        prompt_neg = SeasoningManager.get_system_prompt(-10)
        self.assertIn("誤字脱字", prompt_neg)
        
        # 150 → 100 (Deep)
        prompt_over = SeasoningManager.get_system_prompt(150)
        self.assertIn("深く解釈", prompt_over)


if __name__ == "__main__":
    unittest.main()
