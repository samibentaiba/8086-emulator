#!/usr/bin/env bash
# ==============================================================================
# 8086 Emulator — Automated Linux & macOS Application Installer
# Installs CLI launchers (emu8086, emu8086-tui, emu8086-gui) into ~/.local/bin
# and Desktop Entries into ~/.local/share/applications
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
APPS_DIR="${HOME}/.local/share/applications"
ICON_DIR="${HOME}/.local/share/icons/hicolor/256x256/apps"

echo "======================================================================"
echo "  Installing 8086 Emulator (TUI & GUI Applications)"
echo "======================================================================"

# 1. Ensure user directories exist
mkdir -p "$BIN_DIR"
mkdir -p "$APPS_DIR"
mkdir -p "$ICON_DIR"

# 2. Make repository launchers executable
chmod +x "$REPO_DIR/bin/emu8086"
chmod +x "$REPO_DIR/bin/emu8086-tui"
chmod +x "$REPO_DIR/bin/emu8086-gui"

# 3. Create symlinks in ~/.local/bin
ln -sf "$REPO_DIR/bin/emu8086" "$BIN_DIR/emu8086"
ln -sf "$REPO_DIR/bin/emu8086-tui" "$BIN_DIR/emu8086-tui"
ln -sf "$REPO_DIR/bin/emu8086-gui" "$BIN_DIR/emu8086-gui"

echo "✓ CLI launchers installed into $BIN_DIR:"
echo "    - emu8086      (Unified terminal command)"
echo "    - emu8086-tui  (Neovim-style interactive modal TUI)"
echo "    - emu8086-gui  (PyQt5 desktop workbench)"

# 4. Install desktop icon if present
if [ -f "$REPO_DIR/image/logo.png" ]; then
    cp "$REPO_DIR/image/logo.png" "$ICON_DIR/emu8086.png"
    echo "✓ Application icon installed to $ICON_DIR/emu8086.png"
fi

# 5. Install Desktop Entries
if [ -d "$REPO_DIR/desktop" ]; then
    cp "$REPO_DIR/desktop/emu8086-tui.desktop" "$APPS_DIR/"
    cp "$REPO_DIR/desktop/emu8086-gui.desktop" "$APPS_DIR/"
    echo "✓ Desktop applications installed to $APPS_DIR"
fi

# 6. Update desktop database if available
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

echo ""
echo "======================================================================"
echo "  Installation Complete!"
echo "======================================================================"
echo "You can now run from ANY terminal:"
echo "    emu8086-tui                (Open new buffer like Neovim)"
echo "    emu8086-tui <filename.asm> (Edit & debug assembly file)"
echo "    emu8086-gui                (Launch desktop GUI)"
echo ""
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Notice: Make sure '$BIN_DIR' is in your PATH. Add to ~/.bashrc or ~/.zshrc:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi
