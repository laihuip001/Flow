## 2024-05-21 - Regex Substitution vs Loop Replace
**Learning:** For replacing a small set of unique strings repeated many times in a large text, iterating with `str.replace` is significantly faster than using a single combined regex with `re.sub` and a Python callback. The overhead of invoking the Python callback for thousands of matches outweighs the benefit of a single pass.
**Action:** Prefer `str.replace` loop over `re.sub` callback when the number of unique search terms is small (<20) but occurrence count is high.

## 2024-05-21 - Pre-calculation in Hot Paths
**Learning:** Pre-compiling regexes and pre-calculating uppercase keywords in `__init__` yielded a ~6% performance improvement in `PrivacyScanner`.
**Action:** Always hoist invariant calculations (like `.upper()` on constants) out of hot loops like `scan` methods.
