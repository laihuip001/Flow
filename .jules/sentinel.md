## 2026-01-04 - Authentication Bypass on Sensitive Endpoints
**Vulnerability:** Several endpoints (`/history`, `/analyze`) were exposed without authentication, allowing unauthorized access to global clipboard history and usage of analysis features.
**Learning:** Adding new features ("P2 Features") often introduces new endpoints that might be missed during security reviews if they are not strictly added to the `dependencies=[Depends(verify_token)]` list or a global Router dependency.
**Prevention:** Use `APIRouter` with `dependencies` at the router level for groups of related endpoints to ensure auth is applied by default, rather than relying on per-endpoint decorators.
