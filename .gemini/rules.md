# Flow AI Development Rules (Gemini Code Assist)

> Version: 4.0.0 | Last Updated: 2026-01-06

This file configures AI coding assistance for the Flow AI project.

---

## 1. Project Context

- **Product:** Flow AI v4.0 - Text Pre-processing Tool  
- **Philosophy:** "Pre-processing × Speed" (前処理と速度)
- **Core Concept:** The "Seasoning" spectrum (0-100) replaces discrete styles

---

## 2. Architecture Rules

### File Structure

```
src/
├── core/      # Business Logic (processor, seasoning, privacy)
├── api/       # FastAPI Endpoints
├── app/       # Flet Desktop GUI
└── infra/     # Database, External Services
```

### Import Order (PEP8 + isort)

1. Standard Library
2. Third-party
3. Local (`from src.core...`)

---

## 3. Coding Standards (See CONSTITUTION.md Section 6)

### Must Follow

- **Type Hints:** ALL functions require parameter and return types
- **Docstrings:** Google style (Args, Returns, Raises)
- **Constants:** No magic numbers. Use `SALT_MAX = 30`, not `30`
- **Error Handling:** Never `except: pass`. Always log or return structured error

### Naming

| Type | Convention | Example |
|------|------------|---------|
| Class | PascalCase | `CoreProcessor` |
| Function | snake_case | `process_text` |
| Constant | UPPER_SNAKE | `MAX_RETRIES` |

---

## 4. Termux Compatibility

### Banned Libraries (ARM64 incompatible)

- `pandas`, `numpy`, `scipy`, `lxml`
- Any Rust-based dependencies

### PC-Only Libraries (Auto-skip on Termux)

- `flet`, `keyboard`, `pyperclip`

---

## 5. Security Constraints (OWASP LLM)

- **API Keys:** Always from `.env`, never hardcoded
- **PII:** Must be masked before sending to LLM (`mask_pii()`)
- **User Input:** Treat as untrusted (Prompt Injection risk)

---

## 6. Current State

- **Version:** 4.0.0 (Seasoning Update)
- **Test Status:** `test_logic.py`, `test_privacy.py` passing
- **Known Issues:** Some legacy tests may reference `style` instead of `seasoning`

---

## Reference

- Full standards: [CONSTITUTION.md](file:///CONSTITUTION.md)
- System context: [.ai/SYSTEM_CONTEXT.md](file:///.ai/SYSTEM_CONTEXT.md)

### External (dev-rules)

- 共通開発規範: [dev-rules/GEMINI.md](file:///c:/Users/makaron8426/dev/dev-rules/GEMINI.md)
- プロンプトライブラリ: [dev-rules/prompts/](file:///c:/Users/makaron8426/dev/dev-rules/prompts/)
- `/load` ワークフロー: Gレイヤー・Cモジュール等をロード
