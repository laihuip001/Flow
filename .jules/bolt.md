## 2024-05-22 - Regex Optimization vs Correctness
**Learning:** Combined Regex in Python (`re`) can be slower than sequential `findall` if patterns cause frequent partial matches/backtracking (observed ~60ms regression on 100KB). However, sequential regexes fail to handle overlapping matches correctly (e.g. `1234-5678-1234-5678` matching partial My Number instead of Credit Card).
**Action:** Use Combined Regex when pattern overlap or consumption order matters for correctness, even if slightly slower. Prioritize pattern specificity in the regex construction.
