/* Functional 8086 transfers on a clock that advances one learning step per
   falling edge. The two schedules are teaching control words, not Intel ROM data. */
(() => {
  const hex = (v, n = 4) =>
    (v >>> 0).toString(16).toUpperCase().padStart(n, "0");
  const H = (v, n = 4) => hex(v, n) + "h";
  const flagNames = ["CF", "PF", "AF", "ZF", "SF", "OF"];
  const programs = {
    ADD: [0x01, 0xd8],
    SUB: [0x29, 0xd8],
    MEM: [0x26, 0x03, 0x42, 0x06],
  };
  const regNames = [
    "Fetch word",
    "Load opcode",
    "Load ModR/M",
    "Latch AX",
    "Latch BX",
    "Evaluate ALU",
    "Write result",
    "Retire",
  ];
  const memNames = [
    "Fetch prefix and opcode",
    "Latch ES prefix",
    "Load opcode",
    "Fetch addressing bytes",
    "Load ModR/M",
    "Read displacement",
    "Add BP and SI",
    "Load indirect offset",
    "Select ES and IND",
    "Form physical address",
    "Read operand word",
    "Latch AX",
    "Latch OPR",
    "Evaluate ALU",
    "Write result",
    "Retire",
  ];
  const mk = (key, name, terms) => ({ key, name, terms });
  const regOutputs = [
    mk("F", "Prefetch if room", [0, 3, 4, 8, 11, 12]),
    mk("IR", "Load opcode", [1, 9]),
    mk("M", "Load ModR/M", [2, 10]),
    mk("A", "Capture tmpA", [3, 11]),
    mk("B", "Capture tmpB", [4, 12]),
    mk("Σ", "Observe sum", [5, 13]),
    mk("W", "Write AX and flags", [6, 14]),
    mk("N", "Retire", [7, 15]),
  ];
  const memOutputs = [
    mk("F", "Prefetch if room", [0, 3]),
    mk("L", "Consume instruction byte", [1, 2, 4, 5]),
    mk("EA", "Form effective offset", [6, 7]),
    mk("D", "Select / address / read", [8, 9, 10]),
    mk("A", "Capture tmpA", [11]),
    mk("B", "Capture tmpB", [12]),
    mk("Σ", "Observe sum", [13]),
    mk("W", "Write AX and flags", [14]),
    mk("N", "Retire", [15]),
  ];
  let initialA = 3,
    initialB = 1,
    program = "ADD",
    s;
  const isMem = () => program === "MEM";
  const index = () => s.phase + (isMem() ? s.page * 8 : 0);
  const phaseName = () => (isMem() ? memNames : regNames)[index()];
  const line = () =>
    isMem() ? index() : ((s.ir === 0x29 ? 1 : 0) << 3) | s.phase;
  const outputs = () => (isMem() ? memOutputs : regOutputs);
  const enables = () =>
    Object.fromEntries(outputs().map((o) => [o.key, o.terms.includes(line())]));
  const physical = (seg, off) => (seg * 16 + off) & 0xfffff;
  function reset() {
    s = {
      ax: initialA,
      bx: initialB,
      a: initialA,
      b: isMem() ? 0 : initialB,
      c: 0,
      cs: 0x1200,
      es: 0x3000,
      ss: 0x2000,
      ds: 0x4000,
      bp: 0x100,
      si: 4,
      ip: 0x100,
      ind: null,
      opr: null,
      phys: null,
      selectedSegment: null,
      disp: null,
      prefix: null,
      ir: null,
      mod: null,
      op: program === "SUB" ? "SUB" : "ADD",
      queue: [],
      phase: 0,
      page: 0,
      cycles: 0,
      clock: 1,
      flags: { CF: 0, PF: 0, AF: 0, ZF: 0, SF: 0, OF: 0 },
      history: [],
      last: "Ready",
      lastEvent: "Clock paused before the first fetch.",
      lastWord: null,
      retired: 0,
    };
  }
  function inputs() {
    if (isMem() && index() === 7) return [s.c, s.b, false];
    return [s.a, s.b, s.op === "SUB"];
  }
  function calculate(a, b, sub) {
    if (a === undefined) [a, b, sub] = inputs();
    if (sub === undefined) sub = s.op === "SUB";
    const slices = [];
    let carry = +sub,
      word = 0;
    for (let i = 0; i < 16; i++) {
      const A = (a >>> i) & 1,
        rawB = (b >>> i) & 1,
        B = rawB ^ +sub,
        P = A ^ B,
        G = A & B,
        C = carry;
      const t1 = P & G,
        t2 = G & C,
        t3 = P & C,
        t4 = P & G & C,
        upper = G | t2,
        lower = t1 | t3 | t4;
      carry = upper | lower;
      const sum = P ^ C;
      word |= sum << i;
      slices.push({
        A,
        rawB,
        B,
        P,
        G,
        C,
        t1,
        t2,
        t3,
        t4,
        upper,
        lower,
        carry,
        sum,
      });
    }
    const flags = {
      CF: carry ^ +sub,
      PF: +((word & 255).toString(2).replaceAll("0", "").length % 2 === 0),
      AF: slices[3].carry ^ +sub,
      ZF: +(word === 0),
      SF: word >>> 15,
      OF: slices[15].C ^ carry,
    };
    return { word, flags, slices };
  }
  const memoryByte = (address) => {
    if (address === 0x3010a) return 0x34;
    if (address === 0x3010b) return 0x12;
    const codeOffset = address - s.cs * 16;
    return programs[program][
      ((codeOffset - 0x100) & 0xffff) % programs[program].length
    ];
  };
  function fetchPair() {
    if (s.queue.length > 4) return;
    const addr = physical(s.cs, s.ip),
      lo = memoryByte(addr),
      hi = memoryByte((addr + 1) & 0xfffff);
    s.lastWord = hi * 256 + lo;
    s.queue.push(lo, hi);
    s.ip = (s.ip + 2) & 65535;
  }
  const fetchNote = () =>
    s.queue.length > 4
      ? "FIFO has fewer than two free slots; refill waits."
      : "CS:IP " +
        H(s.cs) +
        ":" +
        H(s.ip) +
        " selects " +
        H(physical(s.cs, s.ip), 5) +
        ". Append " +
        H(memoryByte(physical(s.cs, s.ip)), 2) +
        " then " +
        H(memoryByte(physical(s.cs, s.ip) + 1), 2) +
        " to the FIFO. Advance fetch IP by two.";
  const resultNote = () =>
    H(s.a) +
    (s.op === "SUB" ? " − " : " + ") +
    H(s.b) +
    " = " +
    H(calculate().word) +
    ".";
  const writeNote = () =>
    resultNote() +
    " AX and the six arithmetic status flags capture together. " +
    flagNames.map((f) => f + "=" + calculate().flags[f]).join(" · ") +
    ".";
  function describe() {
    const n = index(),
      front = s.queue.length ? H(s.queue[0], 2) : "the next byte";
    if (isMem()) {
      return [
        fetchNote(),
        "Loader consumes " +
          front +
          ". Prefix recognition holds an ES override for this instruction.",
        "Loader transfers " +
          front +
          " from the FIFO to the 8-bit IR. 03h means ADD r16, r/m16.",
        fetchNote(),
        "Latch " +
          front +
          ". 42h splits into 01 | 000 | 010 — disp8, AX and BP+SI. Stage BP in tmpA.",
        "Take " +
          front +
          " from the FIFO. Sign-extend the 8-bit displacement and retain it. Stage SI in tmpB.",
        "Use the EU adder for BP + SI = " +
          H(s.bp + s.si) +
          ". Hold the partial offset in tmpC and stage the displacement in tmpB.",
        "Add the sign-extended displacement. Send " +
          H((s.c + (s.disp || 0)) & 65535) +
          " over the internal bus to IND.",
        "BP-based addressing normally selects SS. The 26h override selects ES; the offset selector takes IND.",
        "Shift ES left four and add IND. " +
          H(s.es, 4) +
          " × 10h + " +
          H(s.ind || 0) +
          " = " +
          H(physical(s.es, s.ind || 0), 5) +
          ".",
        "A0=0 and BHE#=0 select both byte lanes. Read 34h at 3010Ah and 12h at 3010Bh; OPR captures 1234h.",
        "The register read drives " +
          H(s.ax) +
          " onto the 16-bit internal bus. Capture it in tmpA.",
        "OPR drives " +
          H(s.opr || 0) +
          " onto the same bus. Capture the memory operand in tmpB.",
        resultNote() +
          " The combinational sum and flags settle before write-back.",
        writeNote(),
        "Retire ADD and clear the ES override before the following instruction.",
      ][n];
    }
    return [
      fetchNote(),
      "Pop " + front + " from the FIFO into IR. Decode the 8-bit opcode.",
      "Pop " +
        front +
        ". D8h splits into 11 | 011 | 000: register mode, BX, AX.",
      "AX drives " +
        H(s.ax) +
        " onto the bus; tmpA captures it. " +
        fetchNote(),
      "BX drives " +
        H(s.bx) +
        " onto the bus; tmpB captures it. " +
        fetchNote(),
      resultNote() +
        " The combinational sum and flags settle before write-back.",
      writeNote(),
      "Retire the instruction. The next opcode is at the front of the prefetch queue.",
    ][n];
  }
  function capture() {
    const n = index(),
      en = enables();
    s.last = phaseName();
    s.lastEvent = describe();
    if (en.F) fetchPair();
    if (isMem()) {
      if (en.L) {
        const byte = s.queue.shift();
        if (n === 1) {
          s.ir = byte;
          s.prefix = byte;
        }
        if (n === 2) s.ir = byte;
        if (n === 4) {
          s.mod = byte;
          s.a = s.bp;
        }
        if (n === 5) {
          s.disp = byte & 128 ? byte - 256 : byte;
          s.b = s.si;
        }
      }
      if (en.EA) {
        if (n === 6) {
          s.c = calculate().word;
          s.b = s.disp & 65535;
        } else s.ind = calculate().word;
      }
      if (en.D) {
        if (n === 8) s.selectedSegment = "ES";
        if (n === 9) s.phys = physical(s.es, s.ind);
        if (n === 10)
          s.opr = memoryByte(s.phys) + 256 * memoryByte((s.phys + 1) & 0xfffff);
      }
    } else {
      if (en.IR) {
        s.ir = s.queue.shift();
        s.op = s.ir === 0x29 ? "SUB" : "ADD";
      }
      if (en.M) s.mod = s.queue.shift();
    }
    if (en.A) s.a = s.ax;
    if (en.B) s.b = isMem() ? s.opr : s.bx;
    if (en.W) {
      const alu = calculate();
      s.ax = alu.word;
      s.flags = alu.flags;
    }
    if (en.N) {
      s.retired++;
      s.prefix = null;
      s.selectedSegment = null;
    }
    const p = s.phase,
      q0 = p & 1,
      q1 = (p >> 1) & 1,
      q2 = (p >> 2) & 1;
    s.phase = ((q2 ^ (q1 & q0)) << 2) | ((q1 ^ q0) << 1) | (q0 ^ 1);
    if (isMem() && p === 7) s.page ^= 1;
    s.cycles++;
  }
  function half() {
    if (s.clock) capture();
    s.clock ^= 1;
    s.history.push({ clk: s.clock, we: +enables().W });
    if (s.history.length > 34) s.history.shift();
  }
  function step() {
    if (!s.clock) half();
    half();
  }
  function configure(a, b, op) {
    initialA = a & 65535;
    initialB = b & 65535;
    program = Object.hasOwn(programs, op) ? op : "ADD";
    reset();
  }
  reset();
  window.cpu = {
    get s() {
      return s;
    },
    get settings() {
      return { a: initialA, b: initialB, op: program };
    },
    get phaseNames() {
      return isMem() ? memNames.slice(s.page * 8, s.page * 8 + 8) : regNames;
    },
    get outputs() {
      return outputs();
    },
    reset,
    step,
    half,
    configure,
    calculate,
    inputs,
    line,
    index,
    enables,
    isMem,
    hex,
    phaseName,
    describe,
    physical,
    ctrl: (p) => (p === 6 ? enables().W : s.phase === p),
  };
})();
