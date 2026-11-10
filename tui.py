#!/usr/bin/env python3
"""
Antigravity 8086 Interactive Terminal User Interface (TUI)
Neovim / GDB TUI style interactive visual debugger with live telemetry.

Usage:
    python3 tui.py <path_to_asm_file> [options]

Options:
    -g, --gui-windows   Also spawn external Tkinter GUI visualizer windows
    -h, --help          Show this help message

Keybindings:
    [s] / [Space]       Single-step instruction
    [c]                 Continue / Run continuously
    [p]                 Pause continuous run
    [b]                 Toggle breakpoint on selected instruction
    [Tab]               Switch active pane between Disassembly and Memory Inspector
    [k] / [↑]           Navigate up / scroll memory up
    [j] / [↓]           Navigate down / scroll memory down
    [r]                 Reset CPU and reload program
    [m]                 Cycle memory segment (DS, CS, SS, ES, VIDEO)
    [+] / [-]           Speed up / slow down execution
    [q]                 Quit TUI
"""

import sys
import os

from ui.tui import EmulatorTUI


def print_help():
    print("""
Antigravity 8086 Interactive Terminal User Interface (TUI)
Usage:
    python3 tui.py <path_to_asm_file> [options]

Options:
    -g, --gui-windows   Also spawn external Tkinter GUI visualizer windows
    -h, --help          Show this help message

Keybindings inside TUI:
    [s] or [Space]      Single-step forward
    [c]                 Continue running continuously
    [p]                 Pause continuous execution
    [b]                 Toggle breakpoint on selected instruction
    [Tab]               Switch active pane between Disassembly and Memory Inspector
    [k] / [↑]           Navigate up / scroll memory up
    [j] / [↓]           Navigate down / scroll memory down
    [r]                 Reset CPU and reload program
    [m]                 Cycle memory segment inspector (DS, CS, SS, ES, VIDEO)
    [+] / [-]           Speed up / slow down continuous run speed
    [q]                 Quit TUI

Examples:
    python3 tui.py ./tests/Requirement/bubble_sort.asm
    python3 tui.py ./tests/Inout/traffic_lights_test.asm
    python3 tui.py ./tests/Inout/stepper_motor_test.asm
""")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print_help()
        sys.exit(0)

    # Parse arguments
    args = sys.argv[1:]
    enable_gui = False
    asm_file = None

    for arg in args:
        if arg in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif arg in ('-g', '--gui', '--gui-windows'):
            enable_gui = True
        elif not arg.startswith('-') and asm_file is None:
            asm_file = arg

    if not asm_file:
        print("Error: No assembly (.asm) file specified.")
        print("Run 'python3 tui.py --help' for usage instructions.")
        sys.exit(1)

    if not os.path.exists(asm_file):
        print(f"Error: File '{asm_file}' not found.")
        sys.exit(1)

    tui = EmulatorTUI(asm_file, enable_gui_windows=enable_gui)
    tui.run()


if __name__ == "__main__":
    main()
