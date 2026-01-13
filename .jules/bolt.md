## 2024-05-21 - Regex Optimization Fallacies
**Learning:** Combining multiple regex patterns into a single compiled regex (`(?P<A>...)|(?P<B>...)`) was SLOWER (3.9s -> 5.8s) for clean text than iterating over simple individual regexes.
**Reason:** The overhead of iterating `finditer` matches in Python significantly outweighed the C-level loop optimization of `re.findall` for simple patterns that fail fast.
**Action:** For PII scanning, use individual regexes but add "Pre-checks" (e.g. `'@' in text`, `re.search(r'\d')`) to skip expensive regex executions entirely for clean text.
