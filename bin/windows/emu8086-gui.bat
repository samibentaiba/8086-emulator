@echo off
REM ==============================================================================
REM 8086 Emulator Graphical User Interface (GUI) for Windows
REM PyQt5-based visual debugger & microprocessor workbench
REM ==============================================================================
setlocal
set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%..\..\"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"

REM Ensure PyQt5 is installed on Windows
python -c "import PyQt5" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [8086 GUI] Installing 'PyQt5' for graphical workbench...
    pip install PyQt5
)

REM Prefer pythonw if available for no-console windowed GUI, fallback to python
where pythonw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pythonw "%REPO_DIR%mainUI.py" %*
) else (
    python "%REPO_DIR%mainUI.py" %*
)
exit /b %ERRORLEVEL%
