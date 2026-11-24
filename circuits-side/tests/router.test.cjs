const test = require('node:test');
const assert = require('node:assert/strict');
global.window = global;
require('../diagram.js');
const { AutoRouter, Component, LogicGate, PortBox, SchematicCanvas, RoutingError, segmentHitsRect } = global.logicDraw;

function checkSegments(points, obstacles = [], bounds) {
  assert.ok(points.length > 1);
  for (let i = 1; i < points.length; i++) {
    const a = points[i - 1], b = points[i];
    assert.ok(a.x === b.x || a.y === b.y, 'segments are orthogonal');
    assert.notDeepEqual(a, b, 'no zero-length segment');
    for (const r of obstacles) assert.equal(segmentHitsRect(a, b, r), false, `wire crosses ${JSON.stringify(r)}`);
  }
  if (bounds) for (const p of points) {
    assert.ok(p.x >= bounds.x && p.x <= bounds.x + bounds.w);
    assert.ok(p.y >= bounds.y && p.y <= bounds.y + bounds.h);
  }
}

test('detours around obstacles with clearance, deterministically', () => {
  const obstacle = { x: 40, y: 20, w: 20, h: 60 };
  const bounds = { x: 0, y: 0, w: 100, h: 100 };
  const router = new AutoRouter({ obstacles: [obstacle], bounds });
  router.route({ x: 10, y: 50 }, { x: 90, y: 50 });
  const route = router.routes[0];
  checkSegments(route, [{ x: 34, y: 14, w: 32, h: 72 }], bounds);
  assert.deepEqual(route[0], { x: 10, y: 50 });
  assert.deepEqual(route.at(-1), { x: 90, y: 50 });
  const repeat = new AutoRouter({ obstacles: [obstacle], bounds });
  repeat.route({ x: 10, y: 50 }, { x: 90, y: 50 });
  assert.deepEqual(repeat.routes[0], route);
});

test('each pin direction has an outward escape and matching arrival', () => {
  const body = new Component('body', 40, 40, 20, 20);
  const cases = [
    ['L', 0, 10, 10, 50], ['R', 20, 10, 90, 50],
    ['T', 10, 0, 50, 10], ['B', 10, 20, 50, 90],
  ];
  for (const [dir, x, y, ox, oy] of cases) {
    const pin = body.addPin(dir, x, y, dir);
    const router = new AutoRouter({ obstacles: [{ ...body.bounds(), id: body.id }], bounds: { x: 0, y: 0, w: 100, h: 100 } });
    router.route(pin, { x: ox, y: oy });
    checkSegments(router.routes[0], [body.bounds()]);
    const start = router.routes[0][0], next = router.routes[0][1];
    assert.ok(dir === 'L' ? next.x < start.x : dir === 'R' ? next.x > start.x : dir === 'T' ? next.y < start.y : next.y > start.y);
    const incoming = new AutoRouter({ obstacles: [{ ...body.bounds(), id: body.id }] });
    incoming.route({ x: ox, y: oy }, pin);
    checkSegments(incoming.routes[0], [body.bounds()]);
    assert.deepEqual(incoming.routes[0].at(-1), { x: pin.x, y: pin.y });
  }
});

test('a bottom control pin approaches vertically without body penetration', () => {
  const gate = new Component('mux', 50, 20, 30, 40);
  const sel = gate.addPin('sel', 15, 40, 'B');
  const router = new AutoRouter({ obstacles: [{ ...gate.bounds(), id: gate.id }] });
  router.route({ x: 10, y: 80 }, sel);
  const route = router.routes[0];
  assert.equal(route.at(-2).x, sel.x);
  assert.ok(route.at(-2).y > sel.y);
  checkSegments(route, [gate.bounds()]);
});

test('moving components moves their pins and re-routes the same canvas', () => {
  const source = new LogicGate('a', 20, 20, 'buf', 20, 20);
  const target = new LogicGate('b', 100, 20, 'and', 20, 20);
  const canvas = new SchematicCanvas({ bounds: { x: 0, y: 0, w: 180, h: 120 } });
  canvas.addComponent(source).addComponent(target).connect(source.pin('out'), target.pin('in0'));
  const before = canvas.render();
  target.x += 20; target.y += 40;
  assert.equal(target.pin('in0').x, 120);
  assert.equal(target.pin('in0').y, 64);
  const after = canvas.render();
  assert.notEqual(before, after);
  assert.match(after, /120 64|H120|V64/);
  assert.equal(after, canvas.render(), 'repeated render does not accumulate routes');
});

test('reserved label regions and later-added components affect deferred routes', () => {
  const source = new LogicGate('a', 10, 40, 'buf', 10, 10);
  const target = new LogicGate('b', 140, 40, 'buf', 10, 10);
  const canvas = new SchematicCanvas({ bounds: { x: 0, y: 0, w: 180, h: 100 } });
  canvas.connect(source.pin('out'), target.pin('in0'));
  canvas.addComponent(source).addComponent(target);
  canvas.reserve({ x: 50, y: 30, w: 40, h: 30 });
  const svg = canvas.render();
  assert.match(svg, /V24|V66/, 'router uses an edge of the expanded label bounds');
});

test('parallel signals maintain six units between shared spans', () => {
  const router = new AutoRouter({ bounds: { x: 0, y: 0, w: 160, h: 100 } });
  router.route({ x: 20, y: 50 }, { x: 120, y: 50 }, { net: 'first' });
  router.route({ x: 10, y: 52 }, { x: 130, y: 52 }, { net: 'second' });
  const route = router.routes[1];
  checkSegments(route);
  for (let i = 1; i < route.length; i++) {
    const a = route[i - 1], b = route[i];
    if (a.y === b.y && Math.max(a.x, b.x) > 20 && Math.min(a.x, b.x) < 120) {
      assert.ok(Math.abs(a.y - 50) >= 6);
    }
  }
});

test('impossible layouts fail explicitly without appending a wire', () => {
  const router = new AutoRouter({ obstacles: [{ x: 40, y: 0, w: 20, h: 100 }], bounds: { x: 0, y: 0, w: 100, h: 100 } });
  assert.throws(() => router.route({ x: 10, y: 50 }, { x: 90, y: 50 }), RoutingError);
  assert.equal(router.routes.length, 0);
  assert.equal(router.render(), '');
});

test('invalid geometry, hints, and directions fail explicitly', () => {
  const bad = [
    () => new AutoRouter().route({ x: NaN, y: 0 }, { x: 1, y: 1 }),
    () => new AutoRouter().route({ x: 10, y: 10 }, { x: 10, y: 10 }),
    () => new AutoRouter({ stub: -1 }).route({ x: 0, y: 0 }, { x: 1, y: 1 }),
    () => new AutoRouter({ clearance: -1 }).route({ x: 0, y: 0 }, { x: 1, y: 1 }),
    () => new AutoRouter().route({ x: 0, y: 0, dir: 'Q' }, { x: 1, y: 1 }),
    () => new AutoRouter({ obstacles: [{ x: 20, y: 20, w: 40, h: 40 }] }).route({ x: 0, y: 0 }, { x: 80, y: 80 }, { waypoints: [[40, 40]] }),
  ];
  for (const action of bad) assert.throws(action, RoutingError);
});

test('a branch dot requires an actual parent wire and inherits its net', () => {
  const router = new AutoRouter();
  assert.throws(() => router.branch([40, 20], { x: 40, y: 80 }), RoutingError);
  router.route({ x: 0, y: 20 }, { x: 100, y: 20 }, { net: 'data' });
  router.branch([40, 20], { x: 40, y: 80 });
  assert.equal(router.dots.length, 1);
  assert.throws(() => router.branch([70, 20], { x: 70, y: 80 }, { net: 'other' }), RoutingError);
  router.addDot(40, 20);
  assert.throws(() => router.addDot(55, 55), RoutingError);
});

test('port directions match the rendered edge', () => {
  for (const side of ['left', 'right']) {
    const port = new PortBox('port', 10, 10, 30, 40, 'BUS', side);
    const internal = port.addPortPin('internal', 20, 'DATA');
    const external = port.addPortPin('external', 30, 'DATA', true);
    assert.equal(internal.dir, internal.x === 10 ? 'L' : 'R');
    assert.equal(external.dir, external.x === 10 ? 'L' : 'R');
  }
});

test('duplicate components and pins cannot silently replace connections', () => {
  const component = new Component('same', 0, 0, 10, 10);
  component.addPin('a', 0, 5);
  assert.throws(() => component.addPin('a', 0, 5), /Duplicate pin/);
  const canvas = new SchematicCanvas();
  canvas.addComponent(component);
  assert.throws(() => canvas.addComponent(component), /Duplicate component/);
});

test('route inspection returns snapshots that cannot corrupt later routing', () => {
  const router = new AutoRouter();
  router.route({ x: 0, y: 10 }, { x: 100, y: 10 }, { net: 'data' });
  const geometry = router.routes;
  geometry[0][0].x = 500;
  geometry[0].push({ x: 600, y: 10 });
  assert.deepEqual(router.routes[0], [{ x: 0, y: 10 }, { x: 100, y: 10 }]);
});

function parseRoute(path) {
  const tokens = path.match(/[MHV]|-?\d+(?:\.\d+)?(?:e[+-]?\d+)?/gi);
  const points = [];
  let x = 0, y = 0;
  for (let i = 0; i < tokens.length;) {
    const command = tokens[i++];
    if (command === 'M') { x = Number(tokens[i++]); y = Number(tokens[i++]); }
    else if (command === 'H') x = Number(tokens[i++]);
    else if (command === 'V') y = Number(tokens[i++]);
    else assert.fail(`Unexpected route command ${command}`);
    points.push({ x, y });
  }
  return points;
}

test('all three temporary latch banks render connected NAND feedback without body crossings', () => {
  for (const phase of [0, 3, 4, 6, 7]) {
    const svg = global.logicDraw.tempsLogic({ phase, a: 0xa55a, b: 0xffff, c: 0x1234 });
    const components = Array.from(svg.matchAll(/<g data-component="([^"]+)" data-x="([^"]+)" data-y="([^"]+)" data-width="([^"]+)" data-height="([^"]+)"/g),
      ([, id, x, y, w, h]) => ({ id, x: +x, y: +y, w: +w, h: +h }));
    const wires = Array.from(svg.matchAll(/<path\b[^>]*\bd="([^"]+)"[^>]*\bdata-net="([^"]+)"/g),
      ([, path, net]) => ({ net, points: parseRoute(path) }));
    assert.equal(components.length, 15);
    assert.equal(wires.length, 30);
    for (const wire of wires) checkSegments(wire.points, components, { x: 6, y: 6, w: 456, h: 210 });
    for (let i = 0; i < wires.length; i++) for (let j = i + 1; j < wires.length; j++) {
      if (wires[i].net === wires[j].net) continue;
      for (let a = 1; a < wires[i].points.length; a++) for (let b = 1; b < wires[j].points.length; b++) {
        const p = wires[i].points[a - 1], q = wires[i].points[a];
        const r = wires[j].points[b - 1], s = wires[j].points[b];
        if (p.y === q.y && r.y === s.y && Math.max(Math.min(p.x, q.x), Math.min(r.x, s.x)) < Math.min(Math.max(p.x, q.x), Math.max(r.x, s.x))) {
          assert.ok(Math.abs(p.y - r.y) >= 6, `${wires[i].net} and ${wires[j].net} have insufficient horizontal separation`);
        }
        if (p.x === q.x && r.x === s.x && Math.max(Math.min(p.y, q.y), Math.min(r.y, s.y)) < Math.min(Math.max(p.y, q.y), Math.max(r.y, s.y))) {
          assert.ok(Math.abs(p.x - r.x) >= 6, `${wires[i].net} and ${wires[j].net} have insufficient vertical separation`);
        }
      }
    }
    for (const bank of ['tmpa', 'tmpb', 'tmpc']) {
      const routes = wires.filter(wire => wire.net.startsWith(bank + '.'));
      assert.equal(routes.length, 10);
      const q = components.find(c => c.id === bank + '_q');
      const notq = components.find(c => c.id === bank + '_notq');
      const qFeedback = routes.find(wire => wire.net === bank + '.q');
      const notqFeedback = routes.find(wire => wire.net === bank + '.notq');
      assert.deepEqual(qFeedback.points[0], { x: q.x + q.w, y: q.y + q.h / 2 });
      assert.deepEqual(qFeedback.points.at(-1), { x: notq.x, y: notq.y + 4 });
      assert.deepEqual(notqFeedback.points[0], { x: notq.x + notq.w, y: notq.y + notq.h / 2 });
      assert.deepEqual(notqFeedback.points.at(-1), { x: q.x, y: q.y + q.h - 4 });
    }
  }
});
