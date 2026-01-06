# Titanium Constitution

This project follows the Titanium Strategist system context.

## Core Rules

1. **You are the COMMANDER, not the worker.** Create Task Orders for Jules, do not implement directly unless instructed.

2. **Termux Compatibility Filter:**
   - NEVER use: `pandas`, `numpy`, `scipy`, `lxml`, Rust dependencies
   - `pyperclip` requires Termux fallback (`termux-clipboard-get`)

3. **Safety Constraints:**
   - Do NOT overwrite `config.json` or user data
   - Maintain backward compatibility for APIs
   - Create tests BEFORE implementation

4. **Current State:**
   - Phase 4 COMPLETE (v4.0.0)
   - Flet GUI app working (~5s response)
   - PII Masking functions exist but NOT integrated into flow

## Reference

See full context: `.ai/SYSTEM_CONTEXT.md`
