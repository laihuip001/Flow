@echo off
chcp 65001 > nul
title AI Clipboard Pro Menu

echo ========================================
echo   AI Clipboard Pro v3.3 Titanium
echo ========================================
echo.
echo  [1] Analyze - 記事からコンポーネント抽出
echo  [2] Enhance - プロンプト強化
echo  [3] Structure - テキスト構造化
echo  [4] Business - ビジネス文書校正
echo  [5] Casual - カジュアル変換
echo  [6] Proofread - 校正
echo  [7] Summary - 要約
echo  [8] English - 英語翻訳
echo  [0] Exit
echo.
set /p choice="Select: "

if "%choice%"=="1" set style=analyze_component
if "%choice%"=="2" set style=enhance
if "%choice%"=="3" set style=structure
if "%choice%"=="4" set style=business
if "%choice%"=="5" set style=casual
if "%choice%"=="6" set style=proofread
if "%choice%"=="7" set style=summary
if "%choice%"=="8" set style=english
if "%choice%"=="0" exit

powershell -ExecutionPolicy Bypass -File "%~dp0ai_convert.ps1" -Style "%style%"
pause
