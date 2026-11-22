@echo off
REM 8086 Digital Logic Circuit Workbench Launcher (Helmut Neemann's Digital)
set "SCRIPT_DIR=%~dp0"
set "JAR=%SCRIPT_DIR%..\..\digital-circuit\bin\Digital\Digital.jar"
set "DEFAULT_CIRCUIT=%SCRIPT_DIR%..\..\digital-circuit\i8086_system_board.dig"

if "%~1"=="" (
    java -jar "%JAR%" "%DEFAULT_CIRCUIT%"
) else (
    java -jar "%JAR%" %*
)
