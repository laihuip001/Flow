@echo off
REM AI Clipboard Pro - Reasoning Enhancer Style
REM プロンプトに思考プロセス(CoT)を追加して強化するバッチ
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "ai_convert.ps1" -Style "reasoning_enhancer"
pause
