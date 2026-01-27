## 2025-01-27 - PrivacyScanner Optimization
**Learning:** Pre-compiling regexes in `__init__` vs using `re.findall` (which caches internally) showed only a ~1.3% improvement for simple patterns. However, combined with pre-calculating uppercase keywords, the total improvement was ~4-6% for PII masking.
**Action:** Always measure regex optimizations in Python; internal caching is often good enough. Pre-compilation is still best practice for class-based scanners to ensure validity at startup and avoid cache eviction in complex apps.
