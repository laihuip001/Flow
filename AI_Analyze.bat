@echo off
REM AI Clipboard Pro - Analyze Component Style
REM 記事からプロンプトエンジニアリングのコンポーネントを抽出するバッチ
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File "ai_convert.ps1" -Style "analyze_component"
pause
