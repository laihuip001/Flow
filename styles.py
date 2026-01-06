"""
Styles Module - スタイル定義とプロンプト生成

責務: スタイル設定の管理、プロンプト構築
"""


class StyleManager:
    """スタイル定義とプロンプト生成"""

    STYLES = {
        "business": {
            "system": "Rewrite as polite business email. Keep meaning.",
            "params": {"temperature": 0.3},
        },
        "casual": {
            "system": "Rewrite casually for chat. Add emoji. Keep meaning.",
            "params": {"temperature": 0.5},
        },
        "summary": {
            "system": "Summarize in concise bullet points. Keep meaning.",
            "params": {"temperature": 0.2},
        },
        "english": {
            "system": "Translate to professional English. Keep meaning.",
            "params": {"temperature": 0.3},
        },
        "proofread": {
            "system": "Fix typos only. Keep original meaning.",
            "params": {"temperature": 0.0},
        },
    }

    def get_config(self, style_key: str, app_name: str = None) -> dict:
        """スタイルに対応する設定を取得"""
        if style_key in self.STYLES:
            return self.STYLES[style_key]
        # フォールバック: proofread
        return self.STYLES["proofread"]
