## 2024-05-22 - Timing Attack in Token Verification
**Vulnerability:** API token verification was using simple string comparison (`!=`), which is vulnerable to timing attacks.
**Learning:** Python's string comparison exits early on mismatch, leaking information about how much of the token matched.
**Prevention:** Use `secrets.compare_digest()` for comparing secrets, as it runs in constant time regardless of the content.
