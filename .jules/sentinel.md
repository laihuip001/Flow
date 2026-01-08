## 2024-02-14 - Input Validation Enforcement
**Vulnerability:** Unbounded input length and unconstrained integer ranges in API models.
**Learning:** Pydantic models should explicitly define constraints using `Field(..., max_length=N, ge=Min, le=Max)` to prevent DoS via massive payloads and logic errors from out-of-range values. Defaults alone do not enforce validation.
**Prevention:** Always add explicit validation constraints to Pydantic models for user-facing inputs.
