const test = require('node:test');
const assert = require('node:assert/strict');
global.window = global;
require('../model.js');
require('../diagram.js');
require('../render-engine.js');
const generatedLogic = [];
const getComponentLogic = global.logicDraw.getComponentLogic;
global.logicDraw.getComponentLogic = (...args) => {
  generatedLogic.push(args[0]);
  return getComponentLogic(...args);
};
require('../architecture.js');
const board = global.board;
const EPSILON = 1e-7;

function intersectsInterior(a, b, box, margin = 0) {
  const [x, y, w, h] = box;
  const left = x - margin, right = x + w + margin;
  const top = y - margin, bottom = y + h + margin;
  return a.y === b.y
    ? a.y > top + EPSILON && a.y < bottom - EPSILON &&
      Math.max(a.x, b.x) > left + EPSILON && Math.min(a.x, b.x) < right - EPSILON
    : a.x > left + EPSILON && a.x < right - EPSILON &&
      Math.max(a.y, b.y) > top + EPSILON && Math.min(a.y, b.y) < bottom - EPSILON;
}

function verifyLayout(layout) {
  assert.equal(layout.connections.length, board.nets.length);
  for (const { net, points } of layout.connections) {
    const [id, source, target, , from, to] = net;
    assert.ok(points.length >= 2, id);
    const start = layout.pins[from], finish = layout.pins[to];
    assert.deepEqual(points[0], { x: start.x, y: start.y }, `${id} source`);
    assert.deepEqual(points.at(-1), { x: finish.x, y: finish.y }, `${id} target`);
    assert.equal(start.owner, source);
    assert.equal(finish.owner, target);
    assert.equal(points[1].y, start.y, `${id} leaves horizontally`);
    assert.ok(points[1].x > start.x, `${id} leaves the output to its right`);
    assert.equal(points.at(-2).y, finish.y, `${id} enters horizontally`);
    assert.ok(points.at(-2).x < finish.x, `${id} enters the input from its left`);
    for (const p of points) {
      assert.ok(Number.isFinite(p.x) && Number.isFinite(p.y), id);
      assert.ok(p.x >= 10 && p.x <= board.W - 10 && p.y >= 6 && p.y <= board.H - 6, `${id} stays on the board`);
    }
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1], b = points[i];
      assert.ok(a.x === b.x || a.y === b.y, `${id} is orthogonal`);
      assert.notDeepEqual(a, b, `${id} has no empty segments`);
      for (const [owner, box] of Object.entries(board.N)) {
        assert.equal(intersectsInterior(a, b, box), false, `${id} crosses ${owner}`);
        // The straight terminal escape is the only allowed portion inside its
        // own six-unit clearance envelope; every other segment avoids it.
        if ((owner === source && i === 1) || (owner === target && i === points.length - 1)) continue;
        assert.equal(intersectsInterior(a, b, box, 6), false, `${id} loses clearance at ${owner}`);
      }
    }
  }
  for (let i = 0; i < layout.connections.length; i++) {
    const first = layout.connections[i];
    for (const second of layout.connections.slice(i + 1)) {
      if (first.net[4] === second.net[4]) continue; // Connected branches share a signal.
      for (let a = 1; a < first.points.length; a++) for (let b = 1; b < second.points.length; b++) {
        const p = first.points[a - 1], q = first.points[a];
        const r = second.points[b - 1], s = second.points[b];
        if (p.y === q.y && r.y === s.y &&
          Math.max(Math.min(p.x, q.x), Math.min(r.x, s.x)) < Math.min(Math.max(p.x, q.x), Math.max(r.x, s.x)) - EPSILON) {
          assert.ok(Math.abs(p.y - r.y) >= 6 - EPSILON, `${first.net[0]} overlaps ${second.net[0]} horizontally`);
        }
        if (p.x === q.x && r.x === s.x &&
          Math.max(Math.min(p.y, q.y), Math.min(r.y, s.y)) < Math.min(Math.max(p.y, q.y), Math.max(r.y, s.y)) - EPSILON) {
          assert.ok(Math.abs(p.x - r.x) >= 6 - EPSILON, `${first.net[0]} overlaps ${second.net[0]} vertically`);
        }
      }
    }
  }
}

test('all production nets attach to named terminals and connect every unit without collisions', () => {
  assert.equal(Object.keys(board.N).length, 34);
  assert.equal(board.nets.length, 53);
  assert.equal(new Set(board.nets.map(net => net[0])).size, board.nets.length, 'net IDs are unique');
  assert.equal(new Set(board.nets.map(net => `${net[4]}:${net[5]}`)).size, board.nets.length, 'no duplicate connections');
  const connected = new Set(board.nets.flatMap(net => [net[1], net[2]]));
  assert.deepEqual([...connected].sort(), Object.keys(board.N).sort(), 'every displayed unit participates in the graph');
  const layout = board.layout();
  verifyLayout(layout);
  assert.equal(board.layout(), layout, 'unchanged geometry reuses the route cache');
});

test('moving and resizing real units recomputes terminal positions and obstacle-safe routes', () => {
  for (const [id, dx, dy, dw, dh] of [['ram', 80, 100, 0, 0], ['internal', 0, 20, 0, 0], ['alu', 0, 0, 24, 16]]) {
    const original = board.N[id].slice();
    const before = board.layout();
    try {
      for (const [index, delta] of [dx, dy, dw, dh].entries()) board.N[id][index] += delta;
      const after = board.layout();
      assert.notEqual(after, before, `${id} invalidates cached routes`);
      assert.notDeepEqual(after.pins, before.pins, `${id} moves its connected terminals`);
      verifyLayout(after);
    } finally {
      board.N[id] = original;
    }
  }
});

test('zoom and viewport culling preserve visible wire routes and reveal entering cards', () => {
  const layout = board.layout();
  const paths = svg => Array.from(svg.matchAll(/<g data-net="([^"]+)"><title>[^<]*<\/title><path d="([^"]+)"/g), m => [m[1], m[2]]);
  const macro = board.render(1, 'alu', 0);
  assert.equal(paths(macro).length, board.nets.length);
  const [x, y, w, h] = board.N.alu;
  const focus = { x1: x - 5, y1: y - 5, x2: x + w + 5, y2: y + h + 5 };
  const detail = board.render(4, 'alu', 0, focus);
  const fullPaths = new Map(paths(macro));
  assert.ok(paths(detail).length > 0 && paths(detail).length < board.nets.length);
  for (const [id, path] of paths(detail)) assert.equal(path, fullPaths.get(id), `${id} keeps its routed geometry`);
  assert.ok(detail.includes('data-logic="alu"'));
  assert.ok(!detail.includes('data-node="ram"'));
  const [rx, ry, rw, rh] = board.N.ram;
  const panned = board.render(4, 'alu', 0, { x1: rx - 5, y1: ry - 5, x2: rx + rw + 5, y2: ry + rh + 5 });
  assert.ok(panned.includes('data-logic="ram"'));
  assert.ok(!panned.includes('data-node="alu"'));
  assert.equal(board.layout(), layout, 'camera changes must not reroute the board');
});

test('production scenes only generate visible cards and reuse markup during camera movement', () => {
  const renderer = new global.CircuitRendering.SceneRenderer(128, 10000000);
  const region = id => {
    const [x, y, w, h] = board.N[id];
    return { x1: x - 5, y1: y - 5, x2: x + w + 5, y2: y + h + 5 };
  };
  const svg = frame => frame.items.map(item => item.markup).join('');
  const layout = board.layout();
  for (const scale of [1, 4]) {
    renderer.clear();
    generatedLogic.length = 0;
    const scene = board.scene(scale, 'alu', 0);
    assert.deepEqual(generatedLogic, [], 'building scene descriptors must not generate gate SVG');
    const focused = renderer.frame(scene, region('alu'));
    assert.ok(focused.visible < focused.total);
    assert.match(svg(focused), /data-node="alu"/);
    assert.doesNotMatch(svg(focused), /data-node="ram"/);
    assert.deepEqual(generatedLogic, scale < 1.4 ? [] : ['alu']);

    const repeated = renderer.frame(board.scene(scale, 'alu', 0), region('alu'));
    assert.equal(repeated.generated, 0, 'unchanged camera/state reuses cached SVG');
    const panned = renderer.frame(board.scene(scale, 'alu', 0), region('ram'));
    assert.match(svg(panned), /data-node="ram"/);
    assert.doesNotMatch(svg(panned), /data-node="alu"/);
    assert.deepEqual(generatedLogic, scale < 1.4 ? [] : ['alu', 'ram']);
    const returned = renderer.frame(board.scene(scale, 'alu', 0), region('alu'));
    assert.equal(returned.generated, 0, 'returning to a visited card reuses its SVG');
    assert.equal(board.layout(), layout, 'visibility changes do not recompute routes');
  }
});

test('changing demonstration programs invalidates cached control logic even with identical registers', () => {
  const renderer = new global.CircuitRendering.SceneRenderer();
  const previous = global.cpu.settings;
  const [x, y, w, h] = board.N.dec;
  const view = { x1: x, y1: y, x2: x + w, y2: y + h };
  try {
    global.cpu.configure(3, 0, 'ADD');
    const registers = JSON.stringify(global.cpu.s);
    const before = renderer.frame(board.scene(4, 'dec', 0), view);
    global.cpu.configure(3, 0, 'MEM');
    assert.equal(JSON.stringify(global.cpu.s), registers, 'regression requires identical CPU state');
    const after = renderer.frame(board.scene(4, 'dec', 0), view);
    assert.ok(after.generated > 0);
    assert.notEqual(after.items.find(item => item.id === 'node:dec').markup,
      before.items.find(item => item.id === 'node:dec').markup);
  } finally {
    global.cpu.configure(previous.a, previous.b, previous.op);
  }
});
