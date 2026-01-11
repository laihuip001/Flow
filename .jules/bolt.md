## 2024-05-22 - Single-Pass Regex Optimization
**Learning:** Combining multiple regex patterns into a single master regex with named groups (`(?P<NAME>pattern)`) ensures deterministic matching order and prevents partial matches of overlapping patterns (e.g., `CREDIT_CARD` vs `MY_NUMBER`).
**Action:** When dealing with multiple PII patterns, always use a single compiled regex and order patterns by specificity (longest first) to ensure correctness and O(N) scanning efficiency.
