@echo off
REM AI Clipboard Pro - Structure Data Style
REM テキストをObsidian向けの構造化Markdownに整形するバッチ
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "ai_convert.ps1" -Style "structure_data"
pause
