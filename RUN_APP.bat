@echo off
chcp 65001 > nul
echo ========================================================
echo   AI Clipboard Pro v4.0 - Launcher
echo ========================================================
echo.

REM バッチファイルのあるディレクトリに移動
cd /d "%~dp0"
echo [INFO] Working Directory: %CD%
echo.

REM Python 3.14のフルパス
set PYTHON_EXE=C:\Users\laihuip001\AppData\Local\Programs\Python\Python314\python.exe

echo [1/3] Checking Python...
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at: %PYTHON_EXE%
    pause
    exit /b 1
)
echo [OK] Python found.

echo.
echo [2/3] Starting Backend Server (Port 8000)...
start "AI-Clipboard-Backend" /min "%PYTHON_EXE%" main.py
echo [OK] Backend started in background.

echo.
echo [3/3] Waiting for backend to initialize...
timeout /t 3 /nobreak > nul

echo.
echo [INFO] Launching Flet GUI...
echo ========================================================
"%PYTHON_EXE%" flet_app/main.py

echo.
echo [INFO] GUI closed. Stopping backend...
taskkill /fi "WINDOWTITLE eq AI-Clipboard-Backend*" /f > nul 2>&1
echo [DONE] Goodbye!
pause
