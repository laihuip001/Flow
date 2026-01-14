## 2026-01-14 - Timing Attack in Auth Token Verification
**Vulnerability:** The API token verification used standard string comparison (`!=`), which is vulnerable to timing attacks.
**Learning:** Even simple auth checks need constant-time comparison to prevent side-channel attacks. The codebase documentation claimed constant-time comparison was used, but the code differed.
**Prevention:** Always use `secrets.compare_digest()` for comparing sensitive strings like tokens or passwords.
