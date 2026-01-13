# ========================================
# Flow v4.1: 下処理の美学 (Pre-processing Philosophy)
# ========================================
# 設計原則:
# 1. 下処理の美学 → 素材を活かす。過剰加工しない
# 2. 非破壊的介入 → 既存AIの人格を上書きしない。黒子に徹する
# 3. ゼロ・フリクション → 最短・最速。思考を止めない
# ========================================

# Thresholds (レベル境界)
LIGHT_MAX = 40
MEDIUM_MAX = 70
RICH_MAX = 90  # 91-100 is Deep

# 3-Stage Seasoning (v4.2)
RESOLVED_LIGHT = 30
RESOLVED_MEDIUM = 60
RESOLVED_RICH = 100


class SeasoningManager:
    """
    「生言語の翻訳者」としてのプロンプト管理
    Level 0-100 のスペクトラムで下処理の強度を制御
    """

    @staticmethod
    def get_system_prompt(level: int = LIGHT_MAX, user_prompt: str = "") -> str:
        """
        システムプロンプト生成（速度最優先）
        
        - Role指定なし（既存チャットのSystem Instructionと競合しない）
        - 日本語指示（日本語入力には日本語指示が正確）
        - 最短トークン（レイテンシ削減）
        """
        level = max(0, min(100, level))

        if level <= LIGHT_MAX:
            # Light: 最小限の整形。素材を最大限活かす
            base = (
                "入力文を整形してください。\n"
                "・誤字脱字と句読点を修正\n"
                "・曖昧な表現を明確化\n"
                "・元の意図とトーンは維持\n"
                "出力は整形後のテキストのみ。説明不要。"
            )
        elif level <= MEDIUM_MAX:
            # Medium: 標準的な下処理。プロンプトとして使いやすく
            base = (
                "入力文をプロンプトとして整形してください。\n"
                "・構造を整理し、要点を明確に\n"
                "・冗長な表現を簡潔に\n"
                "・必要なら箇条書きに変換\n"
                "出力は整形後のテキストのみ。説明不要。"
            )
        elif level <= RICH_MAX:
            # Rich: 積極的な補完。足りない文脈を推測して追加
            base = (
                "入力文を強化してください。\n"
                "・不足している情報を推測して補完\n"
                "・論理構造を改善\n"
                "・具体例や詳細を追加可\n"
                "出力は強化後のテキストのみ。説明不要。"
            )
        else:
            # Deep: 深い文脈理解。インキュベーター的な処理
            base = (
                "入力文を深く解釈し再構築してください。\n"
                "・行間を読み、真意を抽出\n"
                "・欠けているリンクを推測\n"
                "・洞察を加えて昇華させる\n"
                "出力は再構築後のテキストのみ。説明不要。"
            )
        
        # ユーザーカスタム指示を追加（設定されていれば）
        if user_prompt:
            return f"{base}\n\n追加指示: {user_prompt}"
        return base

    @staticmethod
    def get_level_label(level: int) -> str:
        """レベルの日本語ラベル"""
        if level <= LIGHT_MAX:
            return "Light（軽め）"
        if level <= MEDIUM_MAX:
            return "Medium（標準）"
        if level <= RICH_MAX:
            return "Rich（濃いめ）"
        return "Deep（深い）"


    @staticmethod
    def resolve_level(level: int) -> int:
        """
        Seasoning値を3段階（Light/Medium/Rich）に正規化する。
        (v4.2 Opt-in: UIはv4.3で更新)
        
        Args:
            level: 0-100の入力
        
        Returns:
            30 (Light), 60 (Medium), or 100 (Rich)
        """
        if level <= 45:
            return RESOLVED_LIGHT
        if level <= 75:
            return RESOLVED_MEDIUM
        return RESOLVED_RICH
