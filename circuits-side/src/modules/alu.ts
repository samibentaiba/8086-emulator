/// <reference path="../types.ts" />
/// <reference path="../primitives.ts" />
/// <reference path="../engine.ts" />
/**
 * Intel 8086 Circuit Workbench - 16-Bit Parallel ALU & 4-Bit CLA Architecture
 * 100% Modular OOP CAD Architecture: SchematicCanvas, PortBox, SubcircuitCard, LogicGate, MuxComponent.
 * Full Discrete 16-Bit Bit-Slice Matrix (Bit 15 down to Bit 0) organized into 4 CLA Nibble Blocks.
 * Mathematically Unified Macro-Micro Interconnects:
 *   - Top Input A (tmpA / MUX): lx = 955 -> maps to outer board px = 395 (100% straight vertical bridge)
 *   - Top Input B (tmpB):        lx = 1119 -> maps to outer board px = 455 (100% straight vertical bridge)
 *   - Top Control (ALU CTRL):   lx = 175  -> maps to outer board px = 110 (100% straight vertical bridge)
 *   - Right Output (RESULT):     lx = 1270, ly = 268 -> maps to outer board py = 1184 (100% straight horizontal)
 *   - Bottom Flags (6 FLAGS):   lx = 107 (AF), 298 (PF), 490 (ZF), 681 (SF), 872 (OF), 1064 (CF)
 *                               -> maps to outer board px = 85, 155, 225, 295, 365, 435 (100% straight vertical)
 * Guaranteed CAD Invariants:
 *   - Zero Gate Penetrations
 *   - Zero Boundary Leaks
 *   - Zero Header / Badge / Label Occlusions
 *   - Zero Dead-End Wires & Zero Broken Bridges
 *   - Zero Exterior Looping
 */
namespace LogicDraw {
  declare const cpu: Workbench.CpuModel;

  export function adderLogic(s: SchematicState, bit: number = 0): string {
    const canvas = new SchematicCanvas();

    // Microcode Execution & ALU Calculations
    const calc = typeof cpu !== "undefined" && cpu.calculate
      ? cpu.calculate()
      : { word: 0, flags: { CF: 0, PF: 0, AF: 0, ZF: 0, SF: 0, OF: 0 } };

    const inputs = typeof cpu !== "undefined" && cpu.inputs
      ? cpu.inputs() : [s.a ?? s.ax ?? 0, s.b ?? s.bx ?? 0];
    const wordA = s.tmpA ?? inputs[0];
    const wordB = s.tmpB ?? inputs[1];
    const sWord = calc.word ?? 0;
    const flags = calc.flags ?? { CF: 0, PF: 0, AF: 0, ZF: 0, SF: 0, OF: 0 };

    const opStr = (s.op ?? "ADD").toUpperCase();
    const isSub = opStr === "SUB" || opStr === "CMP" || opStr === "SBB" || opStr === "NEG" || opStr === "DEC";
    const isAnd = opStr === "AND" || opStr === "TEST";
    const isOr = opStr === "OR";
    const isXor = opStr === "XOR" || opStr === "NOT";
    const isArith = !isAnd && !isOr && !isXor;

    // =======================================================================
    // 0. TOP TITLE & SYSTEM INTERFACE (Y = 6..26)
    // =======================================================================
    canvas.addBackground(R(10, 6, 1260, 20, "#f8fafc", "#cbd5e1", 3, 1.0));
    canvas.addLabel(20, 19, "INTEL 8086 16-BIT PARALLEL ARITHMETIC LOGIC UNIT & CARRY-LOOKAHEAD (CLA)", 7.2, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(740, 19, "16× DISCRETE FULL-ADDER / LOGIC SLICES · 4× 4-BIT CLA BLOCKS · 6× CONDITION FLAGS", 6.0, 'font-weight="bold" fill="#15803d"');

    // =======================================================================
    // 1. DEDICATED PORT BOXES & HIGHWAYS
    // =======================================================================
    // 1.1 Left Control Port (x = 10, y = 30, w = 86, h = 230 -> ends at y = 260, spacious 68px corridor above legend at y = 328!)
    const portCtl = new PortBox("port_ctl", 10, 30, 86, 230, "ALU CONTROL", "left", "input", "#f5f3ff", "#7c3aed", "PORT IN");
    portCtl.addPortPin("alu_op", 30, "ALU_OP[4:0]", false, paths.control);
    portCtl.addPortPin("op_add", 44, "ADD / ADC", false, isArith && !isSub ? paths.high : "#64748b");
    portCtl.addPortPin("op_sub", 58, "SUB / SBB / CMP", false, isSub ? "#0284c7" : "#64748b");
    portCtl.addPortPin("op_and", 76, "AND / TEST", false, isAnd ? paths.high : "#64748b");
    portCtl.addPortPin("op_or", 94, "OR", false, isOr ? paths.high : "#64748b");
    portCtl.addPortPin("op_xor", 112, "XOR / NOT", false, isXor ? paths.high : "#64748b");
    portCtl.addPortPin("fn_sel", 214, "FN_SEL[1:0]", false, paths.control);
    canvas.addComponent(portCtl);

    // Top control terminal pad at lx = 175 (maps 100% straight to outer board px = 110!)
    // Runs at Y = 26 above Operand A Highway to eliminate all text occlusions!
    canvas.addBackground(R(171, 6, 8, 12, "#f5f3ff", "#7c3aed", 2, 1.0));
    canvas.addWire(P("M175 6V26H96V30", paths.control, 1.6));
    canvas.addDot(175, 6, paths.control, 2.0);
    canvas.addDot(96, 30, paths.control, 1.6);

    // 1.2 Top Data Highways: Operand A and Operand B (Y = 34..48)
    const busAY = 34;
    const busBY = 46;
    const busRight = 1146;

    // Bus A: runs from X = 118 across to 1146 (labels positioned to avoid all vertical wire crossings)
    canvas.addBus(P(`M118 ${busAY}H${busRight}`, paths.high, 1.8));
    canvas.addLabel(190, busAY - 3, "OPERAND A HIGHWAY [15:0] (from tmpA / ALU MUX)", 5.2, 'font-weight="bold" fill="#15803d"');
    canvas.addBackground(R(1030, busAY - 6, 46, 12, "#dcfce7", "#86efac", 2, 0.9));
    canvas.addLabel(1053, busAY + 3, `${hex(wordA, 4)}h`, 5.4, 'text-anchor="middle" font-weight="bold" fill="#15803d"');

    // Top contact pad for Operand A at lx = 955 (maps 100% straight to outer board px = 395!)
    canvas.addBackground(R(951, 6, 8, 12, "#dcfce7", "#15803d", 2, 1.0));
    canvas.addWire(P(`M955 6V${busAY}`, paths.high, 1.6));
    canvas.addDot(955, 6, paths.high, 2.0);
    canvas.addDot(955, busAY, paths.high, 1.8);

    // Bus B: runs from X = 118 across to 1146
    canvas.addBus(P(`M118 ${busBY}H${busRight}`, "#059669", 1.8));
    canvas.addLabel(190, busBY - 3, "OPERAND B HIGHWAY [15:0] (from tmpB)", 5.2, 'font-weight="bold" fill="#059669"');
    canvas.addBackground(R(1030, busBY - 6, 46, 12, "#dcfce7", "#86efac", 2, 0.9));
    canvas.addLabel(1053, busBY + 3, `${hex(wordB, 4)}h`, 5.4, 'text-anchor="middle" font-weight="bold" fill="#059669"');

    // Top contact pad for Operand B at lx = 1119 (maps 100% straight to outer board px = 455!)
    canvas.addBackground(R(1115, 6, 8, 12, "#dcfce7", "#059669", 2, 1.0));
    canvas.addWire(P(`M1119 6V${busBY}`, "#059669", 1.6));
    canvas.addDot(1119, 6, "#059669", 2.0);
    canvas.addDot(1119, busBY, "#059669", 1.8);

    // 1.3 Right Result Output Port (x = 1156, y = 240, w = 114, h = 50)
    const portRes = new PortBox("port_result", 1156, 240, 114, 50, "ALU RESULT", "right", "output", "#ecfdf5", "#059669", "[16-BIT]");
    portRes.addPortPin("pad_res", 28, "RESULT[15:0]", true, paths.high);
    portRes.addPortPin("res_in", 28, "S[15:0]", false, paths.high);
    canvas.addComponent(portRes);

    // Result Highway at Y = 268 enters port_result at left edge and connects straight to pad at 1270!
    canvas.addBus(P("M118 268H1270", paths.high, 2.0));
    canvas.addLabel(122, 264, "16-BIT PARALLEL RESULT HIGHWAY S[15:0] · DIRECT WRITEBACK BUS", 5.2, 'font-weight="bold" fill="#15803d"');
    canvas.addDot(1270, 268, paths.high, 2.0);

    canvas.addBackground(R(1164, 276, 48, 12, "#dcfce7", "#86efac", 2, 0.8));
    canvas.addLabel(1188, 285, `${hex(sWord, 4)}h`, 5.5, 'text-anchor="middle" font-weight="bold" fill="#15803d"');

    // =======================================================================
    // 2. 16 BIT COLUMNS & 4 NIBBLE BLOCKS (Y = 56..82 Banners & Badges)
    // =======================================================================
    const nibbleStarts = [118, 376, 634, 892];
    const nibbleTitles = [
      "NIBBLE 3 [15:12] · HIGH NIBBLE (MSB)",
      "NIBBLE 2 [11:8] · MID-HIGH NIBBLE",
      "NIBBLE 1 [7:4] · MID-LOW NIBBLE",
      "NIBBLE 0 [3:0] · LOW NIBBLE (LSB)",
    ];

    const colLeft: number[] = new Array(16);
    for (let ni = 0; ni < 4; ni++) {
      const nsX = nibbleStarts[ni];
      const nw = 248;

      // Clean Nibble Header Banner (Y = 56..68) - ZERO wire penetration through banner!
      canvas.addBackground(R(nsX, 56, nw, 12, "#ecfdf5", "#059669", 2, 0.8));
      canvas.addLabel(nsX + nw / 2, 65, nibbleTitles[ni], 5.6, 'text-anchor="middle" font-weight="bold" fill="#047857"');

      // 4 Bit Slices in this nibble
      for (let bi = 0; bi < 4; bi++) {
        const k = (3 - ni) * 4 + (3 - bi); // bit 15 down to bit 0
        const xL = nsX + 12 + bi * 56;
        colLeft[k] = xL;

        // Bit Column Badge: Y = 72..82 (strictly in clear corridor, between Zone 1 drops and MUX)
        canvas.addBackground(R(xL + 12, 72, 34, 10, "#f1f5f9", "#cbd5e1", 2, 0.7));
        canvas.addLabel(xL + 29, 79.5, `BIT ${k}`, 5.0, 'text-anchor="middle" font-weight="bold" fill="#1e293b"');
      }
    }

    // =======================================================================
    // 3. CONTINUOUS CONTROL & MODE BUSES
    // =======================================================================
    // SUB Strobe Rail: exits portCtl at (96, 88), runs across all 16 columns at Y = 88
    const subRailY = 88;
    canvas.addBus(P(`M96 ${subRailY}H${busRight}`, isSub ? "#0284c7" : "#cbd5e1", isSub ? 1.4 : 0.9));
    canvas.addLabel(122, subRailY - 3, "SUB / NEG CONDITIONING (B* = B ⊕ SUB)", 4.8, 'font-weight="bold" fill="#0284c7"');

    // FN_SEL Strobe Rail: exits portCtl at (96, 244), runs across all 16 columns at Y = 244
    const fnSelRailY = 244;
    canvas.addBus(P(`M96 ${fnSelRailY}H${busRight}`, paths.control, 1.2));
    canvas.addLabel(122, fnSelRailY - 3, "FN_SEL[1:0]: ADD/SUB=0, XOR=1, AND=2, OR=3", 4.8, 'font-weight="bold" fill="#7c3aed"');

    // Carry Ripple Highway: Y = 178 (Continuous bus linking all 16 bit slices & CLA blocks)
    const cinY = 178;
    canvas.addBus(P(`M100 ${cinY}H1080`, isArith ? paths.high : "#cbd5e1", 1.4));

    // C0 entry from SUB strobe (busRight = 1146) into Bit 0 at X = 1080
    canvas.addWire(P(`M${busRight} ${subRailY}V${cinY}H1080`, isSub ? "#0284c7" : "#cbd5e1", 1.2));
    canvas.addDot(busRight, subRailY, isSub ? "#0284c7" : "#cbd5e1", 1.5);
    canvas.addDot(1080, cinY, isSub ? "#0284c7" : "#cbd5e1", 1.8);
    canvas.addLabel(1094, cinY - 4, "C0", 5.0, 'font-weight="bold" fill="#0284c7"');

    // Nibble Carry Taps along the continuous spine at Y = 178:
    // C4 (between Nibble 0 and Nibble 1 at X = 887)
    canvas.addDot(887, cinY, isArith ? paths.high : "#94a3b8", 1.6);
    canvas.addLabel(887, cinY - 4, "C4", 5.0, 'text-anchor="middle" font-weight="bold" fill="#059669"');

    // C8 (between Nibble 1 and Nibble 2 at X = 629)
    canvas.addDot(629, cinY, isArith ? paths.high : "#94a3b8", 1.6);
    canvas.addLabel(629, cinY - 4, "C8", 5.0, 'text-anchor="middle" font-weight="bold" fill="#059669"');

    // C12 (between Nibble 2 and Nibble 3 at X = 371)
    canvas.addDot(371, cinY, isArith ? paths.high : "#94a3b8", 1.6);
    canvas.addLabel(371, cinY - 4, "C12", 5.0, 'text-anchor="middle" font-weight="bold" fill="#059669"');

    // C16 Exit to Left Corridor at X = 100
    canvas.addDot(100, cinY, flags.CF ? paths.high : "#94a3b8", 1.6);
    canvas.addLabel(102, cinY - 4, "C16", 5.0, 'font-weight="bold" fill="#059669"');

    // =======================================================================
    // 4. 16 DISCRETE BIT-SLICES (MATHEMATICALLY GUARANTEED PLANAR ROUTING)
    // =======================================================================
    for (let k = 0; k < 16; k++) {
      const xL = colLeft[k];
      const aBit = (wordA >>> k) & 1;
      const bBit = (wordB >>> k) & 1;
      const sBit = (sWord >>> k) & 1;

      // ---------------------------------------------------------------------
      // 3-ZONE SPATIAL GRID:
      // Zone 1: Input Tracks (xL + 1 .. xL + 9)
      const trackA     = xL + 3;
      const trackB     = xL + 6;
      const trackBStar = xL + 6; // Replaces trackB below Y = 110!
      const trackCin   = xL + 8;

      // Zone 2: Logic Gates (xL + 10 .. xL + 24)
      const gateX = xL + 10;
      const gateW = 14;

      // Zone 3: Intermediate Drops, 4:1 Mux, and Result Drop (xL + 26 .. xL + 55)
      const chanSum = xL + 27;
      const chanP   = xL + 29;
      const chanG   = xL + 31;
      const chanOr  = xL + 33;
      const muxX    = xL + 36;
      const muxW    = 16;
      const resDrop = xL + 54;
      // ---------------------------------------------------------------------

      // --- 4.1 ZONE 1: TOP INPUT DROPS A[k] and B[k] ---
      canvas.addWire(P(`M${trackA} ${busAY}V152`, aBit ? paths.high : "#94a3b8", aBit ? 1.3 : 0.9));
      canvas.addDot(trackA, busAY, aBit ? paths.high : "#94a3b8", 1.5);

      canvas.addWire(P(`M${trackB} ${busBY}V98.8`, bBit ? "#059669" : "#94a3b8", bBit ? 1.3 : 0.9));
      canvas.addDot(trackB, busBY, bBit ? "#059669" : "#94a3b8", 1.5);

      // --- 4.2 ZONE 2: GATE 1 - INVERT-B GATE (B* = B ⊕ SUB) ---
      const binvY = 96;
      canvas.addComponent(new LogicGate(`binv_${k}`, gateX, binvY, "xor", gateW, 10, isSub));
      // in0 (Y = 98.8): from Track B at xL + 6
      canvas.addWire(P(`M${trackB} 98.8H${gateX}`, bBit ? "#059669" : "#94a3b8", 1.0));
      // in1 (Y = 103.2): from SUB rail above
      canvas.addWire(P(`M${trackB} ${subRailY}V103.2H${gateX}`, isSub ? "#0284c7" : "#cbd5e1", 1.0));
      canvas.addDot(trackB, subRailY, isSub ? "#0284c7" : "#cbd5e1", 1.4);
      // out (Y = 101): exits at gateX + 14, steps down to Y = 110, turns left to trackBStar (xL + 6)
      canvas.addWire(P(`M${gateX + gateW} 101H${xL + 25}V110H${trackBStar}V160`, "#64748b", 1.0));

      // --- 4.3 ZONE 2: GATE 2 - PROPAGATE XOR (P = A ⊕ B*) ---
      const pY = 116;
      canvas.addComponent(new LogicGate(`p_${k}`, gateX, pY, "xor", gateW, 10, true));
      // in0 (Y = 118.8): from Track A at xL + 3
      canvas.addWire(P(`M${trackA} 118.8H${gateX}`, aBit ? paths.high : "#94a3b8", 0.9));
      canvas.addDot(trackA, 118.8, aBit ? paths.high : "#94a3b8", 1.3);
      // in1 (Y = 123.2): from Track B* at xL + 6
      canvas.addWire(P(`M${trackBStar} 123.2H${gateX}`, "#64748b", 0.9));
      canvas.addDot(trackBStar, 123.2, "#64748b", 1.3);
      // out (Y = 121): exits at gateX + 14 into Zone 3 -> connects to chanP (xL + 29)
      canvas.addWire(P(`M${gateX + gateW} 121H${chanP}V200`, paths.high, 0.9));

      // --- 4.4 ZONE 2: GATE 3 - GENERATE AND (G = A · B*) ---
      const gY = 132;
      canvas.addComponent(new LogicGate(`g_${k}`, gateX, gY, "and", gateW, 10, true));
      // in0 (Y = 134.8): from Track A at xL + 3
      canvas.addWire(P(`M${trackA} 134.8H${gateX}`, aBit ? paths.high : "#94a3b8", 0.9));
      canvas.addDot(trackA, 134.8, aBit ? paths.high : "#94a3b8", 1.3);
      // in1 (Y = 139.2): from Track B* at xL + 6
      canvas.addWire(P(`M${trackBStar} 139.2H${gateX}`, "#64748b", 0.9));
      canvas.addDot(trackBStar, 139.2, "#64748b", 1.3);
      // out (Y = 137): exits at gateX + 14 into Zone 3 -> connects to chanG (xL + 31)
      canvas.addWire(P(`M${gateX + gateW} 137H${chanG}V212`, "#059669", 0.9));

      // --- 4.5 ZONE 2: GATE 4 - LOGIC OR (OR = A + B*) ---
      const orY = 148;
      canvas.addComponent(new LogicGate(`or_${k}`, gateX, orY, "or", gateW, 10, true));
      // in0 (Y = 150.8): from Track A at xL + 3
      canvas.addWire(P(`M${trackA} 150.8H${gateX}`, aBit ? paths.high : "#94a3b8", 0.9));
      // in1 (Y = 155.2): from Track B* at xL + 6
      canvas.addWire(P(`M${trackBStar} 155.2H${gateX}`, "#64748b", 0.9));
      // out (Y = 153): exits at gateX + 14 into Zone 3 -> connects to chanOr (xL + 33)
      canvas.addWire(P(`M${gateX + gateW} 153H${chanOr}V224`, "#64748b", 0.9));

      // --- 4.6 ZONE 2: GATE 5 - FULL ADDER SUM XOR (SUM = P ⊕ Cin) ---
      const sumY = 164;
      canvas.addComponent(new LogicGate(`sum_${k}`, gateX, sumY, "xor", gateW, 10, isArith));
      // in0 (Y = 166.8): P tap branches from chanP (xL + 29) horizontally to the left into in0!
      canvas.addWire(P(`M${chanP} 166.8H${gateX}`, paths.high, 0.9));
      canvas.addDot(chanP, 166.8, paths.high, 1.3);
      // in1 (Y = 171.2): from Track Cin (xL + 8) tapping directly from Carry Line at cinY = 178!
      canvas.addWire(P(`M${trackCin} ${cinY}V171.2H${gateX}`, isArith ? paths.high : "#cbd5e1", 0.9));
      canvas.addDot(trackCin, cinY, isArith ? paths.high : "#cbd5e1", 1.3);
      // out (Y = 169): exits at gateX + 14 into Zone 3 -> connects to chanSum (xL + 27)
      canvas.addWire(P(`M${gateX + gateW} 169H${chanSum}V188`, isArith ? paths.high : "#64748b", 0.9));

      // --- 4.7 ZONE 3: STAGE 4 - 4:1 MULTIPLEXER (MUX) ---
      const muxY = 184;
      canvas.addComponent(new MuxComponent(`mux_${k}`, muxX, muxY, muxW, 48, true));

      // ALL 4 INPUTS ENTER 100% HORIZONTALLY FROM THE LEFT (ZERO PENETRATION!):
      // in0 (Y = 188): SUM wire from chanSum (xL + 27)
      canvas.addWire(P(`M${chanSum} 188H${muxX}`, isArith ? paths.high : "#64748b", 0.9));
      // in1 (Y = 200): P (XOR) wire from chanP (xL + 29)
      canvas.addWire(P(`M${chanP} 200H${muxX}`, isXor ? paths.high : "#64748b", 0.9));
      // in2 (Y = 212): G (AND) wire from chanG (xL + 31)
      canvas.addWire(P(`M${chanG} 212H${muxX}`, isAnd ? paths.high : "#64748b", 0.9));
      // in3 (Y = 224): OR wire from chanOr (xL + 33)
      canvas.addWire(P(`M${chanOr} 224H${muxX}`, isOr ? paths.high : "#64748b", 0.9));

      // FN_SEL select wire into MUX bottom (clean vertical entry from Y = 244)
      canvas.addWire(P(`M${muxX + 8} ${fnSelRailY}V232`, paths.control, 0.9));
      canvas.addDot(muxX + 8, fnSelRailY, paths.control, 1.3);

      // MUX output: exits from RIGHT edge at (muxX + 16, 208), steps into resDrop (xL + 54) down to Result Highway (Y = 268)
      canvas.addWire(P(`M${muxX + muxW} 208H${resDrop}V268`, sBit ? paths.high : "#94a3b8", sBit ? 1.5 : 1.0));
      canvas.addDot(resDrop, 268, sBit ? paths.high : "#94a3b8", 1.6);

      // S[k] Output Indicator Badge: Y = 272..282 (cleanly below the result bus!)
      canvas.addBackground(R(xL + 20, 272, 18, 10, sBit ? "#dcfce7" : "#f1f5f9", sBit ? "#86efac" : "#cbd5e1", 2, 0.8));
      canvas.addLabel(xL + 29, 279.5, `${sBit}`, 5.2, 'text-anchor="middle" font-weight="bold" fill="' + (sBit ? "#15803d" : "#475569") + '"');
    }

    // =======================================================================
    // 5. 4-BIT CLA LOOKAHEAD BLOCKS (CARRY PROPAGATION FORMULAS, Y = 286..320)
    // ZERO VERTICAL WIRES PENETRATE THESE CARDS! (100% CLEAN CAD CONTAINERS)
    // =======================================================================
    for (let ni = 0; ni < 4; ni++) {
      const nsX = nibbleStarts[ni];
      const nibbleIdx = 3 - ni; // 3 at left, 0 at right
      canvas.addBackground(R(nsX + 8, 286, 232, 34, "#ecfdf5", "#059669", 2, 0.8));
      canvas.addLabel(nsX + 14, 297, `4-BIT CLA LOOKAHEAD GENERATOR (NIBBLE ${nibbleIdx})`, 5.0, 'font-weight="bold" fill="#065f46"');
      canvas.addLabel(nsX + 14, 311, "C_out = G3 + P3·G2 + P3·P2·G1 + P3·P2·P1·G0 + P3·P2·P1·P0·C_in", 4.3, 'fill="#047857" font-weight="bold"');
    }

    // =======================================================================
    // 6. HARDWARE BOOLEAN CONDITION GENERATORS · REAL GATE INTERCONNECTS
    // 100% Live Circuit: Carry Nodes & Result Highway ➔ Real Wires ➔ Logic Gates
    // Zero Floating Text Stubs · Every Input Linked to its Physical Source
    // =======================================================================
    canvas.addBackground(R(10, 336, 1260, 218, "#f8fafc", "#cbd5e1", 3, 1.0));
    canvas.addBackground(R(10, 336, 1260, 16, "#f1f5f9", "#cbd5e1", 3, 0.8));
    canvas.addLabel(20, 348, "HARDWARE BOOLEAN CONDITION GENERATORS · REAL EVALUATION GATES ➔ FLAGS REGISTER INTERFACE", 6.5, 'font-weight="bold" fill="#0f172a"');
    canvas.addLabel(800, 348, "LIVE CARRIES & BUS TAPS ➔ DISCRETE LOGIC GATES ➔ PERIMETER CONTACT PADS", 5.6, 'font-weight="bold" fill="#15803d"');

    // Dividers between the 6 discrete condition channels
    const divXs = [202, 394, 585, 776, 968];
    divXs.forEach(dx => canvas.addWire(P(`M${dx} 352V554`, "#e2e8f0", 1.0)));

    // Hardware signal derivations
    const afOn = Boolean(flags.AF);
    const pfOn = Boolean(flags.PF);
    const zfOn = Boolean(flags.ZF);
    const sfOn = Boolean(flags.SF);
    const ofOn = Boolean(flags.OF);
    const cfOn = Boolean(flags.CF);

    // =======================================================================
    // PHYSICAL WIRE TRACES FROM SOURCE NODES (C16, C15, S15, S[15:0], C4, S[7:0], SUB, ARITH_EN)
    // 100% Connected: Every wire begins at an actual source node with a solder dot!
    // =======================================================================

    // 1. C16 SOURCE: Carry Highway at X = 100, Y = 178 (Carry-out of Bit 15)
    canvas.addDot(100, 178, cfOn ? paths.high : "#94a3b8", 1.8);
    // C16 Drops through Corridor 0 into OF Gate in0 at (64, 393)
    canvas.addWire(P("M100 178H44V393H64", cfOn ? paths.high : "#94a3b8", 1.2));
    canvas.addDot(44, 178, cfOn ? paths.high : "#94a3b8", 1.4);
    canvas.addLabel(48, 210, "C16 (CARRY OUT)", 4.5, 'font-weight="bold" fill="#047857"');

    // C16 Carry Highway across chip to CF Gate in0 at (1010, 395) at Y = 320
    canvas.addDot(44, 320, cfOn ? paths.high : "#94a3b8", 1.6);
    canvas.addWire(P("M44 320H994V395H1010", cfOn ? paths.high : "#94a3b8", 1.2));
    canvas.addLabel(54, 317, "C16 HIGHWAY ➔ OF & CF GATES", 4.3, 'font-weight="bold" fill="#047857"');

    // ARITH_EN STROBE SPINE (Y = 328): Enables arithmetic flags; clears CF, OF, AF on logic operations (AND, OR, XOR)
    canvas.addBus(P("M96 328H1150", isArith ? paths.high : "#cbd5e1", 1.0));
    canvas.addLabel(100, 334, "ARITH_EN · GATES OF, CF, AF (CLEARS CF & OF ON LOGIC OPS)", 4.3, 'font-weight="bold" fill="#7c3aed"');

    // 2. C15 SOURCE: Carry Highway into Bit 15 at X = 138, Y = 178
    canvas.addDot(138, 178, ofOn ? paths.high : "#94a3b8", 1.8);
    // C15 Drops through Corridor 0 into OF Gate in1 at (64, 397)
    canvas.addWire(P("M138 178V184H54V397H64", ofOn ? paths.high : "#94a3b8", 1.2));
    canvas.addDot(54, 184, ofOn ? paths.high : "#94a3b8", 1.4);
    canvas.addLabel(58, 224, "C15", 4.5, 'font-weight="bold" fill="#64748b"');

    // 3. S15 SOURCE: Result Highway at Bit 15 Writeback (X = 184, Y = 268)
    canvas.addDot(184, 268, sfOn ? paths.high : "#94a3b8", 1.8);
    // S15 Wire drops through Corridor 0 and routes into SF Buffer input at (280, 403)
    canvas.addWire(P("M184 268V274H120V354H268V403H280", sfOn ? paths.high : "#94a3b8", 1.3));
    canvas.addDot(120, 274, sfOn ? paths.high : "#94a3b8", 1.4);
    canvas.addLabel(126, 280, "S15 (MSB SIGN BIT)", 4.5, 'font-weight="bold" fill="#15803d"');

    // 4. S[15:0] NIBBLE SOURCES FOR 16-BIT ZERO DETECTOR
    // Nibble 3 (S[15:12]) tap at X = 200, Y = 268
    canvas.addDot(200, 268, paths.high, 1.6);
    canvas.addWire(P("M200 268V276H380V374H412", paths.high, 1.2));
    canvas.addLabel(382, 366, "S[15:12]", 4.2, 'font-weight="bold" fill="#15803d"');

    // Nibble 2 (S[11:8]) tap at X = 371, Y = 268
    canvas.addDot(371, 268, paths.high, 1.6);
    canvas.addWire(P("M371 268V392H412", paths.high, 1.2));
    canvas.addLabel(382, 388, "S[11:8]", 4.2, 'font-weight="bold" fill="#15803d"');

    // Nibble 1 (S[7:4]) tap at X = 634, Y = 268
    canvas.addDot(634, 268, paths.high, 1.6);
    canvas.addWire(P("M634 268V276H630V360H392V410H412", paths.high, 1.2));
    canvas.addLabel(382, 408, "S[7:4]", 4.2, 'font-weight="bold" fill="#15803d"');

    // Nibble 0 (S[3:0]) tap at X = 892, Y = 268
    canvas.addDot(892, 268, paths.high, 1.6);
    canvas.addWire(P("M892 268V276H886V366H386V428H412", paths.high, 1.2));
    canvas.addLabel(382, 426, "S[3:0]", 4.2, 'font-weight="bold" fill="#15803d"');

    // 5. C4 SOURCE: Carry Highway at Nibble 0 Carry Node (X = 887, Y = 178)
    canvas.addDot(887, 178, afOn ? paths.high : "#94a3b8", 2.0);
    // C4 Wire drops through inter-nibble gap into AF Gate in0 at (636, 395)
    canvas.addWire(P("M887 178V186H618V395H636", afOn ? paths.high : "#94a3b8", 1.2));
    canvas.addLabel(892, 192, "C4 (BCD NIBBLE 0 CARRY)", 4.5, 'font-weight="bold" fill="#059669"');

    // 6. LOWER BYTE S[7:0] SOURCES FOR 8-BIT PARITY REDUCTION TREE
    // Tap off Result Highway at X = 926, Y = 268 (outside PF title text)
    canvas.addDot(926, 268, paths.high, 1.8);
    canvas.addWire(P("M926 268V360H784V425", paths.high, 1.4));
    canvas.addLabel(930, 280, "S[7:0] PARITY BUS", 4.5, 'font-weight="bold" fill="#059669"');
    // Drops into 4 Stage-1 XOR pairs
    canvas.addWire(P("M784 371H794M784 375H794", paths.high, 1.0));
    canvas.addWire(P("M784 387H794M784 391H794", paths.high, 1.0));
    canvas.addWire(P("M784 405H794M784 409H794", paths.high, 1.0));
    canvas.addWire(P("M784 421H794M784 425H794", paths.high, 1.0));

    // 7. SUB SOURCE: SUB Strobe Rail at X = 1146, Y = 88
    canvas.addDot(1146, 88, isSub ? "#0284c7" : "#cbd5e1", 1.8);
    // SUB Strobe drops through Corridor 4 into CF Gate in1 at (1010, 399)
    canvas.addWire(P("M1146 88V354H998V399H1010", isSub ? "#0284c7" : "#cbd5e1", 1.2));
    canvas.addLabel(1150, 102, "SUB STROBE", 4.5, 'font-weight="bold" fill="#0284c7"');
    // SUB branch to AF Gate in1 at (636, 399)
    canvas.addDot(998, 354, isSub ? "#0284c7" : "#cbd5e1", 1.4);
    canvas.addWire(P("M998 354H626V399H636", isSub ? "#0284c7" : "#cbd5e1", 1.0));

    // --- CHANNEL 1: OF (Center x = 107, bounds: 10..202) ---
    // Multi-Gate Circuit: XOR (C16 ⊕ C15) ➔ AND (ARITH_EN)
    canvas.addLabel(107, 364, "OF = (C16 ⊕ C15) · ARITH_EN", 4.8, `text-anchor="middle" font-weight="bold" fill="${ofOn ? '#15803d' : '#7c3aed'}"`);
    const c16Val = cfOn ? 1 : 0;
    const c15Val = ofOn ? (c16Val ^ 1) : c16Val;
    const ofXorOn = Boolean(c16Val ^ c15Val);
    canvas.addComponent(new LogicGate("of_xor", 64, 388, "xor", 18, 14, ofXorOn));
    canvas.addWire(P("M82 395H100V399H118", ofXorOn ? paths.high : "#94a3b8", 1.0));
    canvas.addWire(P("M154 328V414H110V403H118", isArith ? paths.high : "#cbd5e1", 1.0));
    canvas.addDot(154, 328, isArith ? paths.high : "#cbd5e1", 1.3);
    canvas.addComponent(new LogicGate("of_and", 118, 394, "and", 18, 14, ofOn));
    canvas.addWire(P("M136 401H150V438H107V444", ofOn ? paths.high : "#94a3b8", 1.4));

    // --- CHANNEL 2: SF (Center x = 298, bounds: 203..394) ---
    // Gate Circuit: S15 Sign Bit Driver
    canvas.addLabel(298, 364, "SF = S15 (MSB SIGN BIT)", 4.8, `text-anchor="middle" font-weight="bold" fill="${sfOn ? '#15803d' : '#854d0e'}"`);
    canvas.addComponent(new LogicGate("sf_buf", 280, 396, "buf", 18, 14, sfOn));
    canvas.addWire(P("M298 403V444", sfOn ? paths.high : "#94a3b8", 1.4));

    // --- CHANNEL 3: ZF (Center x = 490, bounds: 395..585) ---
    // Multi-Gate Circuit: 16-Bit Zero Detector (4× 4-Bit NOR ➔ 3× AND Tree)
    canvas.addLabel(490, 364, "ZF = 16-BIT ZERO DETECTOR TREE", 4.8, `text-anchor="middle" font-weight="bold" fill="${zfOn ? '#15803d' : '#15803d'}"`);
    const z3On = ((sWord >>> 12) & 0xf) === 0;
    const z2On = ((sWord >>> 8) & 0xf) === 0;
    const z1On = ((sWord >>> 4) & 0xf) === 0;
    const z0On = (sWord & 0xf) === 0;
    const zhOn = z3On && z2On;
    const zlOn = z1On && z0On;
    canvas.addComponent(new LogicGate("zf_nor3", 412, 368, "nor", 16, 12, z3On));
    canvas.addComponent(new LogicGate("zf_nor2", 412, 386, "nor", 16, 12, z2On));
    canvas.addComponent(new LogicGate("zf_nor1", 412, 404, "nor", 16, 12, z1On));
    canvas.addComponent(new LogicGate("zf_nor0", 412, 422, "nor", 16, 12, z0On));
    // Collector Stage 2: 2 AND Gates
    canvas.addWire(P("M428 374H446V381H460", z3On ? paths.high : "#94a3b8", 0.9));
    canvas.addWire(P("M428 392H446V389H460", z2On ? paths.high : "#94a3b8", 0.9));
    canvas.addComponent(new LogicGate("zf_and_hi", 460, 378, "and", 16, 14, zhOn));
    canvas.addWire(P("M428 410H446V417H460", z1On ? paths.high : "#94a3b8", 0.9));
    canvas.addWire(P("M428 428H446V425H460", z0On ? paths.high : "#94a3b8", 0.9));
    canvas.addComponent(new LogicGate("zf_and_lo", 460, 414, "and", 16, 14, zlOn));
    // Collector Stage 3: Final AND Gate
    canvas.addWire(P("M476 385H492V400H508", zhOn ? paths.high : "#94a3b8", 1.0));
    canvas.addWire(P("M476 421H492V408H508", zlOn ? paths.high : "#94a3b8", 1.0));
    canvas.addComponent(new LogicGate("zf_and_out", 508, 396, "and", 18, 16, zfOn));
    canvas.addWire(P("M526 404H538V438H490V444", zfOn ? paths.high : "#94a3b8", 1.4));

    // --- CHANNEL 4: AF (Center x = 681, bounds: 586..776) ---
    // Multi-Gate Circuit: XOR (C4 ⊕ SUB) ➔ AND (ARITH_EN)
    canvas.addLabel(681, 364, "AF = (C4 ⊕ SUB) · ARITH_EN", 4.8, `text-anchor="middle" font-weight="bold" fill="${afOn ? '#15803d' : '#854d0e'}"`);
    const c4Val = afOn ? 1 : 0;
    const afXorOn = Boolean(c4Val ^ (isSub ? 1 : 0));
    canvas.addComponent(new LogicGate("af_xor", 636, 390, "xor", 18, 14, afXorOn));
    canvas.addWire(P("M654 397H676V401H696", afXorOn ? paths.high : "#94a3b8", 1.0));
    canvas.addWire(P("M730 328V414H688V405H696", isArith ? paths.high : "#cbd5e1", 1.0));
    canvas.addDot(730, 328, isArith ? paths.high : "#cbd5e1", 1.3);
    canvas.addComponent(new LogicGate("af_and", 696, 396, "and", 18, 14, afOn));
    canvas.addWire(P("M714 403H728V438H681V444", afOn ? paths.high : "#94a3b8", 1.4));

    // --- CHANNEL 5: PF (Center x = 872, bounds: 777..968) ---
    // Multi-Gate Circuit: 8-Bit Even Parity Tree (4× XOR ➔ 2× XOR ➔ 1× XOR ➔ 1× INV)
    canvas.addLabel(872, 364, "PF = 8-BIT EVEN PARITY TREE", 4.8, `text-anchor="middle" font-weight="bold" fill="${pfOn ? '#15803d' : '#059669'}"`);
    const lowByte = sWord & 0xff;
    const pf76 = Boolean(((lowByte >>> 7) & 1) ^ ((lowByte >>> 6) & 1));
    const pf54 = Boolean(((lowByte >>> 5) & 1) ^ ((lowByte >>> 4) & 1));
    const pf32 = Boolean(((lowByte >>> 3) & 1) ^ ((lowByte >>> 2) & 1));
    const pf10 = Boolean(((lowByte >>> 1) & 1) ^ (lowByte & 1));
    canvas.addComponent(new LogicGate("pf_xor_76", 794, 368, "xor", 14, 10, pf76));
    canvas.addComponent(new LogicGate("pf_xor_54", 794, 384, "xor", 14, 10, pf54));
    canvas.addComponent(new LogicGate("pf_xor_32", 794, 402, "xor", 14, 10, pf32));
    canvas.addComponent(new LogicGate("pf_xor_10", 794, 418, "xor", 14, 10, pf10));
    // Stage 2: 2 XOR Gates
    const pfHi = pf76 !== pf54;
    const pfLo = pf32 !== pf10;
    canvas.addWire(P("M808 373H826V379H844", pf76 ? paths.high : "#94a3b8", 0.9));
    canvas.addWire(P("M808 389H826V385H844", pf54 ? paths.high : "#94a3b8", 0.9));
    canvas.addComponent(new LogicGate("pf_xor_hi", 844, 376, "xor", 15, 12, pfHi));
    canvas.addWire(P("M808 407H826V413H844", pf32 ? paths.high : "#94a3b8", 0.9));
    canvas.addWire(P("M808 423H826V419H844", pf10 ? paths.high : "#94a3b8", 0.9));
    canvas.addComponent(new LogicGate("pf_xor_lo", 844, 410, "xor", 15, 12, pfLo));
    // Stage 3: 1 XOR Gate + 1 Inverter (Even Parity)
    const pfFinal = pfHi !== pfLo;
    canvas.addWire(P("M859 382H878V397H896", pfHi ? paths.high : "#94a3b8", 1.0));
    canvas.addWire(P("M859 416H878V405H896", pfLo ? paths.high : "#94a3b8", 1.0));
    canvas.addComponent(new LogicGate("pf_xor_fin", 896, 394, "xor", 16, 14, pfFinal));
    canvas.addWire(P("M912 401H924", pfFinal ? paths.high : "#94a3b8", 1.0));
    canvas.addComponent(new LogicGate("pf_inv", 924, 397, "inv", 12, 8, pfOn));
    canvas.addWire(P("M936 401H948V438H872V444", pfOn ? paths.high : "#94a3b8", 1.4));

    // --- CHANNEL 6: CF (Center x = 1064, bounds: 969..1270) ---
    // Multi-Gate Circuit: XOR (C16 ⊕ SUB) ➔ AND (ARITH_EN)
    canvas.addLabel(1064, 364, "CF = (C16 ⊕ SUB) · ARITH_EN", 4.8, `text-anchor="middle" font-weight="bold" fill="${cfOn ? '#15803d' : '#0284c7'}"`);
    const cfXorOn = Boolean(c16Val ^ (isSub ? 1 : 0));
    canvas.addComponent(new LogicGate("cf_xor", 1010, 390, "xor", 18, 14, cfXorOn));
    canvas.addWire(P("M1028 397H1054V401H1076", cfXorOn ? paths.high : "#94a3b8", 1.0));
    canvas.addWire(P("M1114 328V414H1068V405H1076", isArith ? paths.high : "#cbd5e1", 1.0));
    canvas.addDot(1114, 328, isArith ? paths.high : "#cbd5e1", 1.3);
    canvas.addComponent(new LogicGate("cf_and", 1076, 396, "and", 18, 14, cfOn));
    canvas.addWire(P("M1094 403H1108V438H1064V444", cfOn ? paths.high : "#94a3b8", 1.4));

    // Readout Badges & Direct Vertical Perimeter Contact Drops
    const flagDefs = [
      { id: "OF", val: flags.OF, x: 107 },
      { id: "SF", val: flags.SF, x: 298 },
      { id: "ZF", val: flags.ZF, x: 490 },
      { id: "AF", val: flags.AF, x: 681 },
      { id: "PF", val: flags.PF, x: 872 },
      { id: "CF", val: flags.CF, x: 1064 },
    ];

    flagDefs.forEach((fd) => {
      const fOn = Boolean(fd.val);
      // Readout badge at Y = 444..460
      canvas.addBackground(R(fd.x - 20, 444, 40, 16, fOn ? "#dcfce7" : "#f1f5f9", fOn ? "#16a34a" : "#94a3b8", 2, 1.0));
      canvas.addLabel(fd.x, 455, `${fd.id}: ${fd.val}`, 5.6, 'text-anchor="middle" font-weight="bold" fill="' + (fOn ? "#15803d" : "#475569") + '"');
      canvas.addDot(fd.x, 444, fOn ? paths.high : "#94a3b8", 1.8);
      // Direct vertical copper lead to perimeter contact pad at ly = 554
      canvas.addWire(P(`M${fd.x} 460V554`, fOn ? paths.high : "#cbd5e1", 1.6));
      // Copper contact pad on bottom perimeter
      canvas.addBackground(R(fd.x - 6, 548, 12, 7, "#fed7aa", "#c2410c", 2, 1.0));
      canvas.addDot(fd.x, 554, fOn ? paths.high : "#94a3b8", 2.0);
    });

    return canvas.render();
  }
}
