# Sentinel's Journal

## 2024-05-22 - Missing Authentication on Safety Endpoints
**Vulnerability:** The `/scan` and `/prefetch` endpoints in `src/api/routes/safety.py` were exposed without authentication.
**Learning:** Even utility endpoints like PII scanning or cache prefetching can be abused for DoS or information leakage if left unprotected.
**Prevention:** Verify all routers included in `src/api/main.py` have appropriate `dependencies=[Depends(verify_token)]` unless explicitly intended to be public.

## 2024-05-22 - Timing Attack in Token Verification
**Vulnerability:** `verify_token` used simple string comparison (`!=`) for API tokens.
**Learning:** String comparison fails early on the first mismatched character, allowing attackers to guess the token byte-by-byte (timing attack).
**Prevention:** Use `secrets.compare_digest()` for all sensitive string comparisons.
