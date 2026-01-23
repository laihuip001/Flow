## 2024-05-22 - Authentication Bypass & Timing Attack
**Vulnerability:** `POST /prefetch` endpoint was unauthenticated because `safety_router` was included without dependencies. `verify_token` used insecure string comparison.
**Learning:** Routers included without global dependencies must explicitly define auth dependencies on sensitive routes. String comparison of secrets is vulnerable to timing attacks.
**Prevention:** Use `secrets.compare_digest` for token verification. Explicitly check auth requirements for every exposed endpoint.

## 2024-05-22 - Runtime Import Error masking Security Logic
**Vulnerability:** `src/api/routes/safety.py` attempted to access `PrivacyScanner` from `processor` module where it wasn't exposed.
**Learning:** Runtime errors in security/safety modules can fail open or crash the app.
**Prevention:** Ensure static analysis or basic smoke tests cover all security paths.
