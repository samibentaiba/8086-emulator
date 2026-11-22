/// <reference path="types.ts" />
/// <reference path="primitives.ts" />
/**
 * Intel 8086 Circuit Atlas - OOP Schematic Engine (Auto-Router & Component Graph)
 */
namespace LogicDraw {
  export class Pin implements IPin {
    constructor(
      public owner: IComponent,
      public id: string,
      public x: number,
      public y: number,
      public dir: PinDirection = "L",
      public label: string = "",
      public busWidth: number = 1
    ) {}
  }

  export class Component implements IComponent {
    public pins: Map<string, IPin> = new Map();
    constructor(
      public id: string,
      public x: number,
      public y: number,
      public w: number,
      public h: number,
      public label: string = ""
    ) {}

    addPin(id: string, rx: number, ry: number, dir: PinDirection = "L", label: string = "", busWidth: number = 1): IPin {
      const p = new Pin(this, id, this.x + rx, this.y + ry, dir, label, busWidth);
      this.pins.set(id, p);
      return p;
    }

    pin(id: string): IPin {
      const p = this.pins.get(id);
      if (!p) throw new Error(`Missing pin '${id}' on component '${this.id}'`);
      return p;
    }

    bounds() {
      return { x: this.x, y: this.y, w: this.w, h: this.h, right: this.x + this.w, bottom: this.y + this.h };
    }

    render(): string {
      return "";
    }
  }

  export class LogicGate extends Component {
    public type: GateType;
    public on: boolean;
    public formula: string;

    constructor(id: string, x: number, y: number, type: GateType, w: number = 18, h: number = 12, on: boolean = false, label: string = "", formula: string = "") {
      super(id, x, y, w, h, label);
      this.type = type;
      this.on = on;
      this.formula = formula;

      if (type === "not" || type === "inv" || type === "buf") {
        this.addPin("in0", 0, h / 2, "L");
        this.addPin("out", w, h / 2, "R");
      } else {
        const inOff = h >= 14 ? 4 : 3;
        this.addPin("in0", 0, inOff, "L");
        this.addPin("in1", 0, h - inOff, "L");
        this.addPin("out", w, h / 2, "R");
      }
    }

    render(): string {
      let out = tinyGate(this.x, this.y, this.type, this.w, this.h, this.on);
      if (this.label) {
        out += mono(this.x + this.w / 2, this.y - 4, this.label, 4.8, 'text-anchor="middle" font-weight="bold" fill="#64748b"');
      }
      if (this.formula) {
        out += mono(this.x + this.w / 2, this.y + this.h + 8, this.formula, 4.2, 'text-anchor="middle" font-weight="bold" fill="#047857"');
      }
      return out;
    }
  }

  export class MuxComponent extends Component {
    public on: boolean;
    constructor(id: string, x: number, y: number, w: number = 22, h: number = 54, on: boolean = false) {
      super(id, x, y, w, h, "MUX");
      this.on = on;
      this.addPin("in0", 0, 4, "L", "SUM");
      this.addPin("in1", 0, 18, "L", "XOR");
      this.addPin("in2", 0, 30, "L", "AND");
      this.addPin("in3", 0, 42, "L", "OR");
      this.addPin("sel", w * 0.5, h, "B", "FN_SEL");
      this.addPin("out", w * 0.88, h * 0.5, "R", "OUT", 4);
    }

    render(): string {
      return tinyGate(this.x, this.y, "mux", this.w, this.h, this.on);
    }
  }

  export class SubcircuitCard extends Component {
    constructor(
      id: string,
      x: number,
      y: number,
      w: number,
      h: number,
      public title: string = "",
      public bg: string = "#ffffff",
      public border: string = "#cbd5e1",
      public headerBg: string | null = "#f8fafc"
    ) {
      super(id, x, y, w, h, title);
    }

    render(): string {
      let out = R(this.x, this.y, this.w, this.h, this.bg, this.border, 3, 1);
      if (this.headerBg) {
        out += R(this.x, this.y, this.w, 18, this.headerBg, this.border, 3, 0.8);
      }
      if (this.title) {
        out += mono(this.x + 8, this.y + 12, this.title, 7, 'font-weight="bold" fill="#0f172a"');
      }
      return out;
    }
  }

  export class DffCell extends Component {
    public bitVal: number;
    public active: boolean;
    constructor(id: string, x: number, y: number, w: number = 20, h: number = 22, bitVal: number = 0, active: boolean = false) {
      super(id, x, y, w, h);
      this.bitVal = bitVal;
      this.active = active;
      this.addPin("d", 0, 6, "L");
      this.addPin("clk", 0, h - 6, "L");
      this.addPin("q", w, h / 2, "R");
    }
    render(): string {
      let out = R(this.x, this.y, this.w, this.h, this.bitVal ? "#dcfce7" : "#ffffff", this.bitVal ? "#16a34a" : (this.active ? "#86efac" : "#cbd5e1"), 2, 1.0);
      out += mono(this.x + 3, this.y + 7, "d", 4.2, 'fill="#0284c7" font-weight="bold"');
      out += mono(this.x + this.w - 3, this.y + this.h / 2 + 1.5, "q", 4.2, 'text-anchor="end" fill="#15803d" font-weight="bold"');
      out += P(`M${this.x} ${this.y + this.h - 8}L${this.x + 3} ${this.y + this.h - 6}L${this.x} ${this.y + this.h - 4}`, this.active ? "#0284c7" : "#94a3b8", 1.0);
      out += mono(this.x + this.w / 2 - 1, this.y + this.h / 2 + 2, String(this.bitVal), 7.5, 'text-anchor="middle" font-weight="bold" fill="' + (this.bitVal ? "#15803d" : "#64748b") + '"');
      return out;
    }
  }

  export class TriStateBuffer extends Component {
    public on: boolean;
    public enDir: "T" | "B";
    constructor(id: string, x: number, y: number, w: number = 8, h: number = 8, on: boolean = false, enDir: "T" | "B" = "B") {
      super(id, x, y, w, h);
      this.on = on;
      this.enDir = enDir;
      this.addPin("in", 0, h / 2, "L");
      this.addPin("en", w * 0.5, enDir === "T" ? h * 0.25 : h * 0.75, enDir);
      this.addPin("out", w, h / 2, "R");
    }
    render(): string {
      const col = this.on ? "#16a34a" : "#64748b";
      let out = tinyGate(this.x, this.y, "buf", this.w, this.h, this.on);
      const enY = this.enDir === "T" ? this.y + this.h * 0.25 : this.y + this.h * 0.75;
      const stubY = this.enDir === "T" ? this.y - 2 : this.y + this.h + 2;
      out += P(`M${this.x + this.w * 0.5} ${stubY}V${enY}`, col, 1.2);
      return out;
    }
  }

  export class PortBox extends Component {
    public pinsList: Array<{
      id: string;
      ry: number;
      label: string;
      color?: string;
      isExternal?: boolean;
      busWidth?: number;
    }>;

    constructor(
      id: string,
      x: number,
      y: number,
      w: number,
      h: number,
      public title: string,
      public side: "left" | "right" = "left",
      public boxType: "input" | "output" | "bidirectional" = "input",
      public headerBg: string = "#f1f5f9",
      public borderColor: string = "#cbd5e1",
      public badge: string = ""
    ) {
      super(id, x, y, w, h, title);
      this.pinsList = [];
    }

    addPortPin(
      id: string,
      ry: number,
      label: string,
      isExternal: boolean = false,
      color: string = "#0d9488",
      busWidth: number = 1
    ): IPin {
      const rx = this.side === "left" ? (isExternal ? 0 : this.w) : (isExternal ? this.w : 0);
      const dir: PinDirection = this.side === "left" ? "L" : "R";
      const pin = this.addPin(id, rx, ry, dir, label, busWidth);
      this.pinsList.push({ id, label, color, isExternal, ry, busWidth });
      return pin;
    }

    getPin(id: string) {
      return this.pin(id);
    }

    render(): string {
      const isOut = this.boxType === "output";
      const bg = "#ffffff";
      const bdr = this.borderColor || (isOut ? "#86efac" : "#cbd5e1");
      const hdr = this.headerBg || (isOut ? "#ecfdf5" : "#f1f5f9");

      let out = R(this.x, this.y, this.w, this.h, bg, bdr, 3, 1.2);
      // Header banner (13px high for clean pin spacing)
      out += R(this.x, this.y, this.w, 13, hdr, bdr, 2, 0.8);
      out += mono(this.x + 6, this.y + 9.5, this.title, 5.2, `font-weight="bold" fill="${isOut ? '#15803d' : '#0f172a'}"`);
      if (this.badge) {
        out += mono(this.x + this.w - 6, this.y + 9.5, this.badge, 4.6, `text-anchor="end" font-weight="bold" fill="${isOut ? '#059669' : '#64748b'}"`);
      }

      this.pinsList.forEach((p) => {
        const py = this.y + p.ry;
        const col = p.color || (isOut ? "#059669" : "#7c3aed");

        if (this.side === "left") {
          // Left-side PortBox (outer edge is LEFT x, inner edge is RIGHT x + w)
          if (p.isExternal) {
            // Prominent copper contact pad on left perimeter
            out += R(this.x - 4, py - 5, 8, 10, "#fed7aa", "#c2410c", 2, 1.0);
            out += dot(this.x, py, col, 2.0);
            out += mono(this.x + 8, py + 3, p.label, 5.2, `font-weight="bold" fill="${col}"`);
          } else {
            // Internal signal line exiting to the right
            out += mono(this.x + 6, py + 3, p.label, 5.0, `font-weight="bold" fill="#334155"`);
            out += mono(this.x + this.w - 12, py + 3, "▶", 4.5, `fill="${col}"`);
            out += dot(this.x + this.w, py, col, 1.6);
            out += P(`M${this.x + this.w - 4} ${py}H${this.x + this.w}`, col, 1.2);
          }
        } else {
          // Right-side PortBox (outer edge is RIGHT x + w, inner edge is LEFT x)
          if (p.isExternal) {
            // Prominent copper contact pad on right perimeter
            out += R(this.x + this.w - 4, py - 5, 8, 10, isOut ? "#dcfce7" : "#fed7aa", isOut ? "#15803d" : "#c2410c", 2, 1.0);
            out += dot(this.x + this.w, py, col, 2.0);
            out += mono(this.x + this.w - 8, py + 3, p.label, 5.2, `text-anchor="end" font-weight="bold" fill="${col}"`);
          } else {
            // Internal signal line entering/exiting from the left
            out += dot(this.x, py, col, 1.6);
            out += P(`M${this.x} ${py}H${this.x + 4}`, col, 1.2);
            const arrow = isOut ? "▶" : "◀";
            out += mono(this.x + 7, py + 3, arrow, 4.5, `fill="${col}"`);
            out += mono(this.x + 14, py + 3, p.label, 5.0, `font-weight="bold" fill="#334155"`);
          }
        }
      });

      return out;
    }
  }

  export class SchematicCanvas {
    public backgrounds: string[] = [];
    public buses: string[] = [];
    public components: IComponent[] = [];
    public wires: string[] = [];
    public dots: string[] = [];
    public labels: string[] = [];

    addBackground(svg: string): this {
      this.backgrounds.push(svg);
      return this;
    }

    addBus(svg: string): this {
      this.buses.push(svg);
      return this;
    }

    addWire(svg: string): this {
      this.wires.push(svg);
      return this;
    }

    addComponent(c: IComponent): this {
      this.components.push(c);
      return this;
    }

    addDot(x: number, y: number, color: string = "#94a3b8", r: number = 1.6): this {
      this.dots.push(dot(x, y, color, r));
      return this;
    }

    addLabel(x: number, y: number, text: string | number, size: number = 6, opt: string = ""): this {
      this.labels.push(mono(x, y, text, size, opt));
      return this;
    }

    render(): string {
      // Guaranteed CAD Layer Order:
      // 1. Backgrounds & Subcircuit cards
      // 2. Continuous data buses & wordlines
      // 3. Components (Gates, Latches, Buffers)
      // 4. Tap wires
      // 5. Solder dots (exact intersections)
      // 6. Overlaid text & badges
      return (
        this.backgrounds.join("") +
        this.buses.join("") +
        this.components.map((c) => c.render()).join("") +
        this.wires.join("") +
        this.dots.join("") +
        this.labels.join("")
      );
    }
  }

  export class AutoRouter {
    public paths: string[] = [];
    public dots: string[] = [];
    public slashes: string[] = [];
    public labels: string[] = [];

    route(p1: RoutePoint, p2: RoutePoint, opt: RouteOptions = {}): this {
      const c = opt.color || paths.data;
      const w = opt.width || 1.0;
      let d = "";

      if (opt.waypoints && opt.waypoints.length > 0) {
        d = `M${p1.x} ${p1.y}`;
        for (const pt of opt.waypoints) {
          if (Array.isArray(pt)) d += ` L${pt[0]} ${pt[1]}`;
          else if (typeof pt === "object" && pt.x !== undefined) d += ` L${pt.x} ${pt.y}`;
        }
        d += ` L${p2.x} ${p2.y}`;
      } else if (p1.y === p2.y) {
        d = `M${p1.x} ${p1.y}H${p2.x}`;
      } else if (p1.x === p2.x) {
        d = `M${p1.x} ${p1.y}V${p2.y}`;
      } else if (opt.viaX !== undefined) {
        d = `M${p1.x} ${p1.y}H${opt.viaX}V${p2.y}H${p2.x}`;
      } else if (opt.viaY !== undefined) {
        d = `M${p1.x} ${p1.y}V${opt.viaY}H${p2.x}V${p2.y}`;
      } else if (p1.dir === "R" && p2.dir === "L") {
        const midX = opt.midX || (p1.x + p2.x) / 2;
        d = `M${p1.x} ${p1.y}H${midX}V${p2.y}H${p2.x}`;
      } else if ((p1.dir === "B" || p1.dir === "T") && p2.dir === "L") {
        d = `M${p1.x} ${p1.y}V${p2.y}H${p2.x}`;
      } else if (p1.dir === "R" && (p2.dir === "T" || p2.dir === "B")) {
        d = `M${p1.x} ${p1.y}H${p2.x}V${p2.y}`;
      } else {
        d = `M${p1.x} ${p1.y}H${p2.x}V${p2.y}`;
      }

      this.paths.push(P(d, c, w));
      if (opt.busSlash) {
        const sx = opt.slashX !== undefined ? opt.slashX : (p1.x + p2.x) / 2;
        const sy = opt.slashY !== undefined ? opt.slashY : (p1.y + p2.y) / 2;
        this.slashes.push(busSlash(sx, sy, opt.busSlash, c));
      }
      return this;
    }

    branch(from: RoutePoint | [number, number], to: RoutePoint, opt: BranchOptions = {}): this {
      const c = opt.color || paths.data;
      const fromX = Array.isArray(from) ? from[0] : from.x;
      const fromY = Array.isArray(from) ? from[1] : from.y;

      if (opt.dot !== false) {
        this.dots.push(dot(fromX, fromY, c, opt.dotRadius || 1.6));
      }

      const startPin: RoutePoint = { x: fromX, y: fromY, dir: opt.dir || "B" };
      return this.route(startPin, to, opt);
    }

    addDot(x: number, y: number, color: string = paths.data, r: number = 1.8): this {
      this.dots.push(dot(x, y, color, r));
      return this;
    }

    addSlash(x: number, y: number, width: string = "4", color: string = paths.data): this {
      this.slashes.push(busSlash(x, y, width, color));
      return this;
    }

    addLabel(x: number, y: number, text: string | number, size: number = 5, opt: string = ""): this {
      this.labels.push(mono(x, y, text, size, opt));
      return this;
    }

    render(): string {
      return this.paths.join("") + this.dots.join("") + this.slashes.join("") + this.labels.join("");
    }
  }
}
