"""
Privacy Module - PII検知とマスキング

責務: 個人情報の検知、マスク、復元
"""
import re


class PrivacyScanner:
    """個人情報検知（警告のみ・置換なし）"""

    def __init__(self):
        # パターン定義 (順序が重要: より具体的・長いパターンを先に記述)
        # Note: 辞書の順序はPython 3.7+で保持されるが、念のためリストで順序を明示するか、
        # ここでの定義順序に依存する形で結合する。
        self.patterns = {
             # Specific / Long patterns
            "AWS_KEY": r"AKIA[0-9A-Z]{16}",
            "API_KEY": r"(?:sk-|pk_|AIza|ghp_|xox[baprs]-)[a-zA-Z0-9_-]{20,}", # Non-capturing group for prefix
            "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "CREDIT_CARD": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}",
            "MY_NUMBER": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}",
            # Generic patterns
            "PHONE": r"\d{2,4}-\d{2,4}-\d{3,4}",
            "IP_ADDRESS": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            "ZIP": r"〒?\d{3}-\d{4}",
        }

        # 単一のコンパイル済み正規表現を作成 (Performance Optimization)
        # (?P<name>pattern) 形式で結合
        combined_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.patterns.items())
        self.combined_pattern = re.compile(combined_regex)

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

    def scan(self, text: str) -> dict:
        findings = {}

        # Single-pass Regex Scan (O(N))
        # finditer returns non-overlapping matches
        for match in self.combined_pattern.finditer(text):
            kind = match.lastgroup
            value = match.group(kind)

            if kind not in findings:
                findings[kind] = set()
            findings[kind].add(value)

        # Convert sets to lists
        findings = {k: list(v) for k, v in findings.items()}

        # キーワードマッチ
        text_upper = text.upper()
        keyword_hits = [kw for kw in self.sensitive_keywords if kw.upper() in text_upper]
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
        for kw in self.sensitive_keywords:
            if kw.upper() in text_upper:
                return True, kw
        return False, None


def mask_pii(text: str) -> tuple[str, dict]:
    """
    PIIをプレースホルダに置換してAPIに送信可能にする。

    Returns:
        tuple: (masked_text, mapping) - マスク済テキストと復元用マッピング
    """
    scanner = PrivacyScanner()
    findings = scanner.scan(text)

    if not findings["has_risks"]:
        return text, {}

    masked_text = text
    mapping = {}
    counter = 0

    # 置換順序は findings の順序に依存しないが、
    # scan 結果は重複しないトークンに基づいているため、
    # シンプルに置換して問題ない。

    for pii_type, values in findings["risks"].items():
        for val in values:
            if val in masked_text:  # まだ置換されていない場合のみ
                placeholder = f"[PII_{counter}]"
                masked_text = masked_text.replace(val, placeholder)
                mapping[placeholder] = val
                counter += 1

    return masked_text, mapping


def unmask_pii(text: str, mapping: dict) -> str:
    """
    プレースホルダをオリジナルのPIIに復元する。
    """
    result = text
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)
    return result
