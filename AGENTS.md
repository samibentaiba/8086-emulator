# AGENTS.md — 8086 Emulator AI Agent & Developer Knowledge Base

> **Target Audience**: AI Coding Assistants (Antigravity, Claude Code, Cursor, Copilot, Codex, Gemini) and human contributors maintaining or extending this Intel 8086 emulator fork.
> **Repository**: [`samibentaiba/8086-emulator`](https://github.com/samibentaiba/8086-emulator.git)  
> **Original Base**: ZubinGou/8086-emulator  
> **Current Version**: `v5.2.0` (LazyVim Modal Editor, 1-to-1 Execution Tracking, Zero-Glitch TUI, 53 Unit Tests)

---

## 1. High-Level System Architecture & Mental Model

The emulator is written in Python (>=3.9) and models an Intel 8086 microprocessor using a **2-stage pipelined architecture** coupled with virtual memory, virtual I/O peripherals, and multiple frontend interfaces:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 Source Code (*.asm)                    │
                  └──────────────────────────┬─────────────────────────────┘
                                             │ Assembler.compile()
                                             ▼
                  ┌────────────────────────────────────────────────────────┐
                  │             Executable Structure (exe_file)            │
                  │  - Segment spaces (CS, DS, SS, ES)                     │
                  │  - Tag & Variable dictionaries                         │
                  └──────────────────────────┬─────────────────────────────┘
                                             │ Memory.load()
                                             ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                 1MB Physical Memory                    │
                  │              (0x00000 - 0xFFFFF bytes)                 │
                  └───────────────▲────────────────────────▲───────────────┘
                                  │                        │
                      Fetch Cycle │          Execute Cycle │ Read/Write
                                  │                        │
  ┌───────────────────────────────┴────────┐      ┌────────┴───────────────────────────────┐
  │         Bus Interface Unit (BIU)       │      │         Execution Unit (EU)            │
  │  - CS, DS, SS, ES, IP registers        │ FIFO │  - AX, BX, CX, DX, SP, BP, SI, DI       │
  │  - 20-bit address generator            ├─────►│  - Flags: CF, ZF, SF, OF, PF, AF, IF, DF│
  │  - 6-byte instruction prefetch queue   │      │  - Arithmetic, Logic, Transfer Engine   │
  └────────────────────────────────────────┘      └────────┬──────────────────────┬────────┘
                                                           │                      │
                                               I/O Bus (IN/OUT)        Interrupts (INT xx)
                                                           │                      │
                                                           ▼                      ▼
                                          ┌──────────────────────┐  ┌──────────────────────┐
                                          │  PeripheralManager   │  │   IVT (0x00000)      │
                                          │  - Port 4: Traffic   │  │   - INT 10h (BIOS)   │
                                          │  - Port 7: Stepper   │  │   - INT 21h (DOS)    │
                                          │  - 0xB8000: Video    │  │   - INT 0-4 (CPU)    │
                                          └──────────────────────┘  └──────────────────────┘
```

### 1.1 Key Technical Principles
1. **Interpreter-Style Instruction Representation**:
   - The assembler does **not** emit x86 binary machine code. Instead, instructions are parsed into tokenized Python lists:
     ```python
     ['MOV', 'AX', '0x2000']
     ['OUT', '4', 'AX']
     ['LOOP', '0x4']
     ```
   - These token lists are stored directly inside `space[segment][offset]`.
2. **20-bit Physical Address Calculation**:
   $$\text{Physical Address} = (\text{Segment} \times 16) + \text{Offset} = (\text{Segment} \ll 4) + \text{Offset}$$
   - Segment default base addresses:
     - `DS` = `0x2000` $\rightarrow$ Physical base `0x20000`
     - `CS` = `0x3000` $\rightarrow$ Physical base `0x30000`
     - `SS` = `0x5000` $\rightarrow$ Physical base `0x50000`
     - `ES` = `0x7000` $\rightarrow$ Physical base `0x70000`
     - `Video Buffer` $\rightarrow$ Physical base `0xB8000` (CGA 80x25 text mode)
3. **Execution Loop Lifecycle**:
   - Each clock cycle alternates between:
     1. `BIU.run()`: Prefetches up to 6 instruction bytes into the instruction queue.
     2. `EU.run()`: Pops from queue, decodes opcode in `control_circuit()`, executes ALU/data operations, updates flags, and handles I/O or interrupts.

---

## 2. Codebase Map & File Responsibilities

| File Path | Role | Key Classes / Functions | Notes |
|---|---|---|---|
| [`main.py`](file:///home/sami/Documents/GitHub/8086-emulator/main.py) | CLI entry point & argument parser | `main()` | Handles `-n` (no debug), `-t` (TUI), `-i` (interrupt log), `-g` (peripheral visualizer windows). |
| [`tui.py`](file:///home/sami/Documents/GitHub/8086-emulator/tui.py) | Standalone TUI debugger launcher | `main()` | Pure curses, zero external dependencies. |
| [`mainUI.py`](file:///home/sami/Documents/GitHub/8086-emulator/mainUI.py) | PyQt5 Desktop GUI launcher | `main()` | Graphical interface with code editor and memory grids. |
| [`emulator/cpu.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/cpu.py) | CPU orchestration & clock cycle driver | `class CPU` | Coordinates BIU/EU cycles, `iterate()`, `debug()`, cleanup hooks. |
| [`emulator/assembler.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/assembler.py) | MASM-style 8086 interpreter/assembler | `class Assembler`, `class AssemblyError`, `to_decimal()` | Two-pass parsing, `EQU` constants, `PROC`/`ENDP`, resilient `ASSUME` pre-scanning. |
| [`emulator/memory.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/memory.py) | 1MB Flat Memory Array | `class Memory` | `rb()`, `wb()`, `load()`, little-endian word read/write. |
| [`emulator/register.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/register.py) | Status & Control Flags Register | `class FR` | CF, ZF, SF, OF, PF, AF, IF, DF, TF bit flags. |
| [`emulator/instructions.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/instructions.py) | Instruction tables & classifications | Lists: `all_ins`, `transfer_control_ins`, etc. | Opcode categories and token validation. |
| [`emulator/pipeline_units/bus_interface_unit.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/pipeline_units/bus_interface_unit.py) | Prefetch queue & segment address generator | `class bus_interface_unit` | 6-byte instruction FIFO, physical address calculation. |
| [`emulator/pipeline_units/execution_unit.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/pipeline_units/execution_unit.py) | Opcode decoding & execution engine | `class execution_unit` | Central `control_circuit()` (~1500 lines), INT 10H/21H APIs, file descriptors. |
| [`emulator/peripherals/manager.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/peripherals/manager.py) | Central I/O Bus Manager | `class PeripheralManager` | Singleton managing I/O ports `0x0000`–`0xFFFF`. |
| [`emulator/peripherals/traffic_lights.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/peripherals/traffic_lights.py) | Port 4 Traffic Lights device | `class TrafficLightsDevice` | 12-bit word, North/West/South/East RYG LED mapping, Tkinter IPC. |
| [`emulator/peripherals/stepper_motor.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/peripherals/stepper_motor.py) | Port 7 Stepper Motor device | `class StepperMotorDevice` | 4-bit coil excitation, 32 steps/rev, ready bit polling (bit 7), Tkinter dial. |
| [`emulator/peripherals/video_display.py`](file:///home/sami/Documents/GitHub/8086-emulator/emulator/peripherals/video_display.py) | CGA 80x25 text buffer monitor (`0xB8000`) | `class VideoDisplayDevice` | ASCII character + color attribute byte pair decoding. |
| [`ui/tui.py`](file:///home/sami/Documents/GitHub/8086-emulator/ui/tui.py) | Full-screen curses interactive debugger | `class EmulatorTUI` | Disassembly pane, Register diffs, Hardware telemetry, Hex/Stack viewer. |
| [`ui/mainwindow.py`](file:///home/sami/Documents/GitHub/8086-emulator/ui/mainwindow.py) | PyQt5 main window controller | `class MainWindow` | Menu bar, peripheral launch actions, memory tables. |
| [`pyproject.toml`](file:///home/sami/Documents/GitHub/8086-emulator/pyproject.toml) | Modern packaging configuration | Metadata & Entry points | Provides `pip install -e .`, `emu8086`, `emu8086-tui`. |

---

## 3. Peripheral Hardware Specifications (EMU8086 Standard)

### Port 4 — Virtual Traffic Lights (`OUT 4, AX` / `IN AX, 4`)
- **Size**: 12 active bits (16-bit word).
- **Bit Mapping**:
  - `Bits 0–2`: **North** (Bit 0: Red, Bit 1: Yellow, Bit 2: Green)
  - `Bits 3–5`: **West** (Bit 3: Red, Bit 4: Yellow, Bit 5: Green)
  - `Bits 6–8`: **South** (Bit 6: Red, Bit 7: Yellow, Bit 8: Green)
  - `Bits 9–11`: **East** (Bit 9: Red, Bit 10: Yellow, Bit 11: Green)
  - `Bits 12–15`: Reserved / 0.
- **Example Patterns**:
  - `0x0249` (0000 0010 0100 1001b): All Red.
  - `0x0924` (0000 1001 0010 0100b): North & South Green, East & West Red.

### Port 7 — Virtual Stepper Motor (`OUT 7, AL` / `IN AL, 7`)
- **Size**: 8-bit byte.
- **Output (`OUT 7, AL`)**:
  - `Bits 0–3`: Coils A, B, C, D excitation.
  - Full revolution = 32 half-steps ($11.25^\circ$ per step).
  - CW Half-step sequence: `06h` $\rightarrow$ `04h` $\rightarrow$ `03h` $\rightarrow$ `02h` $\rightarrow$ repeat.
  - CCW Half-step sequence: `03h` $\rightarrow$ `01h` $\rightarrow$ `06h` $\rightarrow$ `02h` $\rightarrow$ repeat.
- **Input (`IN AL, 7`)**:
  - `Bit 7` (`0x80`): **Ready Flag**. Returns `1` when ready for next step. Assembler code polls this before issuing `OUT 7, AL`.

### Physical Address `0xB8000` — CGA Text Mode Video Mirror
- 80 columns $\times$ 25 rows = 2,000 characters (4,000 bytes).
- Even byte: ASCII character code.
- Odd byte: CGA attribute byte (`Foreground: bits 0-3`, `Background: bits 4-6`, `Blink: bit 7`).

---

## 4. Interrupt Vector Table & Supported System Calls

### BIOS Video Services (`INT 10H`)
- `AH=00H`: Set Video Mode (`AL=03H` color text 80x25).
- `AH=02H`: Set Cursor Position (`DH`=row, `DL`=column, `BH`=page).
- `AH=03H`: Get Cursor Position (returns `DH`=row, `DL`=column).
- `AH=06H`: Scroll Window Up / Clear screen (`AL`=lines).
- `AH=09H`: Write Character & Attribute (`AL`=char, `BL`=attribute, `CX`=count).
- `AH=0EH`: Teletype Output (`AL`=char).
- `AH=0FH`: Get Current Video Mode.

### DOS System Services (`INT 21H`)
- `AH=00H` / `AH=4CH`: Terminate program (`AL`=exit code).
- `AH=01H`: Character input with echo (`AL`=char).
- `AH=02H`: Display character (`DL`=char).
- `AH=09H`: Display `$`-terminated string (`DS:DX`=address).
- `AH=2AH`: Get system date (`CX`=year, `DH`=month, `DL`=day).
- `AH=2CH`: Get system time (`CH`=hour, `CL`=minute, `DH`=sec, `DL`=1/100s).
- `AH=3CH`: Create file (`DS:DX`=ASCIIZ filename, `CX`=attribute $\rightarrow$ `AX`=handle).
- `AH=3DH`: Open file (`DS:DX`=ASCIIZ filename, `AL`=mode $\rightarrow$ `AX`=handle).
- `AH=3EH`: Close file (`BX`=handle).
- `AH=3FH`: Read file (`BX`=handle, `CX`=bytes, `DS:DX`=buffer $\rightarrow$ `AX`=read).
- `AH=40H`: Write file (`BX`=handle, `CX`=bytes, `DS:DX`=buffer $\rightarrow$ `AX`=written).
- `AH=41H`: Delete file (`DS:DX`=ASCIIZ filename).

---

## 5. Strict Guidelines & Invariants for AI Agents

When editing or extending this codebase, adhere strictly to these rules:

1. **Preserve Existing Signatures**:
   - Do not alter parameters or return signatures in `cpu.py`, `bus_interface_unit.py`, `execution_unit.py`, or `assembler.py`.
2. **Windows Multiprocessing Safety**:
   - Any module that launches subprocesses via Python's `multiprocessing` must protect standalone/demo entry points with:
     ```python
     if __name__ == '__main__':
     ```
   - On Windows, `multiprocessing` defaults to `spawn` (not `fork`), which re-imports the main file.
3. **No Blocking `input()` in TUI Mode**:
   - `cpu.py` must never call blocking `input()` when running in TUI mode (`self.tui_mode == True`).
   - Terminal input instructions (`IN`, `INT 21H AH=01h/07h/08h`) must catch `(EOFError, OSError)` gracefully.
4. **Assembler Error Handling**:
   - Never use `sys.exit("Compile Error")` or bare `assert` for syntax errors. Raise `AssemblyError(message, line, source)`.
5. **Decoupled Peripheral Architecture**:
   - Do not hardcode peripheral state inside `execution_unit.py`. Route I/O port reads/writes through `self.peripherals.read_port(port)` and `self.peripherals.write_port(port, value)`.
6. **All 53 Unit Tests Must Pass**:
   - Always run `python3 -m unittest discover tests` before pushing commits.

---

## 6. How to Run & Verify

### Run Automated Test Suite
```bash
python3 -m unittest discover tests
```
*Expected result: 53 tests passing in under 45 seconds.*

### Run CLI Verification
```bash
# Continuous headless run (bubble sort benchmark)
python3 main.py ./tests/Requirement/bubble_sort.asm -n

# Run system date/time interrupt test
python3 main.py ./tests/Interrupt/show_date_time.asm -n

# Run EMU8086 hardware demos
python3 main.py ./tests/Hardware/traffic_lights_demo.asm -n
python3 main.py ./tests/Hardware/stepper_motor_demo.asm -n
python3 main.py ./tests/Hardware/hello_video_demo.asm -n
```

### Run Full-Screen TUI
```bash
python3 tui.py ./tests/Requirement/bubble_sort.asm
# Keybindings: [s] step, [c] run, [p] pause, [b] breakpoint, [Tab] switch pane, [v] stack view, [q] quit
```

### Install in Editable Mode
```bash
pip install -e .
emu8086 ./tests/Hardware/traffic_lights_demo.asm -n
emu8086-tui ./tests/Requirement/bubble_sort.asm
```
