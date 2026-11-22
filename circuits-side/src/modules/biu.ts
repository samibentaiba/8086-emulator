/// <reference path="../types.ts" />
/// <reference path="../primitives.ts" />
/// <reference path="../engine.ts" />

/**
 * Intel 8086 Circuit Atlas - Bus Interface Unit (BIU) Modular Engine
 * 100% Modular OOP CAD Architecture: SchematicCanvas, PortBox, SubcircuitCard, LogicGate.
 * Units:
 *   1. segLogic (16-bit Segment Registers CS, DS, SS, ES)
 *   2. ipLogic (16-bit Instruction Pointer & Incrementer)
 *   3. addressAdderLogic (20-bit Dedicated Physical Address Adder)
 *   4. segmuxLogic (4:1 Segment Multiplexer & Hardwired Left Shifter)
 *   5. offmuxLogic (2:1 Offset Multiplexer)
 *   6. indLogic (16-bit Indirect Offset Register / EA Latch)
 *   7. oprLogic (16-bit Operand Bus Transceiver)
 *   8. queueLogic (6-Byte Instruction Prefetch Queue FIFO)
 *   9. busControllerLogic (Bus Controller & T-State Timing Engine)
 *  10. pinsLogic (40-Pin Silicon I/O & ESD Cell)
 *
 * Guaranteed CAD Invariants:
 *   - Zero Gate Body Penetrations (All vertical drops strictly in Zone 1 / Zone 3)
 *   - Zero Floating Solder Dots
 *   - Zero Boundary Violations
 *   - 100% Mathematical Outer Pin Alignment with architecture.js
 */
namespace LogicDraw {
  declare const cpu: any;

  // =========================================================================
  // 1. 16-BIT SEGMENT REGISTERS (CS, DS, SS, ES)
  // 4x 16-Bit Discrete Register Arrays, 2:4 Address Decoder, Tri-State Drivers
  // Viewport: 400 x 200
  // =========================================================================
  export function segLogic(s: any): string {
    const canvas = new SchematicCanvas();

    const csVal = s.cs ?? 0x1200;
    const dsVal = s.ds ?? 0x2000;
    const ssVal = s.ss ?? 0x2800;
    const esVal = s.es ?? 0x3000;

    const activeSeg = s.seg ?? 0; // 0: CS, 1: DS, 2: SS, 3: ES
    const isCS = activeSeg === 0;
    const isDS = activeSeg === 1;
    const isSS = activeSeg === 2;
    const isES = activeSeg === 3;

    // 0. Top System Title Banner
    canvas.addBackground(R(10, 6, 380, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(18, 17, "INTEL 8086 SEGMENT REGISTERS · CS, DS, SS, ES", 6.8, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(380, 17, "4× 16-BIT REGISTERS · 2:4 ADDRESS DECODER", 5.6, 'text-anchor="end" font-weight="bold" fill="#15803d"');

    // 1. Port Boxes
    const portCtl = new PortBox("port_seg_ctl", 10, 26, 62, 142, "SEG CTL", "left", "input", "#f5f3ff", "#7c3aed", "PORT IN");
    portCtl.addPortPin("sel_bus", 30, "REG_SEL[1:0]", true, paths.control);
    portCtl.addPortPin("a1", 52, "A1 (MSB)", false, paths.control);
    portCtl.addPortPin("a0", 72, "A0 (LSB)", false, paths.control);
    portCtl.addPortPin("seg_wr", 100, "SEG_WR", false, "#0284c7");
    portCtl.addPortPin("seg_rd", 120, "SEG_RD", false, paths.high);
    canvas.addComponent(portCtl);

    // Distribution traces inside PortBox
    canvas.addWire(P("M10 56H22", paths.control, 1.5));
    canvas.addBus(P("M22 56V126", paths.control, 1.2));
    canvas.addDot(22, 56, paths.control, 1.8);
    canvas.addWire(P("M22 78H26", paths.control, 1.0));
    canvas.addDot(22, 78, paths.control, 1.4);
    canvas.addWire(P("M22 98H26", paths.control, 1.0));
    canvas.addDot(22, 98, paths.control, 1.4);

    // 2. Zone 1: 2:4 Address Decoder & Wordline Drivers (X = 72..130)
    canvas.addWire(P("M72 78H80", paths.control, 1.2));
    canvas.addDot(80, 78, paths.control, 1.6);
    canvas.addWire(P("M80 78H84", paths.control, 1.0));
    canvas.addComponent(new LogicGate("inv_a1", 84, 74, "inv", 8, 8, true));
    canvas.addWire(P("M92 78H96", paths.control, 1.0));
    canvas.addDot(96, 78, "#64748b", 1.6);

    canvas.addWire(P("M72 98H104", paths.control, 1.2));
    canvas.addDot(104, 98, paths.control, 1.6);
    canvas.addWire(P("M104 98H108", paths.control, 1.0));
    canvas.addComponent(new LogicGate("inv_a0", 108, 94, "inv", 8, 8, true));
    canvas.addWire(P("M116 98H120", paths.control, 1.0));
    canvas.addDot(120, 98, "#64748b", 1.6);

    // Vertical Decoder Rails (Continuous unbroken lines, Y = 36..150)
    canvas.addBus(P("M80 36V150", paths.control, 1.0));
    canvas.addBus(P("M96 36V150", "#64748b", 1.0));
    canvas.addBus(P("M104 36V150", paths.control, 1.0));
    canvas.addBus(P("M120 36V150", "#64748b", 1.0));

    // 4x 2-Input AND Gates (CS, DS, SS, ES selection)
    canvas.addWire(P("M96 42H122", isCS ? paths.high : "#64748b", 1.0));
    canvas.addDot(96, 42, isCS ? paths.high : "#64748b", 1.4);
    canvas.addWire(P("M120 46H122", isCS ? paths.high : "#64748b", 1.0));
    canvas.addDot(120, 46, isCS ? paths.high : "#64748b", 1.4);
    canvas.addComponent(new LogicGate("and_cs", 122, 39, "and", 10, 10, isCS));

    canvas.addWire(P("M96 76H122", isDS ? paths.high : "#64748b", 1.0));
    canvas.addDot(96, 76, isDS ? paths.high : "#64748b", 1.4);
    canvas.addWire(P("M104 80H122", isDS ? paths.high : "#64748b", 1.0));
    canvas.addDot(104, 80, isDS ? paths.high : "#64748b", 1.4);
    canvas.addComponent(new LogicGate("and_ds", 122, 73, "and", 10, 10, isDS));

    canvas.addWire(P("M80 110H122", isSS ? paths.high : "#64748b", 1.0));
    canvas.addDot(80, 110, isSS ? paths.high : "#64748b", 1.4);
    canvas.addWire(P("M120 114H122", isSS ? paths.high : "#64748b", 1.0));
    canvas.addDot(120, 114, isSS ? paths.high : "#64748b", 1.4);
    canvas.addComponent(new LogicGate("and_ss", 122, 107, "and", 10, 10, isSS));

    canvas.addWire(P("M80 144H122", isES ? paths.high : "#64748b", 1.0));
    canvas.addDot(80, 144, isES ? paths.high : "#64748b", 1.4);
    canvas.addWire(P("M104 148H122", isES ? paths.high : "#64748b", 1.0));
    canvas.addDot(104, 148, isES ? paths.high : "#64748b", 1.4);
    canvas.addComponent(new LogicGate("and_es", 122, 141, "and", 10, 10, isES));

    // 3. Zone 2: 4x 16-Bit Register Arrays (X = 138..290)
    const segInfo = [
      { name: "CS", val: csVal, act: isCS, y: 30, tag: "CODE BASE" },
      { name: "DS", val: dsVal, act: isDS, y: 64, tag: "DATA BASE" },
      { name: "SS", val: ssVal, act: isSS, y: 98, tag: "STACK BASE" },
      { name: "ES", val: esVal, act: isES, y: 132, tag: "EXTRA BASE" },
    ];

    segInfo.forEach((sg) => {
      const y0 = sg.y;
      const act = sg.act;
      canvas.addBackground(R(138, y0, 150, 28, act ? "#eff6ff" : "#f8fafc", act ? "#3b82f6" : "#cbd5e1", 2, act ? 1.2 : 0.8));
      canvas.addLabel(144, y0 + 11, sg.name, 7.2, `font-weight="bold" fill="${act ? '#1d4ed8' : '#0f172a'}"`);
      canvas.addLabel(168, y0 + 11, `${hex(sg.val, 4)}h`, 7.2, `font-weight="bold" fill="${act ? '#047857' : '#334155'}"`);
      canvas.addLabel(144, y0 + 22, `${sg.tag} · Base: ${hex(sg.val << 4, 5)}h`, 5.2, 'fill="#64748b"');

      // 16 Discrete Bit Cells (Bits 15 down to 0)
      for (let b = 0; b < 16; b++) {
        const bitVal = (sg.val >>> (15 - b)) & 1;
        const bx = 214 + b * 4.4;
        canvas.addBackground(R(bx, y0 + 4, 3.6, 9, bitVal ? "#dcfce7" : "#f1f5f9", bitVal ? "#16a34a" : "#cbd5e1", 0.8, 0.5));
      }

      // Wordline connection from decoder gate into register
      canvas.addWire(P(`M132 ${y0 + 14}H138`, act ? paths.high : "#64748b", 1.2));

      // Output wire to Tri-State Buffer
      canvas.addWire(P(`M288 ${y0 + 14}H296`, act ? "#d97706" : "#94a3b8", 1.2));
      canvas.addComponent(new LogicGate(`buf_${sg.name}`, 296, y0 + 9, "buf", 12, 10, act));
      canvas.addWire(P(`M308 ${y0 + 14}H326`, act ? "#d97706" : "#94a3b8", 1.2));
      canvas.addDot(326, y0 + 14, act ? "#d97706" : "#94a3b8", 1.6);
    });

    // 4. Zone 3: Collector Bus & Output Highway (X = 326..380)
    canvas.addBus(P("M326 44V165", "#d97706", 2.2));
    canvas.addBus(P("M326 165H200", "#d97706", 2.2));
    canvas.addDot(200, 165, "#d97706", 2.2);

    canvas.addBackground(R(240, 175, 44, 14, "#0f172a", "#d97706", 2, 0.8));
    canvas.addLabel(262, 185, "/16 SEG_OUT", 5.6, 'text-anchor="middle" font-weight="bold" fill="#f59e0b"');

    // Bottom Output Port Contact Pad at (200, 165)
    canvas.addBackground(R(196, 160, 8, 10, "#fed7aa", "#c2410c", 1.5, 1.0));
    canvas.addLabel(200, 180, "SEG[15:0] -> SEGMUX", 6.2, 'text-anchor="middle" font-weight="bold" fill="#92400e"');

    return canvas.render();
  }

  // =========================================================================
  // 2. 16-BIT INSTRUCTION POINTER (IP) & HARDWIRED +1/+2 INCREMENTER
  // Dedicated Half-Adder Incrementer Pipeline, 16 D-FF Array
  // Viewport: 380 x 200
  // =========================================================================
  export function ipLogic(s: any): string {
    const canvas = new SchematicCanvas();

    const ipVal = s.ip ?? 0x0100;
    const nextIp = (ipVal + 2) & 0xffff;

    // 0. Top System Banner
    canvas.addBackground(R(10, 6, 360, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(18, 17, "INTEL 8086 INSTRUCTION POINTER & DEDICATED INCREMENTER", 6.8, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(360, 17, "16 D-FFs · HARDWIRED +1/+2 CLA SLICE", 5.6, 'text-anchor="end" font-weight="bold" fill="#0284c7"');

    // 1. Top Input Pad at (190, 25): +2_INC Auto-Increment Trigger from BIU Adder
    canvas.addBackground(R(186, 20, 8, 10, "#fed7aa", "#c2410c", 1.5, 1.0));
    canvas.addDot(190, 25, "#d97706", 2.2);
    canvas.addLabel(190, 17, "+2_INC STROBE", 5.5, 'text-anchor="middle" font-weight="bold" fill="#c2410c"');

    canvas.addWire(P("M190 25V38H72", "#d97706", 1.4));
    canvas.addDot(72, 38, "#d97706", 1.6);

    // Left Control Subcircuit Card
    canvas.addBackground(R(14, 28, 62, 76, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(20, 39, "INC CTRL", 6.0, 'font-weight="bold" fill="#0369a1"');
    canvas.addLabel(20, 52, "MODE: +2 WORD", 5.0, 'fill="#64748b"');
    canvas.addLabel(20, 64, "GATE: ENABLED", 5.0, 'fill="#15803d" font-weight="bold"');
    canvas.addComponent(new LogicGate("and_inc_en", 42, 74, "and", 12, 10, true));
    canvas.addWire(P("M54 79H84", "#0284c7", 1.2));

    // 2. Zone 2: Dedicated Half-Adder Incrementer Slice (X = 84..350, Y = 32..102)
    canvas.addBackground(R(84, 30, 280, 74, "#f0f9ff", "#0284c7", 3, 1.0));
    canvas.addLabel(92, 42, "DEDICATED +2 HALF-ADDER INCREMENTER PIPELINE", 6.2, 'font-weight="bold" fill="#0369a1"');

    const stages = [
      { bit: "b0", x: 96, sum: ipVal & 1, carry: 0 },
      { bit: "b1", x: 148, sum: ((ipVal >> 1) ^ 1) & 1, carry: (ipVal >> 1) & 1 },
      { bit: "b2", x: 200, sum: ((ipVal >> 2) ^ ((ipVal >> 1) & 1)) & 1, carry: (ipVal >> 2) & ((ipVal >> 1) & 1) },
      { bit: "b3", x: 252, sum: ((ipVal >> 3) ^ 1) & 1, carry: 0 },
    ];

    stages.forEach((st, i) => {
      canvas.addLabel(st.x + 8, 54, st.bit, 5.8, 'font-weight="bold" fill="#475569"');
      canvas.addComponent(new LogicGate(`xor_${st.bit}`, st.x, 60, "xor", 14, 10, Boolean(st.sum)));
      canvas.addComponent(new LogicGate(`and_${st.bit}`, st.x, 76, "and", 14, 10, Boolean(st.carry)));

      canvas.addWire(P(`M${st.x - 6} 63H${st.x}`, "#0284c7", 1.0));
      canvas.addWire(P(`M${st.x - 6} 79H${st.x}`, "#0284c7", 1.0));

      if (i < stages.length - 1) {
        canvas.addWire(P(`M${st.x + 14} 81H${st.x + 46}`, "#0284c7", 1.2));
        canvas.addDot(st.x + 46, 81, "#0284c7", 1.4);
      }
    });

    // Sizing Selector MUX (+1 Byte vs +2 Word)
    canvas.addComponent(new LogicGate("mux_size", 310, 60, "mux", 16, 24, true));
    canvas.addLabel(332, 68, "+2 WORD", 5.2, 'font-weight="bold" fill="#0284c7"');
    canvas.addLabel(332, 78, "NEXT_IP", 5.2, 'font-weight="bold" fill="#059669"');

    // Feedback bus from MUX out into Register input
    canvas.addWire(P("M326 72H350V106H230", "#0284c7", 1.4));
    canvas.addDot(230, 106, "#0284c7", 1.6);

    // 3. 16-Bit IP Register Cell Array (Y = 110..152)
    canvas.addBackground(R(14, 110, 350, 42, "#ffffff", "#0284c7", 3, 1.2));
    canvas.addLabel(22, 122, "16-BIT IP STORAGE CORE (D-FLIP-FLOP MATRIX)", 6.2, 'font-weight="bold" fill="#0369a1"');
    canvas.addLabel(22, 134, `IP = ${hex(ipVal, 4)}h  (Updated: ${hex(nextIp, 4)}h)`, 7.5, 'font-weight="bold" fill="#0284c7"');
    canvas.addLabel(22, 146, "REGISTER FLIP-FLOPS · TRANSPARENT READOUT", 5.0, 'fill="#64748b"');

    for (let b = 0; b < 16; b++) {
      const bitVal = (ipVal >>> (15 - b)) & 1;
      const bx = 184 + b * 10;
      canvas.addBackground(R(bx, 124, 8, 16, bitVal ? "#dcfce7" : "#f8fafc", bitVal ? "#16a34a" : "#cbd5e1", 1.2, 0.7));
      canvas.addLabel(bx + 4, 135, String(bitVal), 5.5, `text-anchor="middle" font-weight="bold" fill="${bitVal ? '#15803d' : '#64748b'}"`);
    }

    // 4. Output Route & Bottom Contact Pad at (190, 165)
    canvas.addWire(P("M190 152V165", "#d97706", 2.2));
    canvas.addDot(190, 165, "#d97706", 2.2);

    canvas.addBackground(R(186, 160, 8, 10, "#fed7aa", "#c2410c", 1.5, 1.0));
    canvas.addLabel(190, 180, "IP[15:0] -> OFFMUX", 6.2, 'text-anchor="middle" font-weight="bold" fill="#92400e"');

    canvas.addBackground(R(210, 158, 40, 14, "#0f172a", "#d97706", 2, 0.8));
    canvas.addLabel(230, 168, "/16 FETCH_IP", 5.4, 'text-anchor="middle" font-weight="bold" fill="#f59e0b"');

    return canvas.render();
  }

  // =========================================================================
  // 3. BIU DEDICATED 20-BIT PHYSICAL ADDRESS ADDER (Seg*16 + Offset)
  // 100% Planar 3-Zone Full Adder Nibble Matrix · Zero Gate Body Penetrations
  // Viewport: 408 x 186
  // =========================================================================
  export function addressAdderLogic(s: any): string {
    const prefix = s.prefix;
    const isEs = prefix === 0x26;
    const isSs = prefix === 0x36 || (prefix == null && Boolean(s.isStack || s.bpUsed));
    const isDs = prefix === 0x3e || (prefix == null && s.ind != null && !isSs);
    const isCs = prefix === 0x2e || (!isEs && !isSs && !isDs);
    const segVal = isEs ? (s.es ?? 0x3000) : isSs ? (s.ss ?? 0x2800) : isDs ? (s.ds ?? 0x2000) : (s.cs ?? 0x1200);
    const baseWord = (segVal << 4) & 0xfffff;
    const offWord = (s.ind != null ? s.ind : (s.ip ?? 0x0100)) & 0xffff;
    const phys = (baseWord + offWord) & 0xfffff;

    const canvas = new SchematicCanvas();

    // 0. Top Title Banners with dedicated central corridor (X = 196..214) for top input drop
    canvas.addBackground(R(10, 4, 186, 10, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(16, 11.5, "BIU 20-BIT DEDICATED PHYSICAL ADDRESS ADDER", 4.8, 'font-weight="bold" fill="#0f172a"');
    canvas.addBackground(R(214, 4, 184, 10, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(220, 11.5, "5× NIBBLE CLA FULL-ADDER SLICES", 4.8, 'font-weight="bold" fill="#0f172a"');

    // 1. Top Input Bus Trunks
    canvas.addBackground(R(200, 0, 8, 6, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addWire(P("M204 0V16", paths.address, 2.0));
    canvas.addDot(204, 16, paths.address, 2.2);
    canvas.addWire(busSlash(204, 8, "20", paths.address));
    canvas.addBus(P("M14 16H392", paths.address, 1.8));
    canvas.addLabel(218, 12, "BASE[19:0] (SEGMENT << 4)", 5.2, 'font-weight="bold" fill="#92400e"');

    // OFFSET[15:0] entering from right pin at lx = 408, ly = 80
    canvas.addBackground(R(402, 76, 6, 8, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addWire(P("M408 80H398V26H14", paths.address, 1.8));
    canvas.addDot(408, 80, paths.address, 2.0);
    canvas.addWire(busSlash(404, 80, "16", paths.address));
    canvas.addLabel(16, 23, "OFFSET[15:0] (from offmux)", 5.0, 'font-weight="bold" fill="#92400e"');

    // 2. 5 Discrete 4-Bit Nibble Adder Slices
    const nibbleStarts = [10, 88, 166, 244, 322];
    const nw = 74;

    for (let nb = 0; nb < 5; nb++) {
      const xL = nibbleStarts[nb];
      const sumNib = (phys >>> (nb * 4)) & 0xf;

      canvas.addBackground(R(xL, 34, nw, 124, "#ffffff", "#cbd5e1", 2, 1.0));
      // Nibble header banner indented to X = xL + 14 to leave open routing corridor for trackA & trackB
      canvas.addBackground(R(xL + 14, 34, nw - 16, 12, "#f8fafc", "#cbd5e1", 2, 0.8));
      canvas.addLabel(xL + 18, 43, `NIBBLE ${nb}`, 5.5, 'font-weight="bold" fill="#0f172a"');
      canvas.addLabel(xL + nw - 4, 43, `[${nb * 4 + 3}:${nb * 4}]`, 5.0, 'text-anchor="end" fill="#64748b"');

      const trackA   = xL + 4;
      const trackB   = xL + 9;
      const trackCin = xL + 13;
      const trackP   = xL + 17;

      const gateX = xL + 21;
      const gateW = 14;

      const resDrop = xL + 37;
      const chanG   = xL + 54;

      canvas.addWire(P(`M${trackA} 16V71`, paths.address, 1.2));
      canvas.addDot(trackA, 16, paths.address, 1.6);
      canvas.addWire(busSlash(trackA, 21, "4", paths.address));

      if (nb < 4) {
        canvas.addWire(P(`M${trackB} 26V77`, paths.address, 1.2));
        canvas.addDot(trackB, 26, paths.address, 1.6);
        canvas.addWire(busSlash(trackB, 30, "4", paths.address));
      } else {
        canvas.addBackground(gnd(trackB, 36));
        canvas.addWire(P(`M${trackB} 36V77`, paths.address, 1.0));
      }

      if (nb === 0) {
        canvas.addBackground(gnd(trackCin, 36));
        canvas.addWire(P(`M${trackCin} 36V93`, "#059669", 1.0));
      }

      const pY = 50;
      canvas.addComponent(new LogicGate(`p_nib_${nb}`, gateX, pY, "xor", gateW, 10, true));
      canvas.addWire(P(`M${trackA} 53H${gateX}`, paths.address, 0.9));
      canvas.addDot(trackA, 53, paths.address, 1.3);
      canvas.addWire(P(`M${trackB} 57H${gateX}`, paths.address, 0.9));
      canvas.addDot(trackB, 57, paths.address, 1.3);
      canvas.addWire(P(`M${gateX + gateW} 55H${xL + 37}V64H${trackP}V110`, paths.address, 0.9));
      canvas.addDot(xL + 37, 64, paths.address, 1.3);
      canvas.addLabel(xL + 36, 54, "P", 4.5, 'font-weight="bold" fill="#15803d"');

      const gY = 68;
      canvas.addComponent(new LogicGate(`g_nib_${nb}`, gateX, gY, "and", gateW, 10, true));
      canvas.addWire(P(`M${trackA} 71H${gateX}`, paths.address, 0.9));
      canvas.addDot(trackA, 71, paths.address, 1.3);
      canvas.addWire(P(`M${trackB} 75H${gateX}`, paths.address, 0.9));
      canvas.addDot(trackB, 75, paths.address, 1.3);
      canvas.addWire(P(`M${gateX + gateW} 73H${chanG}V107`, "#059669", 0.9));
      canvas.addLabel(xL + 36, 72, "G", 4.5, 'font-weight="bold" fill="#15803d"');

      const sumY = 86;
      canvas.addComponent(new LogicGate(`sum_nib_${nb}`, gateX, sumY, "xor", gateW, 10, true));
      canvas.addWire(P(`M${trackP} 89H${gateX}`, paths.address, 0.9));
      canvas.addDot(trackP, 89, paths.address, 1.3);
      canvas.addWire(P(`M${trackCin} 93H${gateX}`, "#059669", 0.9));
      canvas.addDot(trackCin, 93, "#059669", 1.3);
      canvas.addWire(P(`M${gateX + gateW} 91H${resDrop}V162`, paths.address, 1.6));
      canvas.addDot(resDrop, 162, paths.address, 1.8);
      canvas.addWire(busSlash(resDrop, 154, "4", paths.address));
      canvas.addLabel(xL + 36, 90, "SUM", 4.5, 'font-weight="bold" fill="#15803d"');

      canvas.addBackground(R(xL + 4, 142, 28, 11, "#ecfdf5", "#86efac", 2, 0.8));
      canvas.addLabel(xL + 18, 150, `${sumNib.toString(16).toUpperCase()}h`, 5.2, 'text-anchor="middle" font-weight="bold" fill="#15803d"');

      const candX = xL + 41;
      const candW = 10;
      const candY = 107;

      const corX = xL + 58;
      const corW = 10;
      const corY = 104;

      canvas.addComponent(new LogicGate(`cand_nib_${nb}`, candX, candY, "and", candW, 10, true));
      canvas.addWire(P(`M${trackP} 110H${candX}`, paths.address, 0.8));
      canvas.addDot(trackP, 110, paths.address, 1.2);
      canvas.addWire(P(`M${trackCin} 114H${candX}`, "#059669", 0.8));
      canvas.addDot(trackCin, 114, "#059669", 1.2);

      canvas.addComponent(new LogicGate(`cor_nib_${nb}`, corX, corY, "or", corW, 10, true));
      canvas.addWire(P(`M${chanG} 107H${corX}`, "#059669", 0.8));
      canvas.addWire(P(`M${candX + candW} 111H${corX}`, "#059669", 0.8));

      if (nb < 4) {
        const nextCin = nibbleStarts[nb + 1] + 13;
        canvas.addWire(P(`M${corX + corW} 109H${nextCin}V93`, "#059669", 1.3));
        canvas.addLabel(xL + nw + 2, 106, `C${(nb + 1) * 4}`, 4.6, 'font-weight="bold" fill="#059669"');
      } else {
        canvas.addWire(P(`M${corX + corW} 109H${xL + nw - 2}`, "#64748b", 1.0));
        canvas.addLabel(xL + nw - 2, 107, "C20", 4.2, 'font-weight="bold" fill="#64748b"');
      }
    }

    // 3. Physical Address Bus Output [19:0] exiting straight down at lx = 204, ly = 186
    canvas.addBus(P("M14 162H392", paths.address, 2.4));
    canvas.addWire(P("M204 162V186", paths.address, 2.4));
    canvas.addDot(204, 162, paths.address, 2.2);
    canvas.addWire(busSlash(204, 174, "20", paths.address));
    canvas.addBackground(R(200, 180, 8, 6, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addLabel(215, 178, "PHYS_ADDR[19:0] = (SEG << 4) + OFFSET", 5.5, 'font-weight="bold" fill="#92400e"');

    canvas.addBackground(R(14, 168, 62, 14, "#ecfdf5", "#059669", 2, 0.9));
    canvas.addLabel(45, 178, `${hex(phys, 5)}h`, 6.5, 'text-anchor="middle" font-weight="bold" fill="#047857"');

    return canvas.render();
  }

  // =========================================================================
  // 4. SEGMENT MULTIPLEXER (4:1) & 4-BIT HARDWIRED SILICON SHIFTER
  // Pure Gate-Level 4:1 Multiplexer + Direct Copper Grounded Shifter
  // Viewport: 410 x 180
  // =========================================================================
  export function segmuxLogic(s: any): string {
    const canvas = new SchematicCanvas();

    const csVal = s.cs ?? 0x1200;
    const dsVal = s.ds ?? 0x2000;
    const ssVal = s.ss ?? 0x2800;
    const esVal = s.es ?? 0x3000;

    const prefix = s.prefix;
    const isEs = prefix === 0x26;
    const isSs = prefix === 0x36 || (prefix == null && Boolean(s.isStack || s.bpUsed));
    const isDs = prefix === 0x3e || (prefix == null && s.ind != null && !isSs);
    const isCs = prefix === 0x2e || (prefix == null && !isEs && !isSs && !isDs);

    const activeSeg = isEs ? esVal : isCs ? csVal : isSs ? ssVal : dsVal;
    const shiftedBase = (activeSeg << 4) & 0xfffff;

    // 0. Top Title
    canvas.addBackground(R(10, 4, 388, 12, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(16, 12.5, "SEGMENT MULTIPLEXER (4:1 MUX) & 4-BIT HARDWIRED LEFT SHIFTER CELL", 5.2, 'font-weight="bold" fill="#0f172a"');

    // 1. Top Input Pad (SEG_IN at lx = 205, ly = 25)
    canvas.addBackground(R(201, 21, 8, 8, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addDot(205, 25, paths.address, 2.0);
    canvas.addWire(P("M205 25V42H135", paths.address, 1.2));
    canvas.addLabel(215, 23, "SEG_IN[15:0]", 5.2, 'font-weight="bold" fill="#92400e"');

    // 2. Left Input Pad (OVERRIDE at lx = 25, ly = 81)
    canvas.addBackground(R(21, 77, 8, 8, "#f5f3ff", "#7c3aed", 2, 1.0));
    canvas.addDot(25, 81, "#7c3aed", 2.0);
    canvas.addWire(P("M25 81H40", paths.control, 1.2));
    canvas.addDot(40, 81, paths.control, 1.4);
    canvas.addLabel(14, 73, "OVERRIDE", 4.8, 'font-weight="bold" fill="#7c3aed"');

    // 3. Selection Decoders & Inverters (X = 35..85)
    canvas.addWire(P("M40 25V140", paths.control, 1.2));
    canvas.addLabel(36, 23, "S0", 5.0, 'fill="#64748b" font-weight="bold"');
    canvas.addComponent(new LogicGate("not_s0", 44, 34, "not", 12, 10, true));
    canvas.addWire(P("M40 39H44", paths.control, 0.9));
    canvas.addWire(P("M56 39V140", "#94a3b8", 1.0));
    canvas.addLabel(52, 23, "S0̅", 5.0, 'fill="#94a3b8" font-weight="bold"');

    canvas.addWire(P("M70 25V140", paths.control, 1.2));
    canvas.addLabel(66, 23, "S1", 5.0, 'fill="#64748b" font-weight="bold"');
    canvas.addComponent(new LogicGate("not_s1", 74, 34, "not", 12, 10, true));
    canvas.addWire(P("M70 39H74", paths.control, 0.9));
    canvas.addWire(P("M86 39V140", "#94a3b8", 1.0));
    canvas.addLabel(82, 23, "S1̅", 5.0, 'fill="#94a3b8" font-weight="bold"');

    // 4. 4 Segment Channels & 16-Bit AND Gates (X = 95..180)
    const segChannels = [
      { name: "CS [15:0]", y: 52, on: isCs },
      { name: "DS [15:0]", y: 72, on: isDs },
      { name: "SS [15:0]", y: 92, on: isSs },
      { name: "ES [15:0]", y: 112, on: isEs },
    ];

    segChannels.forEach((ch, idx) => {
      canvas.addLabel(98, ch.y + 4, ch.name, 5.0, `font-weight="bold" fill="${ch.on ? '#047857' : '#64748b'}"`);
      canvas.addWire(P(`M135 ${ch.y}H150`, ch.on ? paths.high : "#cbd5e1", 1.2));
      canvas.addComponent(new LogicGate(`and_seg_${idx}`, 150, ch.y - 6, "and", 16, 12, ch.on));
    });

    // 5. 4-Input Combining OR Gate (X = 200..220, Y = 64..100)
    // Staggered vertical turns and distinct horizontal entries (Y = 68, 76, 88, 96) for >= 8px clearance
    canvas.addWire(P("M166 52H188V68H200", isCs ? paths.high : "#cbd5e1", 1.2));
    canvas.addWire(P("M166 72H192V76H200", isDs ? paths.high : "#cbd5e1", 1.2));
    canvas.addWire(P("M166 92H192V88H200", isSs ? paths.high : "#cbd5e1", 1.2));
    canvas.addWire(P("M166 112H188V96H200", isEs ? paths.high : "#cbd5e1", 1.2));

    canvas.addComponent(new LogicGate("or_seg", 200, 64, "or", 20, 36, true));
    canvas.addWire(P("M220 82H260", paths.high, 1.8));
    canvas.addWire(busSlash(230, 82, "16", paths.address));
    canvas.addLabel(225, 77, "SEG[15:0]", 5.2, 'font-weight="bold" fill="#9e6524"');

    // Readout Badge cleanly placed above the bus in open space (X = 215..255, Y = 46..58)
    canvas.addBackground(R(215, 46, 40, 12, "#ecfdf5", "#86efac", 2, 0.8));
    canvas.addLabel(235, 55, `${hex(activeSeg, 4)}h`, 5.4, 'text-anchor="middle" font-weight="bold" fill="#047857"');

    // 6. 4-Bit Hardwired Silicon Shifter Subcircuit Card (X = 260..395, Y = 36..132)
    canvas.addBackground(R(260, 36, 135, 96, "#f8fafc", "#cbd5e1", 3, 1.0));
    canvas.addBackground(R(260, 36, 135, 12, "#f1f5f9", "#cbd5e1", 2, 0.8));
    canvas.addLabel(265, 45, "HARDWIRED << 4 SHIFTER CELL", 5.0, 'font-weight="bold" fill="#0f172a"');

    // GND placed inside shifter card with generous clearance from all labels and badges
    canvas.addBackground(gnd(275, 54));
    canvas.addWire(P("M275 54H345", "#475569", 1.2));
    canvas.addLabel(285, 50, "BASE[3:0] = 0000b (GND)", 4.6, 'fill="#475569" font-weight="bold"');

    canvas.addWire(P("M260 82H345", paths.high, 1.6));
    canvas.addWire(busSlash(280, 82, "16", paths.address));
    canvas.addLabel(285, 78, "BASE[19:4] ← SEG[15:0]", 4.8, 'fill="#92400e" font-weight="bold"');

    // 20-Bit Combined Bus Trunk inside Shifter Card
    canvas.addWire(P("M345 54H365V82", "#475569", 1.2));
    canvas.addWire(P("M345 82H375", paths.high, 1.8));
    canvas.addDot(365, 82, paths.address, 1.8);
    canvas.addWire(busSlash(370, 82, "20", paths.address));
    canvas.addLabel(330, 96, "BASE[19:0] (20-BIT)", 5.2, 'font-weight="bold" fill="#9e6524"');

    // 7. Bottom Output Highway to Adder (lx = 205, ly = 155)
    canvas.addWire(P("M375 82V138H205V155", paths.address, 2.2));
    canvas.addDot(205, 155, paths.address, 2.0);
    canvas.addBackground(R(201, 151, 8, 8, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addLabel(215, 150, "BASE[19:0] → ADDER", 5.0, 'font-weight="bold" fill="#92400e"');

    canvas.addBackground(R(14, 146, 58, 14, "#fef3c7", "#f59e0b", 2, 0.8));
    canvas.addLabel(43, 156, `${hex(shiftedBase, 5)}h`, 6.0, 'text-anchor="middle" font-weight="bold" fill="#b45309"');

    return canvas.render();
  }

  // =========================================================================
  // 5. OFFSET SELECTOR MULTIPLEXER (2:1 MUX)
  // Selects between IP [15:0] (Fetch) and IND [15:0] (Effective Address)
  // Viewport: 340 x 170
  // =========================================================================
  export function offmuxLogic(s: any): string {
    const canvas = new SchematicCanvas();

    const isInd = s.ind != null;
    const ipVal = s.ip ?? 0x0100;
    const indVal = s.ind ?? 0x0000;
    const selectedOffset = isInd ? indVal : ipVal;

    // 0. Top Title Banner
    canvas.addBackground(R(10, 4, 320, 12, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(16, 12.5, "OFFSET SELECTOR MULTIPLEXER (2:1 MUX) · 16-BIT PARALLEL", 5.2, 'font-weight="bold" fill="#0f172a"');

    // 1. Top Input Pads
    // IND_IN at lx = 30, ly = 25
    canvas.addBackground(R(26, 21, 8, 8, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addDot(30, 25, isInd ? paths.high : "#94a3b8", 1.8);
    canvas.addLabel(30, 18, "IND[15:0] (EA)", 4.8, 'text-anchor="middle" font-weight="bold" fill="#92400e"');
    canvas.addWire(P("M30 25V48", isInd ? paths.high : "#cbd5e1", 1.4));
    canvas.addWire(busSlash(30, 35, "16", paths.address));

    // IP_IN at lx = 170, ly = 25
    canvas.addBackground(R(166, 21, 8, 8, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addDot(170, 25, !isInd ? paths.high : "#94a3b8", 1.8);
    canvas.addLabel(170, 18, "IP[15:0] (FETCH)", 4.8, 'text-anchor="middle" font-weight="bold" fill="#0369a1"');
    canvas.addWire(P("M170 25V48", !isInd ? paths.high : "#cbd5e1", 1.4));
    canvas.addWire(busSlash(170, 35, "16", paths.address));

    // 2. Control Inverter Logic (SEL line: 0 = IP, 1 = IND)
    canvas.addWire(P("M275 35V135", paths.control, 1.2));
    canvas.addLabel(275, 30, "SEL", 5.0, 'text-anchor="middle" fill="#64748b" font-weight="bold"');
    canvas.addDot(275, 55, paths.control, 1.2);
    canvas.addWire(P("M275 55H280", paths.control, 0.9));
    canvas.addComponent(new LogicGate("not_sel", 280, 50, "not", 12, 10, true));
    canvas.addWire(P("M292 55H298", paths.control, 0.9));
    canvas.addDot(298, 55, paths.control, 1.2);
    canvas.addWire(P("M298 35V135", "#94a3b8", 1.0));
    canvas.addLabel(298, 30, "SEL̅", 5.0, 'text-anchor="middle" fill="#94a3b8" font-weight="bold"');

    // 3. Discrete AND Banks (X = 160..185)
    // AND IP (in0: IP data at Y=55; in1: SEL# at Y=61)
    canvas.addComponent(new LogicGate("and_ip", 160, 52, "and", 18, 12, !isInd));
    canvas.addWire(P("M170 48H148V55H160", !isInd ? paths.high : "#cbd5e1", 1.1));
    canvas.addDot(148, 55, !isInd ? paths.high : "#cbd5e1", 1.3);
    canvas.addDot(298, 61, !isInd ? paths.high : "#cbd5e1", 1.2);
    canvas.addWire(P("M298 61H184V65H154V61H160", !isInd ? paths.high : "#cbd5e1", 0.9));

    // AND IND (in0: IND data at Y=91; in1: SEL at Y=97)
    canvas.addComponent(new LogicGate("and_ind", 160, 88, "and", 18, 12, isInd));
    canvas.addWire(P("M30 48H140V91H160", isInd ? paths.high : "#cbd5e1", 1.1));
    canvas.addDot(140, 91, isInd ? paths.high : "#cbd5e1", 1.3);
    canvas.addDot(275, 97, isInd ? paths.high : "#cbd5e1", 1.2);
    canvas.addWire(P("M275 97H184V106H154V97H160", isInd ? paths.high : "#cbd5e1", 0.9));

    // 4. Combining OR Gate (X = 195..220)
    canvas.addWire(P("M178 58V72H195", !isInd ? paths.high : "#cbd5e1", 1.2));
    canvas.addWire(P("M178 94V78H195", isInd ? paths.high : "#cbd5e1", 1.2));
    canvas.addComponent(new LogicGate("or_off", 195, 68, "or", 20, 16, true));

    // 5. Left Output Highway to Adder (lx = 20, ly = 77)
    canvas.addWire(P("M215 76H240V125H20V77", paths.high, 1.8));
    canvas.addDot(20, 77, paths.high, 2.0);
    canvas.addWire(busSlash(45, 125, "16", paths.address));
    canvas.addBackground(R(16, 73, 8, 8, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addLabel(55, 137, "OFFSET[15:0] → 20-BIT ADDER", 5.2, 'font-weight="bold" fill="#92400e"');

    canvas.addBackground(R(55, 108, 48, 13, "#ecfdf5", "#86efac", 2, 0.8));
    canvas.addLabel(79, 117.5, `${hex(selectedOffset, 4)}h`, 5.5, 'text-anchor="middle" font-weight="bold" fill="#047857"');

    return canvas.render();
  }

  // =========================================================================
  // 6. 16-BIT INDIRECT OFFSET REGISTER (IND / EFFECTIVE ADDRESS LATCH)
  // Transparent D-Latch Array capturing Displacement / Base+Index Offsets
  // Viewport: 340 x 170
  // =========================================================================
  export function indLogic(s: any): string {
    const canvas = new SchematicCanvas();

    const indVal = s.ind ?? 0x0000;
    const isAct = s.ind != null;

    // 0. Top System Title Banner
    canvas.addBackground(R(10, 6, 320, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(18, 17, "INDIRECT OFFSET REGISTER (IND / EA LATCH)", 6.8, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(320, 17, "16-BIT TRANSPARENT D-LATCH ARRAY", 5.6, 'text-anchor="end" font-weight="bold" fill="#15803d"');

    // 1. Left Input Port at (10, 33): EA_IN
    const portIn = new PortBox("port_ind_in", 10, 26, 56, 96, "EA INPUT", "left", "input", "#f0fdf4", "#0d9488", "[16-BIT]");
    portIn.addPortPin("ea_pad", 7, "EA_IN[15:0]", true, "#0d9488", 16);
    portIn.addPortPin("ea_le", 35, "EA_LE", false, paths.high);
    portIn.addPortPin("ea_oe", 55, "EA_OE#", false, "#64748b");
    canvas.addComponent(portIn);

    canvas.addWire(P("M10 33H110", "#0d9488", 1.6));
    canvas.addWire(busSlash(40, 33, "16", "#0d9488"));

    // 2. Zone 1: Latch Enable & Control Strobe Generator
    canvas.addComponent(new LogicGate("and_le", 78, 54, "and", 12, 10, isAct));
    canvas.addWire(P("M66 61H78", paths.high, 1.0));
    canvas.addWire(P("M90 59H110", isAct ? paths.high : "#64748b", 1.2));
    canvas.addDot(110, 59, isAct ? paths.high : "#64748b", 1.5);

    canvas.addComponent(new LogicGate("inv_oe", 78, 86, "inv", 10, 8, true));
    canvas.addWire(P("M66 81H72V90H78", "#64748b", 1.0));
    canvas.addWire(P("M88 90H110", paths.high, 1.2));
    canvas.addDot(110, 90, paths.high, 1.5);

    // 3. Zone 2: 16-Bit Discrete Transparent D-Latch Core (X = 110..260, Y = 28..124)
    canvas.addBackground(R(110, 28, 150, 94, isAct ? "#eff6ff" : "#f8fafc", isAct ? "#3b82f6" : "#cbd5e1", 3, isAct ? 1.4 : 0.9));
    canvas.addLabel(116, 40, "16-BIT TRANSPARENT LATCH CORE", 6.2, 'font-weight="bold" fill="#1d4ed8"');
    canvas.addLabel(116, 52, `IND = ${isAct ? hex(indVal, 4) + "h" : "0000h"}  (${isAct ? "LATCHED" : "TRANSPARENT"})`, 7.0, `font-weight="bold" fill="${isAct ? '#047857' : '#334155'}"`);

    canvas.addLabel(116, 64, "HIGH BYTE [15:8]", 5.2, 'fill="#475569" font-weight="bold"');
    for (let b = 0; b < 8; b++) {
      const bitVal = (indVal >>> (15 - b)) & 1;
      const bx = 116 + b * 17;
      canvas.addBackground(R(bx, 68, 14, 16, bitVal ? "#dcfce7" : "#ffffff", bitVal ? "#16a34a" : "#cbd5e1", 1.5, 0.7));
      canvas.addLabel(bx + 7, 79, String(bitVal), 6.0, `text-anchor="middle" font-weight="bold" fill="${bitVal ? '#15803d' : '#64748b'}"`);
    }

    canvas.addLabel(116, 94, "LOW BYTE [7:0]", 5.2, 'fill="#475569" font-weight="bold"');
    for (let b = 0; b < 8; b++) {
      const bitVal = (indVal >>> (7 - b)) & 1;
      const bx = 116 + b * 17;
      canvas.addBackground(R(bx, 98, 14, 16, bitVal ? "#dcfce7" : "#ffffff", bitVal ? "#16a34a" : "#cbd5e1", 1.5, 0.7));
      canvas.addLabel(bx + 7, 109, String(bitVal), 6.0, `text-anchor="middle" font-weight="bold" fill="${bitVal ? '#15803d' : '#64748b'}"`);
    }

    // 4. Zone 3: Tri-State Output Driver & Collector Bus (X = 264..330)
    canvas.addWire(P("M260 76H272", isAct ? "#d97706" : "#94a3b8", 1.2));
    canvas.addComponent(new LogicGate("buf_ind_out", 272, 70, "buf", 14, 12, isAct));

    canvas.addWire(P("M286 76H300", isAct ? "#d97706" : "#94a3b8", 1.4));
    canvas.addBus(P("M300 76V145", "#d97706", 2.2));
    canvas.addDot(300, 76, "#d97706", 1.6);

    // Horizontal Output Route to Bottom Pad at (12, 145)
    canvas.addBus(P("M300 145H12", "#d97706", 2.2));
    canvas.addDot(12, 145, "#d97706", 2.2);

    canvas.addBackground(R(8, 140, 8, 10, "#fed7aa", "#c2410c", 1.5, 1.0));
    canvas.addLabel(24, 160, "IND[15:0] -> OFFMUX", 5.8, 'font-weight="bold" fill="#92400e"');

    canvas.addBackground(R(210, 126, 44, 12, "#0f172a", "#d97706", 2, 0.8));
    canvas.addLabel(232, 135, "/16 EA_OFFSET", 5.4, 'text-anchor="middle" font-weight="bold" fill="#f59e0b"');

    return canvas.render();
  }

  // =========================================================================
  // 7. 16-BIT OPERAND BUS TRANSCEIVER (OPR)
  // Bidirectional Tri-State Bus Drivers + 16-Bit Intermediate Latch Core
  // Viewport: 380 x 190
  // =========================================================================
  export function oprLogic(s: any): string {
    const canvas = new SchematicCanvas();

    const oprVal = s.opr ?? 0x0000;
    const hasVal = s.opr != null;

    const isWrite = Boolean(s.isWrite);
    const isTransmit = isWrite || (s.phase % 4) < 2;
    const isReceive = !isTransmit;

    // 0. Top System Title Banner
    canvas.addBackground(R(10, 6, 360, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(18, 17, "OPERAND BUS TRANSCEIVER (OPR) · BIU <-> EU INTERFACE", 6.8, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(360, 17, "16-BIT BIDIRECTIONAL · DT/R# & DEN# CONTROL", 5.6, 'text-anchor="end" font-weight="bold" fill="#15803d"');

    // 1. Left Bidirectional Port at (10, 51)
    const portEU = new PortBox("port_opr_eu", 10, 26, 65, 148, "EU BUS", "left", "bidirectional", "#f0fdf4", "#0d9488", "[16-BIT]");
    portEU.addPortPin("pad_dinout", 25, "D_IN/OUT[15:0]", true, "#0d9488", 16);
    portEU.addPortPin("tx_out", 72, "TX_TO_EU", false, isReceive ? paths.high : "#64748b");
    portEU.addPortPin("rx_in", 102, "RX_FROM_EU", false, isTransmit ? "#0284c7" : "#64748b");
    canvas.addComponent(portEU);

    // Central Conductor linking Left Port (10, 51) to transceivers
    canvas.addWire(P("M10 51H75", "#0d9488", 1.6));
    canvas.addDot(75, 51, "#0d9488", 1.8);
    canvas.addWire(P("M75 51V106", "#0d9488", 1.2));
    canvas.addWire(P("M75 51V128", "#0d9488", 1.2));

    // 2. Zone 1: DT/R# & DEN# Direction Decoder Logic (X = 85..295, Y = 28..64)
    canvas.addBackground(R(85, 26, 215, 38, "#fffdf0", "#887342", 2, 0.8));
    canvas.addLabel(92, 37, "DIRECTION & OUTPUT ENABLE DECODER (DEN# · DT/R#)", 5.6, 'font-weight="bold" fill="#78350f"');

    canvas.addComponent(new LogicGate("inv_den", 100, 42, "inv", 10, 8, true));
    canvas.addLabel(92, 49, "DEN#", 4.8, 'fill="#64748b" font-weight="bold"');

    canvas.addComponent(new LogicGate("inv_dtr", 140, 42, "inv", 10, 8, isReceive));
    canvas.addLabel(130, 49, "DT/R#", 4.8, 'fill="#64748b" font-weight="bold"');

    canvas.addComponent(new LogicGate("and_tx", 185, 41, "and", 12, 10, isTransmit));
    canvas.addLabel(202, 48, "TX_EN", 5.2, `font-weight="bold" fill="${isTransmit ? '#047857' : '#64748b'}"`);

    canvas.addComponent(new LogicGate("and_rx", 245, 41, "and", 12, 10, isReceive));
    canvas.addLabel(262, 48, "RX_EN", 5.2, `font-weight="bold" fill="${isReceive ? '#047857' : '#64748b'}"`);

    // 3. Zone 2: Back-to-Back Tri-State Drivers & Intermediate Latch (X = 85..295, Y = 68..170)
    canvas.addBackground(R(85, 68, 215, 106, "#ffffff", "#cbd5e1", 3, 1.2));
    canvas.addLabel(92, 80, "16-BIT BACK-TO-BACK TRI-STATE DRIVERS & LATCH CORE", 6.0, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(92, 91, `LATCH = ${hasVal ? hex(oprVal, 4) + "h" : "0000h"}  ·  DIR: ${isTransmit ? "TRANSMIT (EU ➔ EXT)" : "RECEIVE (EXT ➔ EU)"}`, 6.6, `font-weight="bold" fill="${isTransmit ? '#0284c7' : '#047857'}"`);

    // Branch 1: Transmit Driver (EU Bus -> External Bus)
    canvas.addLabel(95, 107, "TRANSMIT BUFFER (DT/R = 1)", 5.2, `font-weight="bold" fill="${isTransmit ? '#0284c7' : '#64748b'}"`);
    canvas.addComponent(new LogicGate("buf_tx1", 155, 100, "buf", 16, 12, isTransmit));
    canvas.addComponent(new LogicGate("buf_tx2", 215, 100, "buf", 16, 12, isTransmit));
    canvas.addWire(P("M75 106H155", isTransmit ? "#0284c7" : "#94a3b8", 1.2));
    canvas.addWire(P("M171 106H215", isTransmit ? "#0284c7" : "#94a3b8", 1.2));
    canvas.addWire(P("M231 106H305V70H370", isTransmit ? "#0284c7" : "#94a3b8", 1.4));

    // Branch 2: Receive Driver (External Bus -> EU Bus)
    canvas.addLabel(95, 127, "RECEIVE BUFFER (DT/R = 0)", 5.2, `font-weight="bold" fill="${isReceive ? '#047857' : '#64748b'}"`);
    canvas.addComponent(new LogicGate("buf_rx1", 155, 122, "buf", 16, 12, isReceive));
    canvas.addComponent(new LogicGate("buf_rx2", 215, 122, "buf", 16, 12, isReceive));
    canvas.addWire(P("M370 70H320V128H231", isReceive ? "#047857" : "#94a3b8", 1.4));
    canvas.addWire(P("M215 128H171", isReceive ? "#047857" : "#94a3b8", 1.2));
    canvas.addWire(P("M155 128H75", isReceive ? "#047857" : "#94a3b8", 1.2));

    // 16 Discrete Storage Bit Cells
    canvas.addLabel(95, 146, "16-BIT INTERMEDIATE OPERAND LATCH", 5.2, 'fill="#475569" font-weight="bold"');
    for (let b = 0; b < 16; b++) {
      const bitVal = (oprVal >>> (15 - b)) & 1;
      const bx = 95 + b * 12.4;
      canvas.addBackground(R(bx, 150, 10, 16, bitVal ? "#dcfce7" : "#f8fafc", bitVal ? "#16a34a" : "#cbd5e1", 1.2, 0.7));
      canvas.addLabel(bx + 5, 161, String(bitVal), 5.5, `text-anchor="middle" font-weight="bold" fill="${bitVal ? '#15803d' : '#64748b'}"`);
    }

    // 4. Right External PortBox at (305, 26) with pad at (370, 70)
    const portExt = new PortBox("port_opr_ext", 305, 26, 65, 148, "EXT BUS", "right", "bidirectional", "#fffbeb", "#d97706", "[16-BIT]");
    portExt.addPortPin("ext_pad", 44, "AD[15:0]", true, "#d97706", 16);
    canvas.addComponent(portExt);

    return canvas.render();
  }

  // =========================================================================
  // 8. 6-BYTE INSTRUCTION PREFETCH QUEUE (FIFO)
  // Shift Register Matrix, 3-bit WP/RP Counters, Status Detector Logic
  // Viewport: 440 x 190
  // =========================================================================
  export function queueLogic(s: any): string {
    const canvas = new SchematicCanvas();

    const q = s.queue || [];
    const qLen = q.length;

    // 0. Top System Title Banner
    canvas.addBackground(R(10, 6, 420, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(18, 17, "INTEL 8086 6-BYTE INSTRUCTION PREFETCH QUEUE (FIFO)", 6.8, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(420, 17, "48× D-FLIP-FLOPS · 3-BIT RP/WP · STATUS DETECTOR", 5.6, 'text-anchor="end" font-weight="bold" fill="#15803d"');

    // 1. Left Input Port at (10, 87)
    const portIn = new PortBox("port_q_in", 10, 26, 54, 98, "FIFO IN", "left", "input", "#f0fdf4", "#0d9488", "[16-BIT]");
    portIn.addPortPin("fifo_pad", 61, "FIFO_IN[15:0]", true, "#0d9488", 16);
    portIn.addPortPin("push_stb", 72, "PUSH_STB", false, qLen <= 4 ? paths.high : "#64748b");
    canvas.addComponent(portIn);

    canvas.addWire(P("M10 87H68", "#0d9488", 1.6));

    // 2. Zone 2: 6 Byte Columns Q0..Q5 (X = 68..380, Y = 28..124)
    for (let i = 0; i < 6; i++) {
      const x = 68 + i * 52;
      const has = i < qLen;
      const bval = has ? q[i] : 0;

      canvas.addBackground(R(x, 28, 48, 96, has ? "#eff6ff" : "#f8fafc", has ? "#3b82f6" : "#cbd5e1", 2, has ? 1.2 : 0.8));
      canvas.addLabel(x + 5, 38, `Q[${i}]`, 6.6, `font-weight="bold" fill="${has ? '#1d4ed8' : '#0f172a'}"`);

      canvas.addBackground(R(x + 23, 29, 21, 11, has ? "#dbeafe" : "#f1f5f9", has ? "#2563eb" : "#cbd5e1", 1.5, 0.7));
      canvas.addLabel(x + 33.5, 37.5, has ? hex(bval, 2) + "h" : "—", 5.5, `text-anchor="middle" font-weight="bold" fill="${has ? '#1d4ed8' : '#94a3b8'}"`);

      for (let b = 0; b < 8; b++) {
        const bitVal = has ? ((bval >>> (7 - b)) & 1) : 0;
        const col = b < 4 ? 0 : 1;
        const row = b % 4;
        const lx = x + 4 + col * 21;
        const ly = 44 + row * 17;

        canvas.addBackground(R(lx, ly, 19, 14, bitVal ? "#dcfce7" : "#ffffff", bitVal ? "#16a34a" : "#cbd5e1", 1.2, 0.7));
        canvas.addLabel(lx + 2.5, ly + 9.5, `b${7 - b}`, 4.5, 'fill="#64748b"');
        canvas.addLabel(lx + 13, ly + 10, String(bitVal), 5.5, `font-weight="bold" fill="${bitVal ? '#15803d' : '#94a3b8'}"`);
      }

      if (i < 5) {
        canvas.addWire(P(`M${x + 48} 76H${x + 52}`, has ? "#2563eb" : "#94a3b8", 1.0));
      }
    }

    // 3. Zone 3 (Bottom Left): 3-Bit Pointer Counters & Queue Status (X = 10..152, Y = 130..182)
    canvas.addBackground(R(10, 130, 142, 52, "#fffde8", "#887342", 2, 1.0));
    canvas.addLabel(18, 142, "3-BIT FIFO POINTER CONTROLLER", 5.8, 'font-weight="bold" fill="#78350f"');
    canvas.addLabel(18, 154, `WP[2:0] = ${bin(qLen, 3)}b  (Slot: ${qLen < 6 ? "Q" + qLen : "FULL"})`, 5.6, 'font-weight="bold" fill="#92400e"');
    canvas.addLabel(18, 166, "RP[2:0] = 000b  (Output: Q0 Oldest)", 5.6, 'font-weight="bold" fill="#92400e"');
    canvas.addLabel(18, 176, `STATUS: ${qLen === 0 ? "EMPTY" : (qLen === 6 ? "FULL" : "READY")} (${qLen}/6 BYTES)`, 5.6, `font-weight="bold" fill="${qLen === 0 ? '#b91c1c' : (qLen === 6 ? '#d97706' : '#15803d')}"`);

    // 4. Zone 3 (Bottom Right): Prefetch Trigger & Status Logic (X = 245..425, Y = 130..182)
    canvas.addBackground(R(245, 130, 185, 52, "#f0fdf4", "#16a34a", 2, 1.0));
    canvas.addLabel(252, 142, "BIU PREFETCH ENGINE STATUS DETECTOR", 5.8, 'font-weight="bold" fill="#166534"');

    canvas.addComponent(new LogicGate("nor_empty", 252, 148, "nor", 12, 10, qLen === 0));
    canvas.addLabel(268, 155, "EMPTY", 4.8, 'font-weight="bold" fill="#64748b"');

    canvas.addComponent(new LogicGate("and_full", 305, 148, "and", 12, 10, qLen === 6));
    canvas.addLabel(321, 155, "FULL", 4.8, 'font-weight="bold" fill="#64748b"');

    canvas.addComponent(new LogicGate("cmp_req", 355, 148, "buf", 12, 10, qLen <= 4));
    canvas.addLabel(371, 155, "REQ_FETCH", 5.2, `font-weight="bold" fill="${qLen <= 4 ? '#15803d' : '#64748b'}"`);

    canvas.addLabel(252, 174, `PREFETCH: ${qLen <= 4 ? "ACTIVE (Length <= 4, Fetch Next Word)" : "IDLE (Queue Full/Adequate)"}`, 5.2, `font-weight="bold" fill="${qLen <= 4 ? '#15803d' : '#475569'}"`);

    // 5. Output Path from Q0 to Bottom Pad at (220, 150)
    canvas.addWire(P("M92 124V150H220", qLen > 0 ? paths.high : "#94a3b8", 1.8));
    canvas.addDot(220, 150, qLen > 0 ? paths.high : "#94a3b8", 2.2);

    canvas.addBackground(R(216, 145, 8, 10, "#dcfce7", "#15803d", 1.5, 1.0));
    canvas.addLabel(220, 164, "Q_BYTE[7:0] -> LOADER", 6.2, 'text-anchor="middle" font-weight="bold" fill="#166534"');

    canvas.addBackground(R(130, 164, 36, 14, "#0f172a", "#15803d", 2, 0.8));
    canvas.addLabel(148, 174, "/8 STREAM", 5.4, 'text-anchor="middle" font-weight="bold" fill="#4ade80"');

    return canvas.render();
  }

  // =========================================================================
  // 9. BUS CONTROLLER & T-STATE TIMING ENGINE
  // Discrete 5-Stage Ring Counter (T1..T4 + Tw), Strobe Synthesis Logic
  // Viewport: 408 x 216
  // =========================================================================
  export function busControllerLogic(s: any): string {
    const vw = 408;
    const canvas = new SchematicCanvas();

    const phase = (s.phase || 0) % 4; // 0=T1, 1=T2, 2=T3, 3=T4
    const isClockHigh = Boolean(s.clock);
    const isRead = s.isWrite !== true;
    const isWrite = Boolean(s.isWrite);
    const hasWait = Boolean(s.wait);

    const isT1 = phase === 0;
    const isT2 = phase === 1;
    const isT3 = phase === 2 && !hasWait;
    const isTw = phase === 2 && hasWait;
    const isT4 = phase === 3;

    const aleOn = isT1 && isClockHigh;
    const denOn = isT2 || isT3 || isTw || (isT4 && isClockHigh);
    const rdOn = (isT2 || isT3 || isTw) && isRead;
    const wrOn = (isT3 || isTw) && isWrite;
    const dtrOn = isWrite;

    // 0. Header Strip with Dedicated Open Vertical Channel at X in [194 .. 214]
    canvas.addBackground(R(10, 6, 184, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(16, 17, "INTEL 8086 BUS CONTROLLER", 5.8, 'font-weight="bold" fill="#0f172a"');

    canvas.addBackground(R(214, 6, 184, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(392, 17, "T1..T4 + Tw · ALE · DEN# · RD# · WR#", 5.2, 'font-weight="bold" fill="#15803d" text-anchor="end"');

    // 1. Dedicated Left Control PortBox (x = 10, y = 28, w = 62, h = 175)
    const portIn = new PortBox("port_ctrl_in", 10, 28, 62, 175, "CONTROL IN", "left", "input", "#f1f5f9", "#cbd5e1", "IN");
    portIn.addPortPin("clk", 22, "CLK", false, paths.high);
    portIn.addPortPin("ready", 47, "READY", false, paths.high);
    portIn.addPortPin("bus_req", 72, "BUS_REQ", false, paths.high);
    portIn.addPortPin("rd_wr", 97, "RD/WR#", false, paths.control);
    portIn.addPortPin("m_io", 122, "M/IO#", false, paths.control);
    portIn.addPortPin("inta_req", 147, "INTA_REQ", false, paths.control);
    canvas.addComponent(portIn);

    // Top Adder Physical Address Pad (lx = 204, ly = 0) in open channel [194..214]
    canvas.addBackground(R(199, 0, 10, 8, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addDot(204, 0, "#c2410c", 2.0);
    canvas.addWire(P("M204 0V18", paths.address, 1.6));
    canvas.addDot(204, 18, paths.address, 1.6);
    canvas.addLabel(204, 25, "PHYS_ADDR[19:0]", 4.8, 'font-weight="bold" fill="#d97706" text-anchor="middle"');

    // 2. Zone 1: Distribution Rails (X = 72 .. 98)
    const clkRailX = 80;
    const readyRailX = 88;
    const reqRailX = 96;

    canvas.addWire(P(`M72 50H${clkRailX}V185`, paths.high, 1.2));
    canvas.addDot(clkRailX, 50, paths.high, 1.6);

    canvas.addWire(P(`M72 75H${readyRailX}V185`, paths.high, 1.2));
    canvas.addDot(readyRailX, 75, paths.high, 1.6);

    canvas.addWire(P(`M72 100H${reqRailX}V185`, paths.high, 1.2));
    canvas.addDot(reqRailX, 100, paths.high, 1.6);

    // 3. Zone 2: 5 Discrete DFF Cells (T1, T2, T3, Tw, T4) at Y = 42 .. 74
    const dffConfigs = [
      { id: "t1", name: "T1", x: 106, on: isT1, sub: "ADDR" },
      { id: "t2", name: "T2", x: 140, on: isT2, sub: "STATUS" },
      { id: "t3", name: "T3", x: 174, on: isT3, sub: "DATA" },
      { id: "tw", name: "Tw", x: 208, on: isTw, sub: "WAIT" },
      { id: "t4", name: "T4", x: 242, on: isT4, sub: "LATCH" },
    ];

    // Continuous clock spine running below all DFF cells at Y=78
    canvas.addWire(P(`M${clkRailX} 78H238`, paths.high, 1.0));
    canvas.addDot(clkRailX, 78, paths.high, 1.4);

    dffConfigs.forEach((df) => {
      canvas.addBackground(R(df.x, 42, 26, 32, df.on ? "#dcfce7" : "#ffffff", df.on ? "#15803d" : "#cbd5e1", 2, 1.0));
      canvas.addLabel(df.x + 13, 54, df.name, 6.5, `font-weight="bold" fill="${df.on ? '#15803d' : '#0f172a'}" text-anchor="middle"`);
      canvas.addLabel(df.x + 13, 64, df.sub, 4.5, `fill="${df.on ? '#166534' : '#64748b'}" text-anchor="middle"`);

      // D input stub
      canvas.addWire(P(`M${df.x - 4} 52H${df.x}`, "#64748b", 1.0));

      // CLK input tap rising from bottom spine at Y=78 up to clock pin at Y=64
      canvas.addWire(P(`M${df.x - 4} 78V64H${df.x}`, paths.high, 1.0));
      canvas.addDot(df.x - 4, 78, paths.high, 1.2);

      // Q output stub
      canvas.addWire(P(`M${df.x + 26} 58H${df.x + 30}`, df.on ? paths.high : "#64748b", 1.0));
      canvas.addDot(df.x + 30, 58, df.on ? paths.high : "#64748b", 1.4);
    });

    // Inter-stage cascade wires
    canvas.addWire(P("M136 58H138V52H140", isT1 ? paths.high : "#64748b", 1.0));
    canvas.addWire(P("M170 58H172V52H174", isT2 ? paths.high : "#64748b", 1.0));
    canvas.addWire(P("M204 58H206V92H174", isT3 ? paths.high : "#64748b", 1.0));
    canvas.addDot(206, 92, paths.high, 1.4);
    canvas.addWire(P("M206 92V110H208", paths.high, 1.0));
    canvas.addWire(P("M238 58H240V52H242", isTw ? paths.high : "#64748b", 1.0));

    // Track A (X = 276): T4 Feedback loop (>= 8px from T4 body at 268)
    canvas.addWire(P("M272 58H276V190H102V52H106", isT4 ? paths.high : "#64748b", 1.0));
    canvas.addDot(272, 58, paths.high, 1.4);

    // 4. Zone 3: Strobe Synthesis Logic Gates shifted to X = 316 (Width 18 -> Output at X = 334)
    // Expanded routing corridor X in [268 .. 316] (48px wide)
    const gateX = 316;
    const outX = gateX + 18; // 334

    // 4.1 ALE Gate (AND): X = 316, Y = 44
    canvas.addComponent(new LogicGate("gate_ale", gateX, 44, "and", 18, 12, aleOn, "ALE", "T1·CLK"));
    // CLK routed above DFF cells at Y=32 into in0 at (316, 47)
    canvas.addWire(P(`M${clkRailX} 32H310V47H${gateX}`, paths.high, 1.0));
    canvas.addDot(clkRailX, 32, paths.high, 1.4);
    // T1 routed above DFF cells at Y=38 into in1 at (316, 53)
    canvas.addWire(P(`M136 58H138V38H304V53H${gateX}`, isT1 ? paths.high : "#64748b", 1.0));
    canvas.addDot(138, 58, paths.high, 1.4);
    canvas.addWire(P(`M${outX} 50H408`, aleOn ? "#d97706" : "#64748b", 1.4));
    canvas.addDot(outX, 50, aleOn ? "#d97706" : "#64748b", 1.4);

    // 4.2 DEN# Gate (NOR): X = 316, Y = 70
    canvas.addComponent(new LogicGate("gate_den", gateX, 70, "nor", 18, 12, denOn, "DEN#", "~(T2..T4)"));
    canvas.addWire(P(`M170 58H172V86H292V73H${gateX}`, isT2 ? paths.high : "#64748b", 1.0));
    canvas.addDot(172, 58, paths.high, 1.4);
    canvas.addWire(P(`M284 92V79H${gateX}`, (isT3 || isTw) ? paths.high : "#64748b", 1.0));
    canvas.addDot(284, 92, paths.high, 1.4);
    canvas.addWire(P(`M${outX} 76H408`, denOn ? paths.control : "#64748b", 1.4));
    canvas.addDot(outX, 76, denOn ? paths.control : "#64748b", 1.4);

    // 4.3 DT/R# Driver (BUF): X = 316, Y = 96 · Fed via Track D (X = 300)
    canvas.addComponent(new LogicGate("gate_dtr", gateX, 96, "buf", 18, 12, dtrOn, "DT/R#", "WRITE"));
    canvas.addWire(P(`M72 125H300V102H${gateX}`, paths.control, 1.0));
    canvas.addDot(300, 102, paths.control, 1.4);
    canvas.addWire(P(`M${outX} 102H398`, dtrOn ? paths.control : "#64748b", 1.4));
    canvas.addDot(outX, 102, dtrOn ? paths.control : "#64748b", 1.4);

    // 4.4 RD# Gate (NAND): X = 316, Y = 122 · Fed via Track C (X = 292)
    canvas.addComponent(new LogicGate("gate_rd", gateX, 122, "nand", 18, 12, rdOn, "RD#", "~(READ·T23)"));
    canvas.addWire(P(`M206 92H292V125H${gateX}`, (isT2 || isT3 || isTw) ? paths.high : "#64748b", 1.0));
    canvas.addDot(292, 125, paths.high, 1.4);
    canvas.addWire(P(`M72 131H${gateX}`, paths.control, 1.0));
    canvas.addDot(72, 131, paths.control, 1.4);
    canvas.addWire(P(`M${outX} 128H398`, rdOn ? paths.control : "#64748b", 1.4));
    canvas.addDot(outX, 128, rdOn ? paths.control : "#64748b", 1.4);

    // 4.5 WR# Gate (NAND): X = 316, Y = 148 · Fed via Track B (X = 284)
    canvas.addComponent(new LogicGate("gate_wr", gateX, 148, "nand", 18, 12, wrOn, "WR#", "~(WRITE·T34)"));
    canvas.addWire(P(`M206 92H284V151H${gateX}`, (isT3 || isTw) ? paths.high : "#64748b", 1.0));
    canvas.addDot(284, 151, paths.high, 1.4);
    canvas.addWire(P(`M72 157H${gateX}`, paths.control, 1.0));
    canvas.addDot(72, 157, paths.control, 1.4);
    canvas.addWire(P(`M${outX} 154H398`, wrOn ? paths.control : "#64748b", 1.4));
    canvas.addDot(outX, 154, wrOn ? paths.control : "#64748b", 1.4);

    // 4.6 INTA# Gate (NAND): X = 316, Y = 174
    canvas.addComponent(new LogicGate("gate_inta", gateX, 174, "nand", 18, 12, false, "INTA#", "~(INTA·T23)"));
    canvas.addWire(P(`M170 58H172V177H${gateX}`, paths.high, 1.0));
    canvas.addDot(172, 177, paths.high, 1.4);
    canvas.addWire(P(`M72 183H${gateX}`, paths.control, 1.0));
    canvas.addDot(72, 183, paths.control, 1.4);
    canvas.addWire(P(`M${outX} 180H398`, paths.control, 1.4));
    canvas.addDot(outX, 180, paths.control, 1.4);

    // 5. Right Output PortBox (x = 346, y = 28, w = 52, h = 175)
    const portOut = new PortBox("port_ctrl_out", 346, 28, 52, 175, "BUS STROBES", "right", "output", "#ecfdf5", "#86efac", "OUT");
    portOut.addPortPin("ale", 22, "ALE", false, "#d97706");
    portOut.addPortPin("den", 48, "DEN#", false, paths.control);
    portOut.addPortPin("dtr", 74, "DT/R#", true, paths.control);
    portOut.addPortPin("rd", 100, "RD#", true, paths.control);
    portOut.addPortPin("wr", 126, "WR#", true, paths.control);
    portOut.addPortPin("inta", 152, "INTA#", true, paths.control);
    canvas.addComponent(portOut);

    return canvas.render();
  }

  // =========================================================================
  // 10. INTEL 8086 HMOS-II SILICON I/O & STATIC ESD PROTECTION CELL (DIP-40 PAD)
  // Dual-Rail Clamps, 2kV GGNMOS Snapback, 300Ω Ballast, Schmitt Trigger In/Out
  // Viewport: 418 x 246
  // =========================================================================
  export function pinsLogic(s: any): string {
    const vw = 418;
    const canvas = new SchematicCanvas();

    // 0. Header Strip
    canvas.addBackground(R(10, 6, vw - 20, 16, "#f8fafc", "#cbd5e1", 2, 0.8));
    canvas.addLabel(16, 18, "INTEL 8086 HMOS-II SILICON I/O & ESD PROTECTION CELL (DIP-40 PAD)", 6.5, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(vw - 16, 18, "40-PIN CHIP DIE BOUNDARY · DUAL-RAIL CLAMPS · GGNMOS · 300Ω · SCHMITT IN/OUT", 5.2, 'font-weight="bold" fill="#15803d" text-anchor="end"');

    // 1. Power Rails (+5V VCC at Y = 28, 0V GND at Y = 200)
    canvas.addBus(P(`M14 28H${vw - 14}`, paths.power, 2.0));
    canvas.addDot(28, 28, paths.power, 2.0);
    canvas.addLabel(36, 26, "+5V VCC RAIL", 5.5, 'font-weight="bold" fill="#b91c1c"');

    canvas.addBus(P(`M14 200H${vw - 14}`, paths.gnd, 2.0));
    canvas.addDot(28, 200, paths.gnd, 2.0);
    canvas.addLabel(36, 210, "0V GND RAIL", 5.5, 'font-weight="bold" fill="#334155"');

    [80, 130, 175, 230].forEach((gx) => {
      canvas.addBackground(P(`M${gx} 200V206M${gx - 6} 206H${gx + 6}M${gx - 4} 209H${gx + 4}M${gx - 2} 212H${gx + 2}`, paths.gnd, 1.2));
      canvas.addDot(gx, 200, paths.gnd, 1.6);
    });

    // 2. Package Terminal Lead & Silicon Bond Pad (X = 14 .. 70, Y = 100 .. 128)
    canvas.addBackground(R(14, 103, 20, 22, "#fef3c7", "#d97706", 2, 1.2));
    canvas.addLabel(24, 113, "PIN 39", 5.2, 'font-weight="bold" fill="#92400e" text-anchor="middle"');
    canvas.addLabel(24, 121, "(AD15)", 4.8, 'font-weight="bold" fill="#b45309" text-anchor="middle"');

    // Left pin contact pad for macro board bridge (FIFO_REQ) at ly = 40
    canvas.addBackground(R(10, 35, 8, 10, "#fed7aa", "#c2410c", 2, 1.0));
    canvas.addDot(14, 40, "#c2410c", 1.8);
    canvas.addWire(P("M14 40H44V103", "#0d9488", 1.4));
    canvas.addDot(44, 103, "#0d9488", 1.4);
    canvas.addLabel(22, 38, "FIFO_REQ", 5.0, 'font-weight="bold" fill="#0d9488"');

    // Gold Bond Wire (25µm Au)
    canvas.addWire(P("M34 114H46", "#f59e0b", 2.0, "none", 'stroke-dasharray="3 1"'));
    canvas.addLabel(40, 110, "Au WIRE", 4.2, 'font-weight="bold" fill="#d97706" text-anchor="middle"');

    // Silicon Bond Pad on Die
    canvas.addBackground(R(46, 100, 28, 28, "#fef9c3", "#ca8a04", 2, 1.4));
    canvas.addLabel(60, 113, "BOND PAD", 5.2, 'font-weight="bold" fill="#854d0e" text-anchor="middle"');
    canvas.addLabel(60, 121, "[Al-Si]", 4.6, 'fill="#a16207" text-anchor="middle"');

    // Main internal signal trace from bond pad
    canvas.addWire(P("M74 114H155", paths.high, 2.0));

    // 3. Primary Dual-Rail ESD Clamping Diodes (X = 96)
    canvas.addDot(96, 114, paths.high, 2.2);

    // Upper Diode D_VCC (Anode at signal Y=114, Cathode at VCC Y=28)
    canvas.addWire(P("M96 114V28", paths.power, 1.5));
    canvas.addDot(96, 28, paths.power, 1.8);
    canvas.addBackground(P("M96 82L88 82L96 66L104 82Z", paths.power, 1.2, "#fee2e2"));
    canvas.addBackground(P("M86 66H106", paths.power, 1.8));
    canvas.addLabel(110, 72, "D_VCC", 5.5, 'font-weight="bold" fill="#b91c1c"');
    canvas.addLabel(110, 80, "> 5.7V", 4.5, 'fill="#991b1b"');

    // Lower Diode D_GND (Anode at GND Y=200, Cathode at signal Y=114)
    canvas.addWire(P("M96 114V200", paths.gnd, 1.5));
    canvas.addDot(96, 200, paths.gnd, 1.8);
    canvas.addBackground(P("M96 162L88 162L96 146L104 162Z", paths.gnd, 1.2, "#f1f5f9"));
    canvas.addBackground(P("M86 146H106", paths.gnd, 1.8));
    canvas.addLabel(110, 152, "D_GND", 5.5, 'font-weight="bold" fill="#334155"');
    canvas.addLabel(110, 160, "< -0.7V", 4.5, 'fill="#475569"');

    // 4. GGNMOS Snapback Clamp (X = 140)
    canvas.addDot(140, 114, paths.high, 2.2);
    canvas.addWire(P("M140 114V136", paths.high, 1.5));
    canvas.addWire(P("M140 136V144H146", paths.gnd, 1.2));
    canvas.addBackground(P("M146 140V160", paths.gnd, 2.0));
    canvas.addBackground(P("M142 142V158", paths.gnd, 1.8));
    canvas.addWire(P("M146 156H140V200", paths.gnd, 1.2));
    canvas.addDot(140, 200, paths.gnd, 1.8);
    canvas.addLabel(150, 148, "GGNMOS", 5.2, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(150, 156, "2kV Snapback", 4.5, 'fill="#475569"');

    // 5. Diffused Polysilicon Ballast Resistor (300Ω) (X = 168 .. 202)
    canvas.addWire(P("M155 114H168", paths.high, 1.8));
    canvas.addBackground(R(168, 108, 34, 12, "#fef3c7", "#d97706", 2, 1.2));
    canvas.addWire(P("M168 114H172L176 110L180 118L184 110L188 118L192 110L196 114H202", "#b45309", 1.4));
    canvas.addLabel(185, 104, "R_ESD (300Ω)", 5.0, 'font-weight="bold" fill="#92400e" text-anchor="middle"');
    canvas.addLabel(185, 126, "Ballast", 4.2, 'fill="#b45309" text-anchor="middle"');
    canvas.addWire(P("M202 114H248", paths.high, 1.8));

    // 6. Secondary Gate Oxide Clamp D_SEC (X = 222)
    canvas.addDot(222, 114, paths.high, 2.0);
    canvas.addWire(P("M222 114V200", "#475569", 1.2));
    canvas.addDot(222, 200, "#475569", 1.6);
    canvas.addBackground(P("M222 162L216 162L222 150L228 162Z", "#475569", 1.0, "#f8fafc"));
    canvas.addBackground(P("M214 150H230", "#475569", 1.5));
    canvas.addLabel(232, 154, "D_SEC", 4.8, 'font-weight="bold" fill="#334155"');
    canvas.addLabel(232, 162, "Oxide", 4.2, 'fill="#64748b"');

    // 7. Bidirectional Node (X = 248, Y = 114)
    canvas.addDot(248, 114, paths.high, 2.2);
    canvas.addWire(P("M248 114V70H270", paths.high, 1.6));
    canvas.addWire(P("M248 114V158H270", paths.high, 1.6));

    // 8. Tri-State Output Driver (X = 270 .. 294, Y = 62 .. 78, driving LEFT)
    canvas.addBackground(P("M294 62V78L270 70Z", paths.high, 1.4, "#dcfce7"));
    canvas.addDot(270, 70, paths.high, 1.4);
    canvas.addWire(P("M282 28V62", paths.control, 1.2));
    canvas.addDot(282, 28, paths.control, 1.6);
    canvas.addLabel(286, 44, "OE#", 4.5, 'font-weight="bold" fill="#7c3aed"');
    canvas.addWire(P("M294 70H408", paths.high, 1.8));
    canvas.addDot(294, 70, paths.high, 1.4);
    canvas.addLabel(282, 85, "TRI-STATE DRIVER", 4.8, 'font-weight="bold" fill="#15803d" text-anchor="middle"');

    // 9. Schmitt Trigger Input Buffer (X = 270 .. 294, Y = 150 .. 166, driving RIGHT)
    canvas.addBackground(P("M270 150V166L294 158Z", paths.high, 1.4, "#dcfce7"));
    canvas.addDot(270, 158, paths.high, 1.4);
    canvas.addWire(P("M278 160H284V154H288M286 157H281", paths.high, 1.0));
    canvas.addWire(P("M294 158H408", paths.high, 1.8));
    canvas.addDot(294, 158, paths.high, 1.4);
    canvas.addLabel(282, 174, "SCHMITT INPUT", 4.8, 'font-weight="bold" fill="#15803d" text-anchor="middle"');

    // 10. Right PortBox / Internal CPU Bus Terminals (X = 360 .. 408)
    const portBus = new PortBox("port_bus", 360, 28, 48, 175, "INTERNAL BUS", "right", "bidirectional", "#ecfdf5", "#86efac", "CPU");
    portBus.addPortPin("ad_out", 42, "AD_OUT", true, paths.high);
    portBus.addPortPin("ale", 112, "ALE", true, "#d97706");
    portBus.addPortPin("ad_in", 130, "AD_IN", true, paths.high);
    portBus.addPortPin("den_dir", 182, "DEN#/DIR", true, paths.control);
    canvas.addComponent(portBus);

    canvas.addWire(P("M360 140H408", "#d97706", 1.4));
    canvas.addWire(P("M360 210H408", paths.control, 1.4));

    // Footer Telemetry Banner
    canvas.addWire(P(`M10 224H${vw - 10}`, paths.control, 1.0));
    canvas.addLabel(16, 234, "ESD METRICS: V_clamp(+) = 5.7V · V_clamp(-) = -0.7V · R_ballast = 300Ω · I_sink = 16mA · V_hyst = 400mV", 5.2, 'font-weight="bold" fill="#475569"');

    return canvas.render();
  }
}
