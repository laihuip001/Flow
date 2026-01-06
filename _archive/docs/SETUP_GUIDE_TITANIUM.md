# 🛡️ v3.3 Titanium Setup Guide

## 1. Initialize
1. `cp .env.example .env` & Set API Keys.
2. `pip install -r requirements.txt`

## 2. Dev Routine (PC/Cloud)
* Start work: `./dev_tools/sync.sh start`
* End work: `./dev_tools/sync.sh end`

## 3. Termux Runtime
* **Phantom Process Killer Disable (PC connected):**
  `adb shell device_config put activity_manager max_phantom_processes 2147483647`
* **Start Watcher:**
  `chmod +x maintenance/titanium_watcher.sh`
  `./maintenance/titanium_watcher.sh &`

## 4. AI Agent Context
* Open `.ai/SYSTEM_CONTEXT.md` in Antigravity
* Instruct agent: "Read @SYSTEM_CONTEXT.md and remember the constraints"
