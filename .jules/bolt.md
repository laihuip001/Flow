## 2026-01-23 - Regex Performance Optimization
**Learning:** `re.findall` on large texts is expensive even with compiled patterns if the pattern is complex (like email or API keys). Implementing simple string-inclusion pre-checks (e.g., `if "@" in text`) provides massive speedups (10x-12x) by avoiding the regex engine entirely for non-matching cases.
**Action:** Always consider fast-path pre-checks for expensive operations like regex scanning or heavy parsing.

## 2026-01-23 - Mocking Class Instances vs Global Functions
**Learning:** `unittest.mock.patch` on global functions (like `execute_gemini`) is ineffective if the class under test (`CoreProcessor`) imports the class (`GeminiClient`) and uses it directly. Tests must mock the instance attributes (e.g., `self.processor.gemini_client`) or patch the class constructor to verify integration correctly.
**Action:** Verify how dependencies are consumed (global func vs instance) before writing mocks.
