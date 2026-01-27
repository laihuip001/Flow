import time
import textwrap
import statistics
from src.core.privacy import mask_pii

# 100kb text with some PII
dummy_text = textwrap.dedent("""
    Hello, my email is test.user@example.com.
    Please call me at 090-1234-5678.
    This is sensitive: CONFIDENTIAL.
    Here is some more text to fill space.
""") * 1000  # ~1000 PII instances, ~100KB

times = []
for _ in range(20):
    start = time.time()
    mask_pii(dummy_text)
    duration = time.time() - start
    times.append(duration)

avg_time = statistics.mean(times)
print(f"Average time to mask 100KB text: {avg_time:.4f} seconds (over 20 runs)")
if avg_time > 0.05:
    print("⚠️ SLOW: This will block the event loop noticeably.")
else:
    print("✅ FAST: Negligible impact.")
