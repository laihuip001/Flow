## 2024-05-23 - Timing Attack Mitigation in Auth
**Vulnerability:** The API token verification in `src/api/main.py` used a standard string comparison (`!=`), which is susceptible to timing attacks. Attackers could theoretically determine the valid token byte-by-byte by measuring response times.
**Learning:** Standard string comparisons fail fast on the first mismatched character. This optimization leaks information about secret values.
**Prevention:** Always use `secrets.compare_digest()` for comparing sensitive values like API tokens, passwords, or HMACs. This function runs in constant time regardless of the input content.
