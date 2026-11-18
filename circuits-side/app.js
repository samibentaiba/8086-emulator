(() => {
  "use strict";
  const $ = (id) => document.getElementById(id),
    { N, info, W, H } = board;
  const icons = {
    compass:
      '<circle cx="12" cy="12" r="9"/><path d="m16 8-2.5 5.5L8 16l2.5-5.5z"/>',
    cards:
      '<rect x="4" y="6" width="14" height="14" rx="2"/><path d="M8 3h11a2 2 0 0 1 2 2v11"/>',
    help: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 4.3 1.8c-1.2.9-1.8 1.1-1.8 3"/><path d="M12 17h.01"/>',
    step: '<path d="m6 5 10 7-10 7zM18 5v14"/>',
    play: '<path d="m7 5 11 7-11 7z" fill="currentColor" stroke="none"/>',
    pause: '<path d="M8 5v14M16 5v14" stroke-width="4"/>',
    circuit:
      '<rect x="3" y="4" width="7" height="6" rx="1"/><rect x="14" y="14" width="7" height="6" rx="1"/><path d="M10 7h7v7M6 10v7h8"/>',
    list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.1M3 12h.1M3 18h.1"/>',
    chev: '<path d="m6 9 6 6 6-6"/>',
    expand: '<path d="M4 10V4h6m4 0h6v6m0 4v6h-6m-4 0H4v-6"/>',
    fit: '<path d="M3 9V3h6m6 0h6v6m0 6v6h-6m-6 0H3v-6"/><rect x="7" y="7" width="10" height="10" rx="1"/>',
    inspect:
      '<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="2.5" fill="#fffefa"/><circle cx="15" cy="17" r="2.5" fill="#fffefa"/>',
    mouse:
      '<rect x="6" y="2" width="12" height="20" rx="6"/><path d="M12 5v4"/>',
    wave: '<path d="M1 16h5V7h6v9h6V7h5"/>',
    reset: '<path d="M3 9a9 9 0 1 1 1 9M3 4v6h6"/>',
    zoomin:
      '<circle cx="10" cy="10" r="6.5"/><path d="m15 15 6 6M10 7v6M7 10h6"/>',
  };
  const icon = (n) =>
    `<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">${icons[n] || ""}</svg>`;
  document
    .querySelectorAll("[data-icon]")
    .forEach((n) => (n.outerHTML = icon(n.dataset.icon)));
  const S = {
    sel: "alu",
    scale: 1,
    cx: W / 2,
    cy: H / 2,
    bit: 0,
    mode: "explore",
    freq: 1,
    timer: 0,
    table: false,
    q: 0,
    answer: null,
    score: 0,
    finished: false,
  };
  const canvas = $("canvas"),
    map = $("map"),
    world = $("world");
  function view() {
    const w = canvas.clientWidth || 800,
      h = canvas.clientHeight || 490;
    const fit = Math.max(0.07, Math.min((w - 29) / W, (h - 74) / H)),
      px = fit * S.scale;
    return { w, h, fit, px, vw: w / px, vh: h / px };
  }
  function camera() {
    const v = view();
    updateMini();
    S.cx = Math.min(W + v.vw * 0.16, Math.max(-v.vw * 0.16, S.cx));
    S.cy = Math.min(board.height + v.vh * 0.16, Math.max(-v.vh * 0.16, S.cy));
    map.setAttribute(
      "viewBox",
      `${S.cx - v.vw / 2} ${S.cy - v.vh / 2} ${v.vw} ${v.vh}`,
    );
    $("zoom").textContent = Math.round(S.scale * 100) + "%";
    $("minus").disabled = S.scale <= 0.68;
    $("plus").disabled = S.scale >= 27;
    $("level").textContent =
      S.scale >= 3
        ? "Circuit detail"
        : S.scale >= 1.48
          ? "Block level"
          : "Architecture";
    $("crumbpart").textContent =
      S.scale >= 1.48
        ? " / " + N[S.sel][5] + " / " + info[S.sel][0]
        : " / Intel 8086";
    const m = $("miniview"),
      l = Math.max(0, S.cx - v.vw / 2),
      t = Math.max(0, S.cy - v.vh / 2);
    m.setAttribute("x", l);
    m.setAttribute("y", t);
    m.setAttribute("width", Math.max(0, Math.min(W, S.cx + v.vw / 2) - l));
    m.setAttribute(
      "height",
      Math.max(0, Math.min(board.height, S.cy + v.vh / 2) - t),
    );
  }
  function paint() {
    S.cy = board.reflow(S.scale, S.cy);
    world.innerHTML = board.render(S.scale, S.sel, S.bit);
    camera();
  }
  function coords(clientX, clientY) {
    const r = canvas.getBoundingClientRect(),
      v = view();
    return [
      S.cx + (clientX - r.left - v.w / 2) / v.px,
      S.cy + (clientY - r.top - v.h / 2) / v.px,
    ];
  }
  function zoom(k, x, y) {
    const anchor = x == null ? [S.cx, S.cy] : coords(x, y),
      old = S.scale;
    S.scale = Math.max(0.68, Math.min(27, S.scale * k));
    S.cy = board.reflow(S.scale, S.cy);
    if (old >= 3 !== S.scale >= 3) {
      anchor[1] = board.Y(board.unmap(anchor[1], old >= 3));
    }
    S.cx = anchor[0] - ((anchor[0] - S.cx) * old) / S.scale;
    S.cy = anchor[1] - ((anchor[1] - S.cy) * old) / S.scale;
    paint();
  }
  function fit() {
    S.scale = 1;
    board.reflow(1, S.cy);
    S.cx = W / 2;
    S.cy = H / 2;
    paint();
  }
  function focus(id, deep = true) {
    if (!N[id]) return;
    S.sel = id;
    board.reflow(deep ? 3.3 : 1.52, S.cy);
    const [x, y, w, h] = N[id],
      v = view();
    S.cx = x + w / 2;
    S.cy = y + h / 2;
    S.scale = Math.min(
      24,
      Math.max(
        deep ? 3.3 : 1.52,
        Math.min((v.w - 50) / (v.fit * w), (v.h - 94) / (v.fit * h)) *
          (deep ? 0.91 : 0.65),
      ),
    );
    closeMenu();
    paint();
    inspector();
  }
  function select(id) {
    S.sel = id;
    paint();
    inspector();
  }
  const fields = (a) =>
    a
      .map(
        ([k, v]) =>
          `<div class="sigrow"><span>${k}</span><strong>${v}</strong></div>`,
      )
      .join("");
  const bval = (v) => `<span class="bit ${v ? "high" : ""}">${v}</span>`;
  const section = (title, body, right = "") =>
    `<section class="ins-sect"><div class="sec-head"><h3>${title}</h3>${right}</div>${body}</section>`;
  function escapeHTML(value){return String(value).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}
  function inspector() {
    if (S.mode === "revise") {
      quizUI();
      return;
    }
    const id = S.sel,
      s = cpu.s,
      [name, desc, formula] = info[id],
      gate = ["alu", "dec", "seq"].includes(id);
    $("inspectorTitle").textContent = "Inspector";
    let h = `<span class="section-label">${{ EU: "EXECUTION UNIT", BIU: "BUS INTERFACE UNIT", CU: "CONTROL UNIT" }[N[id][5]]}</span><h3 class="ins-title">${name}</h3><p class="ins-copy">${desc}</p><button class="inspect-go" data-action="focus">${icon("zoomin")}${gate ? "Inspect gates" : "Focus component"}</button>`;
    if (id === "alu") {
      const q = cpu.calculate().slices[S.bit];
      h += section(
        "Boolean logic",
        `<div class="equation">Cᵢ₊₁ = Gᵢ + Pᵢ·Cᵢ</div><div class="rows">${fields(
          [
            ["Propagate · A ⊕ B", bval(q.P)],
            ["Generate · A · B", bval(q.G)],
            ["Carry in → out", q.C + " → " + q.carry],
            ["Sum · P ⊕ C", bval(q.sum)],
          ],
        )}</div><button class="linkbtn" data-action="truth">${S.table ? "Hide" : "Show"} truth table</button>${S.table ? truth(q) : ""}`,
        `<select class="bitpick" aria-label="Inspect bit" id="bitSelect">${Array.from({ length: 16 }, (_, i) => `<option value="${i}" ${i === S.bit ? "selected" : ""}>Bit ${i}</option>`).join("")}</select>`,
      );
      h += section(
        "From your Boolean circuit",
        '<p class="ins-copy">Let A = Pᵢ, M = Gᵢ and C = Cᵢ. The four product gates feed the two intermediate OR gates and a final OR. Every branch is drawn in the slice.</p><div class="equation compact">X = M + M·C + A·M + A·C + A·M·C</div>' +
          fields([
            ["Upper OR · M + M·C", bval(q.upper)],
            ["Lower OR · AM + AC + AMC", bval(q.lower)],
            ["Reduced · M + A·C", bval(q.carry)],
          ]) +
          '<p class="mini note">Absorption gives M + M·C = M and M + A·M = M. The equivalent carry is Gᵢ + Pᵢ·Cᵢ. The silicon uses a different internal carry implementation.</p>',
      );
    } else if (id === "dec") {
      h += section(
        "Live minterm",
        `<div class="equation">e₃…e₀ = ${cpu.line().toString(2).padStart(4, "0")} → S${cpu.line()}</div>` +
          fields([
            ["Enabled phase", cpu.phaseNames[s.phase]],
            ["Write enable", bval(+cpu.ctrl(6))],
            ["Write equation", cpu.isMem() ? "S₁₄" : "S₆ + S₁₄"],
          ]),
      );
      h += section(
        "Decoded output lines",
        fields(
          cpu.outputs.map((o) => [
            o.key + " · " + o.name,
            bval(+cpu.enables()[o.key]),
          ]),
        ) +
          '<p class="mini note">Each control line is the OR of its tapped minterms. A dot joins that row to the vertical input wire. An unmarked crossing has no connection.</p>',
      );
    } else if (id === "seq") {
      h += section(
        "Sequential logic",
        `<div class="equation">${formula}</div>` +
          fields([
            ["Q₂ Q₁ Q₀", s.phase.toString(2).padStart(3, "0")],
            [
              "Next on falling edge",
              ((s.phase + 1) & 7).toString(2).padStart(3, "0"),
            ],
            [
              "J₀=K₀ / J₁=K₁ / J₂=K₂",
              `1 / ${s.phase & 1} / ${+((s.phase & 3) === 3)}`,
            ],
          ]),
      );
      h += section(
        "Feedback on the same edge",
        '<p class="ins-copy">J = K = 0 holds Q. J = K = 1 toggles Q. Each stage samples the old outputs, so 011 becomes 100 together. The triangle and bubble indicate a falling-edge input.</p>' +
          fields([
            ["Memory page", cpu.isMem() ? s.page : "unused"],
            ["Page toggle condition", cpu.isMem() ? "Q₂ · Q₁ · Q₀" : "—"],
          ]),
      );
    } else if (id === "clk") {
      h += section(
        "Period",
        `<div class="equation">${S.freq} Hz → T = ${1 / S.freq} s</div>` +
          fields([
            ["Clock level", bval(s.clock)],
            ["Falling edges", s.cycles],
            ["Current phase", cpu.phaseNames[s.phase]],
          ]),
      );
    } else {
      const word = (v) => (v == null ? "—" : cpu.hex(v) + "h"),
        byte = (v) => (v == null ? "—" : cpu.hex(v, 2) + "h"),
        phys = (v) => (v == null ? "—" : cpu.hex(v, 5) + "h");

      const props = {
        regs: [
          [
            "AX · AH / AL",
            word(s.ax) +
              " · " +
              cpu.hex(s.ax >>> 8, 2) +
              "/" +
              cpu.hex(s.ax & 255, 2),
          ],
          ["BX", word(s.bx)],
          ["BP / SI", word(s.bp) + " / " + word(s.si)],
        ],
        internal: [
          ["Data width", "16 bits"],
          ["Register write-back", word(cpu.calculate().word)],
        ],
        temps: [
          ["tmpA", word(s.a)],
          ["tmpB", word(s.b)],
          ["tmpC · EA temporary", word(s.c)],
        ],
        aluctl: [
          ["Instruction ALU action", s.op],
          ["Complement operand B", bval(+(s.op === "SUB"))],
        ],
        mux: [
          ["First arithmetic operand", word(cpu.inputs()[0])],
          ["Second arithmetic operand", word(cpu.inputs()[1])],
        ],
        flags: Object.entries(s.flags).map(([k, v]) => [k, (s.undefinedFlags||[]).includes(k)?"?":bval(v)]),
        seg: [
          ["CS", word(s.cs)],
          ["DS", word(s.ds)],
          ["SS", word(s.ss)],
          ["ES", word(s.es)],
        ],
        ip: [
          ["Next BIU fetch IP", word(s.ip)],
          ["Queued ahead", s.queue.length + " bytes"],
        ],
        ind: [
          ["Latched offset", word(s.ind)],
          ["Signed disp8", s.disp ?? "—"],
        ],
        segmux: [
          ["Code fetch", "CS · " + word(s.cs)],
          ["Operand selection", s.selectedSegment || "—"],
          ["Override valid", bval(+(s.prefix === 0x26))],
        ],
        offmux: [
          ["Fetch offset", word(s.ip)],
          ["Data offset", word(s.ind)],
        ],
        adder: [
          ["Next fetch address", phys(cpu.physical(s.cs, s.ip))],
          ["Latched operand address", phys(s.phys)],
        ],
        opr: [
          ["Operand latch", word(s.opr)],
          ["Source address", s.phys==null?"—":phys(s.phys)],
        ],
        memory: [
          ["Last fetched word", word(s.lastWord)],
          ["Operand read address", phys(s.phys)],
          ["OPR", word(s.opr)],
        ],
        ext: [
          ["Address width", "20 bits"],
          ["Data width", "16 bits"],
          ["Example word access", "A0=0 · BHE#=0"],
        ],
        queue: [
          ["Occupancy", s.queue.length + " / 6"],
          [
            "Oldest → newest",
            s.queue.map((v) => cpu.hex(v, 2)).join(" ") || "empty",
          ],
        ],
        loader: [
          ["Queue head", byte(s.queue[0])],
          ["IR", byte(s.ir)],
          ["ModR/M", byte(s.mod)],
          ["Displacement", s.disp ?? "—"],
        ],
        ir: [
          ["Opcode", byte(s.ir)],
          ["ModR/M", byte(s.mod)],
          [
            "mod | reg | r/m",
            s.mod == null
              ? "—"
              : (s.mod >>> 6).toString(2).padStart(2, "0") +
                " | " +
                ((s.mod >>> 3) & 7).toString(2).padStart(3, "0") +
                " | " +
                (s.mod & 7).toString(2).padStart(3, "0"),
          ],
        ],
        prefix: [
          ["Prefix byte", byte(s.prefix)],
          ["Override valid", bval(+(s.prefix === 0x26))],
          ["Default for [BP+SI]", "SS"],
        ],
        pla: [
          ["Opcode input", byte(s.ir)],
          ["Class outputs", "15 lines"],
          ["Prefix recognized", s.prefix === 0x26 ? "26h · ES" : "—"],
        ],
        trom: [
          ["mod + r/m inputs", "2 + 3 bits"],
          [
            "Dispatch context",
            s.mod === 0x42
              ? "BP+SI+disp8"
              : s.mod === 0xd8
                ? "Register form"
                : "—",
          ],
          ["Target width", "13 bits"],
        ],
        engine: [
          ["Opcode entry source", byte(s.ir)],
          ["Return register", "13 bits"],
          ["Flags available", "CF · PF · AF · ZF · SF · OF"],
        ],
        mar: [
          ["Logical block", "9 bits"],
          ["Sequence counter", "4 bits"],
        ],
        rom: [
          ["Physical storage", "512 × 21 bits"],
          ["Total bits", "10,752"],
        ],
        ctl: [
          ["Learning minterm", "S" + cpu.line()],
          ["Enabled action", cpu.phaseName()],
          ["AX write enable", bval(+cpu.enables().W)],
        ],
      };
      h += section(
        "Signal values",
        `<div class="equation">${formula.replace(/</g, "&lt;")}</div>` +
          fields(props[id] || []),
      );
    }
    if (id === "alu")
      h += section(
        "Carry across the word",
        '<div class="slice-map">' +
          cpu
            .calculate()
            .slices.map(
              (v, i) =>
                '<button data-slice="' +
                i +
                '" class="' +
                (i === S.bit ? "chosen" : "") +
                '" title="Inspect bit ' +
                i +
                '">b' +
                i +
                "<b>" +
                v.C +
                "→" +
                v.carry +
                "</b></button>",
            )
            .join("") +
          "</div>",
      );
    h += cpu.isProgram ? section("Executing program",'<div class="equation compact">'+escapeHTML(cpu.s.instruction || "Ready to fetch")+'</div>'+fields([["Architectural IP",cpu.hex(cpu.s.execIP)+"h"],["Next BIU fetch",cpu.hex(cpu.s.ip)+"h"],["Instructions retired",cpu.s.retired]])) : section(
      "Instruction",
      `<select id="instruction" class="control-select" aria-label="Instruction"><option ${cpu.settings.op === "ADD" ? "selected" : ""} value="ADD">01 D8 · ADD AX, BX</option><option ${cpu.settings.op === "SUB" ? "selected" : ""} value="SUB">29 D8 · SUB AX, BX</option><option ${cpu.settings.op === "MEM" ? "selected" : ""} value="MEM">26 03 42 06 · ADD AX, ES:[BP+SI+6]</option></select>
 <div class="word-form"><label>AX <input id="axIn" class="wordinput" maxlength="4" aria-label="Initial AX hexadecimal" value="${cpu.hex(cpu.settings.a)}"></label><label>BX <input id="bxIn" class="wordinput" maxlength="4" aria-label="Initial BX hexadecimal" value="${cpu.hex(cpu.settings.b)}"></label></div><small id="editmsg" class="mini">Hex inputs · edits restart the trace.</small>`,
    );
    if (id === "flags")
      h += section(
        "16-bit FLAGS word",
        '<div class="equation compact">15…12: 1111 · 11 OF · 10 DF · 9 IF · 8 TF · 7 SF · 6 ZF · 5 0 · 4 AF · 3 0 · 2 PF · 1 1 · 0 CF</div><p class="mini note">Original 8086 readback. TF is single-step, IF enables maskable interrupts, and DF chooses string direction. Arithmetic updates the six status flags.</p>',
      );
    if (id === "queue")
      h += section(
        "Byte order",
        '<div class="fifo-strip">' +
          Array.from(
            { length: 6 },
            (_, i) =>
              "<span>" +
              (s.queue[i] == null ? "·" : cpu.hex(s.queue[i], 2)) +
              "</span>",
          ).join("") +
          '</div><p class="mini note">Oldest byte at left. These are logical positions in the queue.</p>',
      );
    const near = [
      ...new Set(
        board.nets
          .filter((n) => n[1] === id || n[2] === id)
          .map((n) => (n[1] === id ? n[2] : n[1]))
          .filter((k) => k !== id),
      ),
    ];
    h += section(
      "Connected to",
      `<div class="unit-focus">${near.map((k) => `<button data-focus="${k}">${N[k][4]}</button>`).join("")}</div>`,
    );
    const connected = board.nets.filter((n) => n[1] === id || n[2] === id);
    h += section(
      "Routed signals",
      "<details><summary>" +
        connected.length +
        " named connections</summary>" +
        connected
          .map(
            (n) =>
              '<div class="wire-note"><b>' +
              n[4] +
              " → " +
              n[5] +
              "</b><span>" +
              n[3] +
              "</span></div>",
          )
          .join("") +
        "</details>",
    );
    $("inspectorBody").innerHTML = h;
  }
  function truth(q) {
    let h =
      '<table class="tt"><thead><tr><th>A</th><th>B*</th><th>Cᵢ</th><th>Σ</th><th>Cout</th></tr></thead><tbody>';
    for (let n = 0; n < 8; n++) {
      let a = n >> 2,
        b = (n >> 1) & 1,
        c = n & 1;
      h += `<tr class="${a === q.A && b === q.B && c === q.C ? "current" : ""}"><td>${a}</td><td>${b}</td><td>${c}</td><td>${a ^ b ^ c}</td><td>${(a & b) | ((a ^ b) & c)}</td></tr>`;
    }
    return (
      h +
      '</tbody></table><small class="mini">B* is complemented for SUB.</small>'
    );
  }
  const questions = [
    [
      "alu",
      "Boolean algebra",
      "If P = 1, G = 0 and Cᵢ = 1, what leaves the carry output?",
      ["0", "1", "It waits for a clock edge"],
      1,
      "G + P·Cᵢ = 0 + 1·1 = 1. A combinational output follows its inputs.",
    ],
    [
      "dec",
      "Combinational logic",
      "With OP = 0 and Q₂Q₁Q₀ = 110, which decoder line is active?",
      ["S3", "S6", "S14"],
      1,
      "0110₂ is 6. S6 joins S14 at the OR gate that enables AX write-back.",
    ],
    [
      "seq",
      "Sequential logic",
      "Before a falling edge Q₂Q₁Q₀ = 011. What state follows?",
      ["010", "100", "111"],
      1,
      "Q0 toggles every edge. With Q0 and Q1 both high, all three stages toggle together.",
    ],
    [
      "clk",
      "Clock frequency",
      "At 2 Hz, how long is one full clock cycle?",
      ["2 seconds", "0.25 seconds", "0.5 seconds"],
      2,
      "The period is 1/f, so 1/2 = 0.5 seconds. There is one falling edge in each complete cycle.",
    ],
    [
      "queue",
      "Instruction fetch",
      "A two-byte word enters an empty queue. The loader consumes the opcode. How many bytes remain?",
      ["0", "1", "2"],
      1,
      "Two enter and one leaves. The ModR/M byte stays at the front of the queue.",
    ],
    [
      "prefix",
      "Segment override",
      "26 03 42 06 uses BP+SI. Which segment supplies the operand base?",
      ["CS", "SS", "ES"],
      2,
      "BP-based addressing defaults to SS. The 26h prefix overrides the operand segment with ES. Code fetch continues to use CS.",
    ],
    [
      "adder",
      "Physical address",
      "ES=3000h and IND=010Ah. Which physical address is read?",
      ["310Ah", "3010Ah", "3000Ah"],
      1,
      "Shift the segment left four places: 30000h + 010Ah = 3010Ah.",
    ],
    [
      "rom",
      "Microcode",
      "What is the width of one physical 8086 microinstruction?",
      ["13 bits", "16 bits", "21 bits"],
      2,
      "The logical micro-address has 13 bits. It selects a 21-bit control word from a 512-word physical store.",
    ],
    [
      "regs",
      "Write-back",
      "The ALU result changes while AX write-enable is low. What happens to AX?",
      [
        "AX immediately copies the result",
        "AX keeps its stored word",
        "AX clears to zero",
      ],
      1,
      "The register holds its word until the clock edge with its write-enable asserted.",
    ],
  ];
  function quizUI() {
    $("inspectorTitle").textContent = "Revision";
    if (S.finished) {
      $("inspectorBody").innerHTML =
        `<span class="section-label">REVISION COMPLETE</span><h3 class="ins-title">${S.score} / ${questions.length} first try</h3><p class="ins-copy">You traced Boolean logic, the decoder, clocked state, timing and register write-back on the CPU.</p><button class="inspect-go" data-action="restartQuiz">Practice again</button>`;
      return;
    }
    let [id, topic, q, choices, correct, exp] = questions[S.q];
    $("inspectorBody").innerHTML =
      `<div class="sec-head"><span class="section-label">${topic.toUpperCase()}</span><span class="mini">${S.q + 1} / ${questions.length}</span></div><h3 class="ins-title" style="font-size:19px">${q}</h3>
 ${choices.map((v, i) => `<button class="choice ${S.answer === i ? (i === correct ? "good" : "bad") : ""}" data-answer="${i}" ${S.answer == null ? "" : "disabled"}>${v}</button>`).join("")}
 ${S.answer == null ? "" : `<div class="feedback"><strong>${S.answer === correct ? "Correct." : "Correct answer · " + choices[correct] + ". "}</strong> ${exp}</div><button class="button primary" data-action="nextQuiz">${S.q === questions.length - 1 ? "Finish revision" : "Next question"}</button>`}
 ${section("On the schematic", `<p class="ins-copy">${info[id][1]}</p><button class="linkbtn" data-focus="${id}">Focus ${info[id][0]} →</button>`)}`;
  }
  function mode(which) {
    pause();
    S.mode = which;
    $("explore").setAttribute("aria-pressed", which === "explore");
    $("revise").setAttribute("aria-pressed", which === "revise");
    if (which === "revise" && !S.finished) focus(questions[S.q][0]);
    else inspector();
  }
  function timing() {
    const s = cpu.s;
    $("edgeLastLabel").textContent = s.cycles
      ? "Last · " + s.last
      : "Before first edge";
    $("edgeLast").textContent = s.lastEvent;
    $("edgeNextLabel").textContent = "Next · " + cpu.phaseName();
    $("edgeNext").textContent = cpu.describe();
    $("cycles").textContent = String(s.cycles).padStart(3, "0");
    $("phaseName").textContent = cpu.phaseNames[s.phase];
    $("period").textContent = "Period " + 1 / S.freq + " s";
    const history = s.history.slice(-32);
    let html = '<path d="M0 20H660M0 48H660" fill="none" stroke="#e1e7da"/>';
    const draw = (v, top, low, c) => {
      if (!history.length)
        return `<path d="M0 ${v === "clk" && s.clock ? top : low}H660" stroke="${c}" fill="none" stroke-dasharray="3 4" />`;
      let d = "",
        step = 660 / 32,
        start = 32 - history.length;
      history.forEach((item, i) => {
        const x = (start + i) * step,
          y = item[v] ? top : low;
        d += (i === 0 ? "M" + x + " " + y : "V" + y) + "H" + (x + step);
      });
      return `<path d="${d}" fill="none" stroke="${c}" stroke-width="2" vector-effect="non-scaling-stroke"/>`;
    };
    $("wave").innerHTML =
      html + draw("clk", 3, 20, "#317a5a") + draw("we", 32, 47, "#8c729c");
  }
  function refresh() {
    $("traceProgram").value = cpu.settings.op;
    paint();
    timing();
    if (
      !$("inspectorBody").contains(document.activeElement) ||
      !["INPUT", "SELECT"].includes(document.activeElement.tagName)
    )
      inspector();
  }
  function pause() {
    if (S.timer) clearInterval(S.timer);
    S.timer = 0;
    $("run").innerHTML = icon("play") + "<span>Run clock</span>";
    $("status").textContent = "Paused";
    $("status").classList.remove("on");
  }
  function run() {
    if (S.timer) {
      pause();
      return;
    }
    S.timer = setInterval(() => {
      Promise.resolve(cpu.half()).then(()=>{refresh();if(program.active && (program.done || program.error))pause()});
    }, 500 / S.freq);
    $("run").innerHTML = icon("pause") + "<span>Pause</span>";
    $("status").textContent = "Running";
    $("status").classList.add("on");
  }
  function setupInputs() {
    const a = $("axIn"),
      b = $("bxIn");
    if (!a || !b) return;
    if (!/^[\da-f]{1,4}$/i.test(a.value) || !/^[\da-f]{1,4}$/i.test(b.value)) {
      $("editmsg").textContent = "Use 1–4 hexadecimal digits (0–9, A–F).";
      return;
    }
    pause();
    cpu.configure(
      parseInt(a.value, 16),
      parseInt(b.value, 16),
      $("instruction").value,
    );
    refresh();
    inspector();
  }
  $("inspectorBody").addEventListener("change", (e) => {
    if (e.target.id === "bitSelect") {
      S.bit = +e.target.value;
      paint();
      inspector();
    } else setupInputs();
  });
  $("inspectorBody").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.target.matches("input")) e.target.blur();
  });
  $("inspectorBody").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.slice != null) {
      S.bit = +b.dataset.slice;
      paint();
      inspector();
      return;
    }
    if (b.dataset.focus) focus(b.dataset.focus);
    if (b.dataset.answer != null && S.answer == null) {
      S.answer = +b.dataset.answer;
      if (S.answer === questions[S.q][4]) S.score++;
      quizUI();
    }
    switch (b.dataset.action) {
      case "focus":
        focus(S.sel);
        break;
      case "truth":
        S.table = !S.table;
        inspector();
        break;
      case "nextQuiz":
        S.q++;
        S.answer = null;
        if (S.q === questions.length) {
          S.finished = true;
          quizUI();
        } else focus(questions[S.q][0]);
        break;
      case "restartQuiz":
        S.q = 0;
        S.score = 0;
        S.answer = null;
        S.finished = false;
        mode("revise");
        break;
    }
  });
  function closeMenu() {
    $("components").hidden = true;
    $("find").setAttribute("aria-expanded", "false");
  }
  $("components").innerHTML = ["EU", "BIU", "CU"]
    .map(
      (unit) =>
        `<div class="menu-unit">${{ EU: "Execution unit", BIU: "Bus interface unit", CU: "Control unit" }[unit]}</div>` +
        Object.entries(N)
          .filter(([, n]) => n[5] === unit)
          .map(
            ([k, n]) =>
              `<button class="menuitem" data-goto="${k}">${n[4]} <span>↗</span></button>`,
          )
          .join(""),
    )
    .join("");
  $("find").onclick = () => {
    const open = $("components").hidden;
    $("components").hidden = !open;
    $("find").setAttribute("aria-expanded", open);
  };
  $("components").onclick = (e) => {
    const b = e.target.closest("[data-goto]");
    if (b) focus(b.dataset.goto);
  };
  document.addEventListener("click", (e) => {
    if (!e.target.closest("#components,#find")) closeMenu();
  });
  $("plus").onclick = () => zoom(1.48);
  $("minus").onclick = () => zoom(1 / 1.48);
  $("fit").onclick = $("home").onclick = fit;
  $("expand").onclick = () => {
    const on = document.querySelector(".board").classList.toggle("max");
    $("expand").setAttribute(
      "aria-label",
      on ? "Restore schematic size" : "Expand schematic",
    );
    camera();
  };
  $("explore").onclick = () => mode("explore");
  $("revise").onclick = () => mode("revise");
  $("traceProgram").onchange = (e) => {
    pause();
    if(e.target.value==="PROGRAM"){window.programUI.open();return}
    cpu.configure(cpu.settings.a, cpu.settings.b, e.target.value);
    refresh();
    inspector();
  };
  $("step").onclick = async () => {
    pause();
    await cpu.step();
    refresh();
  };
  $("run").onclick = run;
  $("reset").onclick = async () => {
    pause();
    await cpu.reset();
    refresh();
  };
  $("freq").onchange = (e) => {
    const was = S.timer;
    pause();
    S.freq = +e.target.value;
    if (was) run();
    timing();
    inspector();
  };
  canvas.addEventListener("keydown", (e) => {
    const node = e.target.closest("[data-node]");
    if (node && ["Enter", " "].includes(e.key)) {
      e.preventDefault();
      e.stopPropagation();
      focus(node.dataset.node);
    }
  });
  canvas.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      zoom(
        Math.exp(
          -Math.sign(e.deltaY) * Math.min(Math.abs(e.deltaY) * 0.0025, 0.33),
        ),
        e.clientX,
        e.clientY,
      );
    },
    { passive: false },
  );
  const pointers = new Map();
  let start = null,
    dragged = false,
    pinch = 0,
    lastTap = { id: null, t: 0 };
  canvas.addEventListener("pointerdown", (e) => {
    if (e.button !== 0) return;
    const node = e.target.closest("[data-node]")?.dataset.node || null;
    canvas.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, [e.clientX, e.clientY]);
    if (pointers.size === 1) {
      start = { x: e.clientX, y: e.clientY, node };
      dragged = false;
      canvas.classList.add("drag");
    } else {
      dragged = true;
      pinch = 0;
    }
  });
  canvas.addEventListener("pointermove", (e) => {
    const old = pointers.get(e.pointerId);
    if (!old) return;
    pointers.set(e.pointerId, [e.clientX, e.clientY]);
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()],
        d = Math.hypot(a[0] - b[0], a[1] - b[1]);
      if (pinch > 0 && d > 0)
        zoom(d / pinch, (a[0] + b[0]) / 2, (a[1] + b[1]) / 2);
      pinch = d;
      return;
    }
    if (!start) return;
    dragged =
      dragged || Math.hypot(e.clientX - start.x, e.clientY - start.y) > 3;
    if (dragged) {
      const p = view().px;
      S.cx -= (e.clientX - old[0]) / p;
      S.cy -= (e.clientY - old[1]) / p;
      camera();
    }
  });
  function release(e, cancel = false) {
    if (!pointers.has(e.pointerId)) return;
    pointers.delete(e.pointerId);
    if (!pointers.size) {
      canvas.classList.remove("drag");
      if (!cancel && !dragged && start?.node) {
        const id = start.node;
        if (lastTap.id === id && performance.now() - lastTap.t < 420) {
          focus(id);
          lastTap.t = 0;
        } else {
          select(id);
          lastTap = { id, t: performance.now() };
        }
      }
      start = null;
      pinch = 0;
    }
  }
  canvas.addEventListener("pointerup", (e) => release(e));
  canvas.addEventListener("pointercancel", (e) => release(e, true));
  document.querySelector(".minimap").onclick = (e) => {
    const el = e.currentTarget.querySelector("svg"),
      m = el.getScreenCTM();
    if (!m) return;
    const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(m.inverse());
    S.cx = p.x;
    S.cy = p.y;
    camera();
  };
  let miniLayout = null;
  function updateMini() {
    const height = board.height;
    if (miniLayout === height) return;
    miniLayout = height;
    const mini = $("mininodes").ownerSVGElement;
    mini.setAttribute("viewBox", "0 0 " + W + " " + height);
    mini.querySelectorAll(".miniunit").forEach((n) => n.remove());
    $("mininodes").innerHTML = Object.values(N)
      .map(
        ([x, y, w, h]) =>
          '<rect x="' +
          x +
          '" y="' +
          y +
          '" width="' +
          w +
          '" height="' +
          h +
          '" rx="3" fill="#adbea4"/>',
      )
      .join("");
  }
  document.addEventListener("keydown", (e) => {
    if (
      $("help").open ||
      e.target.matches("input,select,textarea") ||
      e.ctrlKey ||
      e.metaKey ||
      e.altKey
    )
      return;
    if (e.key === "Escape") {
      closeMenu();
      document.querySelector(".board").classList.remove("max");
      camera();
      return;
    }
    if (e.target.closest("button,a") && [" ", "Enter"].includes(e.key)) return;
    const f = {
      "+": () => zoom(1.35),
      "=": () => zoom(1.35),
      "-": () => zoom(1 / 1.35),
      0: fit,
      " ": run,
      ".": () => $("step").click(),
      ArrowLeft: () => {
        S.cx -= 75 / view().px;
        camera();
      },
      ArrowRight: () => {
        S.cx += 75 / view().px;
        camera();
      },
      ArrowUp: () => {
        S.cy -= 75 / view().px;
        camera();
      },
      ArrowDown: () => {
        S.cy += 75 / view().px;
        camera();
      },
    }[e.key];
    if (f) {
      e.preventDefault();
      f();
    }
  });
  $("helptext").innerHTML =
    '<p><b>Follow a connection.</b> Scroll or pinch to zoom. Drag to pan. Click a component to inspect it, or double-click to center it. Components lists every block in the notebook. Zoom reveals register fields, signal widths, and the gate networks.</p><p><b>Run an instruction.</b> Choose a machine-code example in the inspector. Step advances one falling edge. The edge trace names the values transferred and the next action. Green wires show the upcoming transfer. Use Revise to test yourself on the same circuit.</p><p><b>Read the symbols.</b> A dot joins wires. The clock triangle with a bubble marks a falling-edge input. In Boolean formulas, + is OR, · is AND, ⊕ is XOR and ¬ is NOT.</p><p><b>Hardware and teaching logic.</b> The EU, BIU, and microcode paths follow the 8086 notebook. The ripple adder, JK phase controller and 4-to-16 matrix are functional teaching implementations. Dashed links tie the learning controller to the datapath. A learning edge groups one or more hardware transfers. Register traces take eight learning edges and the memory trace takes sixteen. The selected hertz controls playback; Intel bus T-states and microinstruction timing are separate.</p><p><b>Shortcuts</b> &nbsp;+ / − zoom · 0 fit · arrows pan · Space run/pause · period step.</p><p><a href="https://www.righto.com/2022/11/how-8086-processors-microcode-engine.html" target="_blank" rel="noopener">Microcode engine and translation ROM</a> · <a href="https://www.righto.com/2023/01/inside-8086-processors-instruction.html" target="_blank" rel="noopener">Instruction queue</a> · <a href="https://www.righto.com/2023/02/8086-modrm-addressing.html" target="_blank" rel="noopener">ModR/M addressing</a> · <a href="https://www.inf.pucrs.br/~calazans/undergrad/orgcomp_EC/mat_microproc/intel-8086_family_Users_Manual.pdf" target="_blank" rel="noopener">Intel family manual</a></p>';
  $("guide").onclick = () => {
    pause();
    $("help").showModal();
  };
  $("closeHelp").onclick = $("startLab").onclick = () => $("help").close();
  document.querySelector(".brand").onclick = (e) => {
    e.preventDefault();
    mode("explore");
    fit();
  };
  window.atlasUI={refresh,pause,focus,fit};
  new ResizeObserver(camera).observe(canvas);
  paint();
  inspector();
  timing();
})();
