# 🛡️ JULES TASK ORDER: Critical Performance & UX Fix (P0 Emergency)

> **Priority:** P0 (Blocker)
> **Reported Latency:** 90+ seconds (Target: <30s, Ideal: 5s)
> **Second Issue:** App dies when terminal is closed

---

## 1. Context & Objectives

### Issue A: Catastrophic Latency

* **Goal:** Reduce AI processing time from 90+ seconds to <10 seconds for typical text (12 lines).
* **Root Cause Analysis:**
    1. `models/gemini-3-flash-preview` is a preview model with unpredictable latency and rate limits.
    2. System prompts are verbose, consuming unnecessary tokens and increasing TTFT.
    3. Flet GUI → FastAPI → Gemini is a double-hop adding network overhead.

### Issue B: Terminal Dependency

* **Goal:** Allow the Flet GUI app to run independently of the terminal window.
* **Root Cause:** `RUN_APP.bat` runs `python flet_app/main.py` in foreground. Closing terminal kills the process.

---

## 2. Reference Files (Read & Analyze First)

| File | Purpose |
|:--|:--|
| `config.py` | Model configuration (`MODEL_FAST`, `MODEL_SMART`) |
| `logic.py` | `StyleManager.STYLES` (system prompts), `execute_gemini()` |
| `flet_app/main.py` | GUI entry point |
| `RUN_APP.bat` | Launch script |

---

## 3. Constraints (Non-Negotiable)

* **Termux Compat:** Pure Python only. No new dependencies.
* **Safety:** Do NOT delete existing model configs. Add new ones alongside.
* **Backward Compat:** Existing `/process` API must continue to work for HTTP Shortcuts users.
* **Test:** Measure latency before and after with `time` command.

---

## 4. Execution Steps

### Step 1: Switch to Stable Fast Model

**Target:** `config.py`

```diff
- MODEL_FAST: str = "models/gemini-3-flash-preview"
- MODEL_SMART: str = "models/gemini-flash-latest"
+ MODEL_FAST: str = "gemini-2.0-flash"  # Stable, low latency
+ MODEL_SMART: str = "gemini-2.0-flash"  # Same for consistency
```

**Rationale:** Preview models have unpredictable performance. Stable `gemini-2.0-flash` is optimized for speed.

---

### Step 2: Compress System Prompts (Token Reduction)

**Target:** `logic.py` → `StyleManager.STYLES`

Replace verbose Japanese prompts with minimal English instructions (English has fewer tokens per semantic unit).

```python
STYLES = {
    "business": {
        "system": "Rewrite as polite business email. Keep meaning.",
        "params": {"temperature": 0.3}
    },
    "casual": {
        "system": "Rewrite casually for chat. Add emoji.",
        "params": {"temperature": 0.7}
    },
    "summary": {
        "system": "Summarize in bullet points.",
        "params": {"temperature": 0.1}
    },
    "english": {
        "system": "Translate to professional English.",
        "params": {"temperature": 0.2}
    },
    "proofread": {
        "system": "Fix typos only. Keep original meaning.",
        "params": {"temperature": 0.0}
    }
}
```

**Token Savings Estimate:** ~70% reduction per request.

---

### Step 3: Direct API Call (Bypass FastAPI for Local Use)

**Target:** `flet_app/main.py`

For local PC usage, bypass the FastAPI server entirely and call the Gemini API directly from the Flet app. This eliminates:
* HTTP serialization/deserialization overhead
* localhost network latency
* FastAPI middleware processing

Create a new function `call_gemini_direct()` that imports `genai` directly.

```python
# In flet_app/main.py, add direct Gemini call
import os
from google import genai

_client = None
def get_gemini_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            # Try to load from .env in parent directory
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            if os.path.exists(env_path):
                with open(env_path) as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY="):
                            api_key = line.split("=", 1)[1].strip().strip('"')
                            break
        if api_key:
            _client = genai.Client(api_key=api_key)
    return _client

def process_direct(text: str, style: str) -> str:
    """Direct Gemini API call, no FastAPI intermediary."""
    prompts = {
        "business": "Rewrite as polite business email:",
        "casual": "Rewrite casually for chat, add emoji:",
        "summary": "Summarize in bullet points:",
        "english": "Translate to English:",
        "proofread": "Fix typos only:",
    }
    client = get_gemini_client()
    if not client:
        return "Error: API key not configured"
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"{prompts.get(style, prompts['proofread'])}\n\n{text}"
    )
    return response.text
```

Replace `process_text_fast()` HTTP call with `process_direct()`.

---

### Step 4: Fix Terminal Independence

**Target:** `RUN_APP.bat`

Use `pythonw.exe` (windowless Python) or `start /b` with proper detachment:

```batch
@echo off
chcp 65001 > nul
cd /d "%~dp0"

set PYTHON_EXE=C:\Users\laihuip001\AppData\Local\Programs\Python\Python314\pythonw.exe

REM Start backend silently (no window)
start "" /min "%PYTHON_EXE:pythonw=python%" main.py

REM Wait for backend
timeout /t 2 /nobreak > nul

REM Start GUI (also survives terminal close)
start "" "%PYTHON_EXE%" flet_app/main.py
```

Alternatively, create `RUN_APP.vbs` for truly invisible launch:

```vbs
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WshShell.Run "pythonw.exe main.py", 0, False
WScript.Sleep 2000
WshShell.Run "pythonw.exe flet_app/main.py", 0, False
```

---

## 5. Verification Plan

### Latency Test

```powershell
Measure-Command { python -c "from flet_app.main import process_direct; print(process_direct('テスト文章', 'proofread'))" }
```

**Pass Criteria:** < 10 seconds

### Terminal Independence Test

1. Double-click `RUN_APP.bat` (or `.vbs`)
2. Close the terminal window
3. GUI should remain open and functional

---

## 6. Commit

PR Title: `[Titanium] P0: Critical latency fix + terminal independence`

Description:
* Switched model to stable `gemini-2.0-flash`
* Compressed system prompts (70% token reduction)
* Direct Gemini API call in Flet app (bypasses FastAPI for local use)
* VBS launcher for terminal-independent operation
