/** Contracts shared by the CPU demonstration, circuit renderer and UI. */
declare namespace Workbench {
  export type Program = "ADD" | "SUB" | "MEM";
  export type ArithmeticFlag = "CF" | "PF" | "AF" | "ZF" | "SF" | "OF";
  export type Flag = ArithmeticFlag | "TF" | "IF" | "DF";
  export type Flags = Record<Flag, number>;
  export interface CpuState {
    ax: number; bx: number; cx: number; dx: number;
    sp: number; bp: number; si: number; di: number;
    a: number; b: number; c: number;
    cs: number; ds: number; ss: number; es: number; ip: number;
    ind: number | null; opr: number | null; phys: number | null;
    selectedSegment: string | null; disp: number | null;
    prefix: number | null; ir: number | null; mod: number | null;
    op: string; queue: number[]; phase: number; page: number;
    cycles: number; clock: number; retired: number; flags: Flags;
    history: Array<{ clk: number; we: number }>;
    last: string; lastEvent: string; lastWord: number | null;
    mar?: number;
  }
  export interface AluSlice {
    A: number; rawB: number; B: number; P: number; G: number; C: number;
    t1: number; t2: number; t3: number; t4: number;
    upper: number; lower: number; carry: number; sum: number;
  }
  export interface AluResult {
    word: number; flags: Record<ArithmeticFlag, number>; slices: AluSlice[];
  }
  export interface ControlOutput { key: string; name: string; terms: number[] }
  export interface CpuModel {
    readonly s: CpuState;
    readonly settings: { a: number; b: number; op: Program };
    readonly phaseNames: string[];
    readonly outputs: ControlOutput[];
    reset(): void; step(): void; half(): void;
    configure(a: number, b: number, op: string): void;
    calculate(a?: number, b?: number, sub?: boolean): AluResult;
    inputs(): [number, number, boolean];
    line(): number; index(): number; enables(): Record<string, boolean>;
    isMem(): boolean; hex(value: number, digits?: number): string;
    phaseName(): string; describe(): string;
    physical(segment: number, offset: number): number;
    ctrl(phase: number): boolean;
  }
  export type UnitGroup = "EU" | "BIU" | "CU" | "SYS";
  export type UnitBox = [x: number, y: number, width: number, height: number, title: string, group: UnitGroup];
  export type Net = [id: string, source: string, target: string, label: string, from: string, to: string];
  export interface ViewRect { x1: number; y1: number; x2: number; y2: number }
  /** Cheap scene descriptors; expensive SVG is produced only for visible items. */
  export interface RenderItem {
    id: string;
    bounds: ViewRect;
    path?: readonly { x: number; y: number }[];
    version: string;
    render(): string;
  }
  export interface RenderScene { defs: string; items: readonly RenderItem[] }
  export interface CircuitView { body: string; vw: number; vh: number; title: string }
  export interface Board {
    W: number; H: number; readonly height: number;
    N: Record<string, UnitBox>;
    info: Record<string, [string, string, string]>;
    nets: Net[];
    render(scale: number, selected: string, bit: number, view?: ViewRect): string;
    scene(scale: number, selected: string, bit: number): RenderScene;
    reflow(scale: number, cy: number): number;
    Y(y: number): number; unmap(value: number): number;
    activeIds(): string[]; expanded(): boolean;
    layout(): BoardLayout;
  }
  export interface BoardPin { x: number; y: number; dir: "L" | "R"; owner: string; label: string }
  export interface BoardConnection { net: Net; points: Array<{ x: number; y: number }>; color: string }
  export interface BoardLayout { pins: Record<string, BoardPin>; connections: BoardConnection[] }
  /** Narrow public rendering boundary; the application does not depend on gate internals. */
  export interface LogicRenderer {
    R(x: number, y: number, w: number, h: number, fill: string, stroke?: string, radius?: number, strokeWidth?: number): string;
    P(path: string, color?: string, width?: number, fill?: string, attributes?: string): string;
    dot(x: number, y: number, color?: string, radius?: number): string;
    getComponentLogic(id: string, state: CpuState, bit?: number): CircuitView | null;
    AutoRouter: new(options: {
      obstacles: Array<{ id: string; x: number; y: number; w: number; h: number }>;
      bounds: { x: number; y: number; w: number; h: number };
      clearance: number; stub: number;
    }) => {
      route(from: { x: number; y: number; dir: "L" | "R" }, to: { x: number; y: number; dir: "L" | "R" }, options: { net: string }): unknown;
      readonly routes: ReadonlyArray<ReadonlyArray<{ x: number; y: number }>>;
    };
  }
}

interface Window {
  cpu: Workbench.CpuModel;
  board: Workbench.Board;
  logicDraw: Workbench.LogicRenderer;
}
declare const cpu: Workbench.CpuModel;
declare const board: Workbench.Board;
declare const logicDraw: Workbench.LogicRenderer;
