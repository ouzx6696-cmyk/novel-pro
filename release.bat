@echo off
chcp 65001 >nul
setlocal

:: novel-pro release launcher
:: Double-click this file or run from cmd to trigger the full release workflow.

set "PS_SCRIPT=%~dp0release.ps1"

if not exist "%PS_SCRIPT%" (
    echo [ERROR] release.ps1 not found next to this .bat
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*

endlocal
