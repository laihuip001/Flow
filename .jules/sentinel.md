# Sentinel's Journal

## 2025-05-18 - [CRITICAL] Timing Attack in Token Verification
**Vulnerability:** The `verify_token` function in `src/api/main.py` used direct string comparison (`==`) for validating the Bearer token against the configured API token.
**Learning:** String comparison returns false as soon as a mismatch is found, allowing an attacker to deduce the token character by character by measuring response times.
**Prevention:** Use `secrets.compare_digest()` for comparing sensitive strings like passwords, tokens, or API keys. This function takes constant time regardless of where the mismatch occurs.
