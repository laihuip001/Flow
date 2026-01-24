## 2026-01-24 - Timing Attack in API Authentication
**Vulnerability:** The API token verification used simple string comparison (`!=`), which is vulnerable to timing attacks.
**Learning:** Even simple checks in Python can be vulnerable. `src/api/main.py` contained inline auth logic that bypassed standard security modules (which were missing).
**Prevention:** Always use `secrets.compare_digest()` for sensitive string comparisons. Centralize auth logic in `src/api/auth.py`.
