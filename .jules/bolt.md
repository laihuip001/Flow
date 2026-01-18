## 2024-05-22 - Regex Compilation & String Processing
**Learning:** In the privacy scanner, `re.findall` and `.upper()` inside the scanning loop caused significant overhead (~0.6s for 100KB). Pre-compiling regexes and pre-calculating uppercase keywords reduced this to ~0.1s (5x speedup).
**Action:** Always pre-compile regex patterns and pre-process constant string transformations in `__init__` for hot-path classes.
