## 2024-05-22 - [Optimized Regex Scanning]
**Learning:** Combining multiple regex patterns into a single compiled regex with named groups (`|`.join) significantly reduces scanning overhead from O(N*P) to O(N).
**Action:** When performing multiple pattern searches on the same text, always attempt to combine them into a single pass regex. Ensure specific patterns (like Credit Cards) come before generic ones (like Phone Numbers) to prevent incorrect partial matches.
