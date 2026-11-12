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
Neovim / LazyVim Modal Editor & Time-Travel Reverse Debugger

Usage:
    emu8086-tui [file.asm] [options]
    python3 tui.py [file.asm] [options]

If [file.asm] is omitted or does not exist, a new buffer is created with
a standard MASM skeleton ready to edit and save (exactly like Neovim).

Options:
    -g, --gui-windows   Also spawn external Tkinter GUI visualizer windows
    -h, --help          Show this help message

Modal Editing (LazyVim Style):
    [i]                 Enter INSERT mode at cursor
    [a]                 Enter INSERT mode after cursor
    [o] / [O]           Open new line below / above and enter INSERT mode
    [Esc]               Return to NORMAL mode (automatically reassembles code)
    [<Space>w]          Save buffer to disk

Execution & Time-Travel Debugging:
    [s] / [Space]       Single-step forward
    [u]                 Step BACKWARD (Time-Travel Undo)
    [c]                 Run continuously forward
    [C]                 Run continuously backward (Rewind)
    [p]                 Pause continuous run
    [b]                 Toggle breakpoint at cursor line
    [r]                 Reset CPU and reload initial state
    [+] / [-]           Speed up / slow down execution

Navigation & View:
    [h] [j] [k] [l]     Vim directional navigation
    [Tab] / [S-Tab]     Switch active pane
    [m]                 Cycle memory segment (DS, CS, SS, ES, VIDEO)
    [v]                 Toggle stack view
    [t]                 Toggle hardware telemetry
    [z]                 Toggle pane zoom (full-screen pane)
    [?]                 Toggle cheat-sheet help
    [q]                 Quit

Examples:
    emu8086-tui                           # Open new buffer (untitled.asm)
    emu8086-tui my_program.asm            # Edit and debug file
    emu8086-tui tests/Requirement/bubble_sort.asm
""")


def main():
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

    # Neovim-style: If no file is specified, open an interactive untitled buffer
    if not asm_file:
        asm_file = "untitled.asm"

    tui = EmulatorTUI(asm_file, enable_gui_windows=enable_gui)
    tui.run()


if __name__ == "__main__":
    main()
