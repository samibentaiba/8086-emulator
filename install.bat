@echo off
REM ==============================================================================
REM 8086 Emulator — Windows Automated Installer
REM Configures User PATH and creates Desktop Shortcuts for TUI and GUI apps
REM ==============================================================================
setlocal EnableDelayedExpansion

set "REPO_DIR=%~dp0"
REM Remove trailing backslash if present
if "%REPO_DIR:~-1%"=="\" set "REPO_DIR=%REPO_DIR:~0,-1%"

echo ======================================================================
echo   Installing 8086 Emulator for Windows (TUI and GUI Applications)
echo ======================================================================
echo Repository root: %REPO_DIR%
echo.

REM 1. Verify Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Python 3 was not detected in your PATH!
    echo Please install Python 3.9+ from https://www.python.org/ or the Microsoft Store.
    echo Ensure "Add Python to PATH" is checked during installation.
    echo.
) else (
    echo [OK] Python is detected:
    python --version
    echo.
)

REM 2. Add bin\windows and repo to User PATH safely via PowerShell
echo Adding 8086 Emulator to User PATH...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$binDir = Join-Path '%REPO_DIR%' 'bin\windows';" ^
  "$userPath = [Environment]::GetEnvironmentVariable('Path', 'User');" ^
  "if (-not $userPath) { $userPath = '' };" ^
  "if ($userPath -split ';' -notcontains $binDir) {" ^
  "    $newPath = if ($userPath) { $userPath.TrimEnd(';') + ';' + $binDir } else { $binDir };" ^
  "    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User');" ^
  "    Write-Host '[OK] Added' $binDir 'to User PATH.';" ^
  "} else {" ^
  "    Write-Host '[INFO]' $binDir 'is already in User PATH.';" ^
  "}"

REM 3. Create Windows Desktop Shortcuts via PowerShell
echo Creating Desktop Shortcuts...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$desktop = [Environment]::GetFolderPath('Desktop');" ^
  "$tuiBat = Join-Path '%REPO_DIR%' 'bin\windows\emu8086-tui.bat';" ^
  "$guiBat = Join-Path '%REPO_DIR%' 'bin\windows\emu8086-gui.bat';" ^
  "$tuiLnk = Join-Path $desktop '8086 Emulator (TUI).lnk';" ^
  "$guiLnk = Join-Path $desktop '8086 Emulator (GUI).lnk';" ^
  "$s1 = $ws.CreateShortcut($tuiLnk);" ^
  "$s1.TargetPath = $tuiBat;" ^
  "$s1.WorkingDirectory = '%REPO_DIR%';" ^
  "$s1.Description = '8086 Emulator - Neovim-Style Modal TUI Debugger';" ^
  "$s1.Save();" ^
  "Write-Host '[OK] Created shortcut:' $tuiLnk;" ^
  "$s2 = $ws.CreateShortcut($guiLnk);" ^
  "$s2.TargetPath = $guiBat;" ^
  "$s2.WorkingDirectory = '%REPO_DIR%';" ^
  "$s2.Description = '8086 Emulator - PyQt5 Desktop GUI Workbench';" ^
  "$s2.Save();" ^
  "Write-Host '[OK] Created shortcut:' $guiLnk;"

echo.
echo ======================================================================
echo   Installation Complete!
echo ======================================================================
echo You can launch from any new Command Prompt / PowerShell window:
echo     emu8086-tui                 (Neovim-style editor and debugger)
echo     emu8086-tui <file.asm>      (Open/create file)
echo     emu8086-gui                 (Desktop GUI workbench)
echo.
echo Desktop shortcuts '8086 Emulator (TUI)' and '8086 Emulator (GUI)'
echo have also been added to your Desktop!
echo ======================================================================
pause
