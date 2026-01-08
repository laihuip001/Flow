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
            "API_KEY": r"(sk-|pk_|AIza|ghp_|xox[baprs]-)[a-zA-Z0-9_-]{20,}",
            "AWS_KEY": r"AKIA[0-9A-Z]{16}",
            "CREDIT_CARD": r"\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}",
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

    def scan(self, text: str) -> dict:
        findings = {}
        # Regex パターンマッチ
        for p_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                findings[p_type] = list(set(matches))

        # キーワードマッチ
        text_upper = text.upper()
        keyword_hits = [kw for kw in self.sensitive_keywords if kw.upper() in text_upper]
        if keyword_hits:
            findings["SENSITIVE_KEYWORD"] = keyword_hits

        count = sum(len(v) for v in findings.values())
        return {"has_risks": count > 0, "risks": findings, "risk_count": count}


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

    for pii_type, values in findings["risks"].items():
        for val in values:
            if val in masked_text:  # まだ置換されていない場合のみ
                placeholder = f"[PII_{counter}]"
                masked_text = masked_text.replace(val, placeholder)
                mapping[placeholder] = val
                counter += 1

    return masked_text, mapping


# Cache for unmask regex patterns based on count
_unmask_regex_cache = {}

def unmask_pii(text: str, mapping: dict) -> str:
    """
    プレースホルダをオリジナルのPIIに復元する。
    """
    if not mapping:
        return text

    # Optimization: Use regex for single-pass replacement if mapping uses standard keys
    # Threshold for optimization (N >= 20 verified to be faster with cached regex)
    if len(mapping) >= 20:
        count = len(mapping)

        # Verify keys are standard [PII_0]...[PII_N-1]
        # We MUST verify all keys exist in mapping to avoid KeyError in lambda.
        # This check is O(N) which is negligible compared to O(N*L) of iterative replace.
        keys = [f"[PII_{i}]" for i in range(count)]
        if all(k in mapping for k in keys):
             # Check cache
            pattern = _unmask_regex_cache.get(count)
            if not pattern:
                 # Construct regex: [PII_0]|[PII_1]|...
                 pattern = re.compile("|".join(re.escape(k) for k in keys))
                 _unmask_regex_cache[count] = pattern

            return pattern.sub(lambda m: mapping[m.group(0)], text)

    # Fallback to iterative replacement (slower for large N, but simple)
    result = text
    for placeholder, original in mapping.items():
        result = result.replace(placeholder, original)
    return result
