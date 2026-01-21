## 2024-05-23 - Timing Attack Vulnerability in Auth
**Vulnerability:** API Token verification used simple string comparison (`!=`), making it vulnerable to timing attacks where an attacker could deduce the token character by character.
**Learning:** Even internal API tokens are susceptible to side-channel attacks. Standard equality operators optimize for speed by returning early on mismatch, which leaks information.
**Prevention:** Always use `secrets.compare_digest()` for sensitive string comparisons (tokens, passwords, hashes) to ensure constant-time execution regardless of input.
