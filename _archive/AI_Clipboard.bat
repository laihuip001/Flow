@echo off
chcp 65001 >nul
echo ========================================
echo  AI Clipboard Pro
echo ========================================
echo.
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0pc_clipboard_debug.ps1"
echo.
pause
