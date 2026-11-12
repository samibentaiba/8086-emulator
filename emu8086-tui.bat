@echo off
setlocal
set "REPO_DIR=%~dp0"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"

python -c "import curses" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [8086 TUI] Installing 'windows-curses' for terminal display...
    pip install windows-curses
)

python "%REPO_DIR%tui.py" %*
exit /b %ERRORLEVEL%
