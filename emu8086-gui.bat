@echo off
setlocal
set "REPO_DIR=%~dp0"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"
where pythonw >nul 2>nul
if %ERRORLEVEL% equ 0 (
    start "" pythonw "%REPO_DIR%mainUI.py" %*
) else (
    python "%REPO_DIR%mainUI.py" %*
)
exit /b %ERRORLEVEL%
