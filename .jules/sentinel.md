## 2024-10-24 - Timing Attack in Token Verification
**Vulnerability:** `src/api/main.py` used direct string comparison (`!=`) for verifying Bearer tokens against the configured API token.
**Learning:** Direct string comparison fails early when a character mismatch is found, leaking timing information that can be used to guess the token byte-by-byte.
**Prevention:** Always use `secrets.compare_digest()` for comparing sensitive values (tokens, passwords, hashes) to ensure constant-time comparison.
