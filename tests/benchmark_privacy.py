import time
import textwrap
from privacy import mask_pii

# 100kb text with some PII
dummy_text = textwrap.dedent("""
    Hello, my email is test.user@example.com.
    Please call me at 090-1234-5678.
    This is sensitive: CONFIDENTIAL.
    Here is some more text to fill space.
""") * 1000  # ~1000 PII instances, ~100KB

start = time.time()
mask_pii(dummy_text)
duration = time.time() - start

print(f"Time to mask 100KB text: {duration:.4f} seconds")
if duration > 0.05:
    print("⚠️ SLOW: This will block the event loop noticeably.")
else:
    print("✅ FAST: Negligible impact.")
