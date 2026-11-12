@echo off
REM ==============================================================================
REM 8086 Emulator Interactive Terminal User Interface (TUI) for Windows
REM Neovim-style modal editor & time-travel debugger
REM ==============================================================================
setlocal
set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\..\"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"

REM Ensure windows-curses is installed on Windows
python -c "import curses" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [8086 TUI] Installing 'windows-curses' for terminal display...
    pip install windows-curses
)

python "%REPO_DIR%tui.py" %*
exit /b %ERRORLEVEL%
