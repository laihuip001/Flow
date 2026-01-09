"""
Privacy Module - PII検知とマスキング

責務: 個人情報の検知、マスク、復元
"""
import re


class PrivacyScanner:
    """個人情報検知（警告のみ・置換なし）"""

    def __init__(self):
        # Compile patterns for performance
        self.patterns = {
            # 基本PII
            "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
            "PHONE": re.compile(r"\d{2,4}-\d{2,4}-\d{3,4}"),
            "ZIP": re.compile(r"〒?\d{3}-\d{4}"),
            "MY_NUMBER": re.compile(r"\d{4}[-\s]?\d{4}[-\s]?\d{4}"),
            # 拡張パターン (P0-2)
            "IP_ADDRESS": re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),
            "API_KEY": re.compile(r"(sk-|pk_|AIza|ghp_|xox[baprs]-)[a-zA-Z0-9_-]{20,}"),
            "AWS_KEY": re.compile(r"AKIA[0-9A-Z]{16}"),
            "CREDIT_CARD": re.compile(r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}"),
        }
        # 機密キーワード (大文字小文字無視)
        raw_keywords = [
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
        # Optimize by pre-calculating upper case mapping
        # Storing tuple (original, upper) to return original casing if needed
        self.sensitive_keywords = [(kw, kw.upper()) for kw in raw_keywords]

    def scan(self, text: str) -> dict:
        findings = {}
        # Regex パターンマッチ
        for p_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                findings[p_type] = list(set(matches))

        # キーワードマッチ
        text_upper = text.upper()
        keyword_hits = [kw for kw, kw_upper in self.sensitive_keywords if kw_upper in text_upper]
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
        for kw, kw_upper in self.sensitive_keywords:
            if kw_upper in text_upper:
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

    # Collect all unique values to replace
    all_values = set()
    for values in findings["risks"].values():
        all_values.update(values)

    if not all_values:
        return text, {}

    # Sort by length descending to ensure longer matches are replaced first (e.g. "foo bar" before "foo")
    # This avoids partial replacement issues
    sorted_values = sorted(all_values, key=len, reverse=True)

    # Create a single regex pattern for all values
    # Escape values to treat them as literal strings in regex
    pattern = re.compile('|'.join(map(re.escape, sorted_values)))

    val_to_placeholder = {}

    def replace_callback(match):
        nonlocal counter
        val = match.group(0)

        if val in val_to_placeholder:
            return val_to_placeholder[val]

        placeholder = f"[PII_{counter}]"
        mapping[placeholder] = val
        val_to_placeholder[val] = placeholder
        counter += 1
        return placeholder

    masked_text = pattern.sub(replace_callback, text)

    return masked_text, mapping


def unmask_pii(text: str, mapping: dict) -> str:
    """
    プレースホルダをオリジナルのPIIに復元する。
    """
    result = text
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)
    return result
