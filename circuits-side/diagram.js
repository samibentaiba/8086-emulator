/* Gate geometries for the three CPU-linked teaching circuits. */
(() => {
  const paths = {
    data: "#447961",
    address: "#a47a43",
    control: "#887796",
    clock: "#487e78",
    ink: "#2e4034",
    high: "#176342",
    low: "#7d8778",
  };
  const T = (x, y, v, size = 14, opt = "") =>
    `<text x="${x}" y="${y}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="${size}" fill="#28382d" ${opt}>${v}</text>`;
  const mono = (x, y, v, size = 12, opt = "") =>
    T(x, y, v, size, `style="font-family:Consolas,monospace" ${opt}`);
  const R = (x, y, w, h, fill, stroke = "none", r = 4, sw = 1) =>
    `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  const P = (d, c = "#364639", w = 1.5, fill = "none", more = "") =>
    `<path d="${d}" fill="${fill}" stroke="${c}" stroke-width="${w}" stroke-linejoin="round" stroke-linecap="round" ${more}/>`;
  const dot = (x, y, c = "#34483a", r = 2.3) =>
    `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}"/>`;
  const sg = (d, v) => P(d, v ? paths.high : "#778174", v ? 2.2 : 1.45);
  const tinyGate = (x, y, type, w = 22, h = 15, on = false) => {
    const c = on ? "#166745" : "#475343",
      f = on ? "#d0e9b9" : "#fffade";
    let d =
      type === "and"
        ? `M0 0H${w * 0.5}C${w * 1.16} 0 ${w * 1.16} ${h} ${w * 0.5} ${h}H0Z`
        : `M0 0Q${w * 0.54} 0 ${w} ${h / 2}Q${w * 0.55} ${h} 0 ${h}Q${w * 0.32} ${h / 2} 0 0Z`;
    return `<g transform="translate(${x} ${y})">${type === "xor" ? P(`M-3 0Q${w * 0.2} ${h / 2} -3 ${h}`, c, 1.4) : ""}${P(d, c, 1.45, f)}</g>`;
  };
  function adderLogic(s, i) {
    const q = cpu.calculate().slices[i];
    // Same AND/OR network as the supplied Boolean reference. P,G,C are CPU nets.
    let g =
      mono(5, 11, `BIT ${i}  /  ADDER`, 10) + mono(194, 11, `Cin=${q.C}`, 10);
    g += sg("M40 0V21H19V60", q.A) + sg("M182 0V17H37V70", q.B);
    g +=
      dot(19, 28) +
      dot(37, 38) +
      sg("M19 28H58", q.A) +
      sg("M37 38H58", q.B) +
      tinyGate(53, 23, "xor", 25, 20, !!q.P);
    g +=
      sg("M19 60H53", q.A) +
      sg("M37 70H53", q.B) +
      tinyGate(53, 55, "and", 25, 20, !!q.G);
    g +=
      sg("M78 33H92V145", q.P) +
      sg("M78 65H105V161", q.G) +
      sg("M4 179H118V91", q.C);
    g += mono(84, 27, "P", 10) + mono(94, 59, "G", 10) + mono(5, 173, "Cᵢ", 10);
    const row = [
      { y: 43, a: 92, b: 105, v: q.t1 },
      { y: 80, a: 105, b: 118, v: q.t2 },
      { y: 116, a: 92, b: 118, v: q.t3 },
      { y: 151, a: 92, b: 105, v: q.t4 },
    ];
    // Extend the input rails to every tapped gate.
    g += sg("M92 145V155", q.P) + sg("M105 46V65M105 161V162", q.G);
    row.forEach((r, k) => {
      const y = r.y;
      const valA = r.a === 92 ? q.P : q.G,
        valB = r.b === 105 ? q.G : q.C;
      g +=
        sg(`M${r.a} ${y + 3}H137`, valA) +
        dot(r.a, y + 3) +
        sg(`M${r.b} ${y + 11}H137`, valB) +
        dot(r.b, y + 11);
      if (k === 3) g += sg("M118 158H137", q.C) + dot(118, 158);
      g += tinyGate(137, y, "and", 24, 14, !!r.v);
    });
    g +=
      sg("M105 73H174V66H196", q.G) +
      dot(105, 73) +
      sg("M161 87H179V75H196", q.t2) +
      tinyGate(190, 62, "or", 24, 18, !!q.upper);
    g +=
      sg("M161 50H169V115H196", q.t1) +
      sg("M161 123H196", q.t3) +
      sg("M161 158H177V131H196", q.t4) +
      tinyGate(190, 111, "or", 24, 24, !!q.lower);
    g +=
      sg("M214 71H220V93H236", q.upper) +
      sg("M214 123H221V103H236", q.lower) +
      tinyGate(231, 88, "or", 23, 20, !!q.carry);
    g += sg("M254 98H270", q.carry) + mono(217, 143, `Cout=${q.carry}`, 10);
    g +=
      sg("M92 140H83V183H145", q.P) +
      dot(92, 140) +
      sg("M118 171H127V193H145", q.C) +
      dot(118, 171) +
      tinyGate(140, 178, "xor", 27, 20, !!q.sum) +
      sg("M167 188H181", q.sum) +
      mono(185, 192, `Σᵢ=${q.sum}`, 12);
    return g;
  }

  function decoderLogic() {
    const sel = cpu.line(),
      en = cpu.enables(),
      cy = 148;
    let g = R(42, 9, 71, 126, "#fff0b7", "#6f694b", 1, 1.3);
    const qys = [46, 66, 86, 106];
    [cpu.isMem() ? "PAGE" : "OP", "Q₂", "Q₁", "Q₀"].forEach((v, j) => {
      const yy = qys[j];
      g += mono(19, yy - 3, v, 7.5) + sg(`M9 ${yy}H42`, (sel >> (3 - j)) & 1);
    });
    g += T(47, 75, "Decode", 9, 'font-weight="650"');
    const columns = cpu.outputs.map((o, i) => {
      const center = 139 + i * 26;
      return o.terms.map((t, j) => ({
        t,
        x:
          center +
          (j - (o.terms.length - 1) / 2) * (o.terms.length === 2 ? 7 : 2.5),
        center,
      }));
    });
    for (let k = 0; k < 16; k++) {
      const y = 14 + k * 7.7,
        taps = columns.flat().filter((c) => c.t === k);
      g += mono(110, y + 2.2, `S${k}`, 5.7, 'text-anchor="end"');
      g += sg(`M113 ${y}H${Math.max(120, ...taps.map((t) => t.x))}`, sel === k);
      taps.forEach((t) => {
        const ratio = (t.center + 9 - t.x) / 18,
          yy = cy + 2 * 15 * 0.32 * ratio * (1 - ratio);
        g +=
          sg(`M${t.x} ${y}V${yy}`, sel === k) +
          dot(t.x, y, sel === k ? paths.high : "#515c50", 1.15);
      });
    }
    for (let i = 0; i < cpu.outputs.length; i++) {
      const x = 139 + i * 26,
        k = cpu.outputs[i].key;
      g +=
        `<g transform="translate(${x + 9} ${cy}) rotate(90)">${tinyGate(0, 0, "or", 15, 18, en[k])}</g>` +
        sg(`M${x} 163V172l6 6`, en[k]) +
        mono(x - 3, 171, k, 7, 'text-anchor="end"');
    }
    g +=
      P("M145 178H380", paths.control, 2.4) +
      mono(177, 191, "ENABLE BUS [" + (cpu.outputs.length - 1) + ":0]", 7.2);
    return g;
  }
  function sequencerLogic() {
    const s = cpu.s,
      ph = s.phase,
      memory = cpu.isMem();
    let g =
      sg(memory ? "M5 22H350" : "M5 22H240", s.clock) + mono(4, 15, "CLK", 9);
    const q = [ph & 1, (ph >> 1) & 1, (ph >> 2) & 1, s.page];
    g += mono(0, 64, "1", 9) + sg("M5 70H30M12 70V106H30", 1) + dot(12, 70);
    g += sg("M89 70H140M126 70V106H140", q[0]) + dot(126, 70);
    g += sg("M103 70V148H181", q[0]) + dot(103, 70);
    g += sg("M199 70H218V174H168V158H181", q[1]);
    g +=
      tinyGate(181, 142, "and", 24, 22, !!(q[0] & q[1])) +
      sg("M205 153H236V70H250M236 106H250", q[0] & q[1]) +
      dot(236, 106);
    if (memory) {
      g += sg("M224 153V135H300", q[0] & q[1]) + dot(224, 153);
      g += sg("M309 70H330V169H288V145H300", q[2]);
      g +=
        tinyGate(300, 130, "and", 23, 20, ph === 7) +
        sg("M323 140H342V70H360M342 106H360", ph === 7) +
        dot(342, 106);
    }
    for (let i = 0; i < (memory ? 4 : 3); i++) {
      const x = 30 + i * 110;
      g +=
        R(x, 54, 59, 68, "#fffdf1", "#485545", 1, 1.3) +
        mono(x + 5, 73, "J", 9) +
        mono(x + 5, 109, "K", 9) +
        mono(x + 53, 73, "Q", 9, 'text-anchor="end"') +
        mono(x + 30, 94, `FF-${"ABCP"[i]}`, 10, 'text-anchor="middle"') +
        mono(x + 35, 115, `Q=${q[i]}`, 7.7, 'text-anchor="middle"');
      g +=
        P(`M${x} 83l6 5-6 5`, "#51584a", 1.2) +
        `<circle cx="${x - 3}" cy="88" r="2.8" fill="#fffdf0" stroke="#414b3e"/>` +
        sg(`M${x - 10} 22V88H${x - 6}`, s.clock) +
        dot(x - 10, 22);
      const tap = x + 66;
      g +=
        sg(`M${x + 59} 70H${tap}V182l8 8`, q[i]) +
        dot(tap, 70) +
        mono(tap - 4, 182, `Q${i}`, 8, 'text-anchor="end"');
    }
    g +=
      P(memory ? "M104 190H451" : "M104 190H337", paths.control, 2.4) +
      mono(195, 202, memory ? "PAGE + PHASE [2:0]" : "PHASE [2:0]", 8);
    return g;
  }

  window.logicDraw = {
    adderLogic,
    decoderLogic,
    sequencerLogic,
    T,
    mono,
    R,
    P,
    dot,
    paths,
    tinyGate,
  };
})();
