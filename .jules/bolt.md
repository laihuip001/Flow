## 2024-05-23 - Regex Compilation Optimization
**Learning:** Pre-compiling regex patterns in Python (`re.compile`) and calling `pattern.findall()` is measurably faster than `re.findall(string, ...)` for repeated calls, even with Python's internal regex cache. Also, pre-calculating uppercase strings for keyword search avoids O(K*N) operations in hot loops.
**Action:** Always pre-compile regex patterns in `__init__` for classes that perform repeated text processing. Pre-calculate invariant transformations (like uppercase keywords) during initialization.
