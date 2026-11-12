@echo off
REM ==============================================================================
REM 8086 Emulator Unified Launcher for Windows (CLI / TUI / Headless)
REM ==============================================================================
setlocal
set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\..\"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"

python "%REPO_DIR%main.py" %*
exit /b %ERRORLEVEL%
