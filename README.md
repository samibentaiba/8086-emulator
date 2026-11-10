![](image/logo.png)

# 8086-emulator
![](https://img.shields.io/github/license/samibentaiba/8086-emulator)   ![](https://img.shields.io/github/repo-size/samibentaiba/8086-emulator)   ![Unit Tests](https://img.shields.io/badge/tests-22%2F22%20passing-brightgreen)

An advanced Intel 8086 microprocessor emulator, assembler, and virtual hardware testing sandbox featuring an interactive Neovim/GDB-style Terminal User Interface (TUI), a PyQt5 desktop GUI, and EMU8086-compatible hardware peripherals.

> 🤖 **Working with an AI coding assistant?** Check out [`AGENTS.md`](AGENTS.md) for a comprehensive architecture map, instruction lifecycle trace, peripheral specs, and developer guidelines.

---

## What's New in v5.1 & v5.0 (Major Overhaul)
- **TUI Stack Viewer (`[v]` toggle)**: Real-time inspection of the active call stack (`SS:SP`) showing physical memory addresses, 16-bit word values, and SP offsets directly inside the Memory Inspector pane.
- **Modern Packaging & CLI Entrypoints (`pyproject.toml`)**: Install via `pip install -e .` and invoke tools globally via `emu8086` and `emu8086-tui`.
- **Extended Assembler Directives**: Support for `EQU` symbolic constants, `PROC`/`ENDP` procedure blocks, and resilient `ASSUME` pre-scanning.
- **Structured Error Reporting**: Clear, contextual `AssemblyError` messages pointing to offending lines and source tokens instead of silent exits.
- **Interactive Full-Screen TUI (`tui.py` & `main.py -t`)**: A terminal user interface designed for developers who love Neovim, GDB-TUI, and Claude Code. Features split-pane disassembly, real-time register & flag diff highlighting, live hardware telemetry, and an interactive memory hex inspector.
- **EMU8086 Virtual Traffic Light Hardware (I/O Port 4)**: 12-bit word controller driving 12 independent graphical LEDs (Red, Yellow, Green for North, West, South, East) with real-time terminal telemetry and standalone GUI visualizers.
- **EMU8086 Virtual Stepper Motor Hardware (I/O Port 7)**: 4-bit coil excitation sequencer ($11.25^\circ$ per step, 32 steps per revolution), ready flag polling on bit 7, rotating needle compass telemetry, and animated dial visualizer.
- **CGA 80x25 Text-Mode Video Memory Mirror (`0xB8000`)**: Continuous memory-mapped display buffer decoding character ASCII bytes and CGA color attribute nibbles.
- **Expanded BIOS & DOS Interrupt Services**:
  - `INT 10H` Video Services (AH=00h, 02h, 03h, 06h, 09h, 0Eh, 0Fh).
  - `INT 21H` DOS Services expanded with comprehensive file operations (AH=3Ch Create, 3Dh Open, 3Eh Close, 3Fh Read, 40h Write, 41h Delete).
- **Full English Translation & Codebase Cleanup**: Professional English comments, terminal logs, CLI prompts, and documentation across all modules.

---

## Features
- **Comprehensive Instruction Set**: Supports almost all standard Intel 8086 instructions and addressing modes.
- **MASM-Compatible Assembler**: Core MASM 5.0 directives under the Small memory model (`DB`, `DW`, `DD`, `DUP`, `ORG`, `ASSUME`, `SEGMENT...ENDS`).
- **Pipelined Architecture**: 2-stage pipeline dividing the Bus Interface Unit (BIU) and Execution Unit (EU) with a 6-byte instruction FIFO queue.
- **Full Register Support**: General purpose (AX, BX, CX, DX with AH/AL, BH/BL, CH/CL, DH/DL), Pointer & Index (SP, BP, SI, DI), Segment (CS, DS, SS, ES), Instruction Pointer (IP), and 9 Status/Control Flags (CF, ZF, SF, OF, PF, AF, IF, DF, TF).
- **Flexible Execution Interfaces**:
  1. **TUI Mode**: High-productivity terminal interface with keyboard-driven debugging.
  2. **CLI Mode**: Scriptable command-line runner with single-step debug prompts or non-interactive batch runs.
  3. **GUI Mode**: Rich desktop application built with PyQt5, featuring visual memory panes, code editor, and dedicated peripheral launch menus.
- **Extensive Test Suite**: Over 50 sample assembly programs covering sorting, searching, mathematical algorithms, string operations, interrupts, and I/O hardware peripherals.

---

## Running the Emulator

### 1. Interactive Terminal User Interface (TUI)
Launch the interactive full-screen debugger inside any standard terminal (including SSH, tmux, and Neovim terminal buffers):

```bash
# Direct TUI entry point
python3 tui.py ./tests/Requirement/bubble_sort.asm

# Or via main.py flag
python3 main.py ./tests/Requirement/bubble_sort.asm -t
```

#### TUI Layout & Panes
- **Disassembly Pane (`CS:IP`)**: Displays parsed assembly instructions with current instruction pointer (`▶`), breakpoints (`●`), and active line highlight.
- **CPU Registers & Flags**: Live 16-bit register values and high/low byte breakdowns. **Registers and flags that change during a step are highlighted in bright yellow.**
- **Virtual Hardware Telemetry**: Live status of Port 4 Traffic Lights, Port 7 Stepper Motor (with rotating compass needle), CGA 0xB8000 video buffer cursor, and console log.
- **Memory Inspector**: Real-time hex dump and ASCII decoding for `DS`, `CS`, `SS`, `ES`, or `VIDEO` (`0xB8000`) memory regions.

#### TUI Keybindings
| Key | Action |
|:---:|:---|
| `s` / `Space` / `Enter` | Single-step forward by one instruction |
| `c` | Continue running continuously |
| `p` | Pause continuous execution |
| `b` | Toggle breakpoint on the selected instruction |
| `Tab` | Switch active focus between **Disassembly** and **Memory Inspector** |
| `j` / `Down` | Move selection down (Disassembly) or scroll memory down (+16 bytes) |
| `k` / `Up` | Move selection up (Disassembly) or scroll memory up (-16 bytes) |
| `Page Down` / `Page Up` | Scroll memory by 128 bytes |
| `m` | Cycle memory segment (`DS` $\rightarrow$ `CS` $\rightarrow$ `SS` $\rightarrow$ `ES` $\rightarrow$ `VIDEO`) |
| `v` | Toggle Memory Inspector view mode (**Hex Dump** $\leftrightarrow$ **Stack View**) |
| `r` | Reset CPU and reload assembly program to initial state |
| `+` / `-` | Increase / decrease continuous execution speed |
| `?` / `h` | Display help tooltip |
| `q` | Cleanly exit TUI and restore terminal state |

---

### 2. Command-Line Interface (CLI)

```bash
# Run without interactive debug prompts (continuous run to completion)
python3 main.py ./tests/Requirement/bubble_sort.asm -n

# Run with detailed interrupt trace logging
python3 main.py ./tests/Interrupt/show_date_time.asm -i -n

# Run in interactive CLI single-step debug mode
python3 main.py ./tests/Requirement/bubble_sort.asm
```

#### CLI Debug Mode Commands
When paused in single-step debug mode, the following DOS `DEBUG`-style commands are supported:
- `A`: Interactively input and assemble a new instruction.
- `D [address]`: Dump memory hex and ASCII view starting from the specified address.
- `R`: Print all 16-bit register values and flag states.
- `Enter`: Step to the next instruction.
- `Q`: Terminate execution.

---

### 3. Graphical User Interface (GUI)

Launch the PyQt5 desktop environment:

```bash
python3 mainUI.py
```

![](image/mainUI.png)

#### GUI Controls & Features
- **File Menu**: Create new assembly files (`New`), open existing `.asm` files (`Open`), and save work (`Save`).
- **Execution Bar**:
  - `Load`: Assemble source code and load segments into memory.
  - `Run`: Continuously execute until breakpoint, interrupt, or program exit.
  - `Pause`: Asynchronously pause execution via Non-Maskable Interrupt (`NMI`).
  - `Step`: Single-step execute one instruction.
  - `Stop`: Halt CPU execution.
- **Virtual Devices Menu**: Open independent visualizer windows for **Traffic Lights (Port 4)**, **Stepper Motor (Port 7)**, and **Video Display (0xB8000)**.
- **Live Memory Tables**: Dedicated views for Stack (`SS:SP`), Code (`CS:IP`), and Data (`DS`) segments.

---

## Virtual Hardware Peripherals (EMU8086 Specification)

### 1. Traffic Lights (I/O Port 4)
Simulates a 4-way traffic intersection controller using a 12-bit word written via `OUT 4, AX` or `OUT 4, AL`.

```asm
; Example: Turn North Green ON (Bit 2), East Green ON (Bit 11)
MOV AX, 0000100000000100b
OUT 4, AX
```

#### Port 4 Bit Mapping
| Bits | Direction | Bit 0 / 3 / 6 / 9 | Bit 1 / 4 / 7 / 10 | Bit 2 / 5 / 8 / 11 |
|:---:|:---:|:---:|:---:|:---:|
| **0 – 2** | **North** (Top) | Red | Yellow | Green |
| **3 – 5** | **West** (Left) | Red | Yellow | Green |
| **6 – 8** | **South** (Bottom) | Red | Yellow | Green |
| **9 – 11** | **East** (Right) | Red | Yellow | Green |
| **12 – 15** | Reserved | Unused | Unused | Unused |

---

### 2. Stepper Motor (I/O Port 7)
Simulates a 4-coil unipolar stepper motor with 32 steps per $360^\circ$ rotation ($11.25^\circ$ per step).

```asm
; Check motor ready flag (Bit 7)
WAIT_READY:
    IN AL, 7
    TEST AL, 80h
    JZ WAIT_READY

; Energize coils A and B (Full-step forward)
MOV AL, 00000011b
OUT 7, AL
```

- **Output (`OUT 7, AL`)**: Lower 4 bits specify coil excitation `[D, C, B, A]`. Supports half-step (`01h`, `03h`, `02h`, `06h`, `04h`, `0Ch`, `08h`, `09h`), full-step (`03h`, `06h`, `0Ch`, `09h`), and wave-drive sequences in clockwise (CW) and counter-clockwise (CCW) directions.
- **Input (`IN AL, 7`)**: Bit 7 (`0x80`) returns `1` when the motor is ready for the next step command.

---

### 3. CGA 80x25 Text-Mode Video Display (`0xB8000`)
The emulator continuously monitors physical memory starting at `0xB8000`. Writing characters and attribute bytes directly to video RAM immediately updates the video display.
- **Even bytes**: ASCII character code.
- **Odd bytes**: CGA attribute byte (Low nibble: Foreground color 0–15, High nibble: Background color 0–7).

---

## Interrupt Handling & Vector Table

The interrupt architecture models the Intel 8259A Programmable Interrupt Controller (PIC) and standard 8086 Interrupt Vector Table (IVT).

![](image/interrupts.png)

### Interrupt Vector Table (IVT)
The IVT occupies physical memory `0000:0000` to `0000:03FF` (1,024 bytes, 256 vector slots). Each vector consists of a 2-byte segment and 2-byte offset pointing to the Interrupt Service Routine (ISR).

| Vector Type | Function | Default Address | Description |
|:---:|:---|:---:|:---|
| **00H** | Divide by Zero | `1000:0000` | Triggered by `DIV` or `IDIV` on quotient overflow or zero divisor |
| **01H** | Single Step | `1000:0100` | Handled when Trap Flag (`TF`) is set |
| **02H** | Non-Maskable Interrupt (NMI) | `1000:0200` | Asynchronous high-priority interrupt (used by GUI Pause) |
| **03H** | Breakpoint | `1000:0300` | Triggered by 1-byte opcode `INT 3` (`0xCC`) |
| **04H** | Overflow (`INTO`) | `1000:0400` | Triggered by `INTO` when Overflow Flag (`OF=1`) |
| **10H** | BIOS Video Services | System ISR | Screen modes, cursor control, character output |
| **21H** | DOS System Services | System ISR | I/O, system date/time, disk file APIs |
| **7CH** | User Custom Interrupt | User Defined | Custom ISR routines (e.g. uppercase string conversion) |

---

### BIOS Video Services (`INT 10H`)
| AH Function | Description | Parameters | Return Values |
|:---:|:---|:---|:---|
| **00H** | Set Video Mode | `AL` = Mode (e.g., `03H` for 80x25 color text) | None |
| **02H** | Set Cursor Position | `DH` = Row, `DL` = Column, `BH` = Page | None |
| **03H** | Get Cursor Position | `BH` = Page | `DH` = Row, `DL` = Column |
| **06H** | Scroll Window Up / Clear | `AL` = Lines, `BH` = Attribute | None |
| **09H** | Write Character & Attribute | `AL` = ASCII char, `BL` = Attribute, `CX` = Count | None |
| **0EH** | Teletype Character Output | `AL` = ASCII char | None |
| **0FH** | Get Video Mode | None | `AH` = Columns, `AL` = Mode |

---

### DOS System Services (`INT 21H`)
| AH Function | Description | Parameters | Return Values |
|:---:|:---|:---|:---|
| **00H** | Terminate Program | None | Returns control to emulator |
| **01H** | Keyboard Input with Echo | None | `AL` = Character read |
| **02H** | Display Character | `DL` = ASCII character | Character written to stdout/video |
| **09H** | Display String | `DS:DX` = Pointer to `$`-terminated string | String written to console |
| **2AH** | Get System Date | None | `CX` = Year, `DH:DL` = Month:Day |
| **2CH** | Get System Time | None | `CH:CL` = Hour:Minute, `DH:DL` = Second:1/100s |
| **35H** | Get Interrupt Vector | `AL` = Interrupt number | `ES:BX` = Pointer to ISR |
| **3CH** | Create File | `DS:DX` = Filename (ASCIIZ), `CX` = Attributes | `AX` = File Handle, `CF` = Error |
| **3DH** | Open File | `DS:DX` = Filename (ASCIIZ), `AL` = Access Mode | `AX` = File Handle, `CF` = Error |
| **3EH** | Close File | `BX` = File Handle | `AX` = 0, `CF` = Error |
| **3FH** | Read File | `BX` = File Handle, `CX` = Bytes to read, `DS:DX` = Buffer | `AX` = Bytes read, `CF` = Error |
| **40H** | Write File | `BX` = File Handle, `CX` = Bytes to write, `DS:DX` = Buffer | `AX` = Bytes written, `CF` = Error |
| **41H** | Delete File | `DS:DX` = Filename (ASCIIZ) | `CF` = Error flag |
| **4CH** | Exit with Return Code | `AL` = Return code | Halts CPU and returns exit code |

---

## Architecture & Data Path

The Intel 8086 is a true 16-bit microprocessor with a 20-bit address bus supporting 1MB of physical memory.

![](image/data_path.jpg)

### Addressing Modes
| Mode | Syntax | Effective Address (EA) | Default Segment | Example |
|:---|:---|:---|:---:|:---|
| **Immediate** | `Imm` | Operand in instruction | — | `MOV AX, 36` |
| **Register** | `Reg` | Stored in register | — | `INC AX` |
| **Direct** | `[Imm]` | `Imm` | `DS` | `MOV [1234H], AX` |
| **Register Indirect** | `[BX]` / `[BP]` / `[SI]` / `[DI]` | `(Reg)` | `DS` (or `SS` with `BP`) | `MOV [BX], AX` |
| **Based** | `[BX+Imm]` / `[BP+Imm]` | `(Base) + Imm` | `DS` (or `SS` with `BP`) | `MOV AL, [BX+20]` |
| **Indexed** | `[SI+Imm]` / `[DI+Imm]` | `(Index) + Imm` | `DS` | `MOV AH, [SI+2000]` |
| **Based Indexed** | `[BX+SI]` / `[BP+DI]` | `(Base) + (Index)` | `DS` (or `SS` with `BP`) | `MOV AX, [BX+DI]` |
| **Based Indexed with Displacement** | `[BX+DI+Imm]` | `(Base) + (Index) + Imm` | `DS` (or `SS` with `BP`) | `MOV AX, [BX+DI+4]` |

> **Segment Calculation**: `Physical Address = Segment x 16 + Offset`

---

## Instruction Set Matrix & Opcodes

The tables below describe the instruction encoding map:

#### Opcode Map (Part 1)
<table class="tg">
  <tr>
    <th class="tg-d5a7"></th>
    <th class="tg-p8s6">0</th>
    <th class="tg-p8s6">1</th>
    <th class="tg-p8s6">2</th>
    <th class="tg-p8s6">3</th>
    <th class="tg-p8s6">4</th>
    <th class="tg-p8s6">5</th>
    <th class="tg-p8s6">6</th>
    <th class="tg-p8s6">7</th>
  </tr>
  <tr>
    <td class="tg-o1j9">0</td>
    <td class="tg-8qro">ADD<br>Eb Gb</td>
    <td class="tg-b786">ADD<br>Ev Gv</td>
    <td class="tg-8qro">ADD<br>Gb Eb</td>
    <td class="tg-b786">ADD<br>Gv Ev</td>
    <td class="tg-8qro">ADD<br>AL Ib</td>
    <td class="tg-b786">ADD<br>AX Iv</td>
    <td class="tg-8qro">PUSH<br>ES</td>
    <td class="tg-b786">POP<br>ES</td>
  </tr>
  <tr>
    <td class="tg-o1j9">1</td>
    <td class="tg-8qro">ADC<br>Eb Gb</td>
    <td class="tg-b786">ADC<br>Ev Gv</td>
    <td class="tg-8qro">ADC<br>Gb Eb</td>
    <td class="tg-b786">ADC<br>Gv Ev</td>
    <td class="tg-8qro">ADC<br>AL Ib</td>
    <td class="tg-b786">ADC<br>AX Iv</td>
    <td class="tg-8qro">PUSH<br>SS</td>
    <td class="tg-b786">POP<br>SS</td>
  </tr>
  <tr>
    <td class="tg-o1j9">2</td>
    <td class="tg-8qro">AND<br>Eb Gb</td>
    <td class="tg-b786">AND<br>Ev Gv</td>
    <td class="tg-8qro">AND<br>Gb Eb</td>
    <td class="tg-b786">AND<br>Gv Ev</td>
    <td class="tg-8qro">AND<br>AL Ib</td>
    <td class="tg-b786">AND<br>AX Iv</td>
    <td class="tg-8qro">ES:</td>
    <td class="tg-b786">DAA</td>
  </tr>
  <tr>
    <td class="tg-o1j9">3</td>
    <td class="tg-8qro">XOR<br>Eb Gb</td>
    <td class="tg-b786">XOR<br>Ev Gv</td>
    <td class="tg-8qro">XOR<br>Gb Eb</td>
    <td class="tg-b786">XOR<br>Gv Ev</td>
    <td class="tg-8qro">XOR<br>AL Ib</td>
    <td class="tg-b786">XOR<br>AX Iv</td>
    <td class="tg-8qro">SS:</td>
    <td class="tg-b786">AAA</td>
  </tr>
  <tr>
    <td class="tg-o1j9">4</td>
    <td class="tg-8qro">INC<br>AX</td>
    <td class="tg-b786">INC<br>CX</td>
    <td class="tg-8qro">INC<br>DX</td>
    <td class="tg-b786">INC<br>BX</td>
    <td class="tg-8qro">INC<br>SP</td>
    <td class="tg-b786">INC<br>BP</td>
    <td class="tg-8qro">INC<br>SI</td>
    <td class="tg-b786">INC<br>DI</td>
  </tr>
  <tr>
    <td class="tg-o1j9">5</td>
    <td class="tg-8qro">PUSH<br>AX</td>
    <td class="tg-b786">PUSH<br>CX</td>
    <td class="tg-8qro">PUSH<br>DX</td>
    <td class="tg-b786">PUSH<br>BX</td>
    <td class="tg-8qro">PUSH<br>SP</td>
    <td class="tg-b786">PUSH<br>BP</td>
    <td class="tg-8qro">PUSH<br>SI</td>
    <td class="tg-b786">PUSH<br>DI</td>
  </tr>
  <tr>
    <td class="tg-o1j9">6</td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
  </tr>
  <tr>
    <td class="tg-o1j9">7</td>
    <td class="tg-8qro">JO<br>Jb</td>
    <td class="tg-b786">JNO<br>Jb</td>
    <td class="tg-8qro">JB<br>Jb</td>
    <td class="tg-b786">JNB<br>Jb</td>
    <td class="tg-8qro">JZ<br>Jb</td>
    <td class="tg-b786">JNZ<br>Jb</td>
    <td class="tg-8qro">JBE<br>Jb</td>
    <td class="tg-b786">JA<br>Jb</td>
  </tr>
  <tr>
    <td class="tg-o1j9">8</td>
    <td class="tg-l9cj">GRP1<br>Eb Ib</td>
    <td class="tg-spmh">GRP1<br>Ev Iv</td>
    <td class="tg-l9cj">GRP1<br>Eb Ib</td>
    <td class="tg-spmh">GRP1<br>Ev Ib</td>
    <td class="tg-8qro">TEST<br>Gb Eb</td>
    <td class="tg-b786">TEST<br>Gv Ev</td>
    <td class="tg-8qro">XCHG<br>Gb Eb</td>
    <td class="tg-b786">XCHG<br>Gv Ev</td>
  </tr>
  <tr>
    <td class="tg-o1j9">9</td>
    <td class="tg-8qro">NOP</td>
    <td class="tg-b786">XCHG<br>CX AX</td>
    <td class="tg-8qro">XCHG<br>DX AX</td>
    <td class="tg-b786">XCHG<br>BX AX</td>
    <td class="tg-8qro">XCHG<br>SP AX</td>
    <td class="tg-b786">XCHG<br>BP AX</td>
    <td class="tg-8qro">XCHG<br>SI AX</td>
    <td class="tg-b786">XCHG<br>DI AX</td>
  </tr>
  <tr>
    <td class="tg-o1j9">A</td>
    <td class="tg-8qro">MOV<br>AL Ob</td>
    <td class="tg-b786">MOV<br>AX Ov</td>
    <td class="tg-8qro">MOV<br>Ob AL</td>
    <td class="tg-b786">MOV<br>Ov AX</td>
    <td class="tg-8qro">MOV<br>SB</td>
    <td class="tg-b786">MOV<br>SW</td>
    <td class="tg-8qro">CMP<br>SB</td>
    <td class="tg-b786">CMP<br>SW</td>
  </tr>
  <tr>
    <td class="tg-o1j9">B</td>
    <td class="tg-8qro">MOV<br>AL Ib</td>
    <td class="tg-b786">MOV<br>CL Ib</td>
    <td class="tg-8qro">MOV<br>DL Ib</td>
    <td class="tg-b786">MOV<br>BL Ib</td>
    <td class="tg-8qro">MOV<br>AH Ib</td>
    <td class="tg-b786">MOV<br>CH Ib</td>
    <td class="tg-8qro">MOV<br>DH Ib</td>
    <td class="tg-b786">MOV<br>BH Ib</td>
  </tr>
  <tr>
    <td class="tg-o1j9">C</td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-8qro">RET<br>Iw</td>
    <td class="tg-b786">RET</td>
    <td class="tg-8qro">LES<br>Gv Mp</td>
    <td class="tg-b786">LDS<br>Gv Mp</td>
    <td class="tg-8qro">MOV<br>Eb Ib</td>
    <td class="tg-b786">MOV<br>Ev Iv</td>
  </tr>
  <tr>
    <td class="tg-o1j9">D</td>
    <td class="tg-l9cj">GRP2<br>Eb 1</td>
    <td class="tg-spmh">GRP2<br>Ev 1</td>
    <td class="tg-l9cj">GRP2<br>Eb CL</td>
    <td class="tg-spmh">GRP2<br>Ev CL</td>
    <td class="tg-8qro">AAM<br>I0</td>
    <td class="tg-b786">AAD<br>I0</td>
    <td class="tg-9d52"></td>
    <td class="tg-b786">XLAT</td>
  </tr>
  <tr>
    <td class="tg-o1j9">E</td>
    <td class="tg-8qro">LOOPNZ<br>Jb</td>
    <td class="tg-b786">LOOPZ<br>Jb</td>
    <td class="tg-8qro">LOOP<br>Jb</td>
    <td class="tg-b786">JCXZ<br>Jb</td>
    <td class="tg-8qro">IN<br>AL Ib</td>
    <td class="tg-b786">IN<br>AX Ib</td>
    <td class="tg-8qro">OUT<br>Ib AL</td>
    <td class="tg-b786">OUT<br>Ib AX</td>
  </tr>
  <tr>
    <td class="tg-o1j9">F</td>
    <td class="tg-8qro">LOCK</td>
    <td class="tg-o6ju"></td>
    <td class="tg-8qro">REPNZ</td>
    <td class="tg-b786">REPZ</td>
    <td class="tg-8qro">HLT</td>
    <td class="tg-b786">CMC</td>
    <td class="tg-l9cj">GRP3a<br>Eb</td>
    <td class="tg-spmh">GRP3b<br>Ev</td>
  </tr>
</table>

#### Opcode Map (Part 2)
<table class="tg">
  <tr>
    <th class="tg-xqy4"></th>
    <th class="tg-o1j9">8</th>
    <th class="tg-o1j9">9</th>
    <th class="tg-o1j9">A</th>
    <th class="tg-o1j9">B</th>
    <th class="tg-o1j9">C</th>
    <th class="tg-o1j9">D</th>
    <th class="tg-o1j9">E</th>
    <th class="tg-p8s6">F</th>
  </tr>
  <tr>
    <td class="tg-2em6">0</td>
    <td class="tg-8qro">OR<br>Eb Gb</td>
    <td class="tg-b786">OR<br>Ev Gv</td>
    <td class="tg-8qro">OR<br>Gb Eb</td>
    <td class="tg-b786">OR<br>Gv Ev</td>
    <td class="tg-8qro">OR<br>AL Ib</td>
    <td class="tg-b786">OR<br>AX Iv</td>
    <td class="tg-8qro">PUSH<br>CS</td>
    <td class="tg-o6ju"></td>
  </tr>
  <tr>
    <td class="tg-2em6">1</td>
    <td class="tg-8qro">SBB<br>Eb Gb</td>
    <td class="tg-b786">SBB<br>Ev Gv</td>
    <td class="tg-8qro">SBB<br>Gb Eb</td>
    <td class="tg-b786">SBB<br>Gv Ev</td>
    <td class="tg-8qro">SBB<br>AL Ib</td>
    <td class="tg-b786">SBB<br>AX Iv</td>
    <td class="tg-8qro">PUSH<br>DS</td>
    <td class="tg-b786">POP<br>DS</td>
  </tr>
  <tr>
    <td class="tg-2em6">2</td>
    <td class="tg-8qro">SUB<br>Eb Gb</td>
    <td class="tg-b786">SUB<br>Ev Gv</td>
    <td class="tg-8qro">SUB<br>Gb Eb</td>
    <td class="tg-b786">SUB<br>Gv Ev</td>
    <td class="tg-8qro">SUB<br>AL Ib</td>
    <td class="tg-b786">SUB<br>AX Iv</td>
    <td class="tg-8qro">CS:</td>
    <td class="tg-b786">DAS</td>
  </tr>
  <tr>
    <td class="tg-2em6">3</td>
    <td class="tg-8qro">CMP<br>Eb Gb</td>
    <td class="tg-b786">CMP<br>Ev Gv</td>
    <td class="tg-8qro">CMP<br>Gb Eb</td>
    <td class="tg-b786">CMP<br>Gv Ev</td>
    <td class="tg-8qro">CMP<br>AL Ib</td>
    <td class="tg-b786">CMP<br>AX Iv</td>
    <td class="tg-8qro">DS:</td>
    <td class="tg-b786">AAS</td>
  </tr>
  <tr>
    <td class="tg-2em6">4</td>
    <td class="tg-8qro">DEC<br>AX</td>
    <td class="tg-b786">DEC<br>CX</td>
    <td class="tg-8qro">DEC<br>DX</td>
    <td class="tg-b786">DEC<br>BX</td>
    <td class="tg-8qro">DEC<br>SP</td>
    <td class="tg-b786">DEC<br>BP</td>
    <td class="tg-8qro">DEC<br>SI</td>
    <td class="tg-b786">DEC<br>DI</td>
  </tr>
  <tr>
    <td class="tg-2em6">5</td>
    <td class="tg-8qro">POP<br>AX</td>
    <td class="tg-b786">POP<br>CX</td>
    <td class="tg-8qro">POP<br>DX</td>
    <td class="tg-b786">POP<br>BX</td>
    <td class="tg-8qro">POP<br>SP</td>
    <td class="tg-b786">POP<br>BP</td>
    <td class="tg-8qro">POP<br>SI</td>
    <td class="tg-b786">POP<br>DI</td>
  </tr>
  <tr>
    <td class="tg-2em6">6</td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
  </tr>
  <tr>
    <td class="tg-2em6">7</td>
    <td class="tg-8qro">JS<br>Jb</td>
    <td class="tg-b786">JNS<br>Jb</td>
    <td class="tg-8qro">JPE<br>Jb</td>
    <td class="tg-b786">JPO<br>Jb</td>
    <td class="tg-8qro">JL<br>Jb</td>
    <td class="tg-b786">JGE<br>Jb</td>
    <td class="tg-8qro">JLE<br>Jb</td>
    <td class="tg-b786">JG<br>Jb</td>
  </tr>
  <tr>
    <td class="tg-2em6">8</td>
    <td class="tg-8qro">MOV<br>Eb Gb</td>
    <td class="tg-b786">MOV<br>Ev Gv</td>
    <td class="tg-8qro">MOV<br>Gb Eb</td>
    <td class="tg-b786">MOV<br>Gv Ev</td>
    <td class="tg-8qro">MOV<br>Ew Sw</td>
    <td class="tg-b786">LEA<br>Gv M</td>
    <td class="tg-8qro">MOV<br>Sw Ew</td>
    <td class="tg-b786">POP<br>Ev</td>
  </tr>
  <tr>
    <td class="tg-2em6">9</td>
    <td class="tg-8qro">CBW</td>
    <td class="tg-b786">CWD</td>
    <td class="tg-8qro">CALL<br>Ap</td>
    <td class="tg-b786">WAIT</td>
    <td class="tg-8qro">PUSHF</td>
    <td class="tg-b786">POPF</td>
    <td class="tg-8qro">SAHF</td>
    <td class="tg-b786">LAHF</td>
  </tr>
  <tr>
    <td class="tg-2em6">A</td>
    <td class="tg-8qro">TEST<br>AL Ib</td>
    <td class="tg-b786">TEST<br>AX Iv</td>
    <td class="tg-8qro">STOSB</td>
    <td class="tg-b786">STOSW</td>
    <td class="tg-8qro">LODSB</td>
    <td class="tg-b786">LODSW</td>
    <td class="tg-8qro">SCASB</td>
    <td class="tg-b786">SCASW</td>
  </tr>
  <tr>
    <td class="tg-2em6">B</td>
    <td class="tg-8qro">MOV<br>AX Iv</td>
    <td class="tg-b786">MOV<br>CX Iv</td>
    <td class="tg-8qro">MOV<br>DX Iv</td>
    <td class="tg-b786">MOV<br>BX Iv</td>
    <td class="tg-8qro">MOV<br>SP Iv</td>
    <td class="tg-b786">MOV<br>BP Iv</td>
    <td class="tg-8qro">MOV<br>SI Iv</td>
    <td class="tg-b786">MOV<br>DI Iv</td>
  </tr>
  <tr>
    <td class="tg-2em6">C</td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-8qro">RETF<br>Iw</td>
    <td class="tg-b786">RETF</td>
    <td class="tg-8qro">INT<br>3</td>
    <td class="tg-b786">INT<br>Ib</td>
    <td class="tg-8qro">INTO</td>
    <td class="tg-b786">IRET</td>
  </tr>
  <tr>
    <td class="tg-2em6">D</td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
    <td class="tg-9d52"></td>
    <td class="tg-o6ju"></td>
  </tr>
  <tr>
    <td class="tg-2em6">E</td>
    <td class="tg-8qro">CALL<br>Jv</td>
    <td class="tg-b786">JMP<br>Jv</td>
    <td class="tg-8qro">JMP<br>Ap</td>
    <td class="tg-b786">JMP<br>Jb</td>
    <td class="tg-8qro">IN<br>AL DX</td>
    <td class="tg-b786">IN<br>AX DX</td>
    <td class="tg-8qro">OUT<br>DX AL</td>
    <td class="tg-b786">OUT<br>DX AX</td>
  </tr>
  <tr>
    <td class="tg-2em6">F</td>
    <td class="tg-8qro">CLC</td>
    <td class="tg-b786">STC</td>
    <td class="tg-8qro">CLI</td>
    <td class="tg-b786">STI</td>
    <td class="tg-8qro">CLD</td>
    <td class="tg-b786">STD</td>
    <td class="tg-l9cj">GRP4<br>Eb</td>
    <td class="tg-spmh">GRP5<br>Ev</td>
  </tr>
</table>

---

## Assembler & Directives

The built-in assembler compiles standard MASM assembly files using the Small memory model (all code resides in a single 64KB code segment, data/stack resides in independent segments).

| Directive | Description | Example |
|:---:|:---|:---|
| `DB` | Define Byte (8-bit value, string, or ASCII char) | `DB 'Hello, World!$'` |
| `DW` | Define Word (16-bit word, stored little-endian) | `DW 0123H, 0FFFFH` |
| `DD` | Define Doubleword (32-bit dword) | `DD 12345678H` |
| `DUP` | Duplicate pattern in memory | `DB 10 DUP(0)` |
| `ORG` | Set starting address offset | `ORG 100H` |
| `ASSUME` | Associate segment registers with named segments | `ASSUME CS:CODE, DS:DATA` |
| `SEGMENT...ENDS` | Delimit a memory segment | `DATA SEGMENT ... DATA ENDS` |
| `PTR` | Specify operand size (`BYTE PTR`, `WORD PTR`) | `MOV BYTE PTR [BX], 0` |
| `END` | Mark the end of an assembly source file | `END START` |

---

## Automated Test Suite

Run the full automated test suite (including unit tests for virtual peripherals, interrupts, and TUI):

```bash
python3 -m unittest discover tests
```

### Sample Assembly Programs
- `tests/Requirement/bubble_sort.asm`: In-place bubble sort algorithm with step verification.
- `tests/Requirement/fibonacci.asm`: Fibonacci sequence generator.
- `tests/Inout/traffic_lights_test.asm`: EMU8086 4-way traffic light intersection cycling sequence.
- `tests/Inout/stepper_motor_test.asm`: EMU8086 stepper motor multi-phase clockwise/counter-clockwise rotation.
- `tests/Interrupt/video_text_mode_test.asm`: Direct video RAM writing to `0xB8000` text mode buffer.
- `tests/Interrupt/show_date_time.asm`: BIOS & DOS system date and time query routines.

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
