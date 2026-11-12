#!/usr/bin/env python3
"""
Antigravity 8086 Desktop Graphical User Interface (GUI)
PyQt5-based visual emulator, editor, and microprocessor simulator.
"""

import os
import sys

def main():
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.mainwindow import MainWindow
    except ImportError as e:
        print("\n" + "=" * 70)
        print("  [8086 Emulator GUI] PyQt5 is required to launch the Desktop GUI.")
        print("=" * 70)
        print(f"Details: {e}\n")
        print("Installation Options:")
        print("  • Via pip:         pip install PyQt5")
        print("  • Ubuntu / Debian: sudo apt install python3-pyqt5")
        print("  • Fedora:          sudo dnf install python3-qt5")
        print("  • Arch Linux:      sudo pacman -S python-pyqt5")
        print("  • NixOS:           Add pkgs.python3Packages.pyqt5 to your shell/config\n")
        print("ProTip: You can use the full-featured TUI application with zero GUI dependencies:")
        print("  emu8086-tui [file.asm]\n")
        sys.exit(1)

    initial_file = None
    for arg in sys.argv[1:]:
        if arg in ('-h', '--help'):
            print("Usage: emu8086-gui [path_to_asm_file]")
            sys.exit(0)
        elif not arg.startswith('-') and initial_file is None:
            initial_file = arg

    app = QApplication(sys.argv)
    win = MainWindow(app, initial_file=initial_file)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
