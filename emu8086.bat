@echo off
setlocal
set "REPO_DIR=%~dp0"
set "PYTHONPATH=%REPO_DIR%;%PYTHONPATH%"
python "%REPO_DIR%main.py" %*
exit /b %ERRORLEVEL%
