# Constants: Seasoning Thresholds
SALT_MAX = 30
SAUCE_MAX = 70


class SeasoningManager:
    """
    Manages the 'Seasoning' (味付け) of the text processing.
    Level 0-100 spectrum replaces discrete styles.
    """

    @staticmethod
    def get_system_prompt(level: int = SALT_MAX) -> str:
        """
        Returns the system prompt. Optimized for SPEED.
        """
        level = max(0, min(100, level))

        if level <= SALT_MAX:
            # Salt: The absolute fastest path. Minimal instructions.
            return (
                "Role: Text Cleaner.\n"
                "Task: Fix typos, punctuation, and formatting errors ONLY.\n"
                "Constraint: Do NOT change the meaning, tone, or length. Keep it raw.\n"
                "Output: The fixed text only."
            )
        elif level <= SAUCE_MAX:
            # Sauce: Standard polish.
            return (
                "Role: Text Editor.\n"
                "Task: Clarify ambiguity and smooth sentence flow.\n"
                "Constraint: Maintain original intent. Make it clear and professional.\n"
                "Output: The polished text only."
            )
        else:
            # Spice: Enhancement.
            return (
                "Role: Text Enhancer.\n"
                "Task: Elaborate on points and improve logical structure.\n"
                "Detailed context completion is allowed here.\n"
                "Output: The enhanced text only."
            )

    @staticmethod
    def get_level_label(level: int) -> str:
        if level <= SALT_MAX:
            return "Salt (Minimal)"
        if level <= SAUCE_MAX:
            return "Sauce (Standard)"
        return "Spice (Rich)"
