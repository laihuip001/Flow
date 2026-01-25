## 2024-05-23 - Regex Compilation and String Operations
**Learning:** In `PrivacyScanner`, passing string patterns to `re.findall` inside a loop and repeatedly calling `.upper()` on keywords significantly slowed down processing (~0.15s for 100KB).
**Action:** Pre-compiling regexes in `__init__` and pre-calculating uppercase keyword lists reduced processing time by ~40% (to ~0.09s). Always pre-compile regexes in hot paths.
