@echo off
REM 8086 Circuit Atlas Workbench Launcher
set "SCRIPT_DIR=%~dp0"
python "%SCRIPT_DIR%circuit_server.py" %*
