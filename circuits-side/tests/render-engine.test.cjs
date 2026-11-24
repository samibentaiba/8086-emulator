const test = require('node:test');
const assert = require('node:assert/strict');

global.window = global;
require('../render-engine.js');
const { SceneRenderer, intersects, pathIntersects, renderScene } = global.CircuitRendering;
const view = { x1: 10, y1: 10, x2: 20, y2: 20 };
const box = (x1, y1, x2, y2) => ({ x1, y1, x2, y2 });
const scene = (...items) => ({ defs: '<marker id="arrow"/>', items });
const ids = frame => frame.items.map(item => item.id);

function item(id, bounds, calls, version = '1', markup = `<g data-item="${id}"/>`) {
  return { id, bounds, version, render() { calls.push(id); return markup; } };
}

test('off-screen items are omitted without generating their SVG', () => {
  const calls = [];
  const renderer = new SceneRenderer();
  const drawing = scene(
    item('visible', box(12, 12, 15, 15), calls),
    item('offscreen', box(25, 25, 30, 30), calls),
  );
  const frame = renderer.frame(drawing, view);
  assert.deepEqual(ids(frame), ['visible']);
  assert.deepEqual(calls, ['visible']);
  assert.equal(frame.total, 2);
  assert.equal(frame.visible, 1);
  assert.equal(frame.generated, 1);
  assert.deepEqual(ids(renderer.frame(drawing, box(100, 100, 110, 110))), []);
  assert.deepEqual(calls, ['visible'], 'empty views do no geometry rendering work');
});

test('wire visibility follows crossing segments rather than endpoints or enclosing boxes', () => {
  const calls = [];
  const crossing = { ...item('crossing', box(-10, 15, 40, 15), calls),
    path: [{ x: -10, y: 15 }, { x: 40, y: 15 }] };
  const around = { ...item('around', box(-10, -10, 40, 40), calls),
    path: [{ x: -10, y: -10 }, { x: 40, y: -10 }, { x: 40, y: 40 }] };
  assert.equal(pathIntersects(crossing.path, view), true, 'both endpoints can be offscreen');
  assert.equal(intersects(around.bounds, view), true);
  assert.equal(pathIntersects(around.path, view), false, 'the wire itself never enters the view');
  assert.deepEqual(ids(new SceneRenderer().frame(scene(crossing, around), view)), ['crossing']);
  assert.deepEqual(calls, ['crossing']);
});

test('fractional boundaries and single-point paths remain visible at viewport edges', () => {
  const fractional = box(0.25, -2.5, 10.125, 7.75);
  assert.equal(intersects(box(10.125, 7.75, 20, 12), fractional), true);
  assert.equal(intersects(box(10.126, 7.751, 20, 12), fractional), false);
  assert.equal(pathIntersects([{ x: -10, y: 7.75 }, { x: 20, y: 7.75 }], fractional), true);
  assert.equal(pathIntersects([{ x: 10.125, y: -10 }, { x: 10.125, y: 20 }], fractional), true);
  assert.equal(pathIntersects([{ x: 0.25, y: -2.5 }], fractional), true);
  assert.equal(pathIntersects([{ x: 0.24, y: -2.5 }], fractional), false);
  assert.equal(pathIntersects([], fractional), false);
});

test('panning back reuses SVG while changed state invalidates hidden cached items', () => {
  const calls = [];
  const renderer = new SceneRenderer();
  const near = item('near', box(12, 12, 18, 18), calls);
  const far = item('far', box(30, 30, 40, 40), calls);
  const drawing = scene(near, far);
  renderer.frame(drawing, view);
  renderer.frame(drawing, box(30, 30, 40, 40));
  assert.equal(renderer.frame(drawing, view).generated, 0);
  assert.deepEqual(calls, ['near', 'far']);

  const updated = scene(item('near', near.bounds, calls, '2', '<g data-value="new"/>'), far);
  assert.equal(renderer.frame(updated, box(30, 30, 40, 40)).generated, 0);
  const returned = renderer.frame(updated, view);
  assert.equal(returned.generated, 1);
  assert.match(returned.items[0].markup, /data-value="new"/);
  assert.deepEqual(calls, ['near', 'far', 'near']);
});

test('visibility is recomputed independently of markup versions and preserves paint order', () => {
  const calls = [];
  const renderer = new SceneRenderer();
  const a = item('a', box(11, 11, 12, 12), calls);
  const b = item('b', box(13, 13, 14, 14), calls);
  renderer.frame(scene(a, b), view);
  const reordered = renderer.frame(scene(b, a), view);
  assert.deepEqual(ids(reordered), ['b', 'a']);
  assert.equal(reordered.generated, 0);
  const moved = renderer.frame(scene({ ...a, bounds: box(100, 100, 110, 110) }, b), view);
  assert.deepEqual(ids(moved), ['b'], 'a cached object leaving the viewport is still culled');
});

test('overscan uses screen pixels consistently across zoom scales', () => {
  for (const pixelScale of [0.25, 1, 4]) {
    const calls = [];
    const nearX = view.x2 + 63 / pixelScale;
    const farX = view.x2 + 65 / pixelScale;
    const drawing = scene(
      item('near', box(nearX, 12, nearX + 1, 14), calls),
      item('far', box(farX, 12, farX + 1, 14), calls),
    );
    assert.deepEqual(ids(new SceneRenderer().frame(drawing, view, pixelScale, 64)), ['near']);
    assert.deepEqual(ids(new SceneRenderer().frame(drawing, view, pixelScale, 0)), []);
  }
});

test('bounded entry cache keeps recently used SVG and regenerates evicted items', () => {
  const calls = [];
  const renderer = new SceneRenderer(2, 10000);
  const a = item('a', box(10, 10, 20, 20), calls);
  const b = item('b', box(30, 10, 40, 20), calls);
  const c = item('c', box(50, 10, 60, 20), calls);
  const drawing = scene(a, b, c);
  renderer.frame(drawing, a.bounds);
  renderer.frame(drawing, b.bounds);
  assert.equal(renderer.frame(drawing, a.bounds).generated, 0);
  renderer.frame(drawing, c.bounds);
  assert.equal(renderer.frame(drawing, a.bounds).generated, 0, 'recently used a survives eviction');
  assert.equal(renderer.frame(drawing, b.bounds).generated, 1, 'least recently used b is regenerated');
  renderer.clear();
  assert.equal(renderer.frame(drawing, a.bounds).generated, 1);
});

test('character budget limits retained SVG and oversized items still render correctly', () => {
  const calls = [];
  const renderer = new SceneRenderer(10, 40);
  const a = item('a', box(10, 10, 20, 20), calls, '1', 'a'.repeat(30));
  const b = item('b', box(30, 10, 40, 20), calls, '1', 'b'.repeat(30));
  const huge = item('huge', box(50, 10, 60, 20), calls, '1', 'x'.repeat(80));
  const drawing = scene(a, b, huge);
  renderer.frame(drawing, a.bounds);
  renderer.frame(drawing, b.bounds);
  assert.equal(renderer.frame(drawing, a.bounds).generated, 1, 'character budget evicts old markup');
  assert.equal(renderer.frame(drawing, huge.bounds).items[0].markup.length, 80);
  assert.equal(renderer.frame(drawing, huge.bounds).generated, 1, 'oversized items are not retained');
});

test('deleted scene objects release cached markup before being reintroduced', () => {
  const calls = [];
  const renderer = new SceneRenderer();
  const a = item('a', view, calls);
  renderer.frame(scene(a), view);
  assert.equal(renderer.frame(scene(), view).visible, 0);
  assert.equal(renderer.frame(scene(a), view).generated, 1);
  assert.deepEqual(calls, ['a', 'a']);
});

test('full SVG export without a viewport includes all items and shared definitions', () => {
  const calls = [];
  const drawing = scene(item('near', view, calls), item('far', box(100, 100, 120, 120), calls));
  const full = renderScene(drawing);
  assert.equal((full.match(/<defs>/g) || []).length, 1);
  assert.match(full, /data-item="near"/);
  assert.match(full, /data-item="far"/);
  assert.deepEqual(calls, ['near', 'far']);
  const culled = renderScene(drawing, view);
  assert.match(culled, /data-item="near"/);
  assert.doesNotMatch(culled, /data-item="far"/);
});
