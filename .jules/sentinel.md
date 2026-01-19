## 2026-01-19 - Missing Authentication on Sensitive Endpoint
**Vulnerability:** The `/prefetch` endpoint (POST) was exposed without authentication, allowing unauthenticated users to trigger background tasks.
**Learning:** `app.include_router` dependencies apply to ALL routes in the router. If a router contains both public and private endpoints, dependencies must be applied to individual routes instead of the router level.
**Prevention:** Always verify authentication requirements for each endpoint in a router. Use granular `Depends(verify_token)` for mixed routers.

## 2026-01-19 - Timing Attack on Token Verification
**Vulnerability:** Authentication token comparison used standard equality `!=`, which is susceptible to timing attacks.
**Learning:** String comparison time depends on the length of the matching prefix.
**Prevention:** Use `secrets.compare_digest()` for comparing sensitive secrets like API tokens.

## 2026-01-19 - Broken PrivacyScanner Import
**Vulnerability:** `src/api/routes/safety.py` attempted to import `PrivacyScanner` from `src.core.processor`, but it is only available in `src.core.privacy`. This caused the `/scan` endpoint to fail (500 Internal Error).
**Learning:** `CoreProcessor` does not re-export all internal modules.
**Prevention:** Import specific classes from their defining modules. Verify endpoints with integration tests.
