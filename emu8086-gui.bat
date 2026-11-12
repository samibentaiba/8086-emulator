@echo off
setlocal
set "REPO_DIR=%~dp0"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"

python -c "import PyQt5" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [8086 GUI] Installing 'PyQt5' for graphical workbench...
    pip install PyQt5
)

where pythonw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pythonw "%REPO_DIR%mainUI.py" %*
) else (
    python "%REPO_DIR%mainUI.py" %*
)
exit /b %ERRORLEVEL%
