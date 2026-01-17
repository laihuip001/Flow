## 2024-05-23 - Timing Attack on Token Verification
**Vulnerability:** The API token verification in `src/api/main.py` used a simple string comparison (`!=`), which is vulnerable to timing attacks. An attacker could potentially deduce the token by measuring the time it takes for the comparison to fail.
**Learning:** String comparisons using standard operators like `==` or `!=` are not constant-time and should be avoided for sensitive values like passwords or tokens.
**Prevention:** Always use `secrets.compare_digest()` for comparing sensitive strings, as it runs in constant time regardless of the content.
