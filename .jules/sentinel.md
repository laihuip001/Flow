## 2026-01-29 - DoS via Unbounded Input in TextRequest
**Vulnerability:** The `TextRequest` model allowed arbitrary length strings, which could lead to Denial of Service (DoS) via memory exhaustion or CPU saturation during regex scanning in the unauthenticated `/scan` endpoint.
**Learning:** Pydantic models should always enforce reasonable `max_length` constraints on string fields, especially for unauthenticated endpoints.
**Prevention:** Always add `Field(..., max_length=N)` to Pydantic models for user input.
