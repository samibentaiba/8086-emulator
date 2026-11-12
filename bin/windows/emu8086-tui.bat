@echo off
REM ==============================================================================
REM 8086 Emulator Interactive Terminal User Interface (TUI) for Windows
REM Neovim-style modal editor & time-travel debugger
REM ==============================================================================
setlocal
set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\..\"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"

python "%REPO_DIR%tui.py" %*
exit /b %ERRORLEVEL%
