/** Browser controls. Coordinates remain in board space at every viewport size. */
(() => {
  function element<T extends Element>(id: string, kind: { new(...args: never[]): T }): T {
    const found = document.getElementById(id);
    if (!(found instanceof kind)) throw new Error(`Missing workbench element: ${id}`);
    return found;
  }
  const canvas = element("canvas", HTMLDivElement);
  const map = element("map", SVGSVGElement);
  const world = element("world", SVGGElement);
  const renderer = new CircuitRendering.SvgViewportRenderer(world);
  const zoomLabel = element("zoom", HTMLOutputElement);
  const minus = element("minus", HTMLButtonElement);
  const plus = element("plus", HTMLButtonElement);
  const find = element("find", HTMLSelectElement);
  const level = element("level", HTMLSpanElement);
  const crumb = element("crumbpart", HTMLSpanElement);
  const groups: Record<Workbench.UnitGroup, string> = {
    EU: "Execution Unit", BIU: "Bus Interface Unit", CU: "Control Unit", SYS: "System Board",
  };
  const choices = document.createDocumentFragment();
  for (const [group, title] of Object.entries(groups)) {
    const section = document.createElement("optgroup");
    section.label = title;
    for (const [id, box] of Object.entries(board.N)) {
      if (box[5] !== group) continue;
      const option = document.createElement("option");
      option.value = id;
      option.textContent = box[4];
      section.append(option);
    }
    choices.append(section);
  }
  find.append(choices);
  const MIN_SCALE = 0.35;
  const MAX_SCALE = 30;
  const state = { selected: "regs", scale: 0.95, cx: 780, cy: 1300, bit: 0 };
  const pointers = new Map<number, { x: number; y: number }>();
  let moved = false;
  let dragOrigin: { x: number; y: number } | undefined;
  let pendingFrame = 0;

  function view() {
    const width = Math.max(1, canvas.clientWidth);
    const height = Math.max(1, canvas.clientHeight);
    const fit = Math.max(0.001, Math.min(width / board.W, height / board.H));
    const px = fit * state.scale;
    return { width, height, fit, px, vw: width / px, vh: height / px };
  }

  function paint() {
    pendingFrame = 0;
    const v = view();
    state.cx = Math.min(board.W + v.vw / 4, Math.max(-v.vw / 4, state.cx));
    state.cy = Math.min(board.H + v.vh / 4, Math.max(-v.vh / 4, state.cy));
    map.setAttribute("viewBox", `${state.cx - v.vw / 2} ${state.cy - v.vh / 2} ${v.vw} ${v.vh}`);
    // Retain unchanged SVG nodes while the camera moves. The renderer mounts
    // only objects intersecting this viewport and a small screen-space margin.
    renderer.update(board.scene(state.scale, state.selected, state.bit), {
      x1: state.cx - v.vw / 2, y1: state.cy - v.vh / 2,
      x2: state.cx + v.vw / 2, y2: state.cy + v.vh / 2,
    }, v.px);
    zoomLabel.value = `${Math.round(state.scale * 100)}%`;
    minus.disabled = state.scale <= MIN_SCALE;
    plus.disabled = state.scale >= MAX_SCALE;
    level.textContent = state.scale >= 2.4 ? "Gate & Transistor Level" : state.scale >= 1.4 ? "Subsystem Block" : "Architecture Overview";
    const box = board.N[state.selected];
    crumb.textContent = box ? ` / ${box[5]} / ${box[4].split(" · ")[0].split(" (")[0]}` : " / Intel 8086 System";
    find.value = state.selected;
  }

  function schedulePaint() {
    if (!document.hidden && !pendingFrame) pendingFrame = requestAnimationFrame(paint);
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(pendingFrame);
      pendingFrame = 0;
    } else schedulePaint();
  });

  function coords(clientX: number, clientY: number): [number, number] {
    const rect = canvas.getBoundingClientRect();
    const v = view();
    return [state.cx + (clientX - rect.left - v.width / 2) / v.px,
      state.cy + (clientY - rect.top - v.height / 2) / v.px];
  }

  function zoom(factor: number, clientX?: number, clientY?: number) {
    const anchor = clientX === undefined || clientY === undefined ? [state.cx, state.cy] : coords(clientX, clientY);
    const previous = state.scale;
    state.scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, state.scale * factor));
    state.cx = anchor[0] - (anchor[0] - state.cx) * previous / state.scale;
    state.cy = anchor[1] - (anchor[1] - state.cy) * previous / state.scale;
    schedulePaint();
  }

  function fitRegion(x: number, y: number, width: number, height: number) {
    const v = view();
    state.cx = x + width / 2;
    state.cy = y + height / 2;
    state.scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE,
      Math.min(v.width / width, v.height / height) / v.fit * 0.94));
    schedulePaint();
  }
  function fitCpu() {
    const nodes = Object.entries(board.N).filter(([id, box]) => box[5] !== "SYS" || id === "clk").map(([, box]) => box);
    const right = Math.max(...nodes.map(box => box[0] + box[2])) + 40;
    fitRegion(0, 0, right, board.H);
  }
  function fitBoard() { fitRegion(0, 0, board.W, board.H); }
  function focusComponent(id: string, deep = false) {
    const box = board.N[id];
    if (!box) return;
    state.selected = id;
    fitRegion(box[0] - 40, box[1] - 40, box[2] + 80, box[3] + 80);
    if (deep) state.scale = Math.max(3.2, state.scale);
  }

  canvas.addEventListener("wheel", event => {
    event.preventDefault();
    zoom(event.deltaY < 0 ? 1.18 : 1 / 1.18, event.clientX, event.clientY);
  }, { passive: false });

  canvas.style.touchAction = "none";
  canvas.addEventListener("pointerdown", event => {
    if (event.button !== 0) return;
    if (pointers.size === 0) {
      moved = false;
      dragOrigin = { x: event.clientX, y: event.clientY };
    }
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    canvas.setPointerCapture(event.pointerId);
    canvas.style.cursor = "grabbing";
    canvas.focus({ preventScroll: true });
  });
  canvas.addEventListener("pointermove", event => {
    const previous = pointers.get(event.pointerId);
    if (!previous) return;
    const before = [...pointers.values()];
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    const after = [...pointers.values()];
    if (dragOrigin && Math.hypot(event.clientX - dragOrigin.x, event.clientY - dragOrigin.y) > 4) moved = true;
    if (before.length >= 2) {
      moved = true;
      const oldDistance = Math.hypot(before[0].x - before[1].x, before[0].y - before[1].y);
      const newDistance = Math.hypot(after[0].x - after[1].x, after[0].y - after[1].y);
      if (oldDistance > 0) zoom(newDistance / oldDistance, (before[0].x + before[1].x) / 2, (before[0].y + before[1].y) / 2);
      const px = view().px;
      state.cx -= ((after[0].x + after[1].x) - (before[0].x + before[1].x)) / (2 * px);
      state.cy -= ((after[0].y + after[1].y) - (before[0].y + before[1].y)) / (2 * px);
    } else {
      const px = view().px;
      state.cx -= (event.clientX - previous.x) / px;
      state.cy -= (event.clientY - previous.y) / px;
    }
    schedulePaint();
  });
  function release(event: PointerEvent) {
    pointers.delete(event.pointerId);
    if (!pointers.size) {
      canvas.style.cursor = "grab";
      dragOrigin = undefined;
    }
  }
  canvas.addEventListener("pointerup", release);
  canvas.addEventListener("pointercancel", release);
  canvas.addEventListener("lostpointercapture", release);
  window.addEventListener("blur", () => {
    pointers.clear(); dragOrigin = undefined; canvas.style.cursor = "grab";
  });

  function nodeAt(target: EventTarget | null): string | undefined {
    return target instanceof Element ? target.closest("[data-node]")?.getAttribute("data-node") ?? undefined : undefined;
  }
  canvas.addEventListener("click", event => {
    if (moved) return;
    // Pointer capture retargets the click to canvas. Hit-test after capture ends.
    const id = nodeAt(document.elementFromPoint(event.clientX, event.clientY));
    if (id) focusComponent(id);
  });
  canvas.addEventListener("dblclick", event => {
    if (moved) return;
    const id = nodeAt(document.elementFromPoint(event.clientX, event.clientY));
    if (id) focusComponent(id, true);
    else zoom(1.8, event.clientX, event.clientY);
  });
  window.addEventListener("keydown", event => {
    const target = event.target;
    if (target instanceof HTMLElement && (target.matches("input, textarea, select, button") || target.isContentEditable)) return;
    const step = 60 / view().px;
    if (event.key === "+" || event.key === "=") zoom(1.25);
    else if (event.key === "-" || event.key === "_") zoom(1 / 1.25);
    else if (event.key === "0") fitCpu();
    else if (event.key === "ArrowLeft") { state.cx -= step; schedulePaint(); }
    else if (event.key === "ArrowRight") { state.cx += step; schedulePaint(); }
    else if (event.key === "ArrowUp") { state.cy -= step; schedulePaint(); }
    else if (event.key === "ArrowDown") { state.cy += step; schedulePaint(); }
    else if (event.key === "Enter" || event.key === " ") {
      const id = nodeAt(target);
      if (!id) return;
      focusComponent(id, true);
    } else return;
    event.preventDefault();
  });

  minus.addEventListener("click", () => zoom(1 / 1.25));
  plus.addEventListener("click", () => zoom(1.25));
  element("fit", HTMLButtonElement).addEventListener("click", fitCpu);
  element("fitBoard", HTMLButtonElement).addEventListener("click", fitBoard);
  element("home", HTMLButtonElement).addEventListener("click", fitCpu);
  find.addEventListener("change", () => focusComponent(find.value, true));
  if (typeof ResizeObserver !== "undefined") new ResizeObserver(schedulePaint).observe(canvas);
  else window.addEventListener("resize", schedulePaint);
  fitCpu();
})();
