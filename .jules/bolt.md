# Bolt's Journal - Critical Learnings

## 2026-01-24 - Pre-compilation Wins
**Learning:** `PrivacyScanner` was re-compiling regexes and re-calculating uppercase keywords on every scan call. Moving these to `__init__` yielded a ~3.4x speedup (0.38s -> 0.11s for 100KB).
**Action:** Always check loop bodies for invariant calculations or compilations.
