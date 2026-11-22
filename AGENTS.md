# AGENTS.md — 8086 Emulator AI Agent & Developer Knowledge Base

> **Target Audience**: AI Coding Assistants (Antigravity, Claude Code, Cursor, Copilot, Codex, Gemini) and human contributors maintaining or extending this Intel 8086 emulator fork.
> **Repository**: [`samibentaiba/8086-emulator`](https://github.com/samibentaiba/8086-emulator.git)  
> **Original Base**: ZubinGou/8086-emulator  
> **Current Version**: `v5.2.0` (LazyVim Modal Editor, Time-Travel Reverse Debugging, 1-to-1 Execution Tracking, Zero-Glitch TUI, 80 Unit Tests)

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
| [`ui/mainwindow.py`](file:///home/sami/Documents/GitHub/8086-emulator/ui/mainwindow.py) | PyQt5 main window controller | `class MainWindow` | Menu bar, peripheral launch actions, memory tables, Circuit Atlas launcher. |
| [`circuit_server.py`](file:///home/sami/Documents/GitHub/8086-emulator/circuit_server.py) | 8086 Circuit Atlas HTTP Server | `launch_circuit()` | Serves 100% interactive Intel 8086 microprocessor circuit workbench in browser. |
| [`circuits-side/src/`](file:///home/sami/Documents/GitHub/8086-emulator/circuits-side/src/) | Modular TypeScript circuit engine & schematics | `Pin`, `Component`, `LogicGate`, `AutoRouter` | Strongly-typed OOP circuit compiler target for `diagram.js`. |
| [`build_circuits.py`](file:///home/sami/Documents/GitHub/8086-emulator/build_circuits.py) | Circuit TypeScript compiler helper | `main()`, `find_tsc()` | Compiles `circuits-side/src/` -> `circuits-side/diagram.js`. |
| [`circuits-side/diagram.js`](file:///home/sami/Documents/GitHub/8086-emulator/circuits-side/diagram.js) | Gate-level logic schematics for all 29 units | `logicDraw` | Full gate schematics: registers, ALU, flags, address adder, 40-pin DIP chip, etc. |
| [`circuits-side/architecture.js`](file:///home/sami/Documents/GitHub/8086-emulator/circuits-side/architecture.js) | 8086 CPU Architecture & Schematic Renderer | `board` | Multi-scale semantic zoom: architecture -> block level -> gate-level embedded view. |
| [`bin/emu8086-circuit`](file:///home/sami/Documents/GitHub/8086-emulator/bin/emu8086-circuit) | Standalone Circuit Atlas Launcher | Shell script | Zero-dependency browser entry point for interactive 8086 circuit schematic. |
| [`bin/emu8086-tui`](file:///home/sami/Documents/GitHub/8086-emulator/bin/emu8086-tui) | Standalone Linux TUI Launcher | Shell script | Zero-dependency terminal entry point (`readlink -f`). |
| [`bin/emu8086-gui`](file:///home/sami/Documents/GitHub/8086-emulator/bin/emu8086-gui) | Standalone Linux GUI Launcher | Shell script | Desktop entry point with auto-detection for PyQt5 and NixOS. |
| [`bin/emu8086`](file:///home/sami/Documents/GitHub/8086-emulator/bin/emu8086) | Unified CLI Launcher | Shell script | Auto-dispatches to headless CLI (`-n`) or modal TUI. |
| [`install.sh`](file:///home/sami/Documents/GitHub/8086-emulator/install.sh) | Linux / NixOS Automated Installer | Shell script | Symlinks launchers into `~/.local/bin` and registers desktop apps. |
| [`shell.nix`](file:///home/sami/Documents/GitHub/8086-emulator/shell.nix) | NixOS Development Environment | Nix expression | Provides Python 3 + PyQt5 environment with zero manual setup. |
| [`desktop/*.desktop`](file:///home/sami/Documents/GitHub/8086-emulator/desktop/) | Freedesktop Application Entries | Desktop files | System launcher icons & `.asm` file associations. |
| [`pyproject.toml`](file:///home/sami/Documents/GitHub/8086-emulator/pyproject.toml) | Modern packaging configuration | Metadata & Entry points | Provides `pip install -e .`, `emu8086`, `emu8086-tui`, `emu8086-gui`. |

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
  - `0x030C` (0000 0011 0000 1100b): North & South Green, East & West Red.

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
6. **All Unit Tests Must Pass**:
   - Always run `python3 -m unittest discover tests` before pushing commits.

---

## 6. How to Run & Verify

### Run Automated Test Suite
```bash
python3 -m unittest discover tests
```
*Install the dependencies in `requirements.txt` to include the desktop and terminal tests. The current suite contains 109 tests.*

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

---

## 7. Circuit Atlas CAD Schematic Drawing Invariants & Automated Inspection

AI agents extending [`circuits-side/src/`](file:///home/sami/Documents/GitHub/8086-emulator/circuits-side/src/) must adhere strictly to these visual and geometric CAD schematic laws. Any violation causes ugly visual glitches, wire collisions, or gate body occlusions.

### 7.1 The 6 Cardinal CAD Invariants

```
┌───────────────────────────────── 56px Column Grid ─────────────────────────────────┐
│ Zone 1: Input Drops (xL+1..xL+9)  │ Zone 2: Gates (xL+10..xL+24) │ Zone 3: Output & MUX (xL+26..xL+55) │
│ - Track A:      xL + 3           │ - B_INV: Y = 92..102         │ - chanSum: xL + 27 ──► mux.in0     │
│ - Track B / B*: xL + 6           │ - P:     Y = 112..122        │ - chanP:   xL + 29 ──► mux.in1     │
│ - Track Cin:    xL + 8           │ - G:     Y = 130..140        │ - chanG:   xL + 31 ──► mux.in2     │
│ (All turn 90° right into gates)  │ - OR:    Y = 148..158        │ - chanOr:  xL + 33 ──► mux.in3     │
│                                  │ - SUM:   Y = 166..176        │ - MUX:     xL + 36..xL + 52        │
│                                  │ (ZERO vertical wires run     │ - resDrop: xL + 54 ──► Highway     │
│                                  │  through this zone!)         │ (Approaches MUX from left)         │
└──────────────────────────────────┴──────────────────────────────┴────────────────────────────────────┘
```

1. **Rule 1 — Zero Gate Body Penetration (The Roof/Belly Plunge Error)**:
   - Wires MUST NEVER cross through the geometric bounding box of any gate, flip-flop, buffer, or multiplexer.
   - All logic gate inputs (`in0`, `in1`) MUST approach horizontally from the left.
   - All logic gate outputs (`out`) MUST exit horizontally to the right.
   - Control lines (e.g. MUX select) MUST enter vertically at the bottom center (`sel`).
2. **Rule 2 — The 3-Zone Planar Routing Law**:
   - Every column or bit-slice MUST be partitioned into 3 non-overlapping X-coordinate intervals:
     - `Zone 1` ($X \in [X_L, X_L + 9]$): Vertical input drops ($A, B, C_{in}$).
     - `Zone 2` ($X \in [X_L + 10, X_L + 24]$): Gate bodies only. **Zero vertical routing allowed.**
     - `Zone 3` ($X \in [X_L + 25, X_L + 56]$): Intermediate routing tracks, multiplexers, and result drops.
   - Because $Zone_1 \cap Zone_2 = \emptyset$ and $Zone_2 \cap Zone_3 = \emptyset$, wire-to-gate collisions are mathematically impossible.
3. **Rule 3 — Zero Floating Solder Dots & Unbroken Strobe Spines**:
   - Solder dots (`addDot(...)`) must ONLY exist at genuine physical intersections between two or more wire paths.
   - Multi-row strobe spines (e.g., `RDA`, `WE`, `RDB`, `SUB`, `FN_SEL`) must be continuous from the topmost row to the bottommost row (`M x y_top V y_bottom`), never starting halfway down.
   - Never leave a solder dot floating on an open dead-end line.
4. **Rule 4 — Minimum 6px Parallel Clearance (Zero Pixel Smudging)**:
   - Parallel wires must maintain at least **6–8px clear gap**.
   - Never assign identical or near-identical coordinates (e.g. $Y = 110$ for two independent signals), which causes SVG stroke overlap and ugly dark smudges.
5. **Rule 5 — Zero Boundary Leaking & Exterior Wire Looping**:
   - All circuits must be strictly self-contained within their card boundary ($X \in [10, 1270]$, $Y \in [6, 440]$).
   - Buses and highways must connect directly into destination PortBoxes in a **straight horizontal line**, without U-turns or looping outside the card perimeter.
   - Flag lines must drop straight into the bottom flag container (`portFlags`), never running below the bottom margin.
6. **Rule 6 — Zero Text, Header, & Badge Occlusions**:
   - Wires must NEVER cut through component headers, bit badges (`BIT 15`, `BIT 0`), or hex value readouts.
   - Drops from top ports or buses must pass exclusively through dedicated vertical channels located *between* badge labels.

### 7.2 Automated Schematic Linter

Run the automated schematic inspector before submitting any changes:
```bash
python3 build_circuits.py && python3 tools/lint_schematics.py
```
*The inspector verifies that rendered SVGs have 0 gate penetrations, 0 boundary violations, 0 floating dots, and 0 parallel wire collisions.*

