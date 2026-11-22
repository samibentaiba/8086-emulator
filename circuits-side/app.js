(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const { N, info, W, H } = board;

  const S = {
    sel: "regs",
    scale: 0.95,
    cx: 780,
    cy: 1300,
    bit: 0,
    isDragging: false,
    dragStart: { x: 0, y: 0 },
    camStart: { cx: 0, cy: 0 },
  };

  const canvas = $("canvas");
  const map = $("map");
  const world = $("world");

  function view() {
    const w = canvas.clientWidth || window.innerWidth || 1200;
    const h = canvas.clientHeight || (window.innerHeight - 78) || 800;
    const fit = Math.max(0.05, Math.min(w / W, h / H));
    const px = fit * S.scale;
    return { w, h, fit, px, vw: w / px, vh: h / px };
  }

  function camera() {
    const v = view();
    // Keep camera within bounding boundaries with generous margin
    S.cx = Math.min(W + v.vw * 0.25, Math.max(-v.vw * 0.25, S.cx));
    S.cy = Math.min(board.height + v.vh * 0.25, Math.max(-v.vh * 0.25, S.cy));

    map.setAttribute(
      "viewBox",
      `${S.cx - v.vw / 2} ${S.cy - v.vh / 2} ${v.vw} ${v.vh}`,
    );

    if ($("zoom")) {
      $("zoom").textContent = Math.round(S.scale * 100) + "%";
    }
    if ($("minus")) {
      $("minus").disabled = S.scale <= 0.35;
    }
    if ($("plus")) {
      $("plus").disabled = S.scale >= 30;
    }

    if ($("level")) {
      $("level").textContent =
        S.scale >= 2.4
          ? "Gate & Transistor Level"
          : S.scale >= 1.25
            ? "Subsystem Block"
            : "Architecture Overview";
    }

    if ($("crumbpart")) {
      if (N[S.sel]) {
        const grp = N[S.sel][5] || "CPU";
        const title = (N[S.sel][4] || S.sel).split(" · ")[0].split(" (")[0];
        $("crumbpart").textContent = ` / ${grp} / ${title}`;
      } else {
        $("crumbpart").textContent = " / Intel 8086 System";
      }
    }

    if ($("find") && S.sel) {
      if ($("find").value !== S.sel) {
        $("find").value = S.sel;
      }
    }
  }

  function paint() {
    const v = view();
    const vr = {
      x1: S.cx - v.vw * 0.65,
      y1: S.cy - v.vh * 0.65,
      x2: S.cx + v.vw * 0.65,
      y2: S.cy + v.vh * 0.65,
    };
    world.innerHTML = board.render(S.scale, S.sel, S.bit, vr);
    camera();
  }

  function coords(clientX, clientY) {
    const r = canvas.getBoundingClientRect();
    const v = view();
    return [
      S.cx + (clientX - r.left - v.w / 2) / v.px,
      S.cy + (clientY - r.top - v.h / 2) / v.px,
    ];
  }

  function zoom(factor, clientX, clientY) {
    const anchor = (clientX == null || clientY == null) ? [S.cx, S.cy] : coords(clientX, clientY);
    const oldScale = S.scale;
    S.scale = Math.max(0.35, Math.min(30, S.scale * factor));

    S.cx = anchor[0] - ((anchor[0] - S.cx) * oldScale) / S.scale;
    S.cy = anchor[1] - ((anchor[1] - S.cy) * oldScale) / S.scale;
    paint();
  }

  function fitCpu() {
    S.scale = 1.0;
    S.cx = 780;
    S.cy = 1300;
    paint();
  }

  function fitBoard() {
    S.scale = 0.58;
    S.cx = 1360;
    S.cy = 1300;
    paint();
  }

  function focusComponent(id, deep = false) {
    if (!N[id]) return;
    S.sel = id;
    const [x, y, w, h] = N[id];
    const v = view();

    S.cx = x + w / 2;
    S.cy = y + h / 2;

    const targetScale = deep
      ? 3.2
      : Math.min(2.8, Math.max(1.3, Math.min((v.w - 80) / (v.fit * w), (v.h - 80) / (v.fit * h)) * 0.85));

    S.scale = targetScale;
    paint();
  }

  // Mouse wheel zoom
  canvas.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.18 : 1 / 1.18;
      zoom(factor, e.clientX, e.clientY);
    },
    { passive: false },
  );

  // Mouse drag pan
  canvas.addEventListener("mousedown", (e) => {
    if (e.button !== 0) return;
    S.isDragging = true;
    S.dragStart = { x: e.clientX, y: e.clientY };
    S.camStart = { cx: S.cx, cy: S.cy };
    canvas.style.cursor = "grabbing";
  });

  window.addEventListener("mousemove", (e) => {
    if (!S.isDragging) return;
    const v = view();
    const dx = (e.clientX - S.dragStart.x) / v.px;
    const dy = (e.clientY - S.dragStart.y) / v.px;
    S.cx = S.camStart.cx - dx;
    S.cy = S.camStart.cy - dy;
    camera();
  });

  window.addEventListener("mouseup", (e) => {
    if (S.isDragging) {
      S.isDragging = false;
      canvas.style.cursor = "grab";
    }
  });

  // Touch gesture support (Pinch zoom & pan)
  let initialPinchDist = null;
  let initialPinchScale = null;
  let lastTouchPos = null;

  canvas.addEventListener("touchstart", (e) => {
    if (e.touches.length === 1) {
      lastTouchPos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
      S.camStart = { cx: S.cx, cy: S.cy };
    } else if (e.touches.length === 2) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      initialPinchDist = Math.hypot(dx, dy);
      initialPinchScale = S.scale;
    }
  }, { passive: true });

  canvas.addEventListener("touchmove", (e) => {
    if (e.touches.length === 1 && lastTouchPos) {
      const v = view();
      const dx = (e.touches[0].clientX - lastTouchPos.x) / v.px;
      const dy = (e.touches[0].clientY - lastTouchPos.y) / v.px;
      S.cx = S.camStart.cx - dx;
      S.cy = S.camStart.cy - dy;
      camera();
    } else if (e.touches.length === 2 && initialPinchDist) {
      const dx = e.touches[0].clientX - e.touches[1].clientX;
      const dy = e.touches[0].clientY - e.touches[1].clientY;
      const dist = Math.hypot(dx, dy);
      const factor = dist / initialPinchDist;
      S.scale = Math.max(0.35, Math.min(30, initialPinchScale * factor));
      paint();
    }
  }, { passive: true });

  canvas.addEventListener("touchend", () => {
    initialPinchDist = null;
    lastTouchPos = null;
  });

  // Click & Double-Click on component nodes
  canvas.addEventListener("click", (e) => {
    const nodeEl = e.target.closest("[data-node]");
    if (nodeEl) {
      const nodeId = nodeEl.dataset.node;
      focusComponent(nodeId, false);
    }
  });

  canvas.addEventListener("dblclick", (e) => {
    const nodeEl = e.target.closest("[data-node]");
    if (nodeEl) {
      const nodeId = nodeEl.dataset.node;
      focusComponent(nodeId, true);
    } else {
      zoom(1.8, e.clientX, e.clientY);
    }
  });

  // Keyboard navigation
  window.addEventListener("keydown", (e) => {
    const panStep = 60 / view().px;
    if (e.key === "+" || e.key === "=") {
      zoom(1.25);
    } else if (e.key === "-" || e.key === "_") {
      zoom(1 / 1.25);
    } else if (e.key === "0") {
      fitCpu();
    } else if (e.key === "ArrowLeft") {
      S.cx -= panStep;
      camera();
    } else if (e.key === "ArrowRight") {
      S.cx += panStep;
      camera();
    } else if (e.key === "ArrowUp") {
      S.cy -= panStep;
      camera();
    } else if (e.key === "ArrowDown") {
      S.cy += panStep;
      camera();
    }
  });

  // UI Button Controls
  if ($("minus")) $("minus").onclick = () => zoom(1 / 1.25);
  if ($("plus")) $("plus").onclick = () => zoom(1.25);
  if ($("fit")) $("fit").onclick = fitCpu;
  if ($("fitBoard")) $("fitBoard").onclick = fitBoard;
  if ($("home")) $("home").onclick = fitCpu;

  // Component dropdown selection
  if ($("find")) {
    $("find").addEventListener("change", (e) => {
      const targetId = e.target.value;
      if (targetId && N[targetId]) {
        focusComponent(targetId, true);
      }
    });
  }

  // Handle Window Resize
  window.addEventListener("resize", () => {
    paint();
  });

  // Initial render on page load
  paint();
})();
