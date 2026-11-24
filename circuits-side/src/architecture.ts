/* 8086 Microprocessor & System Board Architecture Workbench
   Complete Silicon Die & System Board Inspection Scope
   100% Interconnected Gate-Level, Transistor-Level & Bus Wiring */
(() => {
  const { R, P, dot, getComponentLogic } = logicDraw;


  // Exact coordinates [x, y, w, h, title, group] for all 34 internal & external components
  const spec: Record<string, Workbench.UnitBox> = {
    // === EXECUTION UNIT (EU) ===
    regs: [40, 60, 480, 240, "16-BIT DUAL-PORT REGISTER FILE (AX, BX, CX, DX, SP, BP, SI, DI)", "EU"],
    internal: [40, 340, 480, 170, "16-BIT INTERNAL DATA BUS & CROSSBAR TAPS", "EU"],
    temps: [40, 550, 480, 200, "OPERAND TEMPORARY LATCHES (tmpA, tmpB, tmpC)", "EU"],
    aluctl: [40, 800, 230, 210, "ALU CONTROL DECODER & OPERATION SELECTOR", "EU"],
    mux: [285, 800, 235, 210, "ALU INPUT MULTIPLEXER (3-TO-1)", "EU"],
    alu: [40, 1060, 480, 240, "ARITHMETIC LOGIC UNIT · 16-BIT ADDER/LOGIC SLICE", "EU"],
    flags: [40, 1350, 480, 220, "STATUS & CONTROL FLAGS REGISTER (CF, PF, AF, ZF, SF, OF, TF, IF, DF)", "EU"],

    // === BUS INTERFACE UNIT (BIU) ===
    seg: [620, 60, 420, 220, "16-BIT SEGMENT BASE REGISTERS (CS, DS, SS, ES)", "BIU"],
    ip: [1080, 60, 430, 220, "INSTRUCTION POINTER (IP) & HARDWIRED +1/+2 INCREMENTER", "BIU"],
    segmux: [620, 330, 420, 180, "SEGMENT SELECTOR MULTIPLEXER (4:1) & SHIFTER", "BIU"],
    ind: [1080, 330, 430, 180, "INDIRECT OFFSET REGISTER (IND / EFFECTIVE ADDRESS LATCH)", "BIU"],
    adder: [620, 560, 420, 210, "BIU DEDICATED 20-BIT PHYSICAL ADDRESS ADDER (Seg*16 + Off)", "BIU"],
    offmux: [1080, 560, 430, 200, "OFFSET SELECTOR MULTIPLEXER (2:1)", "BIU"],
    opr: [620, 810, 420, 210, "OPERAND BUS DATA LATCH & TRANSCEIVER (OPR)", "BIU"],
    queue: [1080, 810, 430, 210, "6-BYTE INSTRUCTION PREFETCH QUEUE (FIFO)", "BIU"],
    memory: [620, 1060, 420, 240, "BUS CONTROLLER & T-STATE TIMING ENGINE (T1..T4, ALE, RD, WR)", "BIU"],
    ext: [1080, 1060, 430, 270, "INTEL 8086 SILICON I/O & ESD PROTECTION CELL (AD15..AD0 MUX BUS)", "BIU"],

    // === CONTROL UNIT (CU) ===
    loader: [40, 1640, 450, 200, "INSTRUCTION BYTE LOADER & MODR/M INPUT LATCH", "CU"],
    ir: [530, 1640, 450, 200, "INSTRUCTION REGISTER (8-BIT IR OPCODE LATCH)", "CU"],
    prefix: [1020, 1640, 480, 200, "PREFIX RECOGNITION & SEGMENT OVERRIDE LATCH", "CU"],
    pla: [40, 1880, 450, 200, "GROUP DECODE ROM / INSTRUCTION CLASSIFICATION PLA", "CU"],
    trom: [530, 1880, 450, 200, "TRANSLATION ROM (TROM) / EA DISPATCH MATRIX", "CU"],
    engine: [1020, 1880, 480, 200, "MICROCODE SEQUENCING ENGINE & RETURN STACK", "CU"],
    mar: [40, 2120, 450, 190, "MICROCODE ADDRESS REGISTER (MAR / SEQUENCE COUNTER)", "CU"],
    rom: [530, 2120, 450, 190, "MICROCODE CONTROL STORE ROM (512 WORDS × 21 BITS)", "CU"],
    ctl: [1020, 2120, 480, 190, "CONTROL SIGNAL LATCHES & LOCAL EU/BIU DECODERS", "CU"],
    clk: [40, 2350, 450, 190, "8284A CLOCK GENERATOR (15 MHz CRYSTAL & /3 DIVIDER)", "SYS"],
    seq: [530, 2350, 450, 190, "CLOCK PHASE SEQUENCER (JK FLIP-FLOP COUNTER)", "CU"],
    dec: [1020, 2350, 480, 190, "CONTROL ENABLE MATRIX (4-TO-16 ROW DECODER & OR GATES)", "CU"],

    // === SYSTEM HARDWARE BOARD (SYS) ===
    latches: [1590, 60, 500, 240, "8282 / 74LS373 ADDRESS DEMUX LATCHES (x3 OCTAL D-LATCHES)", "SYS"],
    transceivers: [2130, 60, 500, 240, "8286 / 74LS245 DATA BUS TRANSCEIVERS (x2 OCTAL BIDIRECTIONAL)", "SYS"],
    decoder: [1590, 330, 500, 220, "74LS138 SYSTEM ADDRESS DECODER (A19..A16 CHIP SELECTS)", "SYS"],
    bootrom: [2130, 330, 500, 220, "2764 BOOT EPROM (RESET VECTOR AT 0xFFFF0 / JMP FAR 1200:0100)", "SYS"],
    ram: [1590, 590, 1040, 290, "SYSTEM STATIC RAM (16-BIT: 512KB EVEN + 512KB ODD + 6T CMOS CELL)", "SYS"],
  };

  const N: Record<string, Workbench.UnitBox> = {};
  for (const [id, [x, y, w, h, title, group]] of Object.entries(spec)) {
    N[id] = [Math.round(x * 1.3), Math.round(y * 1.25), w, h, title, group];
  }

  const W = Math.max(...Object.values(N).map(box => box[0] + box[2])) + 48;
  const H = Math.max(...Object.values(N).map(box => box[1] + box[3])) + 48;

  const info: Workbench.Board["info"] = {
    regs: [
      "16-bit Register File",
      "Eight general/index registers (AX, BX, CX, DX, SP, BP, SI, DI). AX..DX split into independent high/low 8-bit registers (AH/AL, BH/BL, CH/CL, DH/DL). Built from dual-port D-flip-flops with read/write port enables.",
      "AX = AH × 256 + AL",
    ],
    internal: [
      "16-bit Internal Data Bus",
      "Central synchronous EU bus with tri-state crossbar connections. Delivers operands from registers to temporary latches, returns ALU results on writeback, and routes displacement words from the prefetch queue.",
      "16-bit data bus = D[15:0]",
    ],
    temps: [
      "Operand Latches (tmpA, tmpB, tmpC)",
      "Dedicated 16-bit intermediate operand registers. tmpA and tmpC feed input multiplexer for first ALU operand; tmpB directly feeds the second ALU operand. tmpC captures effective address displacement.",
      "tmpA, tmpB, tmpC → ALU MUX",
    ],
    aluctl: [
      "ALU Control Decode",
      "Decodes 5-bit ALU micro-operation code and IR opcode into ALU function lines (ADD, SUB, AND, OR, XOR, Invert B, Carry-in). Subtraction sets Carry-in to 1 and inverts operand B: A - B = A + ~B + 1.",
      "A − B = A + ¬B + 1",
    ],
    mux: [
      "ALU Input Multiplexer",
      "16-bit 3-to-1 multiplexer steering tmpA, tmpB, or tmpC into the first ALU input port based on microcode select lines SEL[1:0].",
      "SEL[1:0] → ALU_A[15:0]",
    ],
    alu: [
      "16-bit Arithmetic Logic Unit",
      "16-bit parallel ALU composed of full adder bit-slices. Propagate (P = A ⊕ B) and Generate (G = A · B) logic calculate carry-lookahead across each nibble. Outputs 16-bit result and 6 status signals to FLAGS register.",
      "Cᵢ₊₁ = Gᵢ + Pᵢ·Cᵢ",
    ],
    flags: [
      "Status & Control Flags Register",
      "Contains 6 arithmetic status flags (CF, PF, AF, ZF, SF, OF) and 3 control flags (TF, IF, DF). ZF evaluated via 16-input NOR zero-detector; PF evaluated via lower-byte parity tree; OF evaluated via C14 ⊕ C15.",
      "ZF = ¬(R15 ∨ … ∨ R0) · OF = C14 ⊕ C15",
    ],
    seg: [
      "16-bit Segment Registers",
      "Four 16-bit segment base registers: CS (Code), DS (Data), SS (Stack), ES (Extra). Holds high 16 bits of 20-bit memory base addresses. Shifting left by 4 places multiplies segment by 16.",
      "Base[19:0] = Segment[15:0] × 16",
    ],
    ip: [
      "Instruction Pointer & Incrementer",
      "Maintains the 16-bit offset of the next instruction word to prefetch into the FIFO queue. Connected to hardwired fast +1/+2 adder incrementer that automatically advances IP during prefetch bus cycles.",
      "Physical Fetch = (CS × 16 + IP) mod 2²⁰",
    ],
    ind: [
      "Indirect Offset Register (IND)",
      "Captures the 16-bit effective address (EA) computed by the EU for memory operands (e.g., [BP+SI+disp8]). Feeds the offset input of the BIU dedicated address adder.",
      "IND ← (BP + SI + disp) mod 2¹⁶",
    ],
    segmux: [
      "Segment Selector Multiplexer",
      "4-to-1 multiplexer choosing CS during instruction fetches, SS for stack/BP references, DS for data references, or ES when a 26h segment override prefix is latched.",
      "CS / DS / SS / ES → Base << 4",
    ],
    offmux: [
      "Offset Selector Multiplexer",
      "2-to-1 multiplexer choosing the BIU fetch offset (IP) during code prefetch cycles, or the indirect operand offset (IND) during memory data read/write cycles.",
      "IP (fetch) / IND (data) → Adder",
    ],
    adder: [
      "BIU 20-bit Dedicated Address Adder",
      "Hardware 20-bit parallel adder operating in parallel with the EU. Adds shifted 20-bit segment base to 16-bit offset to produce physical addresses (00000h..FFFFFh) on the 1MB bus.",
      "Address = (Segment × 16 + Offset) mod 2²⁰",
    ],
    opr: [
      "Operand Bus Transceiver (OPR)",
      "Bidirectional 16-bit data latch interfacing the external memory bus with the EU internal data bus during memory read and write cycles. Controlled by DT/R# and DEN#.",
      "OPR = High Byte × 256 + Low Byte",
    ],
    memory: [
      "Bus Controller & T-State Machine",
      "Hardware state machine generating 8086 bus timing states (T1 address phase, T2 status phase, T3 data/wait phase, T4 latch phase). Controls ALE, RD#, WR#, M/IO#, DEN#, DT/R#.",
      "T1 (Addr) → T2 (Status) → T3 (Data) → T4",
    ],
    ext: [
      "Intel 8086 Silicon I/O & ESD Protection Cell",
      "Authentic HMOS II on-chip ESD (Electrostatic Discharge) protection network and bidirectional I/O cell. Each I/O pin features dual clamping diodes (D_VCC and D_GND) to shunt voltage spikes into power rails, a Grounded-Gate NMOS snapback clamp for 2kV human-body-model static strikes, a 300Ω polysilicon ballast resistor, a secondary oxide clamp, a Schmitt trigger input buffer with hysteresis, and a tri-state output driver.",
      "VCC = +5V · GND = 0V · Clamp Window: -0.7V to +5.7V",
    ],
    queue: [
      "6-Byte Instruction Prefetch Queue",
      "Three 16-bit prefetch FIFO registers storing up to six instruction bytes. BIU fills the queue in the background whenever two or more bytes are empty; loader consumes bytes oldest-first.",
      "3 words × 2 bytes = 6 bytes FIFO",
    ],
    loader: [
      "Instruction Loader & Input Latches",
      "Pulls bytes from the prefetch queue, separates prefixes, latches opcodes into IR, and decodes the ModR/M addressing mode byte into register/memory displacement fields.",
      "ModR/M = mod[7:6] | reg[5:3] | r/m[2:0]",
    ],
    ir: [
      "Instruction Register (8-bit IR)",
      "Latches the current machine instruction opcode during execution. Directly drives the group decode PLA and microcode entry jump logic.",
      "IR[7:0] = Opcode",
    ],
    prefix: [
      "Prefix Latch",
      "Latches instruction prefixes such as segment overrides (26h ES, 2Eh CS, 36h SS, 3Eh DS), LOCK (F0h), and REPEAT (F2h/F3h) to modify bus routing for the next instruction.",
      "26h → ES Segment Override Valid",
    ],
    pla: [
      "Group Decode ROM / PLA",
      "AND/OR matrix classifying opcodes into 15 functional categories. Guides instruction loading, immediate operand sizing, and microcode entry routine selection.",
      "Opcode[7:0] → Instruction Class Signals",
    ],
    trom: [
      "Translation ROM (TROM)",
      "Translates ModR/M addressing mode bits (mod[1:0] + r/m[2:0]) and opcode dispatch tags into 13-bit microcode branch target addresses.",
      "mod + r/m → Target Micro-Address",
    ],
    engine: [
      "Microcode Sequencing Engine",
      "Determines the next microinstruction address. Supports sequential execution, conditional jumps based on status flags, subroutine calls, and return via a 13-bit return register.",
      "Next µAddress = Entry / Next / Branch / Return",
    ],
    mar: [
      "Microcode Address Register (MAR)",
      "Holds the 13-bit physical microcode address (9-bit block selector + 4-bit sequence counter). Directly selects a 21-bit microinstruction word from the control store ROM.",
      "9 block bits + 4 sequence bits = 13 bits",
    ],
    rom: [
      "Microcode Control Store ROM",
      "On-chip ROM containing 512 words of 21-bit microinstructions (10,752 bits total). Each word specifies register source, register destination, flag updates, and functional transfer enables.",
      "512 words × 21 bits = 10,752 bits",
    ],
    ctl: [
      "Control Latches & Local Decoders",
      "Latches and distributes microinstruction fields to local decoders across the EU and BIU, strobing register reads/writes, ALU operations, and memory transfer cycles.",
      "Micro-word[20:0] → Distributed Enables",
    ],
    clk: [
      "8284A Clock Generator & Crystal",
      "15 MHz Quartz Crystal oscillator with Schmitt trigger inverters, 3:1 frequency divider flip-flop counter (outputs 5 MHz 33% duty cycle CLK to 8086 Pin 19), and READY / RESET synchronizer circuits.",
      "15 MHz Crystal ÷ 3 = 5 MHz System CLK",
    ],
    seq: [
      "Clock Phase Sequencer",
      "Clocked 3-stage JK flip-flop phase counter driven by the falling clock edge. Generates timing phases Q0, Q1, Q2 and memory page strobes to step through instruction cycles.",
      "Q⁺ = J·¬Q + ¬K·Q",
    ],
    dec: [
      "Control Enable Matrix (Decode)",
      "4-to-16 line decoder driving an OR-matrix of control lines. Dot connections join active phase minterms to control signals for byte loads, ALU execution, and register writeback.",
      "Minterm index = 8·page + 4·Q₂ + 2·Q₁ + Q₀",
    ],
    latches: [
      "8282 / 74LS373 Address Demux Latches",
      "Three 8-bit octal transparent D-latches. Captures time-multiplexed AD0..AD15 and A16..A19 on the falling edge of 8086 ALE (Address Latch Enable) to provide a stable, demultiplexed 20-bit address bus A0..A19.",
      "ALE = 1: Transparent · ALE = 0: Latched A[19:0]",
    ],
    transceivers: [
      "8286 / 74LS245 Data Bus Transceivers",
      "Two 8-bit octal bidirectional bus transceivers isolating 8086 AD0..AD15 pins from the high-capacitance system data bus D0..D15. Steered by DT/R# (Transmit/Receive) and enabled by active-low DEN#.",
      "DEN# = 0: Enabled · DT/R# = 0: Read · DT/R# = 1: Write",
    ],
    decoder: [
      "74LS138 System Address Decoder",
      "3-to-8 line address decoder decoding high-order address bits A19, A18, A17 when M/IO# is high to generate active-low chip select signals: CS_RAM0# (Low RAM), CS_RAM1# (High RAM), CS_VIDEO#, CS_ROM#.",
      "A19..A17 → CS_RAM#, CS_VIDEO#, CS_ROM#",
    ],
    bootrom: [
      "2764 Boot EPROM (Reset Vector)",
      "8KB x 8 CMOS EPROM positioned at the 8086 reset vector 0xFFFF0. Selected upon CPU reset (CS=FFFFh, IP=0000h) to supply bootstrap jump code (EA 00 01 00 12 / JMP FAR 1200:0100h) to begin execution.",
      "Reset Address = FFFF:0000h = FFFF0h",
    ],
    ram: [
      "16-bit System Static RAM (Even/Odd Banks + 6T CMOS Cell)",
      "1 Megabyte 16-bit physical memory organized into 512KB Even Bank (D0..D7, enabled by A0=0) and 512KB Odd Bank (D8..D15, enabled by BHE#=0). Features authentic 6T CMOS SRAM bitcell schematic with cross-coupled inverters and wordline access transistors.",
      "Even Bank (A0=0) · Odd Bank (BHE#=0) · 6T CMOS Cell",
    ],
  };

  const nets: Workbench.Net[] = [
    ["register-word", "regs", "internal", "16-bit register word", "regs.data", "internal.regs"],
    ["temporary-load", "internal", "temps", "16-bit operand load", "internal.temp", "temps.data"],
    ["tmpa-select", "temps", "mux", "16-bit tmpA to MUX", "temps.a", "mux.a"],
    ["tmpb-select", "temps", "mux", "16-bit tmpB to MUX", "temps.b", "mux.b"],
    ["tmpc-select", "temps", "mux", "16-bit tmpC to MUX", "temps.c", "mux.c"],
    ["alu-first", "mux", "alu", "Selected operand A to ALU", "mux.out", "alu.a"],
    ["alu-second", "temps", "alu", "Operand B to ALU", "temps.b", "alu.b"],
    ["alu-writeback", "alu", "internal", "16-bit ALU result writeback", "alu.out", "internal.wb"],
    ["register-writeback", "internal", "regs", "16-bit internal bus writeback to registers", "internal.write", "regs.write"],
    ["alu-control-fields", "aluctl", "alu", "Decoded ALU operation and carry controls", "aluctl.op", "alu.control"],
    ["alu-input-select", "aluctl", "mux", "ALU input multiplexer selection", "aluctl.sel", "mux.sel"],
    ["ctl-to-aluctl", "ctl", "aluctl", "Microinstruction ALU operation field", "ctl.alu", "aluctl.fn"],
    ["flags-update", "alu", "flags", "ALU condition codes to FLAGS", "alu.flags", "flags.in"],
    ["flags-to-engine", "flags", "engine", "6 condition test lines to branch logic", "flags.out", "engine.cond"],
    ["segment-input", "seg", "segmux", "16-bit segment base to MUX", "seg.out", "segmux.in"],
    ["fetch-offset", "ip", "offmux", "16-bit fetch offset to MUX", "ip.out", "offmux.ip"],
    ["operand-offset", "ind", "offmux", "16-bit effective offset to MUX", "ind.out", "offmux.ind"],
    ["effective-offset", "internal", "ind", "16-bit effective address from the EU", "internal.offset", "ind.in"],
    ["base-to-adder", "segmux", "adder", "20-bit shifted base (Seg << 4)", "segmux.out", "adder.base"],
    ["offset-to-adder", "offmux", "adder", "16-bit offset to Adder", "offmux.out", "adder.off"],
    ["physical-address", "adder", "ext", "20-bit physical address", "adder.sum", "ext.addr"],
    ["prefetch-fifo", "ext", "queue", "Instruction word fetch to FIFO", "ext.bus", "queue.in"],
    ["queue-to-loader", "queue", "loader", "Instruction bytes to Loader", "queue.out", "loader.in"],
    ["queue-to-prefix", "queue", "prefix", "Instruction byte stream to prefix recognition", "queue.out", "prefix.in"],
    ["prefix-override", "prefix", "segmux", "Latched segment override selection", "prefix.segment", "segmux.override"],
    ["operand-read", "ext", "opr", "Memory operand word into the operand latch", "ext.bus", "opr.memory"],
    ["operand-data", "opr", "internal", "Latched 16-bit operand to the EU internal bus", "opr.out", "internal.operand"],
    ["ip-auto-increment", "memory", "ip", "Advance fetch IP after the bus fetch completes", "memory.fetch", "ip.increment"],
    ["loader-to-ir", "loader", "ir", "Opcode byte to IR", "loader.op", "ir.in"],
    ["loader-to-trom", "loader", "trom", "ModR/M byte to TROM", "loader.mod", "trom.mod"],
    ["ir-to-pla", "ir", "pla", "Opcode byte to Group Decode", "ir.out", "pla.in"],
    ["pla-to-engine", "pla", "engine", "Instruction classification signals", "pla.out", "engine.class"],
    ["trom-to-engine", "trom", "engine", "13-bit dispatch target micro-address", "trom.out", "engine.target"],
    ["engine-to-mar", "engine", "mar", "13-bit next micro-address", "engine.out", "mar.in"],
    ["mar-to-rom", "mar", "rom", "13-bit microcode address", "mar.out", "rom.addr"],
    ["rom-to-ctl", "rom", "ctl", "21-bit microinstruction word", "rom.out", "ctl.in"],
    ["ctl-to-regs", "ctl", "regs", "Register read/write strobe lines", "ctl.eu", "regs.en"],
    ["ctl-to-internal", "ctl", "internal", "EU bus transfer strobes", "ctl.eu", "internal.en"],
    ["clock-to-seq", "clk", "seq", "Falling-edge 5 MHz clock to sequencer", "clk.out", "seq.clk"],
    ["seq-to-dec", "seq", "dec", "Phase counter bits Q2..Q0", "seq.out", "dec.in"],
    ["ext-to-latches", "ext", "latches", "Time-multiplexed AD15..AD0 & A19..A16 on ALE", "ext.ad", "latches.in"],
    ["ale-to-latches", "memory", "latches", "8086 ALE Strobe (Pin 25) to STB", "memory.ale", "latches.stb"],
    ["ext-to-transceivers", "ext", "transceivers", "Bidirectional data on DEN# and DT/R#", "ext.ad", "transceivers.in"],
    ["ctrl-to-transceivers", "memory", "transceivers", "DEN# and DT/R# bus control lines", "memory.den", "transceivers.dir"],
    ["latches-to-decoder", "latches", "decoder", "High address bits A19..A16 to decoder", "latches.out", "decoder.in"],
    ["decoder-to-ram", "decoder", "ram", "Active-low RAM chip selects CS_RAM#", "decoder.cs_ram", "ram.cs"],
    ["decoder-to-bootrom", "decoder", "bootrom", "Active-low ROM chip select CS_ROM#", "decoder.cs_rom", "bootrom.cs"],
    ["latches-to-ram", "latches", "ram", "Demultiplexed address bus A19..A1", "latches.out", "ram.addr"],
    ["addr-to-bootrom", "latches", "bootrom", "Latched system address to boot ROM", "latches.out", "bootrom.addr"],
    ["bhe-to-ram", "ext", "ram", "High byte enable for the odd RAM bank", "ext.bhe", "ram.bhe"],
    ["rd-wr-to-ram", "memory", "ram", "Memory read and write strobes", "memory.rw", "ram.control"],
    ["transceivers-to-ram", "transceivers", "ram", "System data bus D15..D0", "transceivers.out", "ram.data"],
    ["transceivers-to-bootrom", "transceivers", "bootrom", "Boot code transfer on D7..D0", "transceivers.out", "bootrom.data"],
  ];

  const unitStyles = {
    EU: { fill: "#f4f8f0", stroke: "#406e42", banner: "#e4eedb", title: "#1e3b20", padCol: "#d97706" },
    BIU: { fill: "#fbf6ec", stroke: "#80663c", banner: "#f3e8d2", title: "#3b2e16", padCol: "#d97706" },
    CU: { fill: "#f7f3fb", stroke: "#6e5982", banner: "#ebe1f4", title: "#31253d", padCol: "#7c3aed" },
    SYS: { fill: "#edf4f7", stroke: "#3d6d82", banner: "#dae8ee", title: "#183340", padCol: "#0284c7" },
  };

  const txt = (x: number, y: number, str: string, size = 10, fill = "#203024", anchor = "start", bold = false) =>
    `<text x="${x}" y="${y}" font-family="Segoe UI,Arial,sans-serif" font-size="${size}" text-anchor="${anchor}" font-weight="${bold ? "bold" : "normal"}" fill="${fill}">${escapeText(str)}</text>`;

  function drawUnitFrame(x: number, y: number, w: number, h: number, code: Workbench.UnitGroup, title: string) {
    const s = unitStyles[code];
    return (
      R(x, y, w, h, s.fill, s.stroke, 8, 2) +
      R(x, y, w, 28, s.banner, s.stroke, 8, 1.2) +
      R(x + 10, y + 5, 42, 18, s.fill, s.stroke, 4, 1.1) +
      txt(x + 31, y + 17, code, 11, s.title, "middle", true) +
      txt(x + 60, y + 18, title, 13, s.title, "start", true)
    );
  }

  function activeIds() {
    const s = cpu.s;
    const ids = [];
    if (s.clock) ids.push("clock-to-seq");
    if ((s.phase % 4) === 0) ids.push("ale-to-latches", "ext-to-latches", "latches-to-decoder", "latches-to-ram");
    if ((s.phase % 4) >= 2) ids.push("ctrl-to-transceivers", "ext-to-transceivers", "transceivers-to-ram", "decoder-to-ram");
    if (s.phase <= 4) ids.push("register-word", "temporary-load", "tmpa-select", "ctl-to-internal");
    if (s.phase >= 4) ids.push("alu-first", "alu-second", "alu-writeback", "register-writeback", "flags-update", "flags-to-engine");
    if (s.prefix != null) ids.push("queue-to-prefix", "prefix-override");
    if (s.opr != null) ids.push("operand-read", "operand-data");
    if (s.queue && s.queue.length <= 4) ids.push("base-to-adder", "offset-to-adder", "physical-address", "prefetch-fifo");
    if (s.ir != null) ids.push("queue-to-loader", "loader-to-ir", "loader-to-trom", "ir-to-pla", "pla-to-engine", "trom-to-engine");
    return ids;
  }

  // One connection graph owns terminal positions and routes at every zoom level.
  // Routes are cached by geometry, and rebuilt when a unit is moved or resized.
  let layoutKey = "";
  let cachedLayout: Workbench.BoardLayout | undefined;
  function layout(): Workbench.BoardLayout {
    const key = JSON.stringify([Object.entries(N).map(([id, box]) => [id, ...box.slice(0, 4)]), nets]);
    if (cachedLayout && key === layoutKey) return cachedLayout;
    const pins: Record<string, Workbench.BoardPin> = {};
    const sides = new Map<string, Set<string>>();
    for (const [, source, target, , from, to] of nets) {
      for (const [owner, name, dir] of [[source, from, "R"], [target, to, "L"]] as const) {
        const side = `${owner}:${dir}`;
        if (!sides.has(side)) sides.set(side, new Set());
        sides.get(side)!.add(name);
      }
    }
    for (const [side, names] of sides) {
      const [owner, direction] = side.split(":");
      const dir = direction === "L" ? "L" : "R";
      const box = N[owner];
      if (!box) throw new Error(`Unknown circuit unit: ${owner}`);
      const [x, y, w, h] = box;
      [...names].forEach((name, index) => {
        pins[name] = { x: dir === "L" ? x : x + w,
          y: y + 32 + ((h - 48) * (index + 1)) / (names.size + 1),
          dir, owner, label: name.slice(name.indexOf(".") + 1).toUpperCase() };
      });
    }
    const router = new logicDraw.AutoRouter({
      obstacles: Object.entries(N).map(([id, [x, y, w, h]]) => ({ id, x, y, w, h })),
      bounds: { x: 10, y: 6, w: W - 20, h: H - 12 }, clearance: 6, stub: 8,
    });
    const connections: Workbench.BoardConnection[] = [];
    for (const net of nets) {
      const [id, , , , from, to] = net;
      const source = pins[from], target = pins[to];
      try {
        router.route({ x: source.x, y: source.y, dir: source.dir },
          { x: target.x, y: target.y, dir: target.dir }, { net: from });
      } catch (error) {
        throw new Error(`Cannot route ${id}: ${error instanceof Error ? error.message : String(error)}`);
      }
      const color = id.includes("clock") ? "#16a34a" :
        /address|offset|base|segment|latches/.test(id) ? "#d97706" :
        /ctl|flags|decoder|mar|rom|seq|engine|pla|trom/.test(id) ? "#7c3aed" : "#0d9488";
      connections.push({ net, points: router.routes[router.routes.length - 1].map(p => ({ x: p.x, y: p.y })), color });
    }
    layoutKey = key;
    cachedLayout = { pins, connections };
    return cachedLayout;
  }
  const escapeText = (value: string) => value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll('"', "&quot;");
  function drawConnection(connection: Workbench.BoardConnection, active: boolean) {
    const { net, points, color } = connection;
    const [id, , , label] = net;
    const path = points.map((point, index) => `${index ? "L" : "M"}${point.x} ${point.y}`).join(" ");
    return `<g data-net="${id}"><title>${escapeText(label)}</title>` +
      P(path, active ? "#10b981" : color, active ? 2.8 : 1.8) + '</g>';
  }
  function drawTerminals(owner: string, macro: boolean, routed: Workbench.BoardLayout) {
    return Object.values(routed.pins).filter(pin => pin.owner === owner).map(pin => {
      const labelX = pin.x + (pin.dir === "L" ? 8 : -8);
      return `<g class="circuit-pin" data-pin="${owner}.${pin.label}">` +
        R(pin.x - 3, pin.y - 3, 6, 6, "#f59e0b", "#78350f", 1, 1) +
        (macro ? txt(labelX, pin.y - 6, pin.label, 7, "#0f172a", pin.dir === "L" ? "start" : "end", true) : "") + '</g>';
    }).join("");
  }

  // High-performance clean architectural block representation when zoomed out (scale < 1.4)
  function drawMacroPreview(id: string, x: number, y: number, w: number, h: number, s: Workbench.CpuState, grp: Workbench.UnitGroup) {
    let out = "";
    const cx = x + w / 2;
    const cy = y + h / 2 + 8;
    const hex = (v: number | null, n = 4) => (v != null ? (v >>> 0).toString(16).toUpperCase().padStart(n, "0") : "0000");

    if (id === "regs") {
      const regs1: Array<[string, number]> = [
        ["AX", s.ax ?? 0],
        ["BX", s.bx ?? 0],
        ["CX", s.cx ?? 0],
        ["DX", s.dx ?? 0],
      ];
      const regs2: Array<[string, number]> = [
        ["SP", s.sp ?? 0xfffe],
        ["BP", s.bp ?? 0x100],
        ["SI", s.si ?? 4],
        ["DI", s.di ?? 0],
      ];
      const rw = (w - 36) / 2;
      regs1.forEach(([k, v], i) => {
        const ry = y + 34 + i * 44;
        out += R(x + 12, ry, rw, 36, "#ffffff", "#94a3b8", 3, 1);
        out += txt(x + 22, ry + 22, k, 12, "#0f172a", "start", true);
        out += R(x + 55, ry + 6, rw - 50, 24, "#f8fafc", "#cbd5e1", 2, 0.8);
        out += txt(x + 65, ry + 22, `${hex(v, 4)}h`, 11, "#047857", "start", true);
      });
      regs2.forEach(([k, v], i) => {
        const ry = y + 34 + i * 44;
        out += R(x + 16 + rw, ry, rw, 36, "#ffffff", "#94a3b8", 3, 1);
        out += txt(x + 26 + rw, ry + 22, k, 12, "#0f172a", "start", true);
        out += R(x + 59 + rw, ry + 6, rw - 50, 24, "#f8fafc", "#cbd5e1", 2, 0.8);
        out += txt(x + 69 + rw, ry + 22, `${hex(v, 4)}h`, 11, "#047857", "start", true);
      });
    } else if (id === "internal") {
      const busVal = (s.lastWord !== undefined && s.lastWord !== null) ? s.lastWord : ((s.ax ?? 0) & 0xffff);
      out += R(cx - 180, y + 36, 360, 95, "#f0fdf4", "#0d9488", 4, 1.2);
      out += txt(cx, y + 60, "16-BIT INTERNAL DATA HIGHWAY & CROSSBAR", 12, "#047857", "middle", true);
      out += txt(cx, y + 80, `BUS[15:0]: ${hex(busVal, 4)}h  (16 PARALLEL DATA TRUNKS)`, 11, "#0f766e", "middle", true);
      out += txt(cx, y + 98, "ARBITRATED TAPS: REGS · tmpA · tmpB · ALU_OUT · QUEUE · OPR", 9.5, "#334155", "middle", false);
    } else if (id === "alu") {
      const calc = cpu.calculate();
      const topW = w - 80;
      const botW = w - 160;
      const aluY1 = y + 40;
      const aluY2 = y + h - 35;
      const poly = `M${cx - topW / 2} ${aluY1} L${cx - 30} ${aluY1} L${cx} ${aluY1 + 35} L${cx + 30} ${aluY1} L${cx + topW / 2} ${aluY1} L${cx + botW / 2} ${aluY2} L${cx - botW / 2} ${aluY2} Z`;
      out += P(poly, "#047857", 2.2, "#ecfdf5");
      out += txt(cx, cy + 5, s.op || "ADD / SUB / LOGIC", 15, "#065f46", "middle", true);
      out += txt(cx - topW / 4, aluY1 - 8, `A: ${hex(s.a || 0, 4)}h`, 10.5, "#0f172a", "middle", true);
      out += txt(cx + topW / 4, aluY1 - 8, `B: ${hex(s.b || 0, 4)}h`, 10.5, "#0f172a", "middle", true);
      out += R(cx - 70, aluY2 + 6, 140, 24, "#10b981", "#047857", 4, 1);
      out += txt(cx, aluY2 + 22, `OUT: ${hex(calc.word, 4)}h`, 11.5, "#ffffff", "middle", true);
    } else if (id === "flags") {
      const calc = cpu.calculate();
      const flist: Workbench.Flag[] = ["CF", "PF", "AF", "ZF", "SF", "OF", "TF", "IF", "DF"];
      const fw = (w - 30) / 9;
      flist.forEach((f, i) => {
        const val = s.flags[f];
        const fx = x + 12 + i * fw;
        out += R(fx, y + 60, fw - 6, 80, val ? "#ecfdf5" : "#f8fafc", val ? "#10b981" : "#cbd5e1", 4, 1.2);
        out += txt(fx + (fw - 6) / 2, y + 85, f, 11, "#0f172a", "middle", true);
        out += `<circle cx="${fx + (fw - 6) / 2}" cy="${y + 115}" r="8" fill="${val ? "#10b981" : "#94a3b8"}" stroke="${val ? "#047857" : "#64748b"}" stroke-width="1.5"/>`;
        out += txt(fx + (fw - 6) / 2, y + 119, val ? "1" : "0", 9, val ? "#ffffff" : "#f8fafc", "middle", true);
      });
      out += txt(cx, y + h - 25, "STATUS & MACHINE CONTROL FLAGS REGISTER", 11, "#475569", "middle", true);
    } else if (id === "queue") {
      const q = s.queue || [];
      const qw = (w - 40) / 6;
      for (let i = 0; i < 6; i++) {
        const has = i < q.length;
        const qx = x + 16 + i * qw;
        out += R(qx, y + 55, qw - 6, 90, has ? "#eff6ff" : "#f8fafc", has ? "#3b82f6" : "#cbd5e1", 4, 1.2);
        out += txt(qx + (qw - 6) / 2, y + 80, `Q[${i}]`, 11, "#1e3a8a", "middle", true);
        const bval = has ? hex(q[i], 2) : "—";
        out += R(qx + 4, y + 95, qw - 14, 34, "#ffffff", "#93c5fd", 2, 0.8);
        out += txt(qx + (qw - 6) / 2, y + 117, bval + (has ? "h" : ""), 12, has ? "#1d4ed8" : "#94a3b8", "middle", true);
      }
      out += txt(cx, y + h - 25, `FIFO LENGTH: ${q.length} / 6 BYTES PREFETCHED`, 11, "#2563eb", "middle", true);
    } else if (id === "adder") {
      const segBase = (s.cs ?? 0x1200) << 4;
      const off = s.ip ?? 0x0100;
      const phys = (segBase + off) & 0xfffff;
      out += R(cx - 150, y + 45, 300, 44, "#fef3c7", "#d97706", 4, 1.2);
      out += txt(cx, y + 72, `SEG BASE (16-bit << 4) = ${hex(segBase, 5)}h`, 11.5, "#92400e", "middle", true);
      out += P(`M${cx} ${y + 89} V${y + 115}`, "#d97706", 2.2, "none", 'marker-end="url(#tip-high)"');
      out += R(cx - 150, y + 115, 300, 44, "#ecfdf5", "#059669", 4, 1.5);
      out += txt(cx, y + 142, `+ OFFSET (${hex(off, 4)}h) = PHYS: ${hex(phys, 5)}h`, 12, "#065f46", "middle", true);
    } else if (id === "seg") {
      const segs: Array<[string, number]> = [
        ["CS (Code)", s.cs ?? 0x1200],
        ["DS (Data)", s.ds ?? 0x2000],
        ["SS (Stack)", s.ss ?? 0x2800],
        ["ES (Extra)", s.es ?? 0x3000],
      ];
      const sw = (w - 30) / 2;
      segs.forEach(([k, v], i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        const sx = x + 12 + col * (sw + 6);
        const sy = y + 42 + row * 65;
        out += R(sx, sy, sw, 52, "#ffffff", "#94a3b8", 4, 1);
        out += txt(sx + 12, sy + 24, k, 11, "#0f172a", "start", true);
        out += txt(sx + 12, sy + 42, `${hex(v, 4)}h (Base: ${hex(v << 4, 5)}h)`, 10, "#d97706", "start", true);
      });
    } else if (id === "ip") {
      const ipVal = s.ip ?? 0x0100;
      out += R(cx - 140, y + 45, 280, 55, "#ffffff", "#0284c7", 4, 1.4);
      out += txt(cx, y + 70, "INSTRUCTION POINTER (IP)", 11, "#0369a1", "middle", true);
      out += txt(cx, y + 90, `${hex(ipVal, 4)}h  (Offset in CS)`, 13, "#0284c7", "middle", true);
      out += P(`M${cx} ${y + 100} V${y + 130}`, "#0284c7", 2, "none", 'marker-end="url(#tip-high)"');
      out += R(cx - 100, y + 130, 200, 36, "#f0fdf4", "#16a34a", 4, 1.2);
      out += txt(cx, y + 153, "+1 / +2 FAST INCREMENT", 10.5, "#15803d", "middle", true);
    } else if (id === "memory") {
      const phase = (s.phase || 0) % 4;
      const tnames = ["T1: Address Output (ALE)", "T2: Bus Turnaround", "T3: Data Access / Fetch", "T4: Complete & Latch"];
      const tw = (w - 30) / 4;
      for (let i = 0; i < 4; i++) {
        const isAct = phase === i;
        const tx = x + 12 + i * tw;
        out += R(tx, y + 55, tw - 6, 85, isAct ? "#ecfdf5" : "#f8fafc", isAct ? "#10b981" : "#cbd5e1", 4, isAct ? 2 : 1);
        out += txt(tx + (tw - 6) / 2, y + 80, `T${i + 1}`, 15, isAct ? "#065f46" : "#64748b", "middle", true);
        out += txt(tx + (tw - 6) / 2, y + 105, isAct ? "ACTIVE" : "IDLE", 9, isAct ? "#10b981" : "#94a3b8", "middle", true);
        out += txt(tx + (tw - 6) / 2, y + 125, i === 0 ? "ALE=1" : (i >= 2 ? "DEN#=0" : "READY"), 8.5, "#475569", "middle", false);
      }
      out += txt(cx, y + h - 22, `BUS CYCLE: ${tnames[phase]}`, 11, "#059669", "middle", true);
    } else if (id === "rom") {
      const mar = s.mar ?? 0x14;
      out += R(cx - 170, y + 42, 340, 95, "#fdf4ff", "#a855f7", 4, 1.2);
      out += txt(cx, y + 68, "INTEL 8086 MICROCODE CONTROL STORE", 11.5, "#7e22ce", "middle", true);
      out += txt(cx, y + 90, `512 WORDS × 21 BITS WIDE`, 10.5, "#6b21a8", "middle", false);
      out += R(cx - 130, y + 102, 260, 24, "#ffffff", "#c084fc", 2, 0.8);
      out += txt(cx, y + 118, `MAR: [${hex(mar, 3)}h]  OUTPUT: 0x002C04`, 10.5, "#9333ea", "middle", true);
      out += txt(cx, y + h - 25, "CONTROLS EU REGISTERS, ALU OPS & BUS SEQUENCING", 10, "#7e22ce", "middle", false);
    } else if (id === "clk") {
      out += R(cx - 150, y + 45, 300, 100, "#f0fdfa", "#0d9488", 4, 1.2);
      out += txt(cx, y + 70, "8284A CLOCK GENERATOR", 12, "#115e59", "middle", true);
      out += txt(cx, y + 92, "14.318 MHz TANK / 3 = 4.77 MHz CLK", 10.5, "#0f766e", "middle", false);
      out += P(`M${cx - 100} ${y + 120} h20 v-15 h20 v15 h20 v-15 h20 v15 h20`, "#0d9488", 2);
    } else if (id === "latches") {
      out += R(cx - 160, y + 45, 320, 100, "#fffbeb", "#d97706", 4, 1.2);
      out += txt(cx, y + 75, "8282 DEMULTIPLEXING ADDRESS LATCHES", 12, "#b45309", "middle", true);
      out += txt(cx, y + 100, "CAPTURES 20-BIT ADDRESS (AD15..AD0 + A19..A16)", 10.5, "#92400e", "middle", false);
      out += txt(cx, y + 125, "STROBED BY 8086 ALE PULSE AT T1", 10, "#d97706", "middle", true);
    } else if (id === "transceivers") {
      out += R(cx - 160, y + 45, 320, 100, "#f0fdf4", "#16a34a", 4, 1.2);
      out += txt(cx, y + 75, "8286 BUS TRANSCEIVERS (16-BIT)", 12, "#15803d", "middle", true);
      out += txt(cx, y + 100, "ISOLATES CPU LOCAL BUS FROM SYSTEM BUS", 10.5, "#166534", "middle", false);
      out += txt(cx, y + 125, "DIRECTION: DT/R#  |  OUTPUT ENABLE: DEN#", 10, "#16a34a", "middle", true);
    } else if (id === "decoder") {
      out += R(cx - 150, y + 45, 300, 95, "#f5f3ff", "#7c3aed", 4, 1.2);
      out += txt(cx, y + 75, "74LS138 3-TO-8 ADDRESS DECODER", 12, "#6d28d9", "middle", true);
      out += txt(cx, y + 100, "DECODES A19..A16 INTO CHIP SELECTS", 10.5, "#5b21b6", "middle", false);
      out += txt(cx, y + 122, "Y0#=RAM (0x00000)  |  Y7#=ROM (0xFFFF0)", 9.5, "#7c3aed", "middle", true);
    } else if (id === "ram") {
      out += R(cx - 240, y + 45, 480, 110, "#f0fdf4", "#15803d", 4, 1.2);
      out += txt(cx, y + 75, "16-BIT SYSTEM STATIC RAM (64KB DUAL BANK)", 13, "#166534", "middle", true);
      out += txt(cx, y + 102, "EVEN BANK (A0=0) · 32KB  |  ODD BANK (BHE#=0) · 32KB", 11, "#15803d", "middle", false);
    } else if (id === "bootrom") {
      out += R(cx - 150, y + 45, 300, 95, "#fff1f2", "#e11d48", 4, 1.2);
      out += txt(cx, y + 75, "2764 BOOT EPROM (8KB)", 12, "#be123c", "middle", true);
      out += txt(cx, y + 100, "RESET VECTOR AT 0xFFFF0 (CS:IP FFFF:0000)", 10.5, "#9f1239", "middle", false);
      out += txt(cx, y + 122, "JMP FAR 1200:0100H INITIALIZATION CODE", 9.5, "#e11d48", "middle", true);
    } else if (id === "ext") {
      out += R(cx - 160, y + 42, 320, 110, "#0f172a", "#334155", 6, 1.8);
      out += txt(cx, y + 72, "HMOS-II SILICON I/O & ESD CELL", 13, "#f8fafc", "middle", true);
      out += txt(cx, y + 94, "3µm HMOS II · AD[15:0] MUX BUS & BIDIRECTIONAL PAD", 10.5, "#38bdf8", "middle", false);
      out += R(cx - 145, y + 108, 290, 32, "#1e293b", "#475569", 3, 1);
      out += txt(cx, y + 123, "DUAL-DIODE RAIL CLAMP · 2kV GGNMOS SNAPBACK", 9.5, "#10b981", "middle", true);
      out += txt(cx, y + 135, "300Ω DIFFUSED BALLAST · SCHMITT TRIGGER I/O", 8.5, "#94a3b8", "middle", false);
    } else {
      out += R(cx - 130, cy - 35, 260, 70, "#f8fafc", "#cbd5e1", 4, 1);
      out += txt(cx, cy, grp, 12, "#475569", "middle", true);
    }
    return out;
  }

  function drawComponent(id: string, box: Workbench.UnitBox, isMacro: boolean,
    selected: boolean, bit: number, state: Workbench.CpuState, routed: Workbench.BoardLayout) {
    const [x, y, w, h, title, group] = box;
    const s = unitStyles[group] || unitStyles.EU;
    const logic = isMacro ? null : getComponentLogic(id, state, bit);
    const vw = (logic && logic.vw) ? logic.vw : 400;
    const vh = (logic && logic.vh) ? logic.vh : 200;

    const clip = `card-${id}`;
    let compSvg = `<defs><clipPath id="${clip}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="3"/></clipPath></defs><g clip-path="url(#${clip})">`;
    // Outer card box
    compSvg += R(x, y, w, h, isMacro ? s.fill : "#ffffff", s.stroke, 3, isMacro ? 1.4 : 1.6);
    // Header strip
    const hdrH = isMacro ? 20 : 16;
    compSvg += R(x, y, w, hdrH, s.banner, s.stroke, 3, 0.8);
    // Header title: in detail mode, clean and compact so it never overflows
    const cleanTitle = title.split(" · ")[0].split(" (")[0];
    const fontSize = isMacro ? 8.5 : 7.2;
    const maxChars = Math.floor((w - 16) / (fontSize * 0.6));
    const shortTitle = cleanTitle.length > maxChars ? cleanTitle.slice(0, maxChars - 1) + "…" : cleanTitle;
    compSvg += txt(x + 8, y + (isMacro ? 14 : 12), shortTitle, fontSize, s.title, "start", true);

    // Dynamic Level-of-Detail (LOD):
    // When zoomed out (scale < 1.4): render clean, high-performance macro representation (NO gate clutter).
    // When zoomed in (scale >= 1.4): render FULL-SIZE crisp electrical logic schematic filling the card!
    if (isMacro) {
      compSvg += drawMacroPreview(id, x, y, w, h, state, group);
    } else if (logic && logic.body) {
      const padX = 6;
      const padY = hdrH + 4;
      const availW = w - padX * 2;
      const availH = h - padY - 4;
      const ratio = Math.min(availW / vw, availH / vh);
      const X = x + padX + (availW - vw * ratio) / 2;
      const Y0 = y + padY + (availH - vh * ratio) / 2;
      compSvg += `<g data-logic="${id}" transform="translate(${X} ${Y0}) scale(${ratio})">${logic.body}</g>`;
    }

    compSvg += "</g>" + drawTerminals(id, isMacro, routed);

    // Selection highlight ring
    if (selected) {
      compSvg += R(x - 3, y - 3, w + 6, h + 6, "none", "#10b981", 6, 3);
    }

    // Clickable container for interaction
    return `<g class="cpu-node" data-node="${id}" role="button" tabindex="0" aria-label="Inspect ${escapeText(title)}">` +
      `<title>${escapeText(title)} · Click to inspect, double-click to focus</title>` +
      compSvg +
      R(x, y, w, h, "transparent", "none", 0, 0) +
      `</g>`;
  }

  const sceneDefs =
    '<marker id="tip-norm" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#0d9488" stroke-width="1.6"/></marker>' +
    '<marker id="tip-high" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#10b981" stroke-width="2.2"/></marker>' +
    '<pattern id="silicon-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#182c24" stroke-width="0.8"/></pattern>';

  /** Cheap descriptors come first; SVG and gate geometry are generated only on demand. */
  function scene(scale: number, sel: string, bit: number): Workbench.RenderScene {
    const active = new Set(activeIds());
    const isMacro = scale < 1.4;
    const routed = layout();
    const state = cpu.s;
    const stateVersion = JSON.stringify([state, cpu.settings]);
    const items: Workbench.RenderItem[] = [{
      id: "background", bounds: { x1: 0, y1: 0, x2: W, y2: H }, version: `${W}:${H}`,
      render: () => `<rect width="${W}" height="${H}" fill="#0b1713"/>` +
        `<rect width="${W}" height="${H}" fill="url(#silicon-grid)"/>`,
    }];
    const nodes = Object.entries(N);

    // Group frames derive from member bounds, just like their routed ports.
    for (const group of ["EU", "BIU", "CU", "SYS"] as const) {
      const boxes = nodes.filter(([id, box]) => (id === "clk" ? "CU" : box[5]) === group).map(([, box]) => box);
      const x = Math.min(...boxes.map(box => box[0])) - 20;
      const y = Math.min(...boxes.map(box => box[1])) - 40;
      const right = Math.max(...boxes.map(box => box[0] + box[2])) + 20;
      const bottom = Math.max(...boxes.map(box => box[1] + box[3])) + 20;
      const titles = { EU: "EXECUTION UNIT", BIU: "BUS INTERFACE UNIT", CU: "CONTROL UNIT & CLOCK", SYS: "SYSTEM BOARD" };
      items.push({
        id: `frame:${group}`, bounds: { x1: x - 1, y1: y - 1, x2: right + 1, y2: bottom + 1 },
        version: `${x}:${y}:${right}:${bottom}`,
        render: () => drawUnitFrame(x, y, right - x, bottom - y, group, titles[group]),
      });
    }

    // Test actual polyline segments, so a wire crossing the screen stays visible
    // even when both endpoint cards are off screen.
    for (const connection of routed.connections) {
      const { net, points, color } = connection;
      const enabled = active.has(net[0]);
      items.push({
        id: `net:${net[0]}`,
        bounds: {
          x1: Math.min(...points.map(point => point.x)) - 2,
          y1: Math.min(...points.map(point => point.y)) - 2,
          x2: Math.max(...points.map(point => point.x)) + 2,
          y2: Math.max(...points.map(point => point.y)) + 2,
        },
        path: points, version: JSON.stringify([points, net[3], color, enabled]),
        render: () => drawConnection(connection, enabled),
      });
    }

    for (const [id, box] of nodes) {
      const [x, y, w, h] = box;
      const selected = id === sel;
      const pins = Object.values(routed.pins).filter(pin => pin.owner === id);
      items.push({
        id: `node:${id}`,
        bounds: { x1: x - 5, y1: y - 5, x2: x + w + 5, y2: y + h + 5 },
        version: JSON.stringify([box, pins, isMacro, selected, bit, stateVersion]),
        render: () => drawComponent(id, box, isMacro, selected, bit, state, routed),
      });
    }
    return { defs: sceneDefs, items };
  }

  // String rendering remains available to inspectors and exported schematics.
  function render(scale: number, sel: string, bit: number, vr?: Workbench.ViewRect) {
    return CircuitRendering.renderScene(scene(scale, sel, bit), vr);
  }

  window.board = {
    W,
    H,
    get height() {
      return H;
    },
    N,
    info,
    nets,
    render,
    scene,
    reflow: (_scale: number, cy: number) => cy,
    Y: (y: number) => y,
    unmap: (v: number) => v,
    activeIds,
    expanded: () => true,
    layout,
  };
})();
