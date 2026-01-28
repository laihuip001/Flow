## 2026-01-28 - Timing Attack in Token Verification
**Vulnerability:** The API token verification in `src/api/main.py` used standard string comparison (`==`), which is susceptible to timing attacks.
**Learning:** Even simple string comparisons for secrets can be vulnerable. Python's `secrets.compare_digest` should always be used for comparing sensitive values.
**Prevention:** Use `secrets.compare_digest` for all secret comparisons. Refactored auth logic to `src/api/auth.py` to centralize this check.
