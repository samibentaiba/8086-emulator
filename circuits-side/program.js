/* Adapt Python execution effects to the same linked schematic and controls. */
(() => {
  const demo = window.cpu;
  let worker;
  let ready;
  let nextRequest = 0;
  const pending = new Map();
  let active = false;
  let source = "";
  let listing = [];
  let snapshots = [];
  let position = -1;
  let halted = false;
  let busy = false;
  let error = "";
  let log = "";
  let currentEvent = null;
  let state = null;
  let instructionCounter = 0;
  let clock = 1;
  let cycles = 0;
  let history = [];
  let lastOutput = "";
  const events = new EventTarget();

  const signalKinds = [
    ["F", "Prefetch", ["fetch"]],
    ["L", "Load instruction byte", ["prefix", "decode"]],
    ["R", "Read operand", ["operand"]],
    ["A", "Address generation", ["address"]],
    ["D", "Read memory", ["memory-read"]],
    ["M", "Write memory", ["memory-write"]],
    ["W", "Register write", ["write"]],
    ["Σ", "ALU / flags", ["alu"]],
    ["B", "Branch / flush", ["branch", "flush"]],
  ];
  function notify() {
    events.dispatchEvent(new Event("change"));
  }
  function request(command, payload = {}) {
    return new Promise((resolve, reject) => {
      const id = ++nextRequest;
      pending.set(id, { resolve, reject });
      worker.postMessage({ id, command, ...payload });
    });
  }
  async function initialize() {
    if (ready) return ready;
    ready = (async () => {
      const base = new URL("./", location.href).href;
      if (window.embeddedProgramWorker) {
        worker = new Worker(URL.createObjectURL(new Blob([window.embeddedProgramWorker], { type: "text/javascript" })), { type: "module" });
      } else {
        worker = new Worker(new URL("program-worker.js", base), { type: "module" });
      }
      worker.onmessage = ({ data }) => {
        const promise = pending.get(data.id);
        if (!promise) return;
        pending.delete(data.id);
        if (data.error) promise.reject(Error(data.error));
        else promise.resolve(data.result);
      };
      worker.onerror = failure => {
        pending.forEach(p => p.reject(Error(failure.message || "The Python worker failed to start.")));
        pending.clear();
        ready = null;
      };
      await request("initialize", { base, ...(window.embeddedPython || {}) });
    })().catch(e => { ready = null; throw e; });
    return ready;
  }
  function normalize(input) {
    const regs = input.registers;
    const operands = input.operands || [];
    return {
      ...Object.fromEntries(Object.entries(regs).map(([key, value]) => [key.toLowerCase(), value])),
      ip: input.fetchIP,
      execIP: regs.IP,
      a: input.alu?.a ?? operands[0] ?? 0,
      b: input.alu?.b ?? operands[1] ?? 0,
      c: input.ind ?? 0,
      flags: input.flags,
      queue: input.queue,
      ir: input.ir,
      mod: input.mod,
      prefix: input.prefix,
      ind: input.ind,
      opr: input.opr,
      phys: input.physical,
      selectedSegment: input.selectedSegment,
      lastWord: input.lastWord,
      phase: Math.max(position, 0) & 7,
      page: (Math.max(position, 0) >> 3) & 1,
      cycles,
      clock,
      retired: input.retired,
      history,
      last: currentEvent?.title || "Program assembled",
      lastEvent: currentEvent?.description || "The assembled bytes are loaded into code memory. Step begins fetching.",
      op: input.alu?.subtract ? "SUB" : input.alu?.operation || "ADD",
      alu: input.alu,
      undefinedFlags: input.undefinedFlags || [],
      instruction: input.instruction,
      instructionAddress: input.instructionAddress,
      sourceLine: input.sourceLine,
      disp: null,
      halted: input.halted,
    };
  }
  async function assemble(text) {
    if (busy) return;
    busy = true;
    error = "";
    notify();
    try {
      await initialize();
      const result = await request("assemble", { source: text });
      source = text;
      listing = result.listing;
      state = result.state;
      active = true;
      currentEvent = null;
      snapshots = [];
      position = -1;
      instructionCounter = 0;
      halted = false;
      log = "";
      lastOutput = "";
      cycles = 0;
      clock = 1;
      history = [];
    } catch (failure) {
      error = failure.message;
      throw failure;
    } finally {
      busy = false;
      notify();
    }
  }
  async function nextEffect() {
    if (busy || error || (halted && position >= snapshots.length - 1)) return;
    busy = true;
    try {
      if (position + 1 >= snapshots.length) {
        const result = await request("step");
        snapshots = result.events;
        position = -1;
        halted = result.halted;
        lastOutput = result.output;
        if (result.omittedEvents) log += "\nRepeated instruction · " + result.omittedEvents + " intermediate effects omitted from the display.\n";
        instructionCounter++;
      }
      if (position + 1 < snapshots.length) {
        position++;
        currentEvent = snapshots[position];
        state = currentEvent.state;
        cycles++;
        if (position === snapshots.length - 1) log += lastOutput;
      }
    } catch (failure) {
      error = failure.message;
    } finally {
      busy = false;
    }
  }
  async function half() {
    if (!active) return demo.half();
    if (busy) return;
    if (clock) await nextEffect();
    clock ^= 1;
    history.push({ clk: clock, we: +(currentEvent?.kind === "write" && currentEvent.register === "AX") });
    if (history.length > 34) history.shift();
    notify();
  }
  async function step() {
    if (!active) return demo.step();
    if (!clock) clock = 1;
    await half();
  }
  async function stepInstruction() {
    if (!active || busy) return;
    const previous = state.retired;
    do {
      await step();
    } while (!error && state.retired === previous && !(halted && position === snapshots.length-1));
  }
  async function back() {
    if (busy || !active) return;
    busy = true;
    try {
      const result = await request("back");
      state = result.state;
      log = result.output;
      snapshots = [];
      position = -1;
      currentEvent = null;
      halted = false;
      error = "";
      clock = 1;
      history = [];
      instructionCounter = Math.max(0, instructionCounter - 1);
    } finally {
      busy = false;
      notify();
    }
  }
  function outputs() {
    if (!active) return demo.outputs;
    const start = Math.max(0, position) & ~15;
    return signalKinds.map(([key, name, kinds]) => ({
      key,
      name,
      terms: snapshots.slice(start, start + 16).flatMap((e, i) => kinds.includes(e.kind) ? [i] : []),
    }));
  }
  function enables() {
    if (!active) return demo.enables();
    return Object.fromEntries(outputs().map(o => [o.key, o.terms.includes(Math.max(position,0)&15)]));
  }
  function calculation(a, b, subtract) {
    if (!active || a !== undefined) return demo.calculate(a, b, subtract);
    const alu = state?.alu;
    if (!alu) return { ...demo.calculate(0,0,false), width:16, operation:"idle" };
    const width = alu.width;
    const logical = ["AND","OR","XOR","TEST","NOT"].includes(alu.operation);
    let carry = alu.subtract ? 1-alu.carry : alu.carry, word=0;
    const slices=[];
    for (let i=0;i<16;i++) {
      const A=alu.a>>>i&1,rawB=alu.b>>>i&1,B=rawB^+alu.subtract,P=A^B,G=A&B,C=carry;
      const t1=P&G,t2=G&C,t3=P&C,t4=P&G&C,upper=G|t2,lower=t1|t3|t4;
      carry=upper|lower;
      let sum=P^C;
      if(logical)sum=alu.result>>>i&1;
      if(i<width)word|=sum<<i;
      slices.push({A,rawB,B,P,G,C,t1,t2,t3,t4,upper,lower,carry,sum});
    }
    return {word,slices,flags:state.flags,width,operation:alu.operation,logical,subtract:alu.subtract};
  }
  const api = {
    get active() { return active; },
    get busy() { return busy; },
    get error() { return error; },
    get source() { return source; },
    get listing() { return listing; },
    get log() { return log; },
    get event() { return currentEvent; },
    get done() { return active && halted && position === snapshots.length-1; },
    get canBack() { return active && instructionCounter > 0; },
    events, assemble, back, stepInstruction,
    memory: address => request("memory", {address}),
    exit() {active=false;error="";notify();},
  };
  window.program = api;
  window.cpu = {
    ...demo,
    get s() {return active ? normalize(state) : demo.s;},
    get settings() {return active ? {a:state.registers.AX,b:state.registers.BX,op:"PROGRAM"} : demo.settings;},
    get outputs() {return outputs();},
    get phaseNames() {return active ? Array(8).fill(currentEvent?.title || "Ready to fetch") : demo.phaseNames;},
    get isProgram() {return active;},
    line: () => active ? Math.max(position,0)&15 : demo.line(),
    index: () => active ? Math.max(position,0) : demo.index(),
    phaseName: () => active ? currentEvent?.title || "Ready to fetch" : demo.phaseName(),
    describe: () => active ? snapshots[position+1]?.description || (halted?"Program execution completed.":"Fetch and decode the next assembled instruction.") : demo.describe(),
    isMem: () => active || demo.isMem(),
    enables,
    ctrl: p => active ? p===6 && enables().W : demo.ctrl(p),
    inputs: () => active ? [state.alu?.a || 0,state.alu?.b || 0,!!state.alu?.subtract] : demo.inputs(),
    calculate: calculation,
    reset: () => active ? assemble(source) : demo.reset(),
    configure(a,b,op) {active=false;demo.configure(a,b,op);notify();},
    half,step,
  };
})();

