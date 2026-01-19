## 2026-01-19 - Regex & Keyword Pre-compilation
**Learning:** In Python classes that perform heavy string scanning (like `PrivacyScanner`), pre-compiling regex patterns (`re.compile`) and pre-calculating derived data (like uppercase keyword lists) in `__init__` yields significant performance gains (5x speedup in this case).
**Action:** Always check `__init__` for opportunities to move expensive initialization or constant calculations out of the hot-path methods like `scan()`.

## 2026-01-19 - Test Environment Gaps
**Learning:** Many existing tests (`tests/test_core_logic.py`, etc.) rely on external services or specific environment configurations (API keys) and fail in a clean environment. This makes regression testing harder.
**Action:** When optimizing, create isolated, self-contained unit tests (like `tests/test_privacy_optimized.py`) to verify specific logic changes without relying on the broader, potentially unstable test suite.
