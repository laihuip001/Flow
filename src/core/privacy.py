"""
Privacy Module - PII検知とマスキング

責務: 個人情報の検知、マスク、復元
"""
import re


class PrivacyScanner:
    """個人情報検知（警告のみ・置換なし）"""

    def __init__(self):
        self.patterns = {
            # 基本PII
            "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "PHONE": r"\d{2,4}-\d{2,4}-\d{3,4}",
            "ZIP": r"〒?\d{3}-\d{4}",
            "MY_NUMBER": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}",
            # 拡張パターン (P0-2)
            "IP_ADDRESS": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            "CREDIT_CARD": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}",
            # API Keys (拡張: v4.1)
            "API_KEY": r"(?:sk-|pk_|AIza|ghp_|gsk_|glpat-|xox[baprs]-|Bearer\s+)[a-zA-Z0-9_-]{20,}",
            "AWS_KEY": r"AKIA[0-9A-Z]{16}",
            # パスワード系 (v4.1)
            "PASSWORD": r"(?i)(?:password|passwd|pwd|secret|token)\s*[=:]\s*['\"]?[^\s'\"]{8,}",
            # 日本住所 (v4.1)
            "JP_ADDRESS": r"(?:東京都|北海道|(?:京都|大阪)府|[^\s]{2,3}県)[^\s]{2,}[市区町村]",
        }
        # Pre-compile patterns for performance
        self.compiled_patterns = {k: re.compile(v) for k, v in self.patterns.items()}

        # 機密キーワード (大文字小文字無視)
        self.sensitive_keywords = [
            "CONFIDENTIAL",
            "NDA",
            "INTERNAL ONLY",
            "機密",
            "社外秘",
            "SECRET",
            "PRIVATE",
            "DO NOT SHARE",
            "取扱注意",
        ]
        # Pre-calculate uppercase keywords for performance
        self.sensitive_keywords_upper = {kw: kw.upper() for kw in self.sensitive_keywords}

    def scan(self, text: str) -> dict:
        findings = {}
        # Regex パターンマッチ
        for p_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                findings[p_type] = list(set(matches))

        # キーワードマッチ
        text_upper = text.upper()
        # Use pre-calculated uppercase keywords
        keyword_hits = [
            kw for kw, kw_upper in self.sensitive_keywords_upper.items()
            if kw_upper in text_upper
        ]
        if keyword_hits:
            findings["SENSITIVE_KEYWORD"] = keyword_hits

        count = sum(len(v) for v in findings.values())
        return {"has_risks": count > 0, "risks": findings, "risk_count": count}

    def check_deny_list(self, text: str) -> tuple[bool, str | None]:
        """
        厳格なDeny List チェック。
        正規表現を問わず、機密キーワードが含まれる場合は即座に拒否する。
        
        Returns:
            tuple: (is_blocked: bool, matched_keyword: str | None)
        """
        text_upper = text.upper()
        for kw, kw_upper in self.sensitive_keywords_upper.items():
            if kw_upper in text_upper:
                return True, kw
        return False, None


class PrivacyHandler:
    """
    Privacy handling logic encapsulated (v5.0 Phase 1)
    """
    def __init__(self):
        self.scanner = PrivacyScanner()

    def mask(self, text: str, use_custom_vocab: bool = True) -> tuple[str, dict]:
        """
        PIIをプレースホルダに置換してAPIに送信可能にする。
        Returns: (masked_text, mapping)
        """
        findings = self.scanner.scan(text)

        masked_text = text
        mapping = {}
        counter = 0

        # 1. Regexベースのマスク
        if findings["has_risks"]:
            for pii_type, values in findings["risks"].items():
                for val in values:
                    if val in masked_text:  # まだ置換されていない場合のみ
                        placeholder = f"[PII_{counter}]"
                        masked_text = masked_text.replace(val, placeholder)
                        mapping[placeholder] = val
                        counter += 1

        # 2. カスタム語彙ベースのマスク（オプション）
        if use_custom_vocab:
            try:
                from .vocab_store import get_vocab_store
                store = get_vocab_store()
                custom_terms = store.find_in_text(masked_text)
                for term in custom_terms:
                    if term in masked_text:
                        placeholder = f"[VOCAB_{counter}]"
                        masked_text = masked_text.replace(term, placeholder)
                        mapping[placeholder] = term
                        counter += 1
            except Exception:
                pass  # vocab_storeが利用不可でもフォールバック

        return masked_text, mapping

    def unmask(self, text: str, mapping: dict) -> str:
        """
        プレースホルダをオリジナルのPIIに復元する。
        """
        result = text
        for placeholder, original in mapping.items():
            result = result.replace(placeholder, original)
        return result


# --- Backward Compatibility Functions ---
_handler = PrivacyHandler()

def mask_pii(text: str, use_custom_vocab: bool = True) -> tuple[str, dict]:
    return _handler.mask(text, use_custom_vocab)

def unmask_pii(text: str, mapping: dict) -> str:
    return _handler.unmask(text, mapping)
