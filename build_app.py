#!/usr/bin/env bash
"""":
exec python3 "$0" "$@"
"""
# ==============================================================================
# 8086 Emulator — Standalone Application Builder (Windows & Linux)
# Compiles standalone self-contained binaries using PyInstaller
# ==============================================================================

import argparse
import os
import platform
import shutil
import subprocess
import sys

REPO_DIR = os.path.abspath(os.path.dirname(__file__))
DIST_DIR = os.path.join(REPO_DIR, "dist")
BUILD_DIR = os.path.join(REPO_DIR, "build")


def check_pyinstaller():
    """Verify PyInstaller is installed in the current Python environment."""
    try:
        import PyInstaller  # noqa: F401
        return True
    except ImportError:
        return False


def build_tui(clean=False):
    """Build the standalone TUI application binary."""
    print("\n======================================================================")
    print("  Building Standalone 8086 TUI Application (Neovim-Style Terminal)")
    print("======================================================================")

    tui_entry = os.path.join(REPO_DIR, "tui.py")
    icon_path = os.path.join(REPO_DIR, "image", "logo.png")

    sep = ";" if platform.system() == "Windows" else ":"
    data_args = []
    if os.path.exists(icon_path):
        data_args.extend(["--add-data", f"{icon_path}{sep}image"])

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "emu8086-tui",
        "--onefile",
        "--console",
        "--paths",
        REPO_DIR,
        "--hidden-import",
        "emulator",
        "--hidden-import",
        "emulator.cpu",
        "--hidden-import",
        "emulator.assembler",
        "--hidden-import",
        "emulator.memory",
        "--hidden-import",
        "emulator.register",
        "--hidden-import",
        "emulator.instructions",
        "--hidden-import",
        "emulator.peripherals",
        "--hidden-import",
        "emulator.peripherals.manager",
        "--hidden-import",
        "emulator.peripherals.traffic_lights",
        "--hidden-import",
        "emulator.peripherals.stepper_motor",
        "--hidden-import",
        "emulator.peripherals.video_display",
        "--hidden-import",
        "ui.tui",
    ] + data_args

    if clean:
        cmd.append("--clean")

    cmd.append(tui_entry)

    print(f"Executing: {' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=REPO_DIR)
    if res.returncode == 0:
        ext = ".exe" if platform.system() == "Windows" else ""
        out_bin = os.path.join(DIST_DIR, f"emu8086-tui{ext}")
        print(f"\n[SUCCESS] TUI binary generated at: {out_bin}")
    else:
        print("\n[ERROR] TUI build failed.")
        return False
    return True


def build_gui(clean=False):
    """Build the standalone GUI application binary (PyQt5)."""
    print("\n======================================================================")
    print("  Building Standalone 8086 GUI Application (PyQt5 Desktop Workbench)")
    print("======================================================================")

    try:
        import PyQt5  # noqa: F401
    except ImportError:
        print("[WARNING] PyQt5 is not installed in the current environment.")
        print("Please run: pip install PyQt5 before compiling the GUI application.")
        return False

    gui_entry = os.path.join(REPO_DIR, "mainUI.py")
    icon_path = os.path.join(REPO_DIR, "image", "logo.png")

    sep = ";" if platform.system() == "Windows" else ":"
    data_args = []
    if os.path.exists(icon_path):
        data_args.extend(["--add-data", f"{icon_path}{sep}image"])

    # Windowed mode on Windows / macOS; console flag omitted
    window_mode = "--windowed" if platform.system() in ("Windows", "Darwin") else "--console"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "emu8086-gui",
        "--onefile",
        window_mode,
        "--paths",
        REPO_DIR,
        "--hidden-import",
        "PyQt5",
        "--hidden-import",
        "PyQt5.QtWidgets",
        "--hidden-import",
        "PyQt5.QtCore",
        "--hidden-import",
        "PyQt5.QtGui",
        "--hidden-import",
        "emulator",
        "--hidden-import",
        "emulator.cpu",
        "--hidden-import",
        "emulator.assembler",
        "--hidden-import",
        "emulator.memory",
        "--hidden-import",
        "emulator.register",
        "--hidden-import",
        "emulator.instructions",
        "--hidden-import",
        "emulator.peripherals",
        "--hidden-import",
        "ui.mainwindow",
    ] + data_args

    if clean:
        cmd.append("--clean")

    cmd.append(gui_entry)

    print(f"Executing: {' '.join(cmd)}\n")
    res = subprocess.run(cmd, cwd=REPO_DIR)
    if res.returncode == 0:
        ext = ".exe" if platform.system() == "Windows" else ""
        out_bin = os.path.join(DIST_DIR, f"emu8086-gui{ext}")
        print(f"\n[SUCCESS] GUI binary generated at: {out_bin}")
    else:
        print("\n[ERROR] GUI build failed.")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="8086 Emulator Standalone Binary Builder (PyInstaller)"
    )
    parser.add_argument("--tui", action="store_true", help="Build standalone TUI binary")
    parser.add_argument("--gui", action="store_true", help="Build standalone GUI binary")
    parser.add_argument("--all", action="store_true", help="Build both TUI and GUI binaries")
    parser.add_argument("--clean", action="store_true", help="Clean build cache before building")

    args = parser.parse_args()

    # Default to --all if neither specified
    if not (args.tui or args.gui or args.all):
        args.all = True

    if not check_pyinstaller():
        print("======================================================================")
        print("  PyInstaller is required to build standalone binaries")
        print("======================================================================")
        print("Please install PyInstaller with:")
        print("    pip install pyinstaller")
        print("\nOr on Ubuntu / Debian:")
        print("    sudo apt install python3-pyinstaller")
        print("\nAfter installing, re-run:")
        print("    python3 build_app.py --all")
        sys.exit(1)

    success = True
    if args.tui or args.all:
        if not build_tui(clean=args.clean):
            success = False

    if args.gui or args.all:
        if not build_gui(clean=args.clean):
            success = False

    if success:
        print("\n======================================================================")
        print("  All requested applications were built successfully!")
        print(f"  Binaries located in: {DIST_DIR}")
        print("======================================================================")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
