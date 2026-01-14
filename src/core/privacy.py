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

        # --- Optimization: Pre-compile patterns and keywords ---
        self._compiled_patterns = []
        self._compile_patterns()

        # Map upper case keyword to original keyword for fast lookup
        self._sensitive_keywords_map = {kw.upper(): kw for kw in self.sensitive_keywords}

    def _compile_patterns(self):
        """Compile regex patterns and attach pre-check functions."""

        def check_always(text, text_upper): return True
        def check_digits(text, text_upper): return bool(re.search(r'\d', text))
        def check_at(text, text_upper): return '@' in text
        def check_hyphen(text, text_upper): return '-' in text

        # PASSWORD: checks for keywords
        password_triggers = ["PASSWORD", "PASSWD", "PWD", "SECRET", "TOKEN"]
        def check_password(text, text_upper):
            return any(k in text_upper for k in password_triggers)

        # API_KEY triggers
        api_triggers = ["sk-", "pk_", "AIza", "ghp_", "gsk_", "glpat-", "xox", "Bearer"]
        def check_api_key(text, text_upper):
            return any(k in text for k in api_triggers)

        # AWS_KEY
        def check_aws_key(text, text_upper): return "AKIA" in text

        # JP_ADDRESS
        jp_triggers = ["都", "道", "府", "県"]
        def check_jp_address(text, text_upper):
            return any(k in text for k in jp_triggers)

        for key, pattern in self.patterns.items():
            regex = re.compile(pattern)
            pre_check = check_always

            if key == "EMAIL":
                pre_check = check_at
            elif key in ["PHONE", "ZIP"]:
                pre_check = check_hyphen
            elif key in ["MY_NUMBER", "IP_ADDRESS", "CREDIT_CARD"]:
                 pre_check = check_digits
            elif key == "API_KEY":
                pre_check = check_api_key
            elif key == "AWS_KEY":
                pre_check = check_aws_key
            elif key == "PASSWORD":
                pre_check = check_password
            elif key == "JP_ADDRESS":
                pre_check = check_jp_address

            self._compiled_patterns.append((key, regex, pre_check))

    def scan(self, text: str) -> dict:
        findings = {}
        # Pre-compute upper case for optimization
        text_upper = text.upper()

        # Regex パターンマッチ
        for p_type, regex, pre_check in self._compiled_patterns:
            if not pre_check(text, text_upper):
                continue

            matches = regex.findall(text)
            if matches:
                findings[p_type] = list(set(matches))

        # キーワードマッチ
        keyword_hits = []
        for kw_upper, kw_orig in self._sensitive_keywords_map.items():
             if kw_upper in text_upper:
                 keyword_hits.append(kw_orig)

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
        for kw_upper, kw_orig in self._sensitive_keywords_map.items():
            if kw_upper in text_upper:
                return True, kw_orig
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
