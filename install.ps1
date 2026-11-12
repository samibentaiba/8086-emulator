# ==============================================================================
# 8086 Emulator — Windows PowerShell Automated Installer
# Configures User PATH and creates Desktop & Start Menu Shortcuts
# ==============================================================================

[CmdletBinding()]
param (
    [switch]$NoShortcuts
)

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BinDir = Join-Path $RepoDir "bin\windows"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Installing 8086 Emulator for Windows (TUI & GUI Applications)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Repository root: $RepoDir"

# 1. Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Warning "Python 3 was not found in PATH. Please install Python 3.9+ from https://python.org"
} else {
    Write-Host "[OK] Detected Python: $(& python --version 2>&1)" -ForegroundColor Green
}

# 2. Add to User PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $UserPath) { $UserPath = "" }
$paths = $UserPath -split ";" | Where-Object { $_ -ne "" }

if ($paths -notcontains $BinDir) {
    $NewPath = ($paths + $BinDir) -join ";"
    [Environment]::SetEnvironmentVariable("Path", $NewPath, "User")
    Write-Host "[OK] Added $BinDir to User PATH." -ForegroundColor Green
} else {
    Write-Host "[INFO] $BinDir is already in User PATH." -ForegroundColor Yellow
}

# 3. Create Shortcuts
if (-not $NoShortcuts) {
    $ws = New-Object -ComObject WScript.Shell
    $Desktop = [Environment]::GetFolderPath("Desktop")

    $tuiBat = Join-Path $BinDir "emu8086-tui.bat"
    $guiBat = Join-Path $BinDir "emu8086-gui.bat"

    $tuiLnk = Join-Path $Desktop "8086 Emulator (TUI).lnk"
    $guiLnk = Join-Path $Desktop "8086 Emulator (GUI).lnk"

    $s1 = $ws.CreateShortcut($tuiLnk)
    $s1.TargetPath = $tuiBat
    $s1.WorkingDirectory = $RepoDir
    $s1.Description = "8086 Emulator - Neovim-Style Modal TUI Debugger"
    $s1.Save()
    Write-Host "[OK] Created Desktop Shortcut: $tuiLnk" -ForegroundColor Green

    $s2 = $ws.CreateShortcut($guiLnk)
    $s2.TargetPath = $guiBat
    $s2.WorkingDirectory = $RepoDir
    $s2.Description = "8086 Emulator - PyQt5 Desktop GUI Workbench"
    $s2.Save()
    Write-Host "[OK] Created Desktop Shortcut: $guiLnk" -ForegroundColor Green
}

# 4. Check & Install Dependencies
$pipCmd = Get-Command pip -ErrorAction SilentlyContinue
if ($pipCmd) {
    Write-Host "Installing Windows dependencies (windows-curses and PyQt5)..." -ForegroundColor Yellow
    & pip install windows-curses PyQt5
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Available commands in any new terminal:"
Write-Host "  - emu8086-tui [file.asm]   (Neovim-style terminal debugger & editor)"
Write-Host "  - emu8086-gui [file.asm]   (PyQt5 graphical microprocessor workbench)"
Write-Host "  - emu8086     [options]    (Unified CLI & headless test runner)"
