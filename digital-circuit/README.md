# Intel 8086 Complete Pure Digital Logic Circuit & System Workbench

A 100% authentic, gate-level digital logic implementation of the **Intel 8086 microprocessor** and its complete microcomputer system board built for **[Helmut Neemann's Digital](https://github.com/hneemann/Digital)** digital logic simulator.

Every single component—from the 1-bit ALU adder slices, dual-port register file, status flags logic, and 20-bit physical address adder, up to the 8284A clock generator, 8282 transparent latches, 8286 transceivers, 74LS138 address decoder, dual-bank RAM, 2764 boot ROM, and DIP-40 CPU package—is constructed out of pure digital logic gates, multiplexers, and flip-flops without any black-box shortcuts.

---

## 1. System Architecture Hierarchy

The circuit design is structured into 17 interconnected `.dig` circuits:

```
                            ┌──────────────────────────────────────────────┐
                            │          i8086_system_board.dig              │
                            │      Complete Microcomputer Motherboard      │
                            └──────────────────────┬───────────────────────┘
                                                   │
        ┌───────────────────┬──────────────────────┼───────────────────────┬────────────────────┐
        │                   │                      │                       │                    │
        ▼                   ▼                      ▼                       ▼                    ▼
┌──────────────┐    ┌──────────────┐     ┌───────────────────┐     ┌──────────────┐     ┌──────────────┐
│ clock_gen_   │    │address_      │     │   i8086_cpu.dig   │     │data_         │     │address_      │
│  8284.dig    │    │ latches_     │     │Intel 8086 CPU DIP4│     │ transceivers_│     │ decoder_     │
│(8284A Clock) │    │  8282.dig    │     └─────────┬─────────┘     │  8286.dig    │     │  74ls138.dig │
└──────────────┘    │ (8282 / 373) │               │               │ (8286 / 245) │     │ (74LS138)    │
                    └──────────────┘               │               └──────────────┘     └───────┬──────┘
                                                   │                                            │
                                ┌──────────────────┴──────────────────┐                 ┌───────┴──────┐
                                │                                     │                 │              │
                                ▼                                     ▼                 ▼              ▼
                     ┌─────────────────────┐               ┌─────────────────────┐┌───────────┐ ┌───────────┐
                     │Bus Interface Unit   │               │Execution Unit (EU)  ││ram_16bit. │ │boot_rom_  │
                     │(BIU) Subcircuits    │               │Subcircuits          ││   dig     │ │  2764.dig │
                     └──────────┬──────────┘               └──────────┬──────────┘│ Dual-Bank │ │Reset Vector│
                                │                                     │           │ 16-bit RAM│ │ 0xFFFF0 ROM│
          ┌─────────────────────┼────────────────────┐                │           └───────────┘ └───────────┘
          │                     │                    │                │
          ▼                     ▼                    ▼                │
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│segment_registers.│  │instruction_      │  │address_adder_    │      │
│      dig         │  │ pointer.dig      │  │   20bit.dig      │      │
│CS, DS, SS, ES    │  │16-bit IP Register│  │PhysAddr =        │      │
│+ 4:1 Mux & Shift │  │+1 / +2 Increment │  │ Base20 + Offset16│      │
└──────────────────┘  └──────────────────┘  └──────────────────┘      │
                                                                      │
                         ┌────────────────────────────────────────────┴──────────────────────────┐
                         │                                     │                                 │
                         ▼                                     ▼                                 ▼
              ┌─────────────────────┐               ┌─────────────────────┐           ┌─────────────────────┐
              │  register_file.dig  │               │    alu_16bit.dig    │           │ flags_register.dig  │
              │Dual-Port 8x16-Bit   │               │16-Bit Parallel ALU  │           │16-Bit Status Flags  │
              │AX,CX,DX,BX,SP,BP,SI │               │16x alu_slice.dig    │           │CF,PF,AF,ZF,SF,OF    │
              │Byte Write Masking   │               └──────────┬──────────┘           │TF, IF, DF Registers │
              └─────────────────────┘                          │                      └─────────────────────┘
                                                               ▼
                                                    ┌─────────────────────┐
                                                    │    alu_slice.dig    │
                                                    │1-Bit Full Adder ALU │
                                                    │Logic Gates & Mux    │
                                                    └─────────────────────┘
```

---

## 2. Component Specifications

| Circuit File | Type | Digital Logic Function |
|---|---|---|
| [`alu_slice.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/alu_slice.dig) | Gate Bit-Slice | 1-bit ALU Full Adder slice using XOR, AND, OR, NOT gates and an 8:1 Multiplexer. Supports ADD, SUB, AND, OR, XOR, NOT. |
| [`alu_16bit.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/alu_16bit.dig) | Arithmetic Unit | 16-bit ripple adder ALU chaining 16 `alu_slice.dig` instances. Computes all standard 8086 status flags: CF, ZF, SF, OF ($C_{14} \oplus C_{15}$), PF (even parity tree on low byte), and AF (auxiliary carry $C_4$). |
| [`register_file.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/register_file.dig) | Storage Unit | Dual-port 16-bit register file (AX, CX, DX, BX, SP, BP, SI, DI) with byte-level write enables (`WrHigh`, `WrLow`). |
| [`segment_registers.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/segment_registers.dig) | Storage Unit | 4x 16-bit segment registers (CS, DS, SS, ES), 4:1 multiplexer, and hardwired 4-bit left shifter (`Base20 = Seg << 4`). |
| [`instruction_pointer.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/instruction_pointer.dig) | Counter / Pointer | 16-bit IP register with +1 byte incrementer, +2 word incrementer, parallel load (JMP/CALL), and reset vector logic. |
| [`address_adder_20bit.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/address_adder_20bit.dig) | Arithmetic Unit | Dedicated 20-bit asynchronous address adder calculating $\text{Physical Address}[19:0] = \text{Base20}[19:0] + \text{Offset16}[15:0]$. |
| [`flags_register.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/flags_register.dig) | Status / Control | 16-bit status & control register capturing CF, PF, AF, ZF, SF, OF, TF, IF, DF with standard 8086 flag word encoding. |
| [`queue_6byte.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/queue_6byte.dig) | Prefetch FIFO | 6-byte instruction FIFO queue with up/down occupancy counter, push/pop control, and flush on branch. |
| [`clock_gen_8284.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/clock_gen_8284.dig) | Clock & Reset | Intel 8284A clock generator with /3 frequency divider (33% duty cycle CLK), power-on Schmitt reset, and READY synchronizer. |
| [`address_latches_8282.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/address_latches_8282.dig) | Bus Interface | 3x 8282 / 74LS373 transparent octal latches demultiplexing AD15..AD0 and A19..A16 on ALE falling edge into stable 20-bit address bus A19..A0. |
| [`data_transceivers_8286.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/data_transceivers_8286.dig) | Bus Interface | 2x 8286 / 74LS245 bidirectional octal bus transceivers controlled by DT/R# and DEN#. |
| [`address_decoder_74ls138.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/address_decoder_74ls138.dig) | Bus Interface | 74LS138 3-to-8 decoder decoding A19..A16 and M/IO# into chip selects: `CS_RAM0_N` (0x0xxxx), `CS_RAM1_N` (0x1..0x7xxxx), `CS_VIDEO_N` (0xBxxxx), and `CS_ROM_N` (0xFxxxx). |
| [`ram_16bit.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/ram_16bit.dig) | Memory | 16-bit dual-bank RAM organized as Even Bank (D7..D0, enabled by A0=0) and Odd Bank (D15..D8, enabled by BHE#=0). |
| [`boot_rom_2764.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/boot_rom_2764.dig) | Memory | 2764 ROM mapped to 0xFFFF0 reset vector containing `EA 00 01 00 12` (`JMP FAR 1200:0100`). |
| [`instruction_decoder.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/instruction_decoder.dig) | Control Circuit | Instruction opcode decoder generating ALU operation selectors, register write enables, and conditional branch evaluations. |
| [`i8086_cpu.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/i8086_cpu.dig) | Microprocessor | Complete Intel 8086 DIP-40 package integrating BIU and EU pipelines, T-states timing generator, and pin mapping. |
| [`i8086_system_board.dig`](file:///home/sami/Documents/GitHub/8086-emulator/digital-circuit/i8086_system_board.dig) | Motherboard System | Top-level microcomputer system motherboard linking CPU, clock generator, latches, transceivers, address decoder, RAM, ROM, and telemetry LEDs. |

---

## 3. How to Launch and Explore

### Launch Interactive GUI
To open the complete system board in Helmut Neemann's *Digital* simulator:
```bash
./bin/emu8086-digital
```
Or open any specific subcircuit directly:
```bash
# Open 16-bit ALU gate schematic
./bin/emu8086-digital digital-circuit/alu_16bit.dig

# Open dual-port Register File
./bin/emu8086-digital digital-circuit/register_file.dig

# Open complete Intel 8086 DIP-40 CPU package
./bin/emu8086-digital digital-circuit/i8086_cpu.dig
```

### Navigating Down to Gate Level in Digital
1. **Semantic Zoom & Subcircuit Exploration**:
   - Double-click (or `Ctrl + double-click`) any subcircuit block (e.g. `i8086_cpu.dig`, `alu_16bit.dig`, or `register_file.dig`) to drill down directly into its internal schematic.
   - Inside `alu_16bit.dig`, double-click any of the 16 `alu_slice.dig` instances to view the raw XOR, AND, OR, NOT gates and multiplexers.
2. **Interactive Simulation**:
   - Press **Play (`F5` or Spacebar)** to start real-time simulation.
   - Click the Clock or press **`C`** to single-step clock cycles.
   - Probe any wire to observe live binary / hexadecimal values and signal transitions.
   - Status LEDs visually indicate bus strobe timing: `ALE_Strobe`, `RD_Read`, `WR_Write`, `M_IO_Select`, and `CPU_Reset`.

---

## 4. Automated Verification & Test Suite

All 17 circuits are validated via embedded truth table test cases and automated unit tests.

### Run Full Python Test Suite
```bash
python3 -m unittest discover tests
```
*Current test count: 117 tests (all passing).*

### Run Standalone Digital CLI Test Vectors
```bash
# Test 16-bit ALU operations and flags
java -jar digital-circuit/bin/Digital/Digital.jar CLI test -circ digital-circuit/alu_16bit.dig

# Test dual-port Register File
java -jar digital-circuit/bin/Digital/Digital.jar CLI test -circ digital-circuit/register_file.dig

# Test 16-bit Dual-Bank RAM
java -jar digital-circuit/bin/Digital/Digital.jar CLI test -circ digital-circuit/ram_16bit.dig

# Test 2764 Boot ROM
java -jar digital-circuit/bin/Digital/Digital.jar CLI test -circ digital-circuit/boot_rom_2764.dig
```
