## 2026-01-18 - Timing Attack Vulnerability in Token Verification
**Vulnerability:** The API token verification logic in `src/api/main.py` used standard string comparison (`!=`) for checking the Bearer token.
**Learning:** Standard string comparison returns early upon finding the first mismatching character. This allows an attacker to perform a timing attack to guess the token byte-by-byte by measuring the response time.
**Prevention:** Use `secrets.compare_digest()` for all sensitive string comparisons (passwords, tokens, API keys). This function is designed to run in constant time regardless of the input content.
