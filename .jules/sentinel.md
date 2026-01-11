## 2025-02-14 - Missing Authentication on Internal State
**Vulnerability:** The `/history` and `/history/add` endpoints were exposed without authentication, allowing any network user to read and modify the application's internal clipboard history state, potentially leaking sensitive user data.
**Learning:** Adding new features (like P2 clipboard history) often introduces new endpoints. Developers might forget to apply global or specific security middlewares (like `verify_token`) to these new "internal" utility endpoints, assuming they are obscure or harmless.
**Prevention:**
1. Adopt a "secure by default" approach where all endpoints require authentication unless explicitly exempted.
2. Use router-level dependencies to enforce authentication for entire groups of endpoints (e.g., `APIRouter(dependencies=[Depends(verify_token)])`) instead of attaching it to each endpoint individually.
3. Review all new endpoints against a security checklist that includes authentication and authorization.
