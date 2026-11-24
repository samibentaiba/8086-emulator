# ==============================================================================
# 8086 Emulator — Windows PowerShell Automated Installer
# Configures User PATH and creates Desktop shortcuts
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

# Install both frontends with the Python interpreter the launchers will use.
$pythonCmd = Get-Command python -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $pythonCmd) {
    throw "Install Python 3.9 or later and add it to PATH, then run the installer again."
}
$pythonExe = $pythonCmd.Source
& $pythonExe -c "import sys; print(sys.version.split()[0]); sys.exit(sys.version_info < (3, 9))"
if ($LASTEXITCODE -ne 0) { throw "The Windows launchers require Python 3.9 or later." }
Write-Host "Installing Windows frontend dependencies with $pythonExe" -ForegroundColor Cyan
& $pythonExe -m pip install -r (Join-Path $RepoDir "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Installing the Windows frontend dependencies failed." }

# 2. Add to User PATH
$UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $UserPath) { $UserPath = "" }
$paths = @($UserPath -split ";" | Where-Object { $_ -ne "" })

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

    $circuitBat = Join-Path $BinDir "emu8086-circuit.bat"
    $circuitLnk = Join-Path $Desktop "8086 Circuit Workbench.lnk"
    $s3 = $ws.CreateShortcut($circuitLnk)
    $s3.TargetPath = $circuitBat
    $s3.WorkingDirectory = $RepoDir
    $s3.Description = "8086 Circuit Workbench - Interactive Hardware Schematic"
    $s3.Save()
    Write-Host "[OK] Created Desktop Shortcut: $circuitLnk" -ForegroundColor Green
}

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Available commands in any new terminal:"
Write-Host "  - emu8086-tui     [file.asm] (Neovim-style terminal debugger & editor)"
Write-Host "  - emu8086-gui     [file.asm] (PyQt5 graphical microprocessor workbench)"
Write-Host "  - emu8086-circuit            (8086 Circuit Workbench interactive schematic)"
Write-Host "  - emu8086         [options]  (Unified CLI & headless test runner)"
