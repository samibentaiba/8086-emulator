import os
import sys
import argparse
from emulator.assembler import Assembler
from emulator.memory import Memory
from emulator.pipeline_units import bus_interface_unit, execution_unit
from emulator.cpu import CPU


INSTRUCTION_QUEUE_SIZE = 6
MEMORY_SIZE = int('FFFFF', 16)  # Memory address space size 1MB
CACHE_SIZE = int('10000', 16)  # Cache size 64KB
SEGMENT_SIZE = int('10000', 16) # Maximum segment size 64KB (10000H)

SEG_INIT = {
    'DS': int('2000', 16), # Initial value of data segment
    'CS': int('3000', 16), # Initial value of code segment
    'SS': int('5000', 16), # Initial value of stack segment
    'ES': int('7000', 16) # Initial value of extra segment
}


def main():
    parser = argparse.ArgumentParser(
        description="Antigravity 8086 Microprocessor Emulator CLI & Interactive TUI",
        epilog="Examples:\n"
               "  python main.py ./tests/Requirement/bubble_sort.asm -t\n"
               "  python main.py ./tests/Interrupt/show_date_time.asm -n\n"
               "  python main.py ./tests/Requirement/bubble_sort.asm -i\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("file", help="Path to 8086 assembly source file (.asm)")
    parser.add_argument("-t", "--tui", action="store_true", help="Launch interactive full-screen Neovim/GDB-style TUI debugger")
    parser.add_argument("-n", "--nodebug", action="store_true", help="Run without interactive debug prompts (continuous run)")
    parser.add_argument("-i", "--interrupt", action="store_true", help="Print interrupt execution information")
    parser.add_argument("-g", "--gui-windows", action="store_true", help="Spawn external GUI visualizer windows for peripherals")

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if not os.path.exists(args.file):
        sys.exit(f"Error: File '{args.file}' not found.")

    # If TUI mode requested, launch the interactive TUI
    if args.tui:
        from ui.tui import EmulatorTUI
        tui = EmulatorTUI(args.file, enable_gui_windows=args.gui_windows)
        tui.run()
        return

    with open(args.file, 'r', encoding='utf-8') as file:
        asm_code = file.read()

    assembler = Assembler(SEG_INIT)
    try:
        exe_file = assembler.compile(asm_code)
    except Exception as err:
        sys.exit(f"\n{err}\n")
    memory = Memory(MEMORY_SIZE, SEGMENT_SIZE)
    memory.load(exe_file) # load code segment

    BIU = bus_interface_unit.bus_interface_unit(INSTRUCTION_QUEUE_SIZE, exe_file, memory)
    EU = execution_unit.execution_unit(BIU, args.interrupt)
    cpu = CPU(BIU, EU, gui_mode=False)
    print("\nCPU initialized successfully.")
    print("=" * 80)

    debug_mode = not args.nodebug
    while not cpu.check_done():
        cpu.iterate(debug=debug_mode)
    cpu.print_end_state()


if __name__ == "__main__":
    main()
