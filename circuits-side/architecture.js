/* 8086 Microprocessor & System Board Architecture Workbench
   Complete Silicon Die & System Board Inspection Scope
   100% Interconnected Gate-Level, Transistor-Level & Bus Wiring */
(() => {
  const { R, P, dot, tinyGate, getComponentLogic, hasLogic } = logicDraw;

  const W = 2720;
  const H = 2600;

  // Exact coordinates [x, y, w, h, title, group] for all 34 internal & external components
  const spec = {
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

  const N = {};
  for (const [id, [x, y, w, h, title, group]] of Object.entries(spec)) {
    N[id] = [x, y, w, h, title, group];
  }

  const info = {
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

  const nets = [
    ["register-word", "regs", "internal", "16-bit register word", "regs.data", "internal.regs"],
    ["temporary-load", "internal", "temps", "16-bit operand load", "internal.temp", "temps.data"],
    ["tmpa-select", "temps", "mux", "16-bit tmpA to MUX", "temps.a", "mux.a"],
    ["tmpb-select", "temps", "mux", "16-bit tmpB to MUX", "temps.b", "mux.b"],
    ["tmpc-select", "temps", "mux", "16-bit tmpC to MUX", "temps.c", "mux.c"],
    ["alu-first", "mux", "alu", "Selected operand A to ALU", "mux.out", "alu.a"],
    ["alu-second", "temps", "alu", "Operand B to ALU", "temps.b", "alu.b"],
    ["alu-writeback", "alu", "internal", "16-bit ALU result writeback", "alu.out", "internal.wb"],
    ["flags-update", "alu", "flags", "ALU condition codes to FLAGS", "alu.flags", "flags.in"],
    ["flags-to-engine", "flags", "engine", "6 condition test lines to branch logic", "flags.out", "engine.cond"],
    ["segment-input", "seg", "segmux", "16-bit segment base to MUX", "seg.out", "segmux.in"],
    ["fetch-offset", "ip", "offmux", "16-bit fetch offset to MUX", "ip.out", "offmux.ip"],
    ["operand-offset", "ind", "offmux", "16-bit effective offset to MUX", "ind.out", "offmux.ind"],
    ["base-to-adder", "segmux", "adder", "20-bit shifted base (Seg << 4)", "segmux.out", "adder.base"],
    ["offset-to-adder", "offmux", "adder", "16-bit offset to Adder", "offmux.out", "adder.off"],
    ["physical-address", "adder", "ext", "20-bit physical address", "adder.sum", "ext.addr"],
    ["prefetch-fifo", "ext", "queue", "Instruction word fetch to FIFO", "ext.bus", "queue.in"],
    ["queue-to-loader", "queue", "loader", "Instruction bytes to Loader", "queue.out", "loader.in"],
    ["loader-to-ir", "loader", "ir", "Opcode byte to IR", "loader.op", "ir.in"],
    ["loader-to-trom", "loader", "trom", "ModR/M byte to TROM", "loader.mod", "trom.mod"],
    ["ir-to-pla", "ir", "pla", "Opcode byte to Group Decode", "ir.out", "pla.in"],
    ["pla-to-engine", "pla", "engine", "Instruction classification signals", "pla.out", "engine.class"],
    ["trom-to-engine", "trom", "engine", "13-bit dispatch target micro-address", "trom.out", "engine.target"],
    ["engine-to-mar", "engine", "mar", "13-bit next micro-address", "engine.out", "mar.in"],
    ["mar-to-rom", "mar", "rom", "13-bit microcode address", "mar.out", "rom.addr"],
    ["rom-to-ctl", "rom", "ctl", "21-bit microinstruction word", "rom.out", "ctl.in"],
    ["ctl-to-regs", "ctl", "regs", "Register read/write strobe lines", "ctl.eu", "regs.en"],
    ["clock-to-cpu", "clk", "seq", "5 MHz CLK to 8086 Pin 19 & Phase Sequencer", "clk.out", "seq.clk"],
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
    ["transceivers-to-ram", "transceivers", "ram", "System data bus D15..D0", "transceivers.out", "ram.data"],
    ["transceivers-to-bootrom", "transceivers", "bootrom", "Boot code transfer on D7..D0", "transceivers.out", "bootrom.data"],
  ];

  const unitStyles = {
    EU: { fill: "#f4f8f0", stroke: "#406e42", banner: "#e4eedb", title: "#1e3b20", padCol: "#d97706" },
    BIU: { fill: "#fbf6ec", stroke: "#80663c", banner: "#f3e8d2", title: "#3b2e16", padCol: "#d97706" },
    CU: { fill: "#f7f3fb", stroke: "#6e5982", banner: "#ebe1f4", title: "#31253d", padCol: "#7c3aed" },
    SYS: { fill: "#edf4f7", stroke: "#3d6d82", banner: "#dae8ee", title: "#183340", padCol: "#0284c7" },
  };

  const txt = (x, y, str, size = 10, fill = "#203024", anchor = "start", bold = false) =>
    `<text x="${x}" y="${y}" font-family="Segoe UI,Arial,sans-serif" font-size="${size}" text-anchor="${anchor}" font-weight="${bold ? "bold" : "normal"}" fill="${fill}">${str}</text>`;

  function drawUnitFrame(x, y, w, h, code, title) {
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
    const s = cpu.s,
      mem = cpu.isMem && cpu.isMem();
    const ids = [];
    if (s.clock) ids.push("clock-to-cpu", "clock-to-seq");
    if ((s.phase % 4) === 0) ids.push("ale-to-latches", "ext-to-latches", "latches-to-decoder", "latches-to-ram");
    if ((s.phase % 4) >= 2) ids.push("ctrl-to-transceivers", "ext-to-transceivers", "transceivers-to-ram", "decoder-to-ram");
    if (s.phase <= 4) ids.push("register-word", "temporary-load", "tmpa-select", "internal-bus-spine");
    if (s.phase >= 4) ids.push("alu-first", "alu-second", "alu-writeback", "flags-update", "flags-to-engine", "internal-bus-spine");
    if (s.queue && s.queue.length <= 4) ids.push("base-to-adder", "offset-to-adder", "physical-address", "prefetch-fifo");
    if (s.ir != null) ids.push("queue-to-loader", "loader-to-ir", "loader-to-trom", "ir-to-pla", "pla-to-engine", "trom-to-engine");
    return ids;
  }

  // Detailed plain-English signal descriptions for complete clarity and beginners
  const netDetails = {
    "internal-bus-spine": { tag: "/16 BUS", title: "Internal 16-Bit Data Highway [15:0]", desc: "Main synchronous CPU data spine linking general registers, temporary latches, ALU result writeback, and bus controller." },
    "register-word": { tag: "/16 WORD", title: "Register Read Output", desc: "Selected register (AX, BX, CX, DX, SP, BP, SI, DI) puts 16-bit word onto internal data highway." },
    "alu-writeback": { tag: "/16 RESULT", title: "ALU Writeback Bus", desc: "Delivers computed 16-bit ALU result back into destination register or memory write buffer." },
    "ctl-to-regs": { tag: "3-BIT SEL", title: "Register Address Select Lines", desc: "3-bit control field specifying which general register is read (Port A/B) or written (Port W)." },
    "temporary-load": { tag: "/16 LATCH", title: "Temporary Latch Data In", desc: "Latches incoming 16-bit operands from internal data bus into temporary registers tmpA, tmpB, or tmpC." },
    "tmpa-select": { tag: "/16 tmpA", title: "Temporary Latch tmpA to MUX", desc: "Feeds first ALU operand from tmpA latch into ALU Input Multiplexer." },
    "tmpb-select": { tag: "/16 tmpB", title: "Temporary Latch tmpB to MUX", desc: "Feeds second ALU operand from tmpB latch into ALU Input Multiplexer." },
    "tmpc-select": { tag: "/16 tmpC", title: "Temporary Latch tmpC to MUX", desc: "Feeds third operand / displacement from tmpC latch into ALU Input Multiplexer." },
    "alu-first": { tag: "/16 OPERAND A", title: "ALU Input Port A", desc: "Primary 16-bit operand selected by MUX fed directly into ALU adder/logic slice." },
    "alu-second": { tag: "/16 OPERAND B", title: "ALU Input Port B", desc: "Secondary 16-bit operand routed from temporary latch B directly into ALU adder/logic slice." },
    "alu-control-fields": { tag: "ALU CTRL", title: "ALU Function & Operation Select", desc: "Microcode control lines selecting operation (ADD, SUB, AND, OR, XOR, CMP, TEST, shifts)." },
    "flags-update": { tag: "6 FLAGS", title: "Condition Flag Update Bus", desc: "Calculated arithmetic status lines: CF (Carry), PF (Parity), AF (Aux), ZF (Zero), SF (Sign), OF (Overflow)." },
    "flags-to-engine": { tag: "COND [5:0]", title: "FLAGS to Microcode Branch Logic", desc: "Routes current flag states to microcode engine for conditional jump evaluation (JZ, JNZ, JC, JO)." },
    "segment-input": { tag: "/16 SEG", title: "Segment Base Address Output", desc: "Outputs 16-bit segment base register (CS, DS, SS, ES) to Segment Selector MUX." },
    "base-to-adder": { tag: "/20 BASE", title: "Shifted Segment Base (Seg << 4)", desc: "Hardwired 4-bit left shift multiplying segment by 16 to form 20-bit base address for 1MB physical space." },
    "fetch-offset": { tag: "/16 IP", title: "Instruction Pointer (IP) Offset", desc: "Offset address of the next machine instruction byte to be prefetched from the code segment." },
    "operand-offset": { tag: "/16 EA", title: "Effective Memory Address Offset", desc: "Indirect memory address offset computed from base, index, and displacement registers." },
    "offset-to-adder": { tag: "/16 OFFSET", title: "Selected Offset to 20-Bit Adder", desc: "16-bit offset feeding secondary input of dedicated BIU address adder." },
    "prefix-override": { tag: "OVERRIDE", title: "Segment Override Signal", desc: "Forces Segment MUX to choose ES, SS, or CS instead of default DS when override prefix is active." },
    "physical-address": { tag: "/20 ADDR", title: "20-Bit Physical Memory Address", desc: "Hardware sum of (Segment * 16) + Offset, addressing the full 1,048,576 byte memory map." },
    "ip-auto-increment": { tag: "+2 IP", title: "IP Fast Increment Pulse", desc: "Automatically advances IP by 1 or 2 bytes during background instruction prefetch cycles." },
    "prefetch-fifo": { tag: "/16 FIFO", title: "Prefetched Machine Code Word", desc: "Directs instruction words fetched from memory into the 6-byte instruction prefetch FIFO." },
    "queue-to-loader": { tag: "/8 STREAM", title: "Instruction Stream Byte", desc: "Pops next sequential instruction byte from FIFO into instruction loader." },
    "loader-to-ir": { tag: "/8 OPCODE", title: "Opcode Byte to IR", desc: "Latches primary opcode into Instruction Register (IR) for decoding." },
    "loader-to-trom": { tag: "MODR/M", title: "ModR/M Addressing Byte", desc: "Provides register/memory addressing mode specification to Translation ROM." },
    "ir-to-pla": { tag: "IR_OP", title: "Opcode to Group Decode PLA", desc: "8-bit opcode feeding Group Decode PLA for instruction category classification." },
    "pla-to-engine": { tag: "CLASS", title: "Instruction Category Lines", desc: "Signals classifying instruction into ALU, MOV, BRANCH, PUSH/POP, STRING, or SYSTEM." },
    "trom-to-engine": { tag: "/13 TARGET", title: "Microcode Entry Routine Address", desc: "13-bit dispatch target address jumping directly to the execution sequence for this opcode." },
    "engine-to-mar": { tag: "/13 µADDR", title: "Next Micro-Instruction Address", desc: "Next microcode address selected by micro-sequencer or branch conditions." },
    "mar-to-rom": { tag: "/13 MAR", title: "Microcode ROM Address Bus", desc: "13-bit word address indexing into 512-word microcode control store ROM." },
    "rom-to-ctl": { tag: "/21 µWORD", title: "21-Bit Microcode Control Word", desc: "Horizontal control word driving functional transfer enables across EU and BIU." },
    "seq-to-dec": { tag: "PHASE", title: "Sequencer Timing Phase Lines", desc: "JK flip-flop phase counter bits Q2..Q0 driving 4-to-16 control enable matrix." },
    "clock-to-cpu": { tag: "5 MHz CLK", title: "Master Clock (Pin 19)", desc: "Synchronous 4.77 MHz 33% duty cycle clock generated by 8284A clock chip." },
    "clock-to-seq": { tag: "CLK", title: "Sequencer Clock Trigger", desc: "Falling clock edge triggering next microcode step and bus state transition." },
    "ext-to-latches": { tag: "/20 MUX", title: "Multiplexed Address/Data Bus (AD15..AD0 & A19..A16)", desc: "Time-multiplexed CPU bus carrying 20-bit address during T1 and 16-bit data during T2..T4." },
    "ale-to-latches": { tag: "ALE", title: "Address Latch Enable Strobe (Pin 25)", desc: "High pulse during T1 commanding 8282 latches to freeze 20-bit address." },
    "ext-to-transceivers": { tag: "/16 LOCAL", title: "Local CPU Data Bus (AD15..AD0)", desc: "Multiplexed data lines feeding 8286 bidirectional transceivers to isolate CPU from system bus." },
    "ctrl-to-transceivers": { tag: "DEN# / DT/R#", title: "Bus Transceiver Control", desc: "DEN# enables transceiver outputs; DT/R# sets transfer direction (transmit vs receive)." },
    "latches-to-decoder": { tag: "A[19:16]", title: "Upper System Address Bits", desc: "High 4 address bits decoded by 74LS138 into RAM, Video, and ROM chip selects." },
    "decoder-to-ram": { tag: "CS_RAM#", title: "RAM Chip Select (Active Low)", desc: "Enables system static RAM when address falls in lower 640KB system memory." },
    "decoder-to-bootrom": { tag: "CS_ROM#", title: "Boot ROM Chip Select (Active Low)", desc: "Enables 2764 Boot EPROM when address falls in top 8KB reset vector region (0xFFFF0)." },
    "latches-to-ram": { tag: "/20 ADDR", title: "Demultiplexed System Address Bus A[19:1]", desc: "Clean non-multiplexed 20-bit address bus driving memory chips." },
    "transceivers-to-ram": { tag: "/16 DATA", title: "System Data Bus D[15:0]", desc: "Buffered 16-bit parallel system data bus connecting CPU to RAM chips." },
    "transceivers-to-bootrom": { tag: "/8 DATA", title: "Boot ROM Data Bus D[7:0]", desc: "Transfers startup initialization machine code from boot EPROM into CPU at reset." },
    "bhe-to-ram": { tag: "BHE#", title: "Bus High Enable (Pin 34)", desc: "Active low signal selecting odd memory bank (D15..D8), allowing byte or word access." },
    "rd-wr-to-ram": { tag: "RD# / WR#", title: "Memory Read / Write Strobes", desc: "Directs memory chips whether to output data onto bus (RD#=0) or store data from bus (WR#=0)." },
  };

  let currentIsMacro = true;

  // Draw authentic copper pin terminal pad along a component border
  // CRITICAL RULE: Pin text labels are rendered strictly INSIDE the component box
  // so external routing channels between units remain 100% free of text collisions!
  // In detail mode (!currentIsMacro), perimeter labels are suppressed because internal PortBoxes provide exact names.
  function terminalPin(x, y, label, dir = "right", isBus = true, width = 16) {
    const pw = dir === "left" || dir === "right" ? 8 : 12;
    const ph = dir === "left" || dir === "right" ? 12 : 8;
    const px = x - pw / 2;
    const py = y - ph / 2;
    let res = `<g class="circuit-pin" data-pin="${label || ''}">`;
    res += `<rect x="${px}" y="${py}" width="${pw}" height="${ph}" rx="2" fill="#f59e0b" stroke="#78350f" stroke-width="1.2"/>`;
    if (label && currentIsMacro) {
      let tx = x, ty = y;
      let anchor = "middle";
      if (dir === "right") { tx -= 8; ty = y - 7; anchor = "end"; }
      else if (dir === "left") { tx += 8; ty = y - 7; anchor = "start"; }
      else if (dir === "bottom") { ty = y - 8; anchor = "middle"; }
      else if (dir === "top") { ty = y - 7; anchor = "middle"; }
      res += `<text x="${tx}" y="${ty}" font-family="Segoe UI,Arial,sans-serif" font-size="7.5" text-anchor="${anchor}" font-weight="bold" fill="#0f172a" paint-order="stroke" stroke="#ffffff" stroke-width="3" stroke-linejoin="round">${label}</text>`;
    }
    res += `</g>`;
    return res;
  }

  // Draw continuous physical interconnect wiring highway between all units
  function drawContinuousInterconnects(activeSet) {
    let g = '<g id="complete-circuit-wiring-highway">';

    // Helper to draw clean orthogonal routed bus lines with junction dots and slashes
    const wireTrace = (netId, d, color = "#0d9488", strokeWidth = 2.4, label = "", lx = 0, ly = 0, isBus = true, widthBits = 16) => {
      const meta = netDetails[netId] || { tag: label || "/16", title: label || netId, desc: "" };
      let res = `<g data-wire="${netId}" data-tag="${meta.tag}" data-title="${meta.title}" data-desc="${meta.desc}" class="circuit-wire">`;
      // Direct single conductor line
      res += P(d, color, strokeWidth, "none", 'stroke-linecap="round" stroke-linejoin="round"');

      // Clean bus width / signal badge
      if (label && lx && ly) {
        const badgeW = label.length * 6.4 + 10;
        res += `<g class="bus-badge" data-wire="${netId}">`;
        res += `<rect x="${lx - 2}" y="${ly - 9}" width="${badgeW}" height="15" rx="3" fill="#0f172a" stroke="${color}" stroke-width="1"/>`;
        res += `<text x="${lx + badgeW / 2 - 2}" y="${ly + 2}" font-family="Consolas,Liberation Mono,monospace" font-size="8" font-weight="bold" fill="${color}" text-anchor="middle">${label}</text>`;
        res += `</g>`;
      }
      res += "</g>";
      return res;
    };

    // =========================================================================
    // 1. EU 16-BIT CENTRAL DATA BUS SPINE (Connects Regs, Internal, Temps, ALU, OPR, IND)
    // Runs vertically in the spacious corridor at X = 555
    // =========================================================================
    // Main vertical highway spine
    g += wireTrace("internal-bus-spine", "M555 80V1184", "#0d9488", 4.2, "/16 INTERNAL BUS", 562, 420);

    // Regs read port (AX..DI) -> Internal Bus
    g += wireTrace("register-word", "M520 93H555", "#0d9488", 3.5);
    g += dot(555, 93, "#0d9488", 3.5);

    // Internal Crossbar Bus Main Tap <-> Internal Bus Highway Spine
    g += wireTrace("internal-bus-spine", "M520 425H555", "#0d9488", 3.8);
    g += dot(555, 425, "#0d9488", 3.8);

    // Internal Bus -> Regs writeback port
    g += wireTrace("alu-writeback", "M555 109H520", "#0d9488", 3.5);
    g += dot(555, 109, "#0d9488", 3.5);

    // CU Control -> Regs address select (PORT A/B/W)
    g += wireTrace("ctl-to-regs", "M1020 2140H20V139H40", "#7c3aed", 2.2);
    g += dot(40, 139, "#7c3aed", 3.2);

    // CU Control -> Internal Crossbar Bus Strobes
    g += wireTrace("ctl-to-regs", "M20 365H40", "#7c3aed", 2.2);
    g += dot(20, 365, "#7c3aed", 2.8);

    // Internal Bus -> Temporary latches (tmpA, tmpB, tmpC)
    g += wireTrace("temporary-load", "M555 610H520", "#0d9488", 3.5);
    g += dot(555, 610, "#0d9488", 3.5);

    // ALU 16-bit Result -> Internal Bus
    g += wireTrace("alu-writeback", "M520 1184H555", "#0d9488", 3.8, "/16 RESULT S[15:0]", 460, 1175);
    g += dot(555, 1184, "#0d9488", 4);

    // BIU OPR Transceiver <-> Internal Bus
    g += wireTrace("operand-data", "M620 880H555", "#0d9488", 3.5);
    g += dot(555, 880, "#0d9488", 3.5);

    // Internal Bus -> IND (Effective Address Offset Latch)
    g += wireTrace("effective-offset", "M555 380H1080", "#0d9488", 3.2, "/16 EA OFFSET", 730, 372);
    g += dot(555, 380, "#0d9488", 3.5);

    // =========================================================================
    // 2. ALU DATAPATH DIRECT WIRING (Temps -> MUX -> ALU, ALU -> Flags -> Engine)
    // CRITICAL FIX: Staggered 3-Track Multi-Channel Routing (Zero Overlap!)
    // Track A: Y = 762 (Sky Blue #0284c7)
    // Track B: Y = 774 (Emerald Green #059669)
    // Track C: Y = 786 (Amber #d97706)
    // =========================================================================
    // tmpA (x: 115, y: 750) -> MUX.tmpA (x: 325, y: 800)
    g += wireTrace("tmpa-select", "M115 750V765H325V800", "#0284c7", 2.4, "/16 tmpA", 160, 765);

    // tmpB (x: 235, y: 750) -> MUX.tmpB (x: 395, y: 800)
    g += wireTrace("tmpb-select", "M235 750V775H395V800", "#059669", 2.4, "/16 tmpB", 270, 775);

    // tmpC (x: 355, y: 750) -> MUX.tmpC (x: 465, y: 800)
    g += wireTrace("tmpc-select", "M355 750V785H465V800", "#d97706", 2.4, "/16 tmpC", 380, 785);

    // ALU Control Decoder (x: 270, y: 890) -> MUX SEL[1:0] (x: 285, y: 890)
    g += wireTrace("alu-control-fields", "M270 890H285", "#7c3aed", 2.0);

    // ALU Control Decoder (x: 110, y: 1010) -> ALU Function Controls (x: 110, y: 1060)
    g += wireTrace("alu-control-fields", "M110 1010V1060", "#7c3aed", 2.2, "ALU_CTRL [4:0]", 55, 1035);

    // MUX Out (x: 395, y: 1010) -> ALU Port A (x: 395, y: 1060)
    g += wireTrace("alu-first", "M395 1010V1060", "#0d9488", 2.8, "/16 OPERAND A", 335, 1035);

    // tmpB Direct Bypass (x: 520, y: 700) -> ALU Port B (x: 455, y: 1060)
    g += wireTrace("alu-second", "M520 700H535V1040H455V1060", "#0d9488", 2.4, "/16 OPERAND B", 450, 1045);

    // ALU (Bottom y: 1300) -> FLAGS (Top y: 1350): 6 dedicated parallel condition flag lines
    // 100% Planar Routing with Clear Signal Badges & Corridor Banner
    const flagMeta = [
      { x: 85, name: "OF" },
      { x: 155, name: "SF" },
      { x: 225, name: "ZF" },
      { x: 295, name: "AF" },
      { x: 365, name: "PF" },
      { x: 435, name: "CF" },
    ];
    g += `<text x="260" y="1312" font-family="Consolas,Liberation Mono,monospace" font-size="7.5" font-weight="bold" fill="#0d9488" text-anchor="middle" letter-spacing="0.5">6× RAW ALU CONDITION SIGNALS ➔ FLAGS REGISTER LATCHES</text>`;
    flagMeta.forEach((fm) => {
      g += wireTrace("flags-update", `M${fm.x} 1300V1350`, "#0d9488", 2.0);
      // Inline signal badge centered at Y = 1326
      g += `<g class="bus-badge" data-wire="flags-update">`;
      g += `<rect x="${fm.x - 12}" y="1320" width="24" height="13" rx="2.5" fill="#0f172a" stroke="#0d9488" stroke-width="1"/>`;
      g += `<text x="${fm.x}" y="1329.5" font-family="Consolas,Liberation Mono,monospace" font-size="7.5" font-weight="bold" fill="#2dd4bf" text-anchor="middle">${fm.name}</text>`;
      g += `</g>`;
    });

    // FLAGS Out (x: 520, y: 1430) -> Microcode Engine (x: 1020, y: 1900): 6 condition test lines
    g += wireTrace("flags-to-engine", "M520 1430H570V1880H1020", "#7c3aed", 2.5, "COND TESTS [5:0]", 600, 1872);

    // =========================================================================
    // 3. BIU 20-BIT ADDRESS PIPELINE (Seg -> SegMUX -> Adder <- OffMUX <- IP/IND)
    // CRITICAL FIX: Base Badge placed in wide open space, zero collision with pins!
    // =========================================================================
    // Segments (x: 830, y: 280) -> SegMUX (x: 830, y: 330)
    g += wireTrace("segment-input", "M830 280V330", "#d97706", 3.5, "/16 SEG_BASE", 845, 305);

    // SegMUX Out (x: 830, y: 510) -> 20-Bit Adder Port A (x: 830, y: 560) (Shifted Left 4 Bits)
    // Direct clean vertical line with zero pin collisions!
    g += wireTrace("base-to-adder", "M830 510V560", "#d97706", 3.8);

    // IP (x: 1295, y: 280) -> OffMUX (x: 1295, y: 560)
    g += wireTrace("fetch-offset", "M1295 280V560", "#d97706", 3.2, "/16 FETCH IP", 1305, 420);

    // IND (x: 1150, y: 510) -> OffMUX (x: 1150, y: 560)
    g += wireTrace("operand-offset", "M1150 510V560", "#d97706", 3.2);

    // OffMUX Out (x: 1080, y: 660) -> 20-Bit Adder Port B (x: 1040, y: 660)
    g += wireTrace("offset-to-adder", "M1080 660H1040", "#d97706", 3.5, "/16 OFFSET", 1045, 650);

    // Prefix Segment Override (x: 1235, y: 1640) -> SegMUX (x: 620, y: 420)
    g += wireTrace("prefix-override", "M1235 1640V1590H585V420H620", "#7c3aed", 2.2, "ES OVERRIDE", 590, 800);

    // 20-Bit Adder Output (x: 830, y: 770) -> Bus Controller (x: 830, y: 1060)
    g += wireTrace("physical-address", "M830 770V1060", "#d97706", 4.5, "/20 PHYS ADDR [19:0]", 845, 915);

    // 20-Bit Adder Feedback -> IP Incrementer Update (x: 830, y: 770 -> x: 1295, y: 60)
    g += wireTrace("ip-auto-increment", "M830 780H1060V220H1295V60", "#d97706", 2.5, "+2 PREFETCH IP", 900, 775);

    // =========================================================================
    // 4. INSTRUCTION PREFETCH QUEUE & MICROCODE EXECUTION ENGINE
    // =========================================================================
    // 8086 DIP-40 Pins (x: 1080, y: 1120) -> Prefetch Queue Input (x: 1080, y: 915)
    g += wireTrace("prefetch-fifo", "M1080 1120H1055V915H1080", "#0d9488", 3.5, "/16 PREFETCH WORD", 990, 1010);

    // Queue Output (x: 1295, y: 1020) -> Loader Left Input (x: 40, y: 1710)
    // Runs cleanly along Y=1570 into clear left margin at X=32, entering Loader at (40, 1710)
    // 100% Zero Collision with CU Header Title Text ("INSTRUCTION DECODE")!
    g += wireTrace("queue-to-loader", "M1295 1020V1570H32V1710H40", "#0d9488", 3.2, "/8 Q-BYTE STREAM", 660, 1562);

    // Loader (x: 490, y: 1740) -> IR Opcode Input (x: 530, y: 1740)
    g += wireTrace("loader-to-ir", "M490 1740H530", "#0d9488", 2.8, "/8 OPCODE", 480, 1732);

    // Loader ModR/M Out (x: 490, y: 1800) -> TROM Input (x: 530, y: 1940)
    g += wireTrace("loader-to-trom", "M490 1800H510V1940H530", "#7c3aed", 2.5, "MODR/M", 475, 1870);

    // IR Opcode Out (x: 755, y: 1840) -> PLA Group Decode (x: 490, y: 1940)
    g += wireTrace("ir-to-pla", "M755 1840V1860H510V1940H490", "#7c3aed", 2.5, "IR_OP", 610, 1852);

    // PLA Group Decode (x: 490, y: 2000) -> Microcode Engine (x: 1020, y: 2000)
    g += wireTrace("pla-to-engine", "M490 2000H1020", "#7c3aed", 3.2, "CLASS LINES [14:0]", 660, 1992);

    // TROM Branch Target (x: 980, y: 1940) -> Microcode Engine (x: 1020, y: 1940)
    g += wireTrace("trom-to-engine", "M980 1940H1020", "#7c3aed", 2.8, "/13 TARGET", 975, 1932);

    // Microcode Engine Next Address (x: 1260, y: 2080) -> MAR (x: 40, y: 2160)
    g += wireTrace("engine-to-mar", "M1260 2080V2095H20V2160H40", "#7c3aed", 3.2, "/13 NEXT µADDR", 460, 2090);

    // MAR Physical Address (x: 490, y: 2215) -> Microcode ROM (x: 530, y: 2215)
    g += wireTrace("mar-to-rom", "M490 2215H530", "#7c3aed", 3.5, "/13 µADDR", 480, 2207);

    // Microcode ROM (x: 980, y: 2215) -> Control Latches & Decoders (x: 1020, y: 2215)
    g += wireTrace("rom-to-ctl", "M980 2215H1020", "#7c3aed", 4.2, "/21 µWORD", 975, 2207);

    // Phase Sequencer (x: 980, y: 2445) -> Control Matrix (x: 1020, y: 2445)
    g += wireTrace("seq-to-dec", "M980 2445H1020", "#7c3aed", 3.2, "Q[2:0] + PAGE", 965, 2437);

    // =========================================================================
    // 5. OFF-CHIP SYSTEM BOARD INTERCONNECTS (8086 -> 8282, 8286, 74LS138, RAM, ROM)
    // =========================================================================
    // 8284A Clock Generator (x: 490, y: 2445) -> 8086 CLK Pin 19 (x: 1230, y: 2535) & Phase Sequencer (x: 530, y: 2445)
    g += wireTrace("clock-to-cpu", "M490 2445H510V2565H1230V2535", "#16a34a", 3.5, "5 MHz CLK (Pin 19)", 780, 2555);
    g += wireTrace("clock-to-seq", "M510 2445H530", "#16a34a", 2.8);
    g += dot(510, 2445, "#16a34a", 3.5);

    // 8086 ALE Strobe (Pin 25: x: 1510, y: 1220) -> 8282 Latches STB (x: 1610, y: 160)
    g += wireTrace("ale-to-latches", "M1510 1220H1550V160H1610", "#d97706", 3.2, "ALE STROBE (Pin 25)", 1515, 680);

    // 8086 Multiplexed Bus AD15..AD0 & A19..A16 (Pins 2-16, 35-39: x: 1510, y: 1150) -> 8282 & 8286
    g += wireTrace("ext-to-latches", "M1510 1150H1565V120H1610", "#0d9488", 4.5, "MUX AD[15:0] & A[19:16]", 1525, 520);
    g += wireTrace("ext-to-transceivers", "M1565 120H2140", "#0d9488", 4.5);
    g += dot(1565, 120, "#0d9488", 4.5);

    // 8086 Control Lines (DEN# Pin 26 & DT/R# Pin 27: x: 1510, y: 1290) -> 8286 Transceivers (x: 2140, y: 180)
    g += wireTrace("ctrl-to-transceivers", "M1510 1290H1535V25H2115V180H2140", "#7c3aed", 2.8, "DEN# & DT/R# (Pins 26/27)", 1760, 28);

    // 8282 Demultiplexed 20-bit System Address Bus A[19:0] (Bottom x: 1855, y: 290)
    g += wireTrace("latches-to-decoder", "M1855 290V320", "#d97706", 4.2, "/20 SYSTEM ADDR A[19:0]", 1865, 305);
    g += wireTrace("latches-to-ram", "M1855 320V570", "#d97706", 4.2, "/20 ADDR BUS A[19:1]", 1865, 470);
    g += dot(1855, 320, "#d97706", 4.5);

    // 8286 Isolated 16-bit System Data Bus D[15:0] (Bottom x: 2385, y: 290)
    g += wireTrace("transceivers-to-ram", "M2385 290V570", "#0d9488", 4.2, "/16 SYSTEM DATA D[15:0]", 2395, 470);

    // 74LS138 Decoder Output -> RAM Chip Select CS_RAM# (x: 1770, y: 530 -> y: 570)
    g += wireTrace("decoder-to-ram", "M1770 530V570", "#7c3aed", 2.8, "CS_RAM# (Y0#)", 1775, 550);

    // 74LS138 Decoder Output -> Boot ROM Chip Select CS_ROM# (x: 2100, y: 420 -> x: 2140, y: 420)
    g += wireTrace("decoder-to-bootrom", "M2100 420H2140", "#7c3aed", 2.8, "CS_ROM# (Y7#)", 2050, 412);

    // System Address Bus Tap -> Boot ROM Address Inputs (x: 1855, y: 350 -> x: 2140, y: 350)
    g += wireTrace("addr-to-bootrom", "M1855 350H2140", "#d97706", 3.2, "/13 ADDR", 1960, 343);
    g += dot(1855, 350, "#d97706", 3.5);

    // Boot ROM Data Out -> System Data Bus D[7:0] (x: 2385, y: 350 -> x: 2640, y: 420 -> x: 2385, y: 420)
    g += wireTrace("transceivers-to-bootrom", "M2385 350H2640V420H2385", "#0d9488", 3.2);

    // 8086 BHE# (Pin 34: x: 1510, y: 1100) -> RAM Odd Bank Select BHE# (x: 1990, y: 570)
    g += wireTrace("bhe-to-ram", "M1510 1100H1525V550H1990V570", "#7c3aed", 2.2, "BHE# (Pin 34)", 1670, 545);

    // 8086 RD# and WR# (Pins 32/29: x: 1510, y: 1260) -> RAM OE# and WE# (x: 1690, y: 570)
    g += wireTrace("rd-wr-to-ram", "M1510 1260H1530V560H1690V570", "#7c3aed", 2.5, "RD# / WR#", 1545, 800);

    g += "</g>";
    return g;
  }

  // 40 Intel 8086 perimeter wire bonding pads matching nand2mario / Intel 8086 silicon die
  function drawDieBondingPads(activePins) {
    const pads = [
      // Left Edge: Pins 1..10 (top to bottom)
      { pin: 1, name: "GND", edge: "left", x: 9, y: 110 },
      { pin: 2, name: "AD14", edge: "left", x: 9, y: 250 },
      { pin: 3, name: "AD13", edge: "left", x: 9, y: 390 },
      { pin: 4, name: "AD12", edge: "left", x: 9, y: 530 },
      { pin: 5, name: "AD11", edge: "left", x: 9, y: 670 },
      { pin: 6, name: "AD10", edge: "left", x: 9, y: 810 },
      { pin: 7, name: "AD9", edge: "left", x: 9, y: 950 },
      { pin: 8, name: "AD8", edge: "left", x: 9, y: 1090 },
      { pin: 9, name: "AD7", edge: "left", x: 9, y: 1230 },
      { pin: 10, name: "AD6", edge: "left", x: 9, y: 1370 },

      // Bottom Edge: Pins 11..20 (left to right)
      { pin: 11, name: "AD5", edge: "bottom", x: 110, y: 2535 },
      { pin: 12, name: "AD4", edge: "bottom", x: 250, y: 2535 },
      { pin: 13, name: "AD3", edge: "bottom", x: 390, y: 2535 },
      { pin: 14, name: "AD2", edge: "bottom", x: 530, y: 2535 },
      { pin: 15, name: "AD1", edge: "bottom", x: 670, y: 2535 },
      { pin: 16, name: "AD0", edge: "bottom", x: 810, y: 2535 },
      { pin: 17, name: "NMI", edge: "bottom", x: 950, y: 2535 },
      { pin: 18, name: "INTR", edge: "bottom", x: 1090, y: 2535 },
      { pin: 19, name: "CLK", edge: "bottom", x: 1230, y: 2535 },
      { pin: 20, name: "GND", edge: "bottom", x: 1370, y: 2535 },

      // Right Edge of Die: Pins 21..30 (bottom to top)
      { pin: 21, name: "RESET", edge: "right", x: 1526, y: 2420 },
      { pin: 22, name: "READY", edge: "right", x: 1526, y: 2280 },
      { pin: 23, name: "TEST#", edge: "right", x: 1526, y: 2140 },
      { pin: 24, name: "QS1", edge: "right", x: 1526, y: 2000 },
      { pin: 25, name: "QS0", edge: "right", x: 1526, y: 1860 },
      { pin: 26, name: "DEN#", edge: "right", x: 1526, y: 1720 },
      { pin: 27, name: "DT/R#", edge: "right", x: 1526, y: 1580 },
      { pin: 28, name: "M/IO#", edge: "right", x: 1526, y: 1440 },
      { pin: 29, name: "WR#", edge: "right", x: 1526, y: 1300 },
      { pin: 30, name: "ALE", edge: "right", x: 1526, y: 1160 },

      // Top Edge: Pins 31..40 (right to left)
      { pin: 31, name: "INTA#", edge: "top", x: 1380, y: 14 },
      { pin: 32, name: "RD#", edge: "top", x: 1240, y: 14 },
      { pin: 33, name: "MN/MX#", edge: "top", x: 1100, y: 14 },
      { pin: 34, name: "BHE#", edge: "top", x: 960, y: 14 },
      { pin: 35, name: "A19/S6", edge: "top", x: 820, y: 14 },
      { pin: 36, name: "A18/S5", edge: "top", x: 680, y: 14 },
      { pin: 37, name: "A17/S4", edge: "top", x: 540, y: 14 },
      { pin: 38, name: "A16/S3", edge: "top", x: 400, y: 14 },
      { pin: 39, name: "AD15", edge: "top", x: 260, y: 14 },
      { pin: 40, name: "VCC", edge: "top", x: 120, y: 14 },
    ];

    let g = '<g class="silicon-bonding-pads" id="bonding-pads">';
    for (const p of pads) {
      const isAct = activePins && activePins.has(p.name);
      const padFill = isAct ? "#fef08a" : "#ca8a04";
      const padStroke = isAct ? "#10b981" : "#854d0e";
      const pw = p.edge === "left" || p.edge === "right" ? (p.edge === "left" ? 10 : 18) : 36;
      const ph = p.edge === "left" || p.edge === "right" ? (p.edge === "left" ? 22 : 36) : 18;

      // Gold bonding pad on silicon perimeter
      g += R(p.x - pw / 2, p.y - ph / 2, pw, ph, padFill, padStroke, 2, isAct ? 2 : 1.2);

      // Gold bond wire curving into the die
      const wireD = p.edge === "left" ? `M${p.x + pw/2} ${p.y}H20`
                  : p.edge === "right" ? `M${p.x - pw/2} ${p.y}H${p.x - pw/2 - 16}`
                  : p.edge === "top" ? `M${p.x} ${p.y + ph/2}V${p.y + ph/2 + 16}`
                  : `M${p.x} ${p.y - ph/2}V${p.y - ph/2 - 16}`;
      g += P(wireD, isAct ? "#10b981" : "#eab308", isAct ? 2.5 : 1.6);
      g += dot(p.x, p.y, isAct ? "#10b981" : "#a16207", 2.2);

      // Text label: top edge labels sit neatly inside the gold bonding pad, zero spillover
      const tx = p.edge === "left" ? p.x
               : p.edge === "right" ? p.x - pw / 2 - 18
               : p.x;
      const ty = p.edge === "left" ? p.y - ph / 2 - 3
               : p.edge === "top" ? p.y + 3.5
               : p.edge === "bottom" ? p.y - ph / 2 - 10
               : p.y + 3.5;
      const anchor = p.edge === "left" ? "middle" : p.edge === "right" ? "end" : "middle";
      const fsize = p.edge === "left" ? 5.2 : (p.edge === "top" ? 6.5 : 8);
      const textFill = isAct ? (p.edge === "top" ? "#166534" : "#10b981") : (p.edge === "top" ? "#78350f" : "#cbd5e1");
      g += txt(tx, ty, `${p.pin}:${p.name}`, fsize, textFill, anchor, true);
    }
    g += '</g>';
    return g;
  }

  // High-performance clean architectural block representation when zoomed out (scale < 1.4)
  function drawMacroPreview(id, x, y, w, h, s, grp) {
    let out = "";
    const cx = x + w / 2;
    const cy = y + h / 2 + 8;
    const hex = (v, n = 4) => (v != null ? (v >>> 0).toString(16).toUpperCase().padStart(n, "0") : "0000");

    if (id === "regs") {
      const regs1 = [
        ["AX", s.ax ?? 0],
        ["BX", s.bx ?? 0],
        ["CX", s.cx ?? 0],
        ["DX", s.dx ?? 0],
      ];
      const regs2 = [
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
      const calc = cpu.calculate ? cpu.calculate() : { word: 0, flags: {} };
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
      const calc = cpu.calculate ? cpu.calculate() : { flags: {} };
      const flist = ["CF", "PF", "AF", "ZF", "SF", "OF", "TF", "IF", "DF"];
      const fw = (w - 30) / 9;
      flist.forEach((f, i) => {
        const val = calc.flags[f] || (f === "IF" ? 1 : 0);
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
      const segs = [
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

  // Draw continuous bridge traces linking outer copper terminal pins to internal schematic nodes
  function drawComponentPinBridges(id, x, y, w, h, X, Y0, ratio, activeSet) {
    let out = '<g class="internal-pin-bridges">';

    const drawBridge = (px, py, lx, ly, netId, color = "#0d9488", strokeWidth = 2.0) => {
      let targetX = X + lx * ratio;
      let targetY = Y0 + ly * ratio;

      let d = "";
      if (Math.abs(px - x) < 3 || Math.abs(px - (x + w)) < 3) {
        // Left/Right pin: check if targetY aligns with py (within 1.5px tolerance for crisp horizontal line)
        if (Math.abs(py - targetY) < 1.5) targetY = py;
        d = (py === targetY) ? `M${px} ${py} H${targetX}` : `M${px} ${py} V${targetY} H${targetX}`;
      } else {
        // Top/Bottom pin: check if targetX aligns with px
        if (Math.abs(px - targetX) < 1.5) targetX = px;
        d = (px === targetX) ? `M${px} ${py} V${targetY}` : `M${px} ${py} H${targetX} V${targetY}`;
      }

      const meta = netDetails[netId] || { tag: "/16", title: netId, desc: "Internal unit bridge lead" };
      let res = `<g data-wire="${netId}" data-tag="${meta.tag}" data-title="${meta.title}" data-desc="${meta.desc}" class="circuit-wire bridge-wire">`;
      // Direct single conductor line
      res += P(d, color, strokeWidth, "none", 'stroke-linecap="round" stroke-linejoin="round"');
      // Solder joint dot at internal circuit connection
      res += dot(targetX, targetY, color, 2.2);
      res += `</g>`;
      return res;
    };

    // Table of pin-to-internal linkages for all units
    const pinMap = {
      regs: [
        { px: x, py: y + 79, lx: 10, ly: 146, netId: "ctl-to-regs", color: "#7c3aed" },
        { px: x + w, py: y + 33, lx: 1272, ly: 20, netId: "register-word", color: "#0d9488" },
        { px: x + w, py: y + 49, lx: 1272, ly: 64, netId: "alu-writeback", color: "#0d9488" },
      ],
      internal: [
        { px: x, py: y + 25, lx: 15, ly: 35, netId: "ctl-to-regs", color: "#7c3aed" },
        { px: x + w, py: y + 85, lx: 445, ly: 70, netId: "internal-bus-spine", color: "#0d9488" },
      ],
      temps: [
        { px: x + w, py: y + 60, lx: 455, ly: 22, netId: "temporary-load", color: "#0d9488" },
        { px: x + 75, py: y + h, lx: 75, ly: 216, netId: "tmpa-select", color: "#0284c7" },
        { px: x + 195, py: y + h, lx: 205, ly: 216, netId: "tmpb-select", color: "#059669" },
        { px: x + 315, py: y + h, lx: 335, ly: 216, netId: "tmpc-select", color: "#d97706" },
      ],
      aluctl: [
        { px: x + w, py: y + 90, lx: 360, ly: 90, netId: "alu-control-fields", color: "#7c3aed" },
        { px: 110, py: y + h, lx: 106, ly: 200, netId: "alu-control-fields", color: "#7c3aed" },
      ],
      mux: [
        { px: x + 40, py: y, lx: 80, ly: 0, netId: "tmpa-select", color: "#0284c7" },
        { px: x + 110, py: y, lx: 190, ly: 0, netId: "tmpb-select", color: "#059669" },
        { px: x + 180, py: y, lx: 300, ly: 0, netId: "tmpc-select", color: "#d97706" },
        { px: x, py: y + 90, lx: 0, ly: 70, netId: "alu-control-fields", color: "#7c3aed" },
        { px: 395, py: y + h, lx: 190, ly: 220, netId: "alu-first", color: "#0d9488" },
      ],
      alu: [
        { px: 110, py: y, lx: 175, ly: 6, netId: "alu-control-fields", color: "#7c3aed" },
        { px: 395, py: y, lx: 955, ly: 6, netId: "alu-first", color: "#0d9488" },
        { px: 455, py: y, lx: 1119, ly: 6, netId: "alu-second", color: "#0d9488" },
        { px: x + w, py: 1184, lx: 1270, ly: 268, netId: "alu-writeback", color: "#0d9488" },
        { px: 85, py: y + h, lx: 107, ly: 554, netId: "flags-update", color: "#0d9488" },
        { px: 155, py: y + h, lx: 298, ly: 554, netId: "flags-update", color: "#0d9488" },
        { px: 225, py: y + h, lx: 490, ly: 554, netId: "flags-update", color: "#0d9488" },
        { px: 295, py: y + h, lx: 681, ly: 554, netId: "flags-update", color: "#0d9488" },
        { px: 365, py: y + h, lx: 872, ly: 554, netId: "flags-update", color: "#0d9488" },
        { px: 435, py: y + h, lx: 1064, ly: 554, netId: "flags-update", color: "#0d9488" },
      ],
      flags: [
        { px: 85, py: y, lx: 107, ly: 6, netId: "flags-update", color: "#0d9488" },
        { px: 155, py: y, lx: 298, ly: 6, netId: "flags-update", color: "#0d9488" },
        { px: 225, py: y, lx: 490, ly: 6, netId: "flags-update", color: "#0d9488" },
        { px: 295, py: y, lx: 681, ly: 6, netId: "flags-update", color: "#0d9488" },
        { px: 365, py: y, lx: 872, ly: 6, netId: "flags-update", color: "#0d9488" },
        { px: 435, py: y, lx: 1064, ly: 6, netId: "flags-update", color: "#0d9488" },
        { px: x + w, py: y + 80, lx: 1270, ly: 208, netId: "flags-to-engine", color: "#7c3aed" },
      ],
      seg: [
        { px: x + 210, py: y + h, lx: 200, ly: 165, netId: "segment-input", color: "#d97706" },
      ],
      segmux: [
        { px: x + 210, py: y, lx: 205, ly: 25, netId: "segment-input", color: "#d97706" },
        { px: x, py: y + 90, lx: 25, ly: 81, netId: "prefix-override", color: "#7c3aed" },
        { px: x + 210, py: y + h, lx: 205, ly: 155, netId: "base-to-adder", color: "#d97706" },
      ],
      adder: [
        { px: x + 210, py: y, lx: 204, ly: 0, netId: "base-to-adder", color: "#d97706" },
        { px: x + w, py: y + 100, lx: 408, ly: 80, netId: "offset-to-adder", color: "#d97706" },
        { px: x + 210, py: y + h, lx: 204, ly: 186, netId: "physical-address", color: "#d97706" },
      ],
      ip: [
        { px: x + 215, py: y, lx: 190, ly: 25, netId: "ip-auto-increment", color: "#d97706" },
        { px: x + 215, py: y + h, lx: 190, ly: 165, netId: "fetch-offset", color: "#d97706" },
      ],
      ind: [
        { px: x, py: y + 50, lx: 10, ly: 33, netId: "effective-offset", color: "#0d9488" },
        { px: x + 70, py: y + h, lx: 12, ly: 145, netId: "operand-offset", color: "#d97706" },
      ],
      offmux: [
        { px: x + 70, py: y, lx: 30, ly: 25, netId: "operand-offset", color: "#d97706" },
        { px: x + 215, py: y, lx: 170, ly: 25, netId: "fetch-offset", color: "#d97706" },
        { px: x, py: y + 100, lx: 20, ly: 77, netId: "offset-to-adder", color: "#d97706" },
      ],
      opr: [
        { px: x, py: y + 70, lx: 25, ly: 51, netId: "operand-data", color: "#0d9488" },
      ],
      queue: [
        { px: x, py: y + 105, lx: 20, ly: 87, netId: "prefetch-fifo", color: "#0d9488" },
        { px: x + 215, py: y + h, lx: 220, ly: 150, netId: "queue-to-loader", color: "#0d9488" },
      ],
      memory: [
        { px: x + 210, py: y, lx: 204, ly: 0, netId: "physical-address", color: "#d97706" },
        { px: x + w, py: y + 70, lx: 408, ly: 50, netId: "ale-to-latches", color: "#d97706" },
        { px: x + w, py: y + 96, lx: 408, ly: 76, netId: "ctrl-to-transceivers", color: "#7c3aed" },
      ],
      loader: [
        { px: x, py: y + 70, lx: 20, ly: 60, netId: "queue-to-loader", color: "#0d9488" },
        { px: x + w, py: y + 100, lx: 380, ly: 65, netId: "loader-to-ir", color: "#0d9488" },
        { px: x + w, py: y + 160, lx: 380, ly: 140, netId: "loader-to-trom", color: "#7c3aed" },
      ],
      ir: [
        { px: x, py: y + 100, lx: 20, ly: 85, netId: "loader-to-ir", color: "#0d9488" },
        { px: x + w, py: y + 100, lx: 320, ly: 85, netId: "ir-to-pla", color: "#7c3aed" },
      ],
      prefix: [
        { px: x, py: y + 100, lx: 25, ly: 85, netId: "queue-to-loader", color: "#0d9488" },
        { px: x + w, py: y + 100, lx: 335, ly: 85, netId: "prefix-override", color: "#7c3aed" },
      ],
      pla: [
        { px: x, py: y + 60, lx: 30, ly: 30, netId: "ir-to-pla", color: "#7c3aed" },
        { px: x + w, py: y + 120, lx: 390, ly: 100, netId: "pla-to-engine", color: "#7c3aed" },
      ],
      trom: [
        { px: x, py: y + 60, lx: 50, ly: 25, netId: "loader-to-trom", color: "#7c3aed" },
        { px: x + w, py: y + 60, lx: 380, ly: 100, netId: "trom-to-engine", color: "#7c3aed" },
      ],
      engine: [
        { px: x, py: y + 60, lx: 25, ly: 60, netId: "trom-to-engine", color: "#7c3aed" },
        { px: x, py: y + 120, lx: 25, ly: 120, netId: "pla-to-engine", color: "#7c3aed" },
        { px: x + 240, py: y + h, lx: 200, ly: 160, netId: "engine-to-mar", color: "#7c3aed" },
      ],
      mar: [
        { px: x, py: y + 40, lx: 25, ly: 85, netId: "engine-to-mar", color: "#7c3aed" },
        { px: x + w, py: y + 95, lx: 335, ly: 85, netId: "mar-to-rom", color: "#7c3aed" },
      ],
      rom: [
        { px: x, py: y + 95, lx: 25, ly: 90, netId: "mar-to-rom", color: "#7c3aed" },
        { px: x + w, py: y + 95, lx: 395, ly: 90, netId: "rom-to-ctl", color: "#7c3aed" },
      ],
      ctl: [
        { px: x, py: y + 95, lx: 25, ly: 85, netId: "rom-to-ctl", color: "#7c3aed" },
        { px: x, py: y + 20, lx: 25, ly: 20, netId: "ctl-to-regs", color: "#7c3aed" },
      ],
      clk: [
        { px: x + w, py: y + 95, lx: 420, ly: 105, netId: "clock-to-cpu", color: "#16a34a" },
      ],
      seq: [
        { px: x, py: y + 95, lx: 25, ly: 95, netId: "clock-to-seq", color: "#16a34a" },
        { px: x + w, py: y + 95, lx: 380, ly: 95, netId: "seq-to-dec", color: "#7c3aed" },
      ],
      ext: [
        { px: x, py: y + 60, lx: 14, ly: 40, netId: "prefetch-fifo", color: "#0d9488" },
        { px: x + w, py: y + 90, lx: 408, ly: 70, netId: "ext-to-latches", color: "#0d9488" },
        { px: x + w, py: y + 160, lx: 408, ly: 140, netId: "ale-to-latches", color: "#d97706" },
        { px: x + w, py: y + 230, lx: 408, ly: 210, netId: "ctrl-to-transceivers", color: "#7c3aed" },
      ],
      latches: [
        { px: x, py: y + 60, lx: 25, ly: 70, netId: "ext-to-latches", color: "#0d9488" },
        { px: x, py: y + 100, lx: 25, ly: 115, netId: "ale-to-latches", color: "#d97706" },
        { px: x + 245, py: y + h, lx: 235, ly: 165, netId: "latches-to-decoder", color: "#d97706" },
      ],
      transceivers: [
        { px: x, py: y + 60, lx: 25, ly: 75, netId: "ext-to-transceivers", color: "#0d9488" },
        { px: x, py: y + 120, lx: 25, ly: 125, netId: "ctrl-to-transceivers", color: "#7c3aed" },
        { px: x + 245, py: y + h, lx: 235, ly: 160, netId: "transceivers-to-ram", color: "#0d9488" },
      ],
      decoder: [
        { px: x + 245, py: y, lx: 60, ly: 30, netId: "latches-to-decoder", color: "#d97706" },
        { px: x + 160, py: y + h, lx: 380, ly: 70, netId: "decoder-to-ram", color: "#7c3aed" },
        { px: x + w, py: y + 90, lx: 380, ly: 155, netId: "decoder-to-bootrom", color: "#7c3aed" },
      ],
      ram: [
        { px: x + 160, py: y, lx: 150, ly: 25, netId: "decoder-to-ram", color: "#7c3aed" },
        { px: x + 245, py: y, lx: 320, ly: 25, netId: "latches-to-ram", color: "#d97706" },
        { px: x + 775, py: y, lx: 760, ly: 25, netId: "transceivers-to-ram", color: "#0d9488" },
      ],
      bootrom: [
        { px: x, py: y + 90, lx: 25, ly: 85, netId: "decoder-to-bootrom", color: "#7c3aed" },
        { px: x + 245, py: y + h, lx: 200, ly: 150, netId: "rom-data", color: "#e11d48" },
      ],
    };

    const bridges = pinMap[id];
    if (bridges) {
      bridges.forEach(b => {
        out += drawBridge(b.px, b.py, b.lx, b.ly, b.netId, b.color, b.width || 2.4);
      });
    }

    out += '</g>';
    return out;
  }

  function render(scale, sel, bit, vr) {
    const active = activeIds();
    const isMacro = scale < 1.4;
    currentIsMacro = isMacro;

    const activePinSet = new Set();
    const phase = (cpu.s.phase || 0) % 4;
    activePinSet.add("CLK");
    activePinSet.add("VCC");
    activePinSet.add("GND");
    if (phase === 0) activePinSet.add("ALE");
    if (phase >= 2) {
      activePinSet.add("RD#");
      activePinSet.add("DEN#");
      activePinSet.add("DT/R#");
    }
    if (cpu.s.op === "SUB" || cpu.s.op === "ADD") activePinSet.add("READY");

    let g = '<defs>';
    g += '<marker id="tip-norm" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#0d9488" stroke-width="1.6"/></marker>';
    g += '<marker id="tip-high" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#10b981" stroke-width="2.2"/></marker>';
    g += '<pattern id="silicon-grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#182c24" stroke-width="0.8"/></pattern>';
    g += '</defs>';

    // 0. Silicon Wafer Substrate & Inspection Scope Ruler Grid
    g += `<rect width="${W}" height="${H}" fill="#0b1713"/>`;
    g += `<rect width="${W}" height="${H}" fill="url(#silicon-grid)"/>`;

    // 1. Draw Silicon Macro Boundaries with Lithography Fiducials
    g += drawUnitFrame(20, 20, 520, 1560, "EU", "EXECUTION UNIT (EU) · 16-BIT DATA PATH, DUAL-PORT REGISTERS & ALU");
    g += drawUnitFrame(610, 20, 930, 1560, "BIU", "BUS INTERFACE UNIT (BIU) · SEGMENTS, 20-BIT ADDER, QUEUE & DIP-40");
    g += drawUnitFrame(20, 1600, 1520, 950, "CU", "CONTROL UNIT (CU) · INSTRUCTION DECODE, MICROCODE ROM & SEQUENCER");
    g += drawUnitFrame(1570, 20, 1110, 2530, "SYS", "SYSTEM BOARD (SYS) · 8282 LATCHES, 8286 TRANSCEIVERS, 74LS138, 16-BIT RAM & ROM");

    // 2. Draw 40 Silicon Die Wire Bonding Pads (Intel 8086 Physical Die Perimeter)
    g += drawDieBondingPads(activePinSet);

    // 3. Draw Continuous Physical Interconnect Wiring Highway (100% Linked Wires)
    g += drawContinuousInterconnects(active);

    // 4. Render all 34 Hardware Components (with Viewport Culling and Dynamic LOD)
    for (const [id, [x, y, w, h, title, group]] of Object.entries(N)) {
      // Viewport culling in detail mode for 60 FPS performance
      if (!isMacro && vr && (x + w < vr.x1 || x > vr.x2 || y + h < vr.y1 || y > vr.y2)) {
        continue;
      }

      const s = unitStyles[group] || unitStyles.EU;
      const logic = getComponentLogic(id, cpu.s, bit);
      const vw = (logic && logic.vw) ? logic.vw : 400;
      const vh = (logic && logic.vh) ? logic.vh : 200;

      let compSvg = "";
      // Outer card box
      compSvg += R(x, y, w, h, isMacro ? s.fill : "#ffffff", s.stroke, 3, isMacro ? 1.4 : 1.6);
      // Header strip
      const hdrH = isMacro ? 20 : 16;
      compSvg += R(x, y, w, hdrH, s.banner, s.stroke, 3, 0.8);
      // Header title: in detail mode, clean and compact so it never overflows
      let cleanTitle = isMacro ? title : (title.includes(" · ") ? title.split(" · ")[0] : title.split(" (")[0]);
      let titleX = x + 8;
      if (id === "alu") {
        titleX = x + 130; // Clear of top ALU_OP contact pad at px = 110!
      } else if (id === "flags" && !isMacro) {
        cleanTitle = "FLAGS";
        titleX = x + 445; // Clear of all 6 top incoming ALU flag pins ending at px = 435!
      } else if (id === "mux" && !isMacro) {
        cleanTitle = "ALU MUX";
      }
      compSvg += txt(titleX, y + (isMacro ? 14 : 12), cleanTitle, isMacro ? 8.5 : 7.2, s.title, "start", true);

      // Dedicated Copper Contact Terminal Pin Pads along the component perimeter
      if (id === "regs") {
        compSvg += terminalPin(x, y + 79, "REG_SEL[2:0]", "left");
        compSvg += terminalPin(x + w, y + 33, "D_OUT[15:0]", "right");
        compSvg += terminalPin(x + w, y + 49, "D_IN[15:0]", "right");
      } else if (id === "internal") {
        compSvg += terminalPin(x, y + 25, "µCODE_CTL", "left");
        compSvg += terminalPin(x + w, y + 85, "BUS[15:0]", "right");
      } else if (id === "temps") {
        compSvg += terminalPin(x + w, y + 60, "D_IN[15:0]", "right");
        compSvg += terminalPin(x + 75, y + h, "tmpA[15:0]", "bottom");
        compSvg += terminalPin(x + 195, y + h, "tmpB[15:0]", "bottom");
        compSvg += terminalPin(x + 315, y + h, "tmpC[15:0]", "bottom");
      } else if (id === "aluctl") {
        compSvg += terminalPin(x + w, y + 90, "SEL[1:0]", "right");
        compSvg += terminalPin(110, y + h, "ALU_OP", "bottom");
      } else if (id === "mux") {
        compSvg += terminalPin(x + 40, y, "tmpA", "top");
        compSvg += terminalPin(x + 110, y, "tmpB", "top");
        compSvg += terminalPin(x + 180, y, "tmpC", "top");
        compSvg += terminalPin(x, y + 90, "SEL[1:0]", "left");
        compSvg += terminalPin(395, y + h, "ALU_A[15:0]", "bottom");
      } else if (id === "alu") {
        compSvg += terminalPin(110, y, "ALU_OP", "top");
        compSvg += terminalPin(395, y, "IN_A[15:0]", "top");
        compSvg += terminalPin(455, y, "IN_B[15:0]", "top");
        compSvg += terminalPin(x + w, 1184, "RESULT[15:0]", "right");
        compSvg += terminalPin(85, y + h, "OF", "bottom");
        compSvg += terminalPin(155, y + h, "SF", "bottom");
        compSvg += terminalPin(225, y + h, "ZF", "bottom");
        compSvg += terminalPin(295, y + h, "AF", "bottom");
        compSvg += terminalPin(365, y + h, "PF", "bottom");
        compSvg += terminalPin(435, y + h, "CF", "bottom");
      } else if (id === "flags") {
        compSvg += terminalPin(85, y, "OF", "top");
        compSvg += terminalPin(155, y, "SF", "top");
        compSvg += terminalPin(225, y, "ZF", "top");
        compSvg += terminalPin(295, y, "AF", "top");
        compSvg += terminalPin(365, y, "PF", "top");
        compSvg += terminalPin(435, y, "CF", "top");
        compSvg += terminalPin(x + w, y + 80, "COND[5:0]", "right");
      } else if (id === "loader") {
        compSvg += terminalPin(x, y + 70, "FIFO_IN[7:0]", "left");
        compSvg += terminalPin(x + w, y + 100, "OPCODE[7:0]", "right");
        compSvg += terminalPin(x + w, y + 160, "MODR/M", "right");
      } else if (id === "seg") {
        compSvg += terminalPin(x + 210, y + h, "SEG[15:0]", "bottom");
      } else if (id === "ip") {
        compSvg += terminalPin(x + 215, y + h, "IP[15:0]", "bottom");
        compSvg += terminalPin(x + 215, y, "+2_INC", "top");
      } else if (id === "ind") {
        compSvg += terminalPin(x + 70, y + h, "IND[15:0]", "bottom");
        compSvg += terminalPin(x, y + 50, "EA_IN", "left");
      } else if (id === "segmux") {
        compSvg += terminalPin(x + 210, y, "SEG_IN", "top");
        compSvg += terminalPin(x, y + 90, "OVERRIDE", "left");
        compSvg += terminalPin(x + 210, y + h, "BASE[19:0]", "bottom");
      } else if (id === "adder") {
        compSvg += terminalPin(x + 210, y, "BASE[19:0]", "top");
        compSvg += terminalPin(x + w, y + 100, "OFFSET[15:0]", "right");
        compSvg += terminalPin(x + 210, y + h, "PHYS_ADDR[19:0]", "bottom");
      } else if (id === "offmux") {
        compSvg += terminalPin(x, y + 100, "OFFSET[15:0]", "left");
        compSvg += terminalPin(x + 70, y, "IND_IN", "top");
        compSvg += terminalPin(x + 215, y, "IP_IN", "top");
      } else if (id === "opr") {
        compSvg += terminalPin(x, y + 70, "D_IN/OUT", "left");
      } else if (id === "queue") {
        compSvg += terminalPin(x, y + 105, "FIFO_IN[15:0]", "left");
        compSvg += terminalPin(x + 215, y + h, "Q_BYTE[7:0]", "bottom");
      } else if (id === "seq") {
        compSvg += terminalPin(x, y + 95, "5MHz_CLK", "left");
        compSvg += terminalPin(x + w, y + 95, "Q[2:0]", "right");
      } else if (id === "memory") {
        compSvg += terminalPin(x + 210, y, "PHYS_ADDR[19:0]", "top");
        compSvg += terminalPin(x + w, y + 70, "ALE", "right");
        compSvg += terminalPin(x + w, y + 96, "DEN#/DIR", "right");
      } else if (id === "ext") {
        compSvg += terminalPin(x, y + 60, "FIFO_REQ", "left");
        compSvg += terminalPin(x + w, y + 90, "AD[15:0]", "right");
        compSvg += terminalPin(x + w, y + 160, "ALE", "right");
        compSvg += terminalPin(x + w, y + 230, "DEN#/DIR", "right");
      } else if (id === "latches") {
        compSvg += terminalPin(x, y + 60, "AD[15:0]", "left");
        compSvg += terminalPin(x, y + 100, "ALE_STB", "left");
        compSvg += terminalPin(x + 245, y + h, "A[19:0]", "bottom");
      } else if (id === "transceivers") {
        compSvg += terminalPin(x, y + 60, "AD[15:0]", "left");
        compSvg += terminalPin(x, y + 120, "DEN#/DIR", "left");
        compSvg += terminalPin(x + 245, y + h, "D[15:0]", "bottom");
      } else if (id === "decoder") {
        compSvg += terminalPin(x + 245, y, "A[19:16]", "top");
        compSvg += terminalPin(x + 160, y + h, "CS_RAM#", "bottom");
        compSvg += terminalPin(x + w, y + 90, "CS_ROM#", "right");
      } else if (id === "bootrom") {
        compSvg += terminalPin(x, y + 90, "CS_ROM#", "left");
        compSvg += terminalPin(x + 245, y + h, "D[7:0]", "bottom");
      } else if (id === "ram") {
        compSvg += terminalPin(x + 245, y, "A[19:1]", "top");
        compSvg += terminalPin(x + 160, y, "CS_RAM#", "top");
        compSvg += terminalPin(x + 775, y, "D[15:0]", "top");
      } else if (id === "clk") {
        compSvg += terminalPin(x + w, y + 95, "5MHz_CLK", "right");
      }

      // Dynamic Level-of-Detail (LOD):
      // When zoomed out (scale < 1.4): render clean, high-performance macro representation (NO gate clutter).
      // When zoomed in (scale >= 1.4): render FULL-SIZE crisp electrical logic schematic filling the card!
      if (isMacro) {
        compSvg += drawMacroPreview(id, x, y, w, h, cpu.s, group);
      } else if (logic && logic.body) {
        const padX = 6;
        const padY = hdrH + 4;
        const availW = w - padX * 2;
        const availH = h - padY - 4;
        const ratio = Math.min(availW / vw, availH / vh);
        const X = x + padX + (availW - vw * ratio) / 2;
        const Y0 = y + padY + (availH - vh * ratio) / 2;
        compSvg += `<g data-logic="${id}" transform="translate(${X} ${Y0}) scale(${ratio})">${logic.body}</g>`;
        compSvg += drawComponentPinBridges(id, x, y, w, h, X, Y0, ratio, active);
      }

      // Selection highlight ring
      if (id === sel) {
        compSvg += R(x - 3, y - 3, w + 6, h + 6, "none", "#10b981", 6, 3);
      }

      // Clickable container for interaction
      g +=
        `<g class="cpu-node" data-node="${id}" role="button" tabindex="0" aria-label="Inspect ${title}">` +
        `<title>${title} · Click to inspect, double-click to focus</title>` +
        compSvg +
        R(x, y, w, h, "transparent", "none", 0, 0) +
        `</g>`;
    }

    return g;
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
    reflow: (scale, cy) => cy,
    Y: (y) => y,
    unmap: (v) => v,
    activeIds,
    expanded: () => true,
  };
})();
