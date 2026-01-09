# Sentinel's Journal

## 2026-01-09 - ReDoS and DoS via Unbounded Input
**Vulnerability:** The `POST /scan` endpoint accepted unbounded text input and processed it with multiple complex regex patterns (including PII detection). A 100KB payload caused a ~20 second delay, indicating a severe Denial of Service (DoS) and potentially Regular Expression Denial of Service (ReDoS) vulnerability.
**Learning:** Even simple regex checks can become a DoS vector if input size is not strictly bounded. Unauthenticated endpoints are particularly dangerous.
**Prevention:** Always enforce strict `max_length` constraints on string inputs using Pydantic fields (e.g., `Field(..., max_length=10000)`). This stops the attack at the validation layer, before any processing logic runs.
