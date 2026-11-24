/// <reference path="../types.ts" />
/// <reference path="../primitives.ts" />
/// <reference path="../engine.ts" />
/**
 * Intel 8086 Circuit Workbench - 16-Bit Dual-Port Register File (AX..DI)
 * 100% Modular OOP CAD Architecture: SchematicCanvas, PortBox, SubcircuitCard, DffCell, TriStateBuffer, LogicGate.
 * Exactly 128 Bascules D (16 bits × 8 registers) + 256 Tri-State Drivers.
 * Guaranteed Layer-Ordering: Zero wire masking, zero floating dots, zero wire collisions.
 */
namespace LogicDraw {
  declare const cpu: Workbench.CpuModel;

  export function registersLogic(s: SchematicState): string {
    const canvas = new SchematicCanvas();

    // Microcode Execution Control Signals (Pure IDLE when s.phase === 0 / reset)
    const en = typeof cpu !== "undefined" && cpu.enables ? cpu.enables() : {};
    const readA = Boolean(en.A); // Active during Phase 3 (Capture tmpA)
    const readB = Boolean(en.B); // Active during Phase 4 (Capture tmpB)
    const isW = Boolean(en.W);   // Active during Phase 6 (Write result)

    const regNames = ["AX", "BX", "CX", "DX", "SP", "BP", "SI", "DI"];
    const regSub = ["AH:AL", "BH:BL", "CH:CL", "DH:DL", "STACK", "BASE", "SRC", "DST"];
    const regVals = [
      s.ax ?? 0,
      s.bx ?? 0,
      s.cx ?? 0,
      s.dx ?? 0,
      s.sp ?? 0xfffe,
      s.bp ?? 0x100,
      s.si ?? 4,
      s.di ?? 0,
    ];

    // =======================================================================
    // 0. TOP TITLE & SYSTEM INTERFACE
    // =======================================================================
    canvas.addBackground(R(10, 6, 1260, 22, "#f8fafc", "#cbd5e1", 3, 1.0));
    canvas.addLabel(20, 20, "INTEL 8086 16-BIT DUAL-PORT REGISTER FILE · MODULAR OOP CAD SCHEMATIC", 7.5, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(780, 20, "128× BASCULES D · 256× TRI-STATE DRIVERS · FULL SIGNAL TRACING", 6.2, 'font-weight="bold" fill="#15803d"');

    // =======================================================================
    // 1. DEDICATED PORT BOXES (Encapsulated Signal Transfer Interfaces)
    // =======================================================================
    // Left Control & Address Input Port (Coordinates aligned with architecture.js targetY = 139)
    const portCtl = new PortBox("port_ctl", 10, 64, 96, 376, "CONTROL & ADDR", "left", "input", "#f5f3ff", "#7c3aed", "PORT IN");
    // Main external copper contact pad on left perimeter (y = 64 + 82 = 146 matches py = 139 in architecture.js!)
    portCtl.addPortPin("bus_sel", 82, "REG_SEL / CTRL", true, paths.control);

    // Internal distributed control leads exiting right into decoder
    portCtl.addPortPin("a2", 20, "A2 (SEL[2])", false, paths.control);
    portCtl.addPortPin("a1", 28, "A1 (SEL[1])", false, paths.control);
    portCtl.addPortPin("a0", 36, "A0 (SEL[0])", false, paths.control);
    portCtl.addPortPin("reg_wr", 116, "REG_WR (WRITE)", false, isW ? "#0284c7" : "#64748b");
    portCtl.addPortPin("rda_en", 146, "RD_A_EN (READ A)", false, readA ? paths.high : "#64748b");
    portCtl.addPortPin("rdb_en", 190, "RD_B_EN (READ B)", false, readB ? "#059669" : "#64748b");
    canvas.addComponent(portCtl);

    // Internal distribution bus inside port_ctl linking main terminal (10, 146) to all leads
    canvas.addWire(P("M10 146H24", paths.control, 1.8));
    canvas.addBus(P("M24 84V254", paths.control, 1.4));
    canvas.addDot(24, 146, paths.control, 2.0);
    canvas.addWire(P("M24 84H28", paths.control, 1.2));
    canvas.addDot(24, 84, paths.control, 1.5);
    canvas.addWire(P("M24 92H28", paths.control, 1.2));
    canvas.addDot(24, 92, paths.control, 1.5);
    canvas.addWire(P("M24 100H28", paths.control, 1.2));
    canvas.addDot(24, 100, paths.control, 1.5);
    canvas.addWire(P("M24 180H28", isW ? "#0284c7" : "#64748b", 1.2));
    canvas.addDot(24, 180, isW ? "#0284c7" : "#64748b", 1.5);
    canvas.addWire(P("M24 210H28", readA ? paths.high : "#64748b", 1.2));
    canvas.addDot(24, 210, readA ? paths.high : "#64748b", 1.5);
    canvas.addWire(P("M24 254H28", readB ? "#059669" : "#64748b", 1.2));
    canvas.addDot(24, 254, readB ? "#059669" : "#64748b", 1.5);

    // Right Data Bus Output Port (ly = 20 matches py = 93 in architecture.js!)
    // Box positioned at y = 4..48, header banner is y = 4..17
    const portDout = new PortBox("port_dout", 1162, 4, 110, 44, "DATA OUT (D_OUT)", "right", "output", "#ecfdf5", "#059669", "[16-BIT]");
    // External copper contact pad on right perimeter at y = 4 + 16 = 20 (strictly below header!)
    portDout.addPortPin("pad_dout", 16, "D_OUT[15:0]", true, readA ? paths.high : "#059669");
    // Internal read bus inputs entering on left edge at y = 4 + 26 = 30 and y = 4 + 38 = 42
    portDout.addPortPin("bus_a", 26, "BUS_A[15:0]", false, readA ? paths.high : "#059669");
    portDout.addPortPin("bus_b", 38, "BUS_B[15:0]", false, readB ? "#059669" : "#0d9488");
    canvas.addComponent(portDout);

    // Traces inside port_dout connecting inputs to pad
    canvas.addWire(P("M1220 30H1250V20H1272", readA ? paths.high : "#059669", 1.2));
    canvas.addDot(1250, 20, readA ? paths.high : "#059669", 1.5);
    canvas.addWire(P("M1220 42H1250V20", readB ? "#059669" : "#0d9488", 1.2));

    // Right Write Data Input Port (ly = 64 matches py = 109 in architecture.js!)
    // Box positioned at y = 50..92, header banner is y = 50..63
    const portDin = new PortBox("port_din", 1162, 50, 110, 42, "WRITE DATA (D_IN)", "right", "input", "#f0f9ff", "#0284c7", "[16-BIT]");
    // External copper contact pad on right perimeter at y = 50 + 14 = 64 (strictly below header!)
    portDin.addPortPin("pad_din", 14, "D_IN[15:0]", true, isW ? "#0284c7" : "#0284c7");
    // Internal writeback bus output exiting on left edge at y = 50 + 28 = 78
    portDin.addPortPin("din_bus", 28, "WRITE[15:0]", false, isW ? "#0284c7" : "#64748b");
    canvas.addComponent(portDin);

    // Traces inside port_din connecting pad to output
    canvas.addWire(P("M1272 64H1250V78H1220", isW ? "#0284c7" : "#64748b", 1.4));
    canvas.addDot(1250, 64, isW ? "#0284c7" : "#64748b", 1.6);

    // =======================================================================
    // 2. TOP DATA HIGHWAYS (Continuous Horizontal Copper Buses, Y = 36..52)
    // =======================================================================
    // Bus A: runs to PortDout BUS_A input at (1162, 30)
    canvas.addBus(P("M270 36H1154V30H1162", readA ? paths.high : "#94a3b8", readA ? 2.0 : 1.2));
    canvas.addLabel(272, 33, "INTERNAL DATA BUS A [15:0] · READ PORT A HIGHWAY", 5.5, 'font-weight="bold" fill="#15803d"');

    // Bus B: runs directly into PortDout BUS_B input at (1162, 42)
    canvas.addBus(P("M270 44H1154V42H1162", readB ? "#059669" : "#94a3b8", readB ? 2.0 : 1.2));
    canvas.addLabel(272, 42, "INTERNAL DATA BUS B [15:0] · READ PORT B HIGHWAY", 5.5, 'font-weight="bold" fill="#059669"');

    // Din: runs from PortDin WRITEBACK output at (1162, 78) up to Y=52 across columns
    canvas.addBus(P("M270 52H1154V78H1162", isW ? "#0284c7" : "#cbd5e1", isW ? 2.0 : 1.2));
    canvas.addLabel(272, 50, "WRITE DATA HIGHWAY D_IN [15:0] · WRITEBACK PORT", 5.5, 'font-weight="bold" fill="#0284c7"');

    // =======================================================================
    // 3. BIT COLUMN X-COORDINATES (16 Columns: Bit 15 down to Bit 0)
    // =======================================================================
    const colX: number[] = [];
    const startX = 304;
    const colW = 50;
    for (let b = 0; b < 16; b++) {
      const byteSpacer = b >= 8 ? 14 : 0;
      colX.push(startX + b * colW + byteSpacer);
    }

    // Byte Header Banners across top of matrix (Y = 58..70)
    const highByteW = 8 * colW - 4;
    const lowByteW = 8 * colW - 4;
    canvas.addBackground(R(startX - 4, 58, highByteW, 12, "#ecfdf5", "#059669", 2, 0.8));
    canvas.addLabel(startX + highByteW / 2 - 2, 67, "HIGH BYTE [15:8]  ·  (AH, BH, CH, DH, SPH, BPH, SIH, DIH)", 5.8, 'text-anchor="middle" font-weight="bold" fill="#047857"');

    const lowByteStartX = startX + 8 * colW + 10;
    canvas.addBackground(R(lowByteStartX, 58, lowByteW, 12, "#ecfdf5", "#059669", 2, 0.8));
    canvas.addLabel(lowByteStartX + lowByteW / 2, 67, "LOW BYTE [7:0]  ·  (AL, BL, CL, DL, SPL, BPL, SIL, DIL)", 5.8, 'text-anchor="middle" font-weight="bold" fill="#047857"');

    // Column Bit Number Badges (Y = 72..84)
    for (let b = 0; b < 16; b++) {
      const k = 15 - b;
      const cx = colX[b] + 25;
      canvas.addBackground(R(cx - 20, 72, 40, 11, "#f1f5f9", "#cbd5e1", 2, 0.7));
      canvas.addLabel(cx, 80, `BIT ${k}`, 5.5, 'text-anchor="middle" font-weight="bold" fill="#1e293b"');
    }

    // =======================================================================
    // 4. DECODER SUBCIRCUIT BOX & RAILS (X = 114..266, Y = 64..440)
    // =======================================================================
    const decLeft = 114;
    const decTop = 64;
    const decW = 152;
    const decH = 376;

    canvas.addBackground(R(decLeft, decTop, decW, decH, "#fffdf0", "#887342", 2, 1.2));
    canvas.addBackground(R(decLeft, decTop, decW, 14, "#fef3c7", "#887342", 2, 0.8));
    canvas.addLabel(decLeft + 6, decTop + 10, "3:8 REGISTER ROW DECODER & WORDLINE DRIVERS", 5.8, 'font-weight="bold" fill="#78350f"');

    // Rails: True and Inverted address lines with clean inverters
    const aRails = [
      { bit: 2, t: 124, c: 140, yIn: 84, invX: 128 },
      { bit: 1, t: 148, c: 164, yIn: 92, invX: 152 },
      { bit: 0, t: 172, c: 188, yIn: 100, invX: 176 },
    ];

    aRails.forEach((ar) => {
      // Wire from PortBox into true rail
      canvas.addWire(P(`M106 ${ar.yIn}H${ar.t}`, paths.control, 1.2));
      canvas.addDot(ar.t, ar.yIn, paths.control, 1.6);

      // Inverter connecting true rail to inverted rail
      canvas.addWire(P(`M${ar.t} ${ar.yIn}H${ar.invX}`, paths.control, 1.0));
      canvas.addComponent(new LogicGate(`inv_${ar.bit}`, ar.invX, ar.yIn - 4, "inv", 10, 8, true));
      canvas.addWire(P(`M${ar.invX + 10} ${ar.yIn}H${ar.c}`, paths.control, 1.0));
      canvas.addDot(ar.c, ar.yIn, "#64748b", 1.6);

      // Continuous vertical rails extending down to row 7
      canvas.addBus(P(`M${ar.t} ${ar.yIn}V436`, paths.control, 1.2));
      canvas.addBus(P(`M${ar.c} ${ar.yIn}V436`, "#64748b", 1.2));
    });

    // Control Strobe Spines inside decoder (Continuous unbroken copper rails across all 8 rows, Y = 70..436)
    const rdaSpineX = 216;
    const wrSpineX = 226;
    const rdbSpineX = 236;

    // 1. Continuous vertical strobe buses (Y = 70 to 436 spanning Row 0 AX down to Row 7 DI)
    canvas.addBus(P(`M${rdaSpineX} 70V436`, readA ? paths.high : "#cbd5e1", readA ? 1.4 : 1.0));
    canvas.addBus(P(`M${wrSpineX} 70V436`, isW ? "#0284c7" : "#cbd5e1", isW ? 1.4 : 1.0));
    canvas.addBus(P(`M${rdbSpineX} 70V436`, readB ? "#059669" : "#cbd5e1", readB ? 1.4 : 1.0));

    // 2. Control leads from PortBox (X = 106) into vertical strobe buses with solid solder junctions
    canvas.addWire(P(`M106 210H${rdaSpineX}`, readA ? paths.high : "#94a3b8", 1.2));
    canvas.addDot(rdaSpineX, 210, readA ? paths.high : "#94a3b8", 1.6);

    canvas.addWire(P(`M106 180H${wrSpineX}`, isW ? "#0284c7" : "#94a3b8", 1.2));
    canvas.addDot(wrSpineX, 180, isW ? "#0284c7" : "#94a3b8", 1.6);

    canvas.addWire(P(`M106 254H${rdbSpineX}`, readB ? "#059669" : "#94a3b8", 1.2));
    canvas.addDot(rdbSpineX, 254, readB ? "#059669" : "#94a3b8", 1.6);

    // =======================================================================
    // 5. 48 DISCRETE CONTINUOUS VERTICAL DATA BUSES (Bit 15 down to 0)
    // =======================================================================
    for (let b = 0; b < 16; b++) {
      const cx = colX[b] + 25;
      const dinX = cx - 15;
      const busAx = cx + 24;
      const busBx = cx + 29;

      // Bus A vertical lead from Y=36
      canvas.addDot(busAx, 36, readA ? paths.high : "#94a3b8", 1.8);
      canvas.addBus(P(`M${busAx} 36V440`, readA ? paths.high : "#94a3b8", readA ? 1.5 : 1.0));

      // Bus B vertical lead from Y=44
      canvas.addDot(busBx, 44, readB ? "#059669" : "#94a3b8", 1.8);
      canvas.addBus(P(`M${busBx} 44V440`, readB ? "#059669" : "#94a3b8", readB ? 1.5 : 1.0));

      // Din vertical lead from Y=52
      canvas.addDot(dinX, 52, isW ? "#0284c7" : "#94a3b8", 1.8);
      canvas.addBus(P(`M${dinX} 52V440`, isW ? "#0284c7" : "#cbd5e1", isW ? 1.5 : 1.0));
    }

    // =======================================================================
    // 6. 8 REGISTER ROWS (AX..DI) × 16 BITS = 128 CELLS (OOP Instances!)
    // =======================================================================
    const endMatrixX = colX[15] + colW;
    const matrixW = endMatrixX - startX + 4;

    for (let r = 0; r < 8; r++) {
      const ry = 88 + r * 44;
      const yc = ry + 22;

      const isSelA = readA && (r === 0);
      const isSelB = readB && (r === 1);
      const isDest = isW && (r === 0);
      const isAct = isSelA || isSelB || isDest;

      // Row background strip (transparent border to avoid fake horizontal line artifacts)
      canvas.addBackground(R(startX - 6, ry + 2, matrixW, 40, isAct ? "#f0fdf4" : (r % 2 === 0 ? "#ffffff" : "#fcfdfe"), isAct ? "#86efac" : "transparent", 2, 0.8));

      // Row Identifier Badge (Placed safely between decoder and bitcells with ZERO wire collisions)
      canvas.addBackground(R(274, yc - 10, 22, 20, isAct ? "#dcfce7" : "#f1f5f9", isAct ? "#86efac" : "#cbd5e1", 2, 0.9));
      canvas.addLabel(285, yc - 1, regNames[r], 6.0, 'text-anchor="middle" font-weight="bold" fill="' + (isAct ? "#15803d" : "#1e293b") + '"');
      canvas.addLabel(285, yc + 7, regSub[r], 4.2, 'text-anchor="middle" fill="' + (isAct ? "#16a34a" : "#64748b") + '"');

      // Hex Value Readout Badge
      const rVal = regVals[r];
      canvas.addBackground(R(endMatrixX + 6, ry + 11, 26, 20, isAct ? "#ecfdf5" : "#f8fafc", isAct ? "#86efac" : "#cbd5e1", 2, 0.8));
      canvas.addLabel(endMatrixX + 19, yc + 4, `${hex(rVal, 4)}h`, 6.0, 'text-anchor="middle" font-weight="bold" fill="' + (isAct ? "#15803d" : "#334155") + '"');

      // Decoder 3-input Address AND Gate (decodes A2, A1, A0 for row r)
      const decAndX = 196;
      canvas.addComponent(new LogicGate(`dec_${r}`, decAndX, yc - 6, "and", 11, 12, isAct));

      const b2 = (r >> 2) & 1 ? aRails[0].t : aRails[0].c;
      const b1 = (r >> 1) & 1 ? aRails[1].t : aRails[1].c;
      const b0 = r & 1 ? aRails[2].t : aRails[2].c;

      // Inputs to 3-input address AND gate
      canvas.addWire(P(`M${b2} ${yc - 4}H${decAndX}`, isAct ? paths.high : "#64748b", 1.2));
      canvas.addDot(b2, yc - 4, isAct ? paths.high : "#475569", 1.6);

      canvas.addWire(P(`M${b1} ${yc}H${decAndX}`, isAct ? paths.high : "#64748b", 1.2));
      canvas.addDot(b1, yc, isAct ? paths.high : "#475569", 1.6);

      canvas.addWire(P(`M${b0} ${yc + 4}H${decAndX}`, isAct ? paths.high : "#64748b", 1.2));
      canvas.addDot(b0, yc + 4, isAct ? paths.high : "#475569", 1.6);

      // ROW_SEL[r] output wire exiting at yc to vertical distribution rail at X = 244
      canvas.addWire(P(`M${decAndX + 11} ${yc}H244`, isAct ? paths.high : "#64748b", 1.2));
      canvas.addDot(244, yc, isAct ? paths.high : "#475569", 1.5);

      // Wordline coordinates: outside cell body (in clear channels above and below badge & cells)
      const rdaWordY = yc - 15; // Above Buffer A and badge (passes at yc-15, badge top is yc-10)
      const weWordY = yc + 12;  // Below cell & badge (passes at yc+12, badge bottom is yc+10)
      const rdbWordY = yc + 18; // Below Buffer B & badge

      // 3 Non-Overlapping Wordline Driver AND Gates (Inside decoder box at X = 250)
      const gateX = 250;

      // 1. RDA Gate: Centered at yc - 14 (y in [yc-17.5 .. yc-10.5])
      canvas.addComponent(new LogicGate(`rda_gate_${r}`, gateX, yc - 17.5, "and", 9, 7, isSelA));
      canvas.addWire(P(`M${rdaSpineX} ${yc - 16}H${gateX}`, isSelA ? paths.high : "#64748b", 1.0));
      canvas.addDot(rdaSpineX, yc - 16, isSelA ? paths.high : "#475569", 1.5);
      canvas.addWire(P(`M244 ${yc}V${yc - 12}H${gateX}`, isSelA ? paths.high : "#64748b", 1.0));

      // 2. WE Gate: Centered at yc + 5 (y in [yc+1.5 .. yc+8.5]) -> 12px gap from RDA gate, 7px gap from row select wire!
      canvas.addComponent(new LogicGate(`we_gate_${r}`, gateX, yc + 1.5, "and", 9, 7, isDest));
      canvas.addWire(P(`M244 ${yc}V${yc + 3}H${gateX}`, isDest ? "#0284c7" : "#64748b", 1.0));
      canvas.addWire(P(`M${wrSpineX} ${yc + 7}H${gateX}`, isDest ? "#0284c7" : "#64748b", 1.0));
      canvas.addDot(wrSpineX, yc + 7, isDest ? "#0284c7" : "#475569", 1.5);

      // 3. RDB Gate: Centered at yc + 15 (y in [yc+11.5 .. yc+18.5]) -> 3px gap from WE gate!
      canvas.addComponent(new LogicGate(`rdb_gate_${r}`, gateX, yc + 11.5, "and", 9, 7, isSelB));
      canvas.addWire(P(`M244 ${yc}V${yc + 13}H${gateX}`, isSelB ? "#059669" : "#64748b", 1.0));
      canvas.addWire(P(`M${rdbSpineX} ${yc + 17}H${gateX}`, isSelB ? "#059669" : "#64748b", 1.0));
      canvas.addDot(rdbSpineX, yc + 17, isSelB ? "#059669" : "#475569", 1.5);

      // Continuous Wordlines across row r (all in clear channels outside the cell body)
      const wlEndX = endMatrixX - 4;
      // RDA Wordline: exits at yc - 14, steps to yc - 15 outside box
      canvas.addBus(P(`M${gateX + 9} ${yc - 14}H268V${rdaWordY}H${wlEndX}`, isSelA ? paths.high : "#cbd5e1", isSelA ? 1.5 : 0.9));
      // WE Wordline: exits at yc + 5, steps down at X = 268 to yc + 12 (below badge)
      canvas.addBus(P(`M${gateX + 9} ${yc + 5}H268V${weWordY}H${wlEndX}`, isDest ? "#0284c7" : "#cbd5e1", isDest ? 1.5 : 0.9));
      // RDB Wordline: exits at yc + 15, steps down at X = 268 to yc + 18 (below badge)
      canvas.addBus(P(`M${gateX + 9} ${yc + 15}H268V${rdbWordY}H${wlEndX}`, isSelB ? "#059669" : "#cbd5e1", isSelB ? 1.5 : 0.9));

      // 16 Bascules D and Tri-State Drivers in Row r
      for (let b = 0; b < 16; b++) {
        const k = 15 - b;
        const cx = colX[b] + 25;
        const dinX = cx - 15;
        const busAx = cx + 24;
        const busBx = cx + 29;

        const bitVal = (rVal >>> k) & 1;

        // OOP Component: DffCell (width 18, height 22, body y in [yc-11 .. yc+11])
        const ffLeft = cx - 9;
        const ffTop = yc - 11;
        canvas.addComponent(new DffCell(`dff_${r}_${k}`, ffLeft, ffTop, 18, 22, bitVal, isAct));

        // WIRE 1: D_IN[k] taps horizontally into D pin at yc-5 (NEVER crosses CLK wire!)
        const dPinY = yc - 5;
        canvas.addWire(P(`M${dinX} ${dPinY}H${ffLeft}`, isDest ? "#0284c7" : "#94a3b8", 1.2));
        canvas.addDot(dinX, dPinY, isDest ? "#0284c7" : "#94a3b8", 1.6);

        // WIRE 2: WE taps into CLK pin at yc+5 (comes from bottom weWordY, completely below D wire!)
        const clkPinY = yc + 5;
        canvas.addWire(P(`M${cx - 12} ${weWordY}V${clkPinY}H${ffLeft}`, isDest ? "#0284c7" : "#94a3b8", 1.2));
        canvas.addDot(cx - 12, weWordY, isDest ? "#0284c7" : "#94a3b8", 1.6);

        // WIRE 3: Q pin exits cell at yc and splits symmetrically to Buffers A & B
        const splitX = cx + 12;
        canvas.addWire(P(`M${ffLeft + 18} ${yc}H${splitX}`, bitVal ? paths.high : "#94a3b8", 1.2));
        canvas.addDot(splitX, yc, bitVal ? paths.high : "#94a3b8", 1.4);

        // OOP Component: TriStateBuffer A (above Q line, centered at yc-7, y in [yc-11 .. yc-3])
        const bufAx = cx + 14;
        const bufAy = yc - 11;
        canvas.addWire(P(`M${splitX} ${yc}V${yc - 7}H${bufAx}`, bitVal ? paths.high : "#94a3b8", 1.1));
        canvas.addComponent(new TriStateBuffer(`bufA_${r}_${k}`, bufAx, bufAy, 8, 8, isSelA, "T"));

        // Enable line from RDA wordline at yc-15 DOWN into top pin of Buffer A (ZERO penetration!)
        canvas.addWire(P(`M${bufAx + 4} ${rdaWordY}V${bufAy - 2}`, isSelA ? paths.high : "#94a3b8", 1.1));
        canvas.addDot(bufAx + 4, rdaWordY, isSelA ? paths.high : "#94a3b8", 1.5);

        // Output to Bus A
        canvas.addWire(P(`M${bufAx + 8} ${yc - 7}H${busAx}`, isSelA ? paths.high : "#94a3b8", isSelA ? 1.6 : 1.1));
        canvas.addDot(busAx, yc - 7, isSelA ? paths.high : "#94a3b8", 1.7);

        // OOP Component: TriStateBuffer B (below Q line, centered at yc+7, y in [yc+3 .. yc+11])
        const bufBx = cx + 14;
        const bufBy = yc + 3;
        canvas.addWire(P(`M${splitX} ${yc}V${yc + 7}H${bufBx}`, bitVal ? paths.high : "#94a3b8", 1.1));
        canvas.addComponent(new TriStateBuffer(`bufB_${r}_${k}`, bufBx, bufBy, 8, 8, isSelB, "B"));

        // Enable line from RDB wordline at yc+18 UP into bottom pin of Buffer B (ZERO penetration!)
        canvas.addWire(P(`M${bufBx + 4} ${rdbWordY}V${bufBy + 10}`, isSelB ? "#059669" : "#94a3b8", 1.1));
        canvas.addDot(bufBx + 4, rdbWordY, isSelB ? "#059669" : "#94a3b8", 1.5);

        // Output to Bus B
        canvas.addWire(P(`M${bufBx + 8} ${yc + 7}H${busBx}`, isSelB ? "#059669" : "#94a3b8", isSelB ? 1.6 : 1.1));
        canvas.addDot(busBx, yc + 7, isSelB ? "#059669" : "#94a3b8", 1.7);
      }
    }

    // =======================================================================
    // 7. BOTTOM MAGNIFIED LEGEND & OPERATIONAL DETAIL CALLOUT
    // =======================================================================
    const legTop = 448;
    canvas.addBackground(R(10, legTop, 1260, 104, "#f8fafc", "#cbd5e1", 3, 1.0));
    canvas.addBackground(R(10, legTop, 1260, 14, "#f1f5f9", "#cbd5e1", 3, 0.8));
    canvas.addLabel(20, legTop + 10, "MAGNIFIED DETAIL OF A SINGLE BIT CELL (k) · INDIVIDUAL SIGNAL TRACING (LINE BY LINE)", 6.5, 'font-weight="bold" fill="#0f172a"');

    const lx = 30;
    const ly = legTop + 22;

    // D_IN Wire
    canvas.addWire(P(`M${lx} ${ly + 8}H${lx + 35}`, "#0284c7", 1.3));
    canvas.addLabel(lx, ly + 5, "D_IN[k] (BLUE WIRE)", 5.2, 'font-weight="bold" fill="#0284c7"');
    canvas.addDot(lx + 20, ly + 8, "#0284c7", 1.5);

    // WE Wire
    canvas.addWire(P(`M${lx + 20} ${ly + 32}H${lx + 35}`, "#0284c7", 1.3));
    canvas.addLabel(lx, ly + 29, "WE WORDLINE (STROBE)", 5.2, 'font-weight="bold" fill="#0284c7"');

    // Bascule D Cell
    canvas.addBackground(R(lx + 35, ly, 40, 42, "#ecfdf5", "#16a34a", 2, 1.2));
    canvas.addLabel(lx + 40, ly + 12, "D", 5.5, 'font-weight="bold" fill="#0284c7"');
    canvas.addLabel(lx + 40, ly + 36, "CLK", 5.0, 'font-weight="bold" fill="#0284c7"');
    canvas.addLabel(lx + 68, ly + 24, "Q", 6.2, 'font-weight="bold" fill="#15803d"');
    canvas.addLabel(lx + 55, ly + 25, "1/0", 8.0, 'text-anchor="middle" font-weight="bold" fill="#15803d"');

    // Q Output Wire
    canvas.addWire(P(`M${lx + 75} ${ly + 21}H${lx + 96}`, paths.data, 1.3));
    canvas.addDot(lx + 96, ly + 21, paths.data, 1.4);

    // Buffer A
    canvas.addWire(P(`M${lx + 96} ${ly + 21}V${ly + 10}H${lx + 104}`, paths.data, 1.1));
    canvas.addComponent(new TriStateBuffer("leg_bufA", lx + 104, ly + 4, 12, 12, true, "T"));
    canvas.addWire(P(`M${lx + 110} ${ly - 4}V${ly + 4}`, paths.high, 1.2));
    canvas.addLabel(lx + 110, ly - 6, "RD_A ENABLE", 4.8, 'text-anchor="middle" font-weight="bold" fill="#15803d"');
    canvas.addWire(P(`M${lx + 116} ${ly + 10}H${lx + 145}`, paths.high, 1.5));
    canvas.addLabel(lx + 150, ly + 13, "BUS_A[k] (DARK GREEN WIRE)", 5.2, 'font-weight="bold" fill="#15803d"');

    // Buffer B
    canvas.addWire(P(`M${lx + 96} ${ly + 21}V${ly + 32}H${lx + 104}`, paths.data, 1.1));
    canvas.addComponent(new TriStateBuffer("leg_bufB", lx + 104, ly + 26, 12, 12, true, "B"));
    canvas.addWire(P(`M${lx + 110} ${ly + 46}V${ly + 38}`, "#059669", 1.2));
    canvas.addLabel(lx + 110, ly + 52, "RD_B ENABLE", 4.8, 'text-anchor="middle" font-weight="bold" fill="#059669"');
    canvas.addWire(P(`M${lx + 116} ${ly + 32}H${lx + 145}`, "#059669", 1.5));
    canvas.addLabel(lx + 150, ly + 35, "BUS_B[k] (TEAL WIRE)", 5.2, 'font-weight="bold" fill="#059669"');

    const tx = lx + 360;
    canvas.addLabel(tx, ly + 10, "WRITE CYCLE: When WE Wordline pulses HIGH on CLK, all 16 Bascules D capture D_IN[15:0] simultaneously.", 5.6, 'fill="#334155"');
    canvas.addLabel(tx, ly + 24, "READ PORT A: Asserting RD_A Wordline opens 16 Tri-State Drivers, driving stored Q[15:0] onto BUS_A[15:0].", 5.6, 'fill="#15803d" font-weight="bold"');
    canvas.addLabel(tx, ly + 38, "READ PORT B: Asserting RD_B Wordline opens 16 Tri-State Drivers, driving stored Q[15:0] onto BUS_B[15:0].", 5.6, 'fill="#059669" font-weight="bold"');
    canvas.addLabel(tx, ly + 52, "DUAL READ: Both RD_A and RD_B can be active in the same clock cycle, reading two distinct registers at once.", 5.6, 'fill="#7c3aed" font-weight="bold"');

    return canvas.render();
  }
}
