"""
Flow AI - SeasoningManager テスト

SeasoningManagerの各メソッドの動作を検証する
"""

import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.seasoning import SeasoningManager, LIGHT_MAX, MEDIUM_MAX, RICH_MAX


class TestSeasoningManager(unittest.TestCase):
    """SeasoningManagerの単体テスト"""

    def test_get_level_label_light(self):
        """Light (0-40) のラベル取得"""
        self.assertEqual(SeasoningManager.get_level_label(0), "Light（軽め）")
        self.assertEqual(SeasoningManager.get_level_label(20), "Light（軽め）")
        self.assertEqual(SeasoningManager.get_level_label(40), "Light（軽め）")

    def test_get_level_label_medium(self):
        """Medium (41-70) のラベル取得"""
        self.assertEqual(SeasoningManager.get_level_label(41), "Medium（標準）")
        self.assertEqual(SeasoningManager.get_level_label(50), "Medium（標準）")
        self.assertEqual(SeasoningManager.get_level_label(70), "Medium（標準）")

    def test_get_level_label_rich(self):
        """Rich (71-90) のラベル取得"""
        self.assertEqual(SeasoningManager.get_level_label(71), "Rich（濃いめ）")
        self.assertEqual(SeasoningManager.get_level_label(80), "Rich（濃いめ）")
        self.assertEqual(SeasoningManager.get_level_label(90), "Rich（濃いめ）")

    def test_get_level_label_deep(self):
        """Deep (91-100) のラベル取得"""
        self.assertEqual(SeasoningManager.get_level_label(91), "Deep（深い）")
        self.assertEqual(SeasoningManager.get_level_label(100), "Deep（深い）")

    def test_get_system_prompt_light(self):
        """Light レベルのプロンプト生成"""
        prompt = SeasoningManager.get_system_prompt(20)
        self.assertIn("誤字脱字", prompt)
        self.assertIn("説明不要", prompt)

    def test_get_system_prompt_medium(self):
        """Medium レベルのプロンプト生成"""
        prompt = SeasoningManager.get_system_prompt(50)
        self.assertIn("プロンプトとして整形", prompt)
        self.assertIn("構造を整理", prompt)

    def test_get_system_prompt_structure(self):
        """プロンプト生成の基本構造チェック"""
        prompt = SeasoningManager.get_system_prompt(30)
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 10)

    def test_resolve_level_boundary(self):
        """v4.2 3段階化の境界値テスト (Light/Medium/Rich)"""
        # Light (<= 45) -> 30
        self.assertEqual(SeasoningManager.resolve_level(0), 30)
        self.assertEqual(SeasoningManager.resolve_level(45), 30)
        
        # Medium (46 - 75) -> 60
        self.assertEqual(SeasoningManager.resolve_level(46), 60)
        self.assertEqual(SeasoningManager.resolve_level(60), 60)
        self.assertEqual(SeasoningManager.resolve_level(75), 60)
        
        # Rich (>= 76) -> 100
        self.assertEqual(SeasoningManager.resolve_level(76), 100)
        self.assertEqual(SeasoningManager.resolve_level(90), 100)
        self.assertEqual(SeasoningManager.resolve_level(100), 100)

    def test_get_system_prompt_rich(self):
        """Rich レベルのプロンプト生成"""
        prompt = SeasoningManager.get_system_prompt(80)
        self.assertIn("強化", prompt)
        self.assertIn("論理構造", prompt)

    def test_get_system_prompt_deep(self):
        """Deep レベルのプロンプト生成"""
        prompt = SeasoningManager.get_system_prompt(95)
        self.assertIn("深く解釈", prompt)
        self.assertIn("洞察", prompt)

    def test_get_system_prompt_with_user_prompt(self):
        """ユーザーカスタム指示の追加"""
        custom = "丁寧語で出力してください"
        prompt = SeasoningManager.get_system_prompt(50, user_prompt=custom)
        self.assertIn("追加指示:", prompt)
        self.assertIn(custom, prompt)

    def test_get_system_prompt_clamps_level(self):
        """レベル値が0-100に収まることを確認"""
        # 負の値は0にclamp
        prompt_neg = SeasoningManager.get_system_prompt(-10)
        prompt_zero = SeasoningManager.get_system_prompt(0)
        self.assertEqual(prompt_neg, prompt_zero)
        
        # 100超えは100にclamp
        prompt_over = SeasoningManager.get_system_prompt(150)
        prompt_hundred = SeasoningManager.get_system_prompt(100)
        self.assertEqual(prompt_over, prompt_hundred)


if __name__ == '__main__':
    unittest.main()
