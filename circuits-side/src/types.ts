/**
 * Intel 8086 Circuit Atlas - TypeScript Core Type Definitions & Interfaces
 */
namespace LogicDraw {
  export type PinDirection = "L" | "R" | "T" | "B";
  export type GateType = "and" | "or" | "xor" | "nand" | "nor" | "not" | "inv" | "buf" | "mux";

  export interface IPin {
    owner: IComponent;
    id: string;
    x: number;
    y: number;
    dir: PinDirection;
    label?: string;
    busWidth?: number;
  }

  export interface IComponent {
    id: string;
    x: number;
    y: number;
    w: number;
    h: number;
    label?: string;
    pins: Map<string, IPin>;
    addPin(id: string, rx: number, ry: number, dir?: PinDirection, label?: string, busWidth?: number): IPin;
    pin(id: string): IPin;
    bounds(): { x: number; y: number; w: number; h: number; right: number; bottom: number };
    render(): string;
  }

  export interface RoutePoint {
    x: number;
    y: number;
    dir?: PinDirection;
  }

  export interface RouteOptions {
    viaX?: number;
    viaY?: number;
    midX?: number;
    waypoints?: Array<[number, number] | { x: number; y: number }>;
    color?: string;
    width?: number;
    busSlash?: string;
    slashX?: number;
    slashY?: number;
  }

  export interface BranchOptions extends RouteOptions {
    dot?: boolean;
    dotRadius?: number;
    dir?: PinDirection;
  }

  export interface BusDescriptor {
    x?: number;
    y: number;
    xStart?: number;
    xEnd?: number;
    xMid?: number;
    yEnd?: number;
    width: string;
    color: string;
  }

  export interface SliceDescriptor {
    index: number;
    name: string;
    sx: number;
  }

  export interface RippleCarryDescriptor {
    xStart: number;
    xEnd: number;
    y: number;
    label: string;
    lblX: number;
    lblY: number;
  }

  export interface FlagDescriptor {
    id: string;
    from: [number, number];
    pinX: number;
    viaY: number;
  }

  export interface DiscreteBitDescriptor {
    index: number;
    dinX: number;
    busAx: number;
    busBx: number;
  }

  export interface ALUCircuitData {
    buses: {
      control: BusDescriptor;
      busA: BusDescriptor;
      busB: BusDescriptor;
      result: BusDescriptor;
    };
    slices: SliceDescriptor[];
    rippleCarry: RippleCarryDescriptor[];
    flags: FlagDescriptor[];
  }
}
