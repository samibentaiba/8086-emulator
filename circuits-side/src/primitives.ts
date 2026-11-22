/// <reference path="types.ts" />
/**
 * Intel 8086 Circuit Atlas - SVG Drawing Primitives & Helpers
 */
namespace LogicDraw {
  export const paths = {
    data: "#1d7853",
    address: "#9e6524",
    control: "#765c8a",
    clock: "#2b7f8c",
    ink: "#223326",
    high: "#157d4c",
    low: "#7b897e",
    chip: "#253328",
    bus: "#156b46",
    power: "#b91c1c",
    gnd: "#334155",
  };

  export const T = (x: number, y: number, v: string | number, size: number = 12, opt: string = ""): string =>
    `<text x="${x}" y="${y}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="${size}" fill="#223326" ${opt}>${v}</text>`;
  
  export const mono = (x: number, y: number, v: string | number, size: number = 10, opt: string = ""): string =>
    T(x, y, v, size, `style="font-family:Consolas,'Liberation Mono',monospace" ${opt}`);
  
  export const R = (x: number, y: number, w: number, h: number, fill: string, stroke: string = "none", r: number = 3, sw: number = 1): string =>
    `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  
  export const P = (d: string, c: string = "#364639", w: number = 1.5, fill: string = "none", more: string = ""): string =>
    `<path d="${d}" fill="${fill}" stroke="${c}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round" ${more}/>`;
  
  export const dot = (x: number, y: number, c: string = "#34483a", r: number = 2.2): string =>
    `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}"/>`;
  
  export const sg = (d: string, v: boolean | number): string => P(d, v ? paths.high : "#778174", v ? 2.0 : 1.3);

  export const tinyGate = (x: number, y: number, type: string, w: number = 22, h: number = 15, on: boolean = false): string => {
    const c = on ? "#166745" : "#475343",
      f = on ? "#d0e9b9" : "#fffade";
    let d = "";
    if (type === "and") {
      d = `M0 0H${w * 0.5}C${w * 1.16} 0 ${w * 1.16} ${h} ${w * 0.5} ${h}H0Z`;
    } else if (type === "or" || type === "xor") {
      d = `M0 0Q${w * 0.54} 0 ${w} ${h / 2}Q${w * 0.55} ${h} 0 ${h}Q${w * 0.32} ${h / 2} 0 0Z`;
    } else if (type === "nand") {
      d = `M0 0H${w * 0.45}C${w * 1.0} 0 ${w * 1.0} ${h} ${w * 0.45} ${h}H0Z`;
    } else if (type === "nor") {
      d = `M0 0Q${w * 0.5} 0 ${w * 0.88} ${h / 2}Q${w * 0.5} ${h} 0 ${h}Q${w * 0.28} ${h / 2} 0 0Z`;
    } else if (type === "not" || type === "inv") {
      d = `M0 0L${w * 0.78} ${h / 2}L0 ${h}Z`;
    } else if (type === "buf") {
      d = `M0 0L${w} ${h / 2}L0 ${h}Z`;
    } else if (type === "mux") {
      d = `M0 0H${w}L${w * 0.75} ${h}H${w * 0.25}Z`;
    } else {
      d = `M0 0H${w}V${h}H0Z`;
    }
    let extra = "";
    if (type === "xor") {
      extra = P(`M-3 0Q${w * 0.2} ${h / 2} -3 ${h}`, c, 1.4);
    } else if (type === "nand" || type === "nor" || type === "not" || type === "inv") {
      const bx = type === "not" || type === "inv" ? w * 0.78 + 2.5 : w - 2;
      extra = `<circle cx="${bx}" cy="${h / 2}" r="2.2" fill="${f}" stroke="${c}" stroke-width="1.3"/>`;
    }
    return `<g transform="translate(${x} ${y})">${extra}${P(d, c, 1.4, f)}</g>`;
  };

  export const dff = (x: number, y: number, w: number = 34, h: number = 38, clk: any = 0, d: any = 0, q: any = 0, lbl: string = "DFF"): string => {
    let out = R(x, y, w, h, q ? "#e7f6ea" : "#fffef4", q ? "#156b46" : "#6a7b70", 2, 1.3);
    out += P(`M${x} ${y + h / 2 - 4} L${x + 5} ${y + h / 2} L${x} ${y + h / 2 + 4}`, "#475569", 1.2);
    out += mono(x + 4, y + 10, "D", 7, 'fill="#334155"');
    out += mono(x + w - 4, y + 10, "Q", 7, 'text-anchor="end" font-weight="bold" fill="' + (q ? "#156b46" : "#334155") + '"');
    out += mono(x + w - 4, y + h - 6, "Q̅", 7, 'text-anchor="end" fill="#64748b"');
    out += mono(x + w / 2, y + h / 2 + 2, lbl, 6.5, 'text-anchor="middle" fill="#475569" font-weight="bold"');
    return out;
  };

  export const dlatch = (x: number, y: number, w: number = 30, h: number = 34, le: any = 0, q: any = 0, lbl: string = "LAT"): string => {
    let out = R(x, y, w, h, q ? "#e7f6ea" : "#fbfdf9", q ? "#156b46" : "#6a7b70", 2, 1.2);
    out += mono(x + 4, y + 11, "D", 7, 'fill="#334155"');
    out += mono(x + 4, y + h - 6, "LE", 6.5, 'fill="' + (le ? "#156b46" : "#64748b") + '" font-weight="bold"');
    out += mono(x + w - 4, y + 11, "Q", 7, 'text-anchor="end" font-weight="bold" fill="' + (q ? "#156b46" : "#334155") + '"');
    out += mono(x + w / 2, y + h / 2, lbl, 6.5, 'text-anchor="middle" fill="#64748b"');
    return out;
  };

  export const gnd = (x: number, y: number): string =>
    P(`M${x} ${y}V${y + 6}M${x - 7} ${y + 6}H${x + 7}M${x - 4} ${y + 9}H${x + 4}M${x - 2} ${y + 12}H${x + 2}`, "#334155", 1.4);

  export const vcc = (x: number, y: number, lbl: string = "+5V"): string =>
    P(`M${x} ${y}V${y - 6}M${x - 6} ${y - 6}H${x + 6}`, "#b91c1c", 1.4) +
    mono(x, y - 8, lbl, 6.5, 'text-anchor="middle" fill="#b91c1c" font-weight="bold"');

  export const busSlash = (x: number, y: number, width: string = "16", color: string = paths.data): string =>
    P(`M${x - 4} ${y + 4}L${x + 4} ${y - 4}`, color, 1.5) +
    mono(x + 3, y - 4, `/${width}`, 6.5, `fill="${color}" font-weight="bold"`);

  export const nmos = (x: number, y: number, on: boolean = false, lbl: string = ""): string => {
    let out = `<g transform="translate(${x} ${y})">`;
    out += P("M0 12H8", on ? paths.high : "#64748b", 1.3);
    out += P("M8 2V22", on ? paths.high : "#64748b", 1.5);
    out += P("M12 2V22", "#334155", 1.5);
    out += P("M12 6H20V0", "#334155", 1.3);
    out += P("M12 18H20V24", "#334155", 1.3);
    if (lbl) out += mono(22, 14, lbl, 6, 'fill="#475569"');
    out += "</g>";
    return out;
  };

  export const pmos = (x: number, y: number, on: boolean = false, lbl: string = ""): string => {
    let out = `<g transform="translate(${x} ${y})">`;
    out += `<circle cx="5" cy="12" r="2.5" fill="#ffffff" stroke="${on ? paths.high : "#64748b"}" stroke-width="1.3"/>`;
    out += P("M0 12H2.5", on ? paths.high : "#64748b", 1.3);
    out += P("M8 2V22", on ? paths.high : "#64748b", 1.5);
    out += P("M12 2V22", "#334155", 1.5);
    out += P("M12 6H20V0", "#334155", 1.3);
    out += P("M12 18H20V24", "#334155", 1.3);
    if (lbl) out += mono(22, 14, lbl, 6, 'fill="#475569"');
    out += "</g>";
    return out;
  };

  export const hex = (v: any, n: number = 4): string => (v != null ? (v >>> 0).toString(16).toUpperCase().padStart(n, "0") : "—");
  export const bin = (v: any, n: number = 8): string => (v != null ? (v >>> 0).toString(2).padStart(n, "0") : "—");
}
