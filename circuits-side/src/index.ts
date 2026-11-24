/// <reference path="types.ts" />
/// <reference path="primitives.ts" />
/// <reference path="engine.ts" />
/// <reference path="modules/registers.ts" />
/// <reference path="modules/alu.ts" />
/// <reference path="modules/flags.ts" />
/// <reference path="modules/biu.ts" />
/// <reference path="modules/eu.ts" />
/// <reference path="modules/cu.ts" />
/// <reference path="modules/sys.ts" />
/**
 * Intel 8086 Circuit Workbench - Central Registry & Browser/Node Interface
 */
namespace LogicDraw {
  const components: Record<string, (s: SchematicState, bit?: number) => Workbench.CircuitView> = {
    regs: (s) => ({ body: registersLogic(s), vw: 1280, vh: 560, title: "16-BIT REGISTER FILE · DUAL PORT" }),
    flags: (s) => ({ body: flagsLogic(s), vw: 1280, vh: 420, title: "16-BIT STATUS & CONTROL FLAGS REGISTER (FR)" }),
    temps: (s) => ({ body: tempsLogic(s), vw: 468, vh: 216, title: "OPERAND TEMPORARY LATCHES" }),
    aluctl: (s) => ({ body: aluctlLogic(s), vw: 360, vh: 200, title: "ALU CONTROL DECODER" }),
    mux: (s) => ({ body: muxLogic(s), vw: 400, vh: 220, title: "ALU INPUT MULTIPLEXER (3:1)" }),
    alu: (s, bit = 0) => ({ body: adderLogic(s, bit), vw: 1280, vh: 560, title: "16-BIT PARALLEL ARITHMETIC LOGIC UNIT & CLA" }),
    internal: (s) => ({ body: internalBusLogic(s), vw: 460, vh: 160, title: "16-BIT INTERNAL DATA BUS & CROSSBAR TAPS" }),
    seg: (s) => ({ body: segLogic(s), vw: 400, vh: 200, title: "SEGMENT REGISTERS (CS, DS, SS, ES)" }),
    ip: (s) => ({ body: ipLogic(s), vw: 380, vh: 200, title: "INSTRUCTION POINTER & INCREMENTER" }),
    ind: (s) => ({ body: indLogic(s), vw: 340, vh: 170, title: "INDIRECT OFFSET REGISTER (IND)" }),
    segmux: (s) => ({ body: segmuxLogic(s), vw: 410, vh: 180, title: "SEGMENT MULTIPLEXER (4:1)" }),
    offmux: (s) => ({ body: offmuxLogic(s), vw: 340, vh: 170, title: "OFFSET MULTIPLEXER (2:1)" }),
    adder: (s) => ({ body: addressAdderLogic(s), vw: 408, vh: 186, title: "BIU 20-BIT ADDRESS ADDER" }),
    opr: (s) => ({ body: oprLogic(s), vw: 380, vh: 190, title: "OPERAND BUS TRANSCEIVER (OPR)" }),
    memory: (s) => ({ body: busControllerLogic(s), vw: 408, vh: 216, title: "BUS CONTROLLER & T-STATES" }),
    ext: (s) => ({ body: pinsLogic(s), vw: 418, vh: 246, title: "INTEL 8086 SILICON I/O & ESD PROTECTION CELL" }),
    queue: (s) => ({ body: queueLogic(s), vw: 440, vh: 190, title: "6-BYTE INSTRUCTION PREFETCH FIFO" }),
    loader: (s) => ({ body: loaderLogic(s), vw: 400, vh: 190, title: "INSTRUCTION LOADER & MODR/M" }),
    ir: (s) => ({ body: irLogic(s), vw: 340, vh: 170, title: "INSTRUCTION REGISTER (8-BIT IR)" }),
    prefix: (s) => ({ body: prefixLogic(s), vw: 360, vh: 170, title: "PREFIX & OVERRIDE LATCH" }),
    pla: (s) => ({ body: plaLogic(s), vw: 410, vh: 190, title: "GROUP DECODE ROM / PLA" }),
    trom: (s) => ({ body: tromLogic(s), vw: 400, vh: 190, title: "TRANSLATION ROM (TROM)" }),
    engine: (s) => ({ body: engineLogic(s), vw: 400, vh: 180, title: "MICROCODE SEQUENCING ENGINE" }),
    mar: (s) => ({ body: marLogic(s), vw: 360, vh: 170, title: "MICROCODE ADDRESS REGISTER (MAR)" }),
    rom: (s) => ({ body: romLogic(s), vw: 420, vh: 180, title: "MICROCODE CONTROL STORE (512×21)" }),
    ctl: (s) => ({ body: ctlLogic(s), vw: 420, vh: 170, title: "CONTROL LATCHES & DECODERS" }),
    clk: (s) => ({ body: clockGenLogic(s), vw: 440, vh: 190, title: "8284A CLOCK GENERATOR" }),
    dec: (s) => ({ body: decLogic(s), vw: 380, vh: 195, title: "CONTROL ENABLE MATRIX (DECODE)" }),
    seq: (s) => ({ body: seqLogic(s), vw: 400, vh: 206, title: "PHASE SEQUENCER (JK FLIP-FLOPS)" }),
    ram: (s) => ({ body: ramLogic(s), vw: 930, vh: 195, title: "SYSTEM STATIC RAM (EVEN/ODD + 6T CELL)" }),
    latches: (s) => ({ body: latchesLogic(s), vw: 470, vh: 195, title: "8282 / 74LS373 ADDRESS LATCHES" }),
    transceivers: (s) => ({ body: transceiversLogic(s), vw: 470, vh: 190, title: "8286 / 74LS245 DATA TRANSCEIVERS" }),
    decoder: (s) => ({ body: decoderChipLogic(s), vw: 420, vh: 190, title: "74LS138 ADDRESS DECODER" }),
    bootrom: (s) => ({ body: bootromLogic(s), vw: 400, vh: 175, title: "2764 BOOT ROM (0xFFFF0)" }),
  };

  export function getComponentLogic(id: string, s: SchematicState, bit: number = 0) {
    const fn = components[id];
    return fn ? fn(s, bit) : null;
  }

  export function hasLogic(id: string): boolean {
    return Boolean(components[id]);
  }

  export function listComponents(): string[] {
    return Object.keys(components);
  }

  const api = {
    adderLogic,
    decoderLogic,
    sequencerLogic,
    decLogic,
    seqLogic,
    registersLogic,
    flagsLogic,
    tempsLogic,
    aluctlLogic,
    muxLogic,
    internalBusLogic,
    segLogic,
    ipLogic,
    indLogic,
    segmuxLogic,
    offmuxLogic,
    addressAdderLogic,
    oprLogic,
    busControllerLogic,
    pinsLogic,
    queueLogic,
    loaderLogic,
    irLogic,
    prefixLogic,
    plaLogic,
    tromLogic,
    engineLogic,
    marLogic,
    romLogic,
    ctlLogic,
    clkLogic,
    clockGenLogic,
    ramLogic,
    latchesLogic,
    transceiversLogic,
    decoderChipLogic,
    bootromLogic,
    hasLogic,
    getComponentLogic,
    listComponents,
    T,
    mono,
    R,
    P,
    dot,
    tinyGate,
    dff,
    dlatch,
    nmos,
    pmos,
    gnd,
    vcc,
    busSlash,
    hex,
    bin,
    paths,
    AutoRouter,
    RoutingError,
    orthogonalRoute,
    segmentHitsRect,
    Component,
    LogicGate,
    MuxComponent,
    SubcircuitCard,
    DffCell,
    TriStateBuffer,
    PortBox,
    SchematicCanvas,
    Pin,
  };

  const exposed = Object.assign(api, components);
  type Host = { logicDraw: typeof exposed };
  const target = (typeof window !== "undefined" ? window : globalThis) as unknown as Host;
  target.logicDraw = exposed;
  if (typeof globalThis !== "undefined") {
    (globalThis as unknown as Host).logicDraw = exposed;
  }
}
