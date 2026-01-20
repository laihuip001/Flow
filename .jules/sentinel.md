## 2024-03-21 - Timing Attack Vulnerability in Auth
**Vulnerability:** The API token verification in `src/api/main.py` used standard string comparison (`!=`), which is susceptible to timing attacks. Attackers could potentially deduce the token byte-by-byte by measuring the time it takes for the server to reject the request.
**Learning:** Even simple string comparisons for secrets can be a security risk. Python's `!=` operator fails fast, which leaks information about how much of the string matched.
**Prevention:** Always use `secrets.compare_digest()` for comparing sensitive values like API tokens, passwords, or hashes. This function takes constant time regardless of the input content, eliminating the timing side channel.
