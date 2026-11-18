/* The coordinates and named terminals come from the user's corrected notebook.
   Semantic zoom allocates more vertical room to the ALU and reroutes the
   adjoining net segments through the same terminals. */
(() => {
  const {
    T,
    mono,
    R,
    P,
    dot,
    tinyGate,
    adderLogic,
    decoderLogic,
    sequencerLogic,
  } = logicDraw;
  const book = notebookSheet,
    W = 1260;
  const spec = {
    regs: [106, 141, 452, 226, "Register file", "EU"],
    internal: [106, 405, 453, 35, "Internal data bus", "EU"],
    temps: [135, 493, 423, 70, "Operand latches", "EU"],
    aluctl: [100, 585, 179, 49, "ALU control decode", "EU"],
    mux: [295, 596, 133, 28, "Input select", "EU"],
    alu: [190, 646, 350, 73, "Arithmetic logic unit", "EU"],
    flags: [110, 775, 480, 85, "FLAGS", "EU"],
    seg: [743, 141, 247, 124, "Segment registers", "BIU"],
    ip: [1030, 141, 146, 52, "IP", "BIU"],
    ind: [1030, 220, 146, 52, "IND", "BIU"],
    segmux: [745, 322, 230, 53, "Segment select", "BIU"],
    offmux: [1006, 322, 170, 53, "Offset select", "BIU"],
    adder: [814, 431, 353, 53, "Address adder", "BIU"],
    opr: [713, 542, 131, 65, "OPR", "BIU"],
    memory: [872, 536, 181, 77, "Bus controller", "BIU"],
    ext: [1142, 536, 71, 77, "Bus pins", "BIU"],
    queue: [825, 670, 344, 116, "Instruction FIFO", "BIU"],
    loader: [844, 900, 324, 72, "Instruction loader", "CU"],
    ir: [143, 925, 260, 52, "Instruction register", "CU"],
    prefix: [906, 993, 248, 63, "Prefix latch", "CU"],
    pla: [861, 1095, 293, 74, "Group Decode ROM / PLA", "CU"],
    trom: [909, 1232, 261, 66, "Translation ROM", "CU"],
    engine: [144, 1037, 286, 73, "Microcode engine", "CU"],
    mar: [144, 1171, 277, 70, "Microcode address register", "CU"],
    rom: [532, 1171, 229, 70, "Microcode ROM", "CU"],
    ctl: [188, 1354, 616, 78, "Control latches & local decode", "CU"],
    clk: [113, 1502, 155, 112, "Learning clock", "CU"],
    seq: [325, 1474, 311, 164, "Phase sequencer", "CU"],
    dec: [721, 1474, 430, 164, "Control enable matrix", "CU"],
  };
  const info = {
    regs: [
      "Register file",
      "AX, BX, CX and DX each split into an 8-bit high and low register. SI, DI, SP and BP hold whole 16-bit words. Register mode and memory mode both write this example’s result into AX.",
      "AX = AH × 256 + AL",
    ],
    internal: [
      "Internal data bus",
      "A selected source drives a 16-bit word. Enabled destinations capture it. Follow the return from the ALU for write-back, the OPR branch for memory data, and the Q path for a displacement.",
      "one 16-bit word = two octets",
    ],
    temps: [
      "Temporary operand latches",
      "tmpA, tmpB and tmpC hold intermediate words. The input selector chooses one of the three for the first ALU input. The second ALU input comes from tmpB.",
      "tmpA / tmpB / tmpC → selector",
    ],
    aluctl: [
      "ALU control decode",
      "Local logic decodes an ALU micro-operation and a two-bit temporary selector. Addition and subtraction share the adder in the gate model. SUB complements B and supplies an initial carry of one.",
      "A − B = A + ¬B + 1",
    ],
    mux: [
      "ALU input selector",
      "The first ALU input can come from tmpA, tmpB or tmpC. With two select bits, three inputs can be addressed. Each of the sixteen data positions has the same selection.",
      "selected input → ALU[15:0]",
    ],
    alu: [
      "Arithmetic logic unit",
      "Inspect one full-adder slice. XOR forms propagate, AND forms generate, and the AND/OR network computes carry. Select another bit to follow the carry across the 16-bit teaching adder.",
      "Cᵢ₊₁ = Gᵢ + Pᵢ·Cᵢ",
    ],
    flags: [
      "Status flags",
      "Write-back captures CF, PF, AF, ZF, SF and OF. PF counts ones in the low byte. AF reports a carry or borrow across bit 3. CF reports unsigned carry or borrow; OF reports signed overflow.",
      "status bit positions: 0, 2, 4, 6, 7, 11",
    ],
    seg: [
      "Segment registers",
      "CS selects code, DS normally selects data, SS selects stack data and ES is the extra segment. All four hold 16-bit values. The BIU shifts the selected value left four to form a base.",
      "base[19:0] = segment[15:0] × 16",
    ],
    ip: [
      "Instruction pointer",
      "The BIU maintains a fetch offset ahead of execution while bytes wait in the FIFO. An aligned word fetch advances the offset by two. The trace displays this next-fetch value.",
      "physical fetch = (CS × 16 + IP) mod 2²⁰",
    ],
    ind: [
      "Indirect offset register",
      "The EU calculates an effective address and sends this 16-bit offset to IND. The BIU can then use IND for a memory operand. In the prefixed example, BP + SI + 6 = 010Ah.",
      "IND ← (BP + SI + signext(disp8)) mod 2¹⁶",
    ],
    segmux: [
      "Segment selector",
      "The BIU selects CS during an instruction fetch. For the example with BP, the data default is SS. A valid 26h override selects ES for that operand read.",
      "fetch → CS    BP-based operand → SS or override",
    ],
    offmux: [
      "Offset selector",
      "Choose the BIU’s instruction fetch offset or the indirect operand offset. This selection feeds the offset input of the address adder.",
      "fetch → IP    memory operand → IND",
    ],
    adder: [
      "BIU address adder / incrementer",
      "Form a 20-bit physical address by adding a shifted segment to a 16-bit offset. Only the low twenty address bits reach the 8086 bus. Incrementing the fetch offset uses the BIU address hardware.",
      "address = (segment × 16 + offset) mod 2²⁰",
    ],
    opr: [
      "Operand bus-data latch",
      "During an aligned word read, the BIU captures both memory bytes. The low-address byte supplies bits 7…0. OPR delivers that word to the EU on the internal data bus.",
      "OPR = high byte × 256 + low byte",
    ],
    memory: [
      "Bus controller",
      "The BIU selects an address, requests a transfer, and routes incoming data to the queue or OPR. A real external bus transfer has T-states with possible wait states. The learning clock groups the transfer into one action.",
      "code fetch → FIFO    data read → OPR",
    ],
    ext: [
      "External bus pins",
      "AD15…AD0 carry the low address during T1 and data during the data phase. A19…A16 share pins with status signals. A0 and active-low BHE# select byte lanes. An odd-addressed word requires two transfers.",
      "A0 = 0 and BHE# = 0 → both byte lanes",
    ],
    queue: [
      "Six-byte instruction queue",
      "Three 16-bit registers store up to six bytes. The loader consumes the oldest byte. BIU word refills need two empty byte slots. Queue contents are shown in consumption order; taken control transfers flush prefetched bytes.",
      "3 words × 2 bytes = 6 bytes",
    ],
    loader: [
      "Instruction loader and input latches",
      "The loader consumes a byte at a time. Prefixes affect the following instruction, an opcode enters IR, and an optional ModR/M byte selects addressing. Displacements can pass from Q onto the internal bus.",
      "ModR/M = mod[7:6] | reg[5:3] | r/m[2:0]",
    ],
    ir: [
      "Instruction register",
      "The 8-bit IR holds the opcode while execution uses it. 01h and 29h use the register field as source. With 03h, the register field is the destination. The ModR/M byte has its own input latches.",
      "01h ADD r/m16,r16    03h ADD r16,r/m16",
    ],
    prefix: [
      "Prefix latch",
      "Recognizing a segment override stores its segment choice and valid state until the instruction completes. 26h overrides the BP-based default SS with ES. Instruction fetch still uses CS.",
      "26h → ES override valid",
    ],
    pla: [
      "Group Decode ROM / PLA",
      "The hardware classifies opcode bit patterns, including prefixes and instruction groups. Its fifteen output class signals guide loading and execution. The separate learning matrix below drives the slowed trace.",
      "opcode[7:0] → instruction class signals",
    ],
    trom: [
      "Translation ROM",
      "The control logic uses this ROM to translate a microcode jump or call tag, or addressing-mode information, into a target micro-address. Mod=01 and r/m=010 select BP+SI with a signed disp8.",
      "mod[1:0] + r/m[2:0] → effective-address dispatch",
    ],
    engine: [
      "Microcode sequencing engine",
      "Opcode entry, sequential advance, conditional transfer, calls and return select the next logical micro-address. A 13-bit return register holds the micro-subroutine return address.",
      "entry / sequential / target / return → next µaddress",
    ],
    mar: [
      "Microcode address register",
      "The original chip combines a 9-bit block with a 4-bit sequence counter. Partial decoding lets different logical addresses select the same physical microcode. The teaching phase counter below has its own encoding.",
      "9 block bits + 4 sequence bits = 13 bits",
    ],
    rom: [
      "Microcode control store",
      "The 8086 contains 512 physical 21-bit microinstructions. A word specifies a source, destination, flag-update request, and type-dependent action. The application shows the field widths without inventing binary ROM contents.",
      "5 source + 5 destination + 1 flag + 10 action = 21",
    ],
    ctl: [
      "Control signal latches and local decoders",
      "A microinstruction is distributed to local decoders. They select register transfers, drive ALU operations, request bus cycles and steer microcode sequencing. Dashed guides below link the learning controller to these functional effects.",
      "ROM word[20:0] → distributed enables",
    ],
    clk: [
      "Learning clock",
      "Set the rate in hertz. Each falling edge advances one instructional transfer in the teaching controller. A full period includes both the high and the low half-cycle.",
      "T = 1 / f",
    ],
    seq: [
      "Clocked phase sequencer",
      "Three JK flip-flops share a falling clock edge. Stage 0 always toggles, stage 1 toggles when old Q0 is one, and stage 2 when old Q1·Q0 is one. For the memory trace a page bit toggles at phase 7.",
      "Q⁺ = J·¬Q + ¬K·Q",
    ],
    dec: [
      "Control enable matrix",
      "Four input bits select exactly one of sixteen rows. Black dots join selected rows to OR gates for the active teaching schedule. Outputs drive byte loads, word transfers and write-back on this same processor trace.",
      "index = 8·bank + 4·Q₂ + 2·Q₁ + Q₀",
    ],
  };
  const N = {},
    nets = book.nets.concat([
      [
        "clock-phase",
        "clk",
        "seq",
        "Falling-edge teaching clock",
        "clk.out",
        "seq.clock",
      ],
      [
        "phase-matrix",
        "seq",
        "dec",
        "Q2…Q0 and memory page when used",
        "seq.phase",
        "dec.inputs",
      ],
      [
        "instruction-mode",
        "ir",
        "dec",
        "Decoded teaching operation selects a control bank",
        "ir.class",
        "dec.mode",
      ],
      [
        "model-control",
        "dec",
        "ctl",
        "Teaching enables for functional transfers",
        "dec.enable",
        "ctl.model",
      ],
    ]);
  let expanded = false;
  const Y = (y, high = expanded) =>
    (y - 56) * 0.54 +
    (high
      ? Math.max(0, Math.min(1, (y - 646) / 73)) * 182 +
        Math.max(0, Math.min(1, (y - 1474) / 164)) * 120
      : 0);
  const inverse = (v, high) =>
    !high || v < Y(646, false)
      ? v / 0.54 + 56
      : v <= Y(719, true)
        ? 646 + (v - Y(646, false)) / (0.54 + 182 / 73)
        : v < Y(1474, true)
          ? (v - 182) / 0.54 + 56
          : v <= Y(1638, true)
            ? 1474 + (v - Y(1474, true)) / (0.54 + 120 / 164)
            : (v - 302) / 0.54 + 56;
  function layout() {
    for (const [id, [x, y, w, h, title, group]] of Object.entries(spec))
      N[id] = [x, Y(y), w, Y(y + h) - Y(y), title, group];
  }
  layout();
  function reflow(scale, cy) {
    const next = scale >= 3;
    if (next === expanded) return cy;
    const old = inverse(cy, expanded);
    expanded = next;
    layout();
    return Y(old);
  }
  const unitColors = {
    EU: ["#eff4e8", "#718c72", "#fcfef6"],
    BIU: ["#f7f0df", "#a38a62", "#fffbed"],
    CU: ["#f1edf4", "#8f7e9c", "#fdfaff"],
  };
  const txt = (
    x,
    y,
    v,
    size = 14,
    c = "#304033",
    anchor = "start",
    bold = false,
  ) =>
    '<text x="' +
    x +
    '" y="' +
    y +
    '" font-family="Segoe UI,Arial,sans-serif" font-size="' +
    size +
    '" text-anchor="' +
    anchor +
    '" font-weight="' +
    (bold ? 650 : 450) +
    '" fill="' +
    c +
    '">' +
    v +
    "</text>";
  function unit(x, top, w, bot, code, title) {
    const [fill, col] = unitColors[code],
      y = Y(top),
      h = Y(bot) - y;
    return (
      R(x, y, w, h, fill, col, 8, 1.45) +
      R(x + 14, y + 4, 47, 18, fill, col, 3, 0.8) +
      txt(x + 37, y + 18, code, 15, col, "middle", true) +
      txt(x + 71, y + 18, title, 19, "#354436", "start", true)
    );
  }
  const titleShort = {
    regs: "General registers",
    alu: "ALU · 16 bit",
    flags: "Status flags",
    memory: "Bus controller",
    mar: "µaddress register",
    engine: "Microcode engine",
    trom: "Translation ROM",
    ctl: "Control latches & local decode",
    aluctl: "ALU decode",
    ext: "Pins",
    pla: "Group Decode ROM",
    ir: "IR · opcode",
    seg: "Segment registers",
    internal: "Internal data bus  ·  16 bits",
    adder: "BIU address adder / incrementer",
  };
  const color = (id) => unitColors[N[id][5]][1];
  function overview(id) {
    const [x, y, w, h, title, unit] = N[id],
      col = color(id),
      fill = unitColors[unit][2],
      m = x + w / 2;
    if (id === "alu")
      return (
        P(
          "M190 " +
            y +
            "H343L365 " +
            (y + h * 0.33) +
            "H428L452 " +
            y +
            "H540L501 " +
            (y + h) +
            "H226Z",
          col,
          1.7,
          fill,
        ) + txt(m, y + h * 0.78, "ALU · 16 bit", 18, col, "middle", true)
      );
    let out = R(x, y, w, h, fill, col, 3, 1.35);
    const subtitles = {
      regs: "AX   BX   CX   DX",
      seg: "DS   SS   CS   ES",
      flags: "CF   PF   AF   ZF   SF   OF",
      temps: "tmpA   ·   tmpB   ·   tmpC",
      queue: "Q0   Q1   Q2    ·    6 bytes",
      rom: "512 × 21 bits",
      engine: "entry / next / branch / return",
      ctl: "EU enables   ·   flags   ·   BIU requests",
      seq: "3 JK stages  ·  page carry",
      dec: "4-to-16 decode  →  OR matrix",
      clk: "CLK ↓",
      memory: "read / fetch",
      loader: "Q → IR + ModR/M",
    };
    const sub = subtitles[id],
      size = Math.min(
        19,
        Math.max(11, w / ((titleShort[id] || title).length * 0.59)),
      );
    out += txt(
      m,
      y + h / 2 + (sub ? -2 : 5),
      titleShort[id] || title,
      size,
      col,
      "middle",
      true,
    );
    if (sub)
      out += txt(
        m,
        y + h / 2 + 13,
        sub,
        Math.min(13, h * 0.28),
        "#46584b",
        "middle",
      );
    if (id === "regs")
      out +=
        txt(
          m,
          y + h / 2 + 32,
          "AH/AL · BH/BL · CH/CL · DH/DL",
          13,
          "#536254",
          "middle",
        ) +
        txt(m, y + h / 2 + 49, "SI   DI   SP   BP", 13, "#536254", "middle");
    return out;
  }
  const dashed = (d, arrow = true) =>
    P(
      d,
      "#8a759a",
      1.5,
      "none",
      'stroke-dasharray="4 3"' + (arrow ? ' marker-end="url(#model-tip)"' : ""),
    );
  function extraRoutes() {
    const [cx, cy, cw, ch] = N.clk,
      [sx, sy, sw, sh] = N.seq,
      [dx, dy, dw, dh] = N.dec;
    const center = sy + sh / 2,
      ctl = N.ctl,
      ir = N.ir;
    return (
      '<g data-wire="clock-phase">' +
      dashed("M" + (cx + cw) + " " + center + "H" + sx) +
      "</g>" +
      '<g data-wire="phase-matrix">' +
      dashed("M" + (sx + sw) + " " + center + "H" + dx) +
      "</g>" +
      '<g data-wire="model-control">' +
      dashed(
        "M" +
          (dx + dw * 0.6) +
          " " +
          dy +
          "V" +
          Y(1452) +
          "H720V" +
          (ctl[1] + ctl[3]),
      ) +
      "</g>" +
      '<g data-wire="instruction-mode">' +
      dashed(
        "M" +
          (ir[0] + ir[2]) +
          " " +
          Y(963) +
          "H705V" +
          Y(1458) +
          "H" +
          (dx + dw * 0.11) +
          "V" +
          dy,
      ) +
      "</g>" +
      txt((cx + cw + sx) / 2, center - 4, "CLK", 9, "#715f83", "middle") +
      txt((sx + sw + dx) / 2, center - 4, "Q / page", 10, "#715f83", "middle")
    );
  }
  function embedded(id, bit) {
    let [x, y, w, h] = N[id];
    const isA = id === "alu",
      isD = id === "dec";
    const fill = unitColors[N[id][5]][2],
      c = color(id);
    const vw = isA ? 270 : isD ? 380 : cpu.isMem() ? 451 : 337,
      vh = isA ? 202 : isD ? 195 : 206;
    const ratio = Math.min(
      (w - (isA ? 72 : 32)) / vw,
      (h - (isA ? 49 : 22)) / vh,
    );
    const X = x + (w - vw * ratio) / 2,
      Y0 = y + (isA ? 22 : 12) + (h - (isA ? 49 : 22) - vh * ratio) / 2;
    const px = (u) => X + u * ratio,
      py = (v) => Y0 + v * ratio;
    const wire = (d) => P(d, "#537861", isA ? 0.85 : 0.65);
    let box = R(x, y, w, h, fill, c, 3, 1.35);
    const append = (d) => {
      box += wire(d);
    };
    if (isA) {
      box += txt(
        x + 6,
        y + 9,
        "FULL ADDER / SLICE " + bit,
        7.2,
        c,
        "start",
        true,
      );
      append("M328 " + y + "V" + (y + 17) + "H" + px(40) + "V" + py(0));
      append("M467 " + y + "V" + (y + 5) + "H435V" + (y + 13) + "H449");
      append("M196 " + Y(658) + "H194V" + (y + 19) + "H449");
      box += tinyGate(
        445,
        y + 10,
        "xor",
        17,
        12,
        !!cpu.calculate().slices[bit].B,
      );
      append(
        "M462 " + (y + 16) + "H474V" + (y + 21) + "H" + px(182) + "V" + py(0),
      );
      box += txt(433, y + 10, "SUB", 5.8, c, "end");
      box += txt(329, y + 8, "Aᵢ", 7, c) + txt(469, y + 7, "Bᵢ", 7, c);
      if (bit === 0) {
        append("M194 " + (y + 19) + "V" + py(179) + "H" + px(4));
        box += dot(194, Y(658), c, 1);
        box += txt(197, py(179) - 4, "C0 ← SUB", 6.1, c);
      } else {
        box +=
          R(193, py(179) - 12, 48, 18, "#eff5e9", c, 1, 0.65) +
          txt(217, py(179) - 2, "bits 0…" + (bit - 1), 6.2, c, "middle");
        append("M241 " + py(179) + "H" + px(4));
        box += txt(243, py(179) - 4, "C" + bit, 6, c);
      }
      append(
        "M" +
          px(270) +
          " " +
          py(98) +
          "H" +
          (x + w - 10) +
          "V" +
          (y + h - 20) +
          "H486V" +
          (y + h - 17),
      );
      box += txt(
        x + w - 4,
        py(98) - 5,
        bit === 15 ? "C16" : "to bit " + (bit + 1),
        7,
        c,
        "end",
      );
      append(
        "M" +
          px(181) +
          " " +
          py(188) +
          "V" +
          (y + h - 21) +
          "H" +
          (x + 12) +
          "V" +
          Y(686) +
          "H210",
      );
      box += txt(x + 15, y + h - 24, "Σᵢ → result[i]", 6.8, c);
      append("M" + px(181) + " " + (y + h - 21) + "V" + (y + h - 17));
      box += dot(px(181), y + h - 21, c, 1.2);
      box += P("M210 " + Y(686) + "H190", c, 0.85);
      const xs = [235, 282, 329, 376, 423, 470];
      box += R(226, y + h - 17, 269, 12, "#eff5e9", c, 1, 0.7);
      box += txt(
        360,
        y + h - 8.5,
        "16-bit result & carries → six status functions",
        7,
        c,
        "middle",
      );
      xs.forEach((xx, i) => {
        box += wire("M" + xx + " " + (y + h - 5) + "V" + (y + h));
      });
      box += txt(x + 4, Y(658) + 6, "op", 7, c);
    } else if (isD) {
      box += txt(
        x + 5,
        y + 8,
        "TEACHING MATRIX  /  " + (cpu.isMem() ? "MEMORY" : "REGISTER"),
        6.4,
        c,
        "start",
        true,
      );
      const rail = x + 7;
      append("M" + x + " " + (y + h / 2) + "H" + rail);
      box += P(
        "M" + rail + " " + py(cpu.isMem() ? 40 : 60) + "V" + py(112),
        c,
        1.6,
      );
      [1, 2, 3].forEach((j) => {
        append(
          "M" + rail + " " + py(50 + j * 20) + "l4 -" + 4 * ratio + "H" + px(9),
        );
      });
      const bankX = x + 23;
      append(
        "M" +
          (x + w * 0.11) +
          " " +
          y +
          "V" +
          (y + 10) +
          "H" +
          bankX +
          "V" +
          (py(46) - 2.5),
      );
      if (cpu.isMem())
        append(
          "M" +
            rail +
            " " +
            py(44) +
            "l4 -" +
            4 * ratio +
            "H" +
            (bankX - 3) +
            "V" +
            (py(46) - 2.5),
        );
      box +=
        R(bankX - 6, py(46) - 3, 13, 6, "#efe9f4", c, 0.5, 0.55) +
        txt(bankX + 0.5, py(46) + 1.2, "SEL", 3.5, c, "middle");
      append("M" + (bankX + 7) + " " + py(46) + "H" + px(9));
      append(
        "M" +
          px(380) +
          " " +
          py(178) +
          "H" +
          (x + w - 6) +
          "V" +
          (y + 5) +
          "H" +
          (x + w * 0.6) +
          "V" +
          y,
      );
    } else {
      box += txt(
        x + 5,
        y + 8,
        "FALLING-EDGE JK SEQUENCER",
        6.5,
        c,
        "start",
        true,
      );
      append(
        "M" +
          x +
          " " +
          (y + h / 2) +
          "H" +
          (x + 7) +
          "V" +
          py(22) +
          "H" +
          px(5),
      );
      append(
        "M" +
          px(cpu.isMem() ? 451 : 337) +
          " " +
          py(190) +
          "H" +
          (x + w - 6) +
          "V" +
          (y + h / 2) +
          "H" +
          (x + w),
      );
    }
    const body = isA
      ? adderLogic(cpu.s, bit)
      : isD
        ? decoderLogic()
        : sequencerLogic();
    return (
      box +
      '<g data-logic="' +
      id +
      '" transform="translate(' +
      X +
      " " +
      Y0 +
      ") scale(" +
      ratio +
      ')">' +
      body +
      "</g>"
    );
  }
  function fifo() {
    const [x, y, w, h] = N.queue,
      c = color("queue"),
      top = y + Math.min(23, h * 0.28),
      row = (h - top + y - 4) / 3;
    let g =
      R(x, y, w, h, "#fbfdf7", c, 3, 1.4) +
      txt(
        x + 8,
        y + 12,
        "FIFO · logical order · oldest first",
        12,
        c,
        "start",
        true,
      );
    for (let k = 0; k < 3; k++) {
      const yy = top + k * row;
      g += txt(x + 10, yy + row * 0.62, "B" + k * 2, 10, c);
      for (let b = 0; b < 2; b++) {
        const xx = x + 44 + b * 147,
          i = k * 2 + b,
          v = cpu.s.queue[i];
        g +=
          R(
            xx,
            yy,
            140,
            row - 2,
            v == null ? "#f1f3e8" : "#dcefd6",
            c,
            1,
            0.65,
          ) +
          txt(
            xx + 70,
            yy + row * 0.61,
            "byte " + i + "  ·  " + (v == null ? "—" : cpu.hex(v, 2) + "h"),
            Math.min(11, row * 0.64),
            c,
            "middle",
          );
      }
    }
    g += txt(x + w - 8, y + 12, cpu.s.queue.length + " / 6", 10, c, "end");
    return g;
  }
  function romword() {
    const [x, y, w, h] = N.rom,
      c = color("rom");
    let g =
        R(x, y, w, h, "#f8f5fa", c, 3, 1.3) +
        txt(x + 5, y + 10, "Microcode ROM  ·  512 × 21", 10, c, "start", true),
      left = x + 4;
    for (const [label, n] of [
      ["source 5", 5],
      ["dest 5", 5],
      ["F", 1],
      ["action / type 10", 10],
    ]) {
      const ww = ((w - 8) * n) / 21;
      g +=
        R(left, y + 14, ww, h - 18, "#f0eaf5", c, 0.3, 0.65) +
        txt(
          left + ww / 2,
          y + 14 + (h - 18) / 2 + 2.3,
          label,
          6.7,
          c,
          "middle",
        );
      left += ww;
    }
    return g;
  }
  function activeIds() {
    const mem = cpu.isMem(),
      n = cpu.index(),
      en = cpu.enables();
    const ids = [];
    if (en.F && cpu.s.queue.length <= 4)
      ids.push(
        "segment-input",
        "fetch-offset",
        "base-to-adder",
        "offset-to-adder",
        "physical-address",
        "external-address",
        "external-data",
        "prefetch",
        "fetch-ip-update",
      );
    if (en.IR || en.M || en.L) ids.push("next-byte");
    if (en.IR || (mem && n === 2))
      ids.push("latched-opcode", "opcode-classification", "opcode-entry");
    if (en.M || (mem && n === 4)) ids.push("modrm-to-trom");
    if (mem && n === 1)
      ids.push("latched-opcode", "opcode-classification", "prefix-load");
    if (mem && n === 5) ids.push("immediate-displacement");
    if (mem && [4, 5].includes(n)) ids.push("register-word", "temporary-load");
    if (mem && n === 6)
      ids.push(
        "tmpa-select",
        "alu-first",
        "alu-second",
        "alu-writeback",
        "temporary-load",
      );
    if (mem && n === 7)
      ids.push(
        "tmpc-select",
        "alu-first",
        "alu-second",
        "alu-writeback",
        "effective-offset",
      );
    if (mem && n === 8)
      ids.push("segment-override", "segment-input", "operand-offset");
    if (mem && n === 9)
      ids.push("base-to-adder", "offset-to-adder", "physical-address");
    if (mem && n === 10)
      ids.push(
        "bus-request",
        "external-address",
        "external-data",
        "operand-to-controller",
      );
    if (en.A || en.B)
      ids.push(
        "temporary-load",
        en.B && mem ? "operand-data" : "register-word",
      );
    if (en["Σ"] || en.W)
      ids.push("tmpa-select", "alu-first", "alu-second", "alu-local-drive");
    if (en.W)
      ids.push(
        "alu-writeback",
        "register-word",
        "flags-write",
        "eu-register-enable",
        "carry",
        "parity",
        "auxiliary",
        "zero",
        "sign",
        "overflow",
      );
    return ids;
  }
  function liveValues() {
    const s = cpu.s,
      green = "#176c48";
    let g = "";
    [
      ["ax", 185],
      ["bx", 210],
      ["bp", 360],
      ["si", 285],
    ].forEach(([key, y]) => (g += txt(326, Y(y), cpu.hex(s[key]), 8.4, green)));
    ["ds", "ss", "cs", "es"].forEach(
      (key, i) => (g += txt(784, Y(182 + 25 * i), cpu.hex(s[key]), 8.5, green)),
    );
    [s.a, s.b, s.c].forEach(
      (value, i) => (g += txt(236 + 141 * i, Y(551), cpu.hex(value), 8, green)),
    );
    ["CF", "PF", "AF", "ZF", "SF", "OF"].forEach(
      (key, i) =>
        (g += txt(
          173 + i * 80,
          Y(794),
          String(s.flags[key]),
          10,
          green,
          "middle",
          true,
        )),
    );
    g += txt(1166, Y(162), cpu.hex(s.ip), 9, green, "end", true);
    if (s.ind != null)
      g += txt(1166, Y(241), cpu.hex(s.ind), 9, green, "end", true);
    return g;
  }
  function render(scale, sel, bit) {
    const section = expanded ? book.gates : book.base,
      mid = scale >= 1.48;
    let g =
      '<defs><marker id="model-tip" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#8a759a"/></marker></defs>';
    g +=
      unit(36, 86, 590, 868, "EU", "Execution unit") +
      unit(679, 86, 545, 868, "BIU", "Bus interface unit") +
      unit(
        36,
        881,
        1188,
        1665,
        "CU",
        "Control unit · execution control within EU",
      );
    g += section["routed-signals"] + extraRoutes();
    const act = activeIds();
    if (act.length)
      g +=
        "<style>" +
        act
          .map((id) => '[data-wire="' + id + '"] path:nth-of-type(2)')
          .join(",") +
        "{stroke-width:3.7;stroke:#18744c}</style>";
    if (mid)
      g +=
        section["execution-unit"] +
        section["bus-interface-unit"] +
        section["control-unit"] +
        section["signal-widths"];
    for (const [id, [x, y, w, h, title]] of Object.entries(N)) {
      let body =
        expanded && ["alu", "seq", "dec"].includes(id)
          ? embedded(id, bit)
          : !mid || ["clk", "seq", "dec"].includes(id)
            ? overview(id)
            : "";
      if (mid && id === "queue") body = fifo();
      if (mid && id === "rom") body = romword();
      if (id === sel)
        body += R(x - 3, y - 2, w + 6, h + 4, "none", "#4d9470", 4, 2.1);
      g +=
        '<g class="cpu-node" data-node="' +
        id +
        '" role="button" tabindex="0" aria-label="Inspect ' +
        title +
        '"><title>' +
        title +
        " · double-click to zoom</title>" +
        body +
        R(x, y, w, h, "transparent", "none", 0, 0) +
        "</g>";
    }
    if (mid) g += liveValues();
    g += txt(
      112,
      Y(1465),
      "Learning controller  ·  functional equivalents",
      11,
      "#705d80",
      "start",
      true,
    );
    return g;
  }
  window.board = {
    W,
    H: Y(1673, false),
    get height() {
      return Y(1673);
    },
    N,
    info,
    nets,
    render,
    reflow,
    Y,
    unmap: inverse,
    activeIds,
    expanded: () => expanded,
  };
})();
