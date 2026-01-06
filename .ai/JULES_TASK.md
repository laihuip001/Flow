# 🛡️ JULES TASK ORDER: Flet GUI PoC (Phase 4.1)

## 1. Context & Objectives

* **Goal:** Create a minimal Flet (Python) GUI app that reads clipboard content and sends it to the existing FastAPI backend (`/process` endpoint), displaying the AI-processed result.
* **Scope:** New directory `flet_app/` with `main.py` and supporting files.
* **Auditors:** 📱 Interface Sovereign, ⚡ UX Designer, 🌉 SRE
* **Reference Files:**
  * `main.py` (Read `/process` endpoint signature)
  * `models.py` (Read `TextRequest` schema)
  * `ROADMAP_TITANIUM.md` (Refer for UI Blueprint)

## 2. Constraints (Non-Negotiable)

* **Termux Compat:** Flet is pure Python and Termux-compatible. Do NOT introduce any C-extension dependencies.
* **Backend Unchanged:** Do NOT modify `main.py` or any existing backend code. The Flet app is a CLIENT only.
* **No Hardcoded URLs:** Backend URL must be configurable (default: `http://localhost:8000`).
* **Style:** `black` formatter, Google Docstring.
* **Test:** Create `flet_app/test_connection.py` to verify backend connectivity BEFORE building UI.

## 3. Execution Steps

### Step 1: Analyze

Read the following files to understand the API contract:

* `main.py` lines 124-143 (`/process` endpoint)
* `models.py` lines 1-20 (`TextRequest` model)

### Step 2: Setup

Create the following directory structure:

```
flet_app/
├── main.py           # Flet application entry point
├── api_client.py     # HTTP client for backend communication
├── test_connection.py # Connectivity test script
└── requirements.txt  # flet, httpx
```

### Step 3: Test Plan (Create First)

Create `flet_app/test_connection.py`:

* Send a POST request to `http://localhost:8000/process` with `{"text": "test", "style": "proofread"}`.
* Assert HTTP 200 response.
* Print result to console.

### Step 4: Implement `api_client.py`

```python
# Signature
async def process_text(text: str, style: str = "business", base_url: str = "http://localhost:8000") -> dict:
    """Send text to backend and return processed result."""
    ...
```

Use `httpx.AsyncClient` for async HTTP calls.

### Step 5: Implement `main.py` (Flet App)

Create a minimal UI with:

1. **TextField (Read-Only):** Displays current clipboard content (use `page.get_clipboard()`).
2. **Dropdown:** Style selector (business, casual, summary, english, proofread).
3. **ElevatedButton:** "Process" button that triggers API call.
4. **TextField (Multiline, Read-Only):** Displays AI-processed result.
5. **ElevatedButton:** "Copy Result" button that copies result to clipboard.

UI must follow the blueprint in `ROADMAP_TITANIUM.md` Section 4.3.

### Step 6: Verify

1. Ensure FastAPI backend is running (`python main.py`).
2. Run `python flet_app/test_connection.py` → Expect PASS.
3. Run `flet flet_app/main.py` → Interact with GUI, verify end-to-end flow.

### Step 7: Commit

Create a PR with:

* Title: `[Titanium] Phase 4.1: Flet GUI PoC`
* Description: Summary of changes, screenshot of working UI.

## 4. Acceptance Criteria

* [ ] `flet_app/test_connection.py` passes against running backend.
* [ ] Flet app launches without errors.
* [ ] User can paste text, select style, click "Process", and see AI result.
* [ ] "Copy Result" button correctly copies text to clipboard.
* [ ] No modifications to existing backend code.
