const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { test } = require('node:test');

function model() {
  const context = vm.createContext({ window: {} });
  vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'model.js'), 'utf8'), context);
  return context.window.cpu;
}

function renderedModel() {
  const context = vm.createContext({});
  context.window = context;
  for (const file of ['model.js', 'diagram.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname, '..', file), 'utf8'), context);
  }
  return context;
}

function retire(cpu, limit = 16) {
  const initial = cpu.s.retired;
  let steps = 0;
  while (cpu.s.retired === initial && steps < limit) {
    cpu.step();
    steps++;
    assert.ok(cpu.s.queue.length <= 6, '8086 prefetch queue must never exceed six bytes');
  }
  assert.equal(cpu.s.retired, initial + 1, 'instruction must retire within its demonstration schedule');
  return steps;
}

test('ALU arithmetic and flags match independent 16-bit arithmetic at boundary values', () => {
  const cpu = model();
  const values = [0, 1, 0x0f, 0x10, 0x7f, 0xff, 0x100, 0x7fff, 0x8000, 0xfffe, 0xffff];
  for (const a of values) for (const b of values) for (const subtract of [false, true]) {
    const actual = cpu.calculate(a, b, subtract);
    const full = subtract ? a - b : a + b;
    const word = full & 0xffff;
    let parity = 0;
    for (let byte = word & 0xff; byte; byte &= byte - 1) parity ^= 1;
    const flags = {
      CF: Number(subtract ? a < b : full > 0xffff),
      AF: Number(((a ^ b ^ word) & 0x10) !== 0),
      PF: 1 ^ parity,
      ZF: Number(word === 0),
      SF: Number((word & 0x8000) !== 0),
      OF: Number(((subtract ? a ^ b : ~(a ^ b)) & (a ^ word) & 0x8000) !== 0),
    };
    const expression = `${a.toString(16)} ${subtract ? '-' : '+'} ${b.toString(16)}`;
    assert.equal(actual.word, word, expression);
    assert.deepEqual({ ...actual.flags }, flags, expression);
  }
});

test('ADD and SUB fetch, decode, write back and retire with 16-bit results', () => {
  for (const [operation, a, b, opcode, result] of [
    ['ADD', 0xffff, 1, 0x01, 0],
    ['SUB', 0, 1, 0x29, 0xffff],
  ]) {
    const cpu = model();
    cpu.configure(a, b, operation);
    assert.equal(cpu.s.ax, a);
    cpu.step();
    assert.deepEqual(Array.from(cpu.s.queue), [opcode, 0xd8]);
    assert.equal(cpu.s.ip, 0x102);
    cpu.step();
    assert.equal(cpu.s.ir, opcode);
    cpu.step();
    assert.equal(cpu.s.mod, 0xd8);
    assert.equal(cpu.s.ax, a, 'decode must not change the destination');
    assert.equal(retire(cpu, 5), 5);
    assert.equal(cpu.s.ax, result);
    assert.equal(cpu.s.bx, b, 'source register must be preserved');
    assert.equal(cpu.s.flags.CF, 1);
    assert.equal(cpu.s.phase, 0);
    assert.equal(cpu.s.cycles, 8);
  }
});

test('memory demonstration applies ES override, reads little-endian operand, and clears prefix at retirement', () => {
  const cpu = model();
  cpu.configure(3, 1, 'MEM');
  cpu.step();
  cpu.step();
  assert.equal(cpu.s.prefix, 0x26);
  for (let i = 0; i < 6; i++) cpu.step();
  assert.equal(cpu.s.ir, 0x03);
  assert.equal(cpu.s.mod, 0x42);
  assert.equal(cpu.s.disp, 6);
  assert.equal(cpu.s.ind, 0x10a, 'BP + SI + displacement');
  cpu.step();
  assert.equal(cpu.s.selectedSegment, 'ES');
  cpu.step();
  assert.equal(cpu.s.phys, 0x3010a);
  cpu.step();
  assert.equal(cpu.s.opr, 0x1234, 'low and high bytes form a little-endian word');
  assert.equal(retire(cpu, 5), 5);
  assert.equal(cpu.s.ax, 0x1237);
  assert.equal(cpu.s.prefix, null);
  assert.equal(cpu.s.selectedSegment, null);
  assert.equal(cpu.s.phase, 0);
  assert.equal(cpu.s.page, 0);
  assert.equal(cpu.s.cycles, 16);
});

test('arithmetic writes preserve TF, IF and DF across repeated instruction execution', () => {
  for (const operation of ['ADD', 'SUB', 'MEM']) {
    const cpu = model();
    cpu.configure(0x7fff, 1, operation);
    Object.assign(cpu.s.flags, { TF: 1, IF: 0, DF: 1 });
    for (let i = 0; i < 12; i++) {
      retire(cpu);
      assert.deepEqual(
        { TF: cpu.s.flags.TF, IF: cpu.s.flags.IF, DF: cpu.s.flags.DF },
        { TF: 1, IF: 0, DF: 1 },
        operation,
      );
    }
  }
});

test('half-clock changes capture only on falling edges and reset restores initial state', () => {
  const cpu = model();
  cpu.configure(0x10003, -1, 'ADD');
  cpu.half();
  assert.equal(cpu.s.clock, 0);
  assert.equal(cpu.s.cycles, 1);
  const queue = Array.from(cpu.s.queue);
  cpu.half();
  assert.equal(cpu.s.clock, 1);
  assert.equal(cpu.s.cycles, 1);
  assert.deepEqual(Array.from(cpu.s.queue), queue);
  retire(cpu);
  cpu.reset();
  assert.equal(cpu.s.ax, 3);
  assert.equal(cpu.s.bx, 0xffff);
  assert.equal(cpu.s.retired, 0);
  assert.equal(cpu.s.cycles, 0);
  assert.equal(cpu.s.history.length, 0);
  assert.equal(cpu.s.queue.length, 0);
  assert.equal(cpu.physical(0xffff, 0x10), 0, 'address generation wraps at 20 bits');
});

test('ALU schematic readouts follow both effective-address additions instead of AX and BX', () => {
  const { cpu, logicDraw } = renderedModel();
  cpu.configure(3, 1, 'MEM');
  for (let i = 0; i < 6; i++) cpu.step();
  const operands = () => Array.from(
    logicDraw.getComponentLogic('alu', cpu.s).body.matchAll(/<text\b[^>]*>([0-9A-F]{4})h<\/text>/g),
    match => match[1],
  ).slice(0, 2);
  assert.equal(cpu.index(), 6);
  assert.deepEqual(operands(), ['0100', '0004'], 'first addition displays BP and SI');
  cpu.step();
  assert.equal(cpu.index(), 7);
  assert.deepEqual(operands(), ['0104', '0006'], 'second addition displays partial address and displacement');
  assert.equal(cpu.s.ax, 3, 'effective-address calculation does not write AX');
  assert.equal(cpu.s.bx, 1);
});

test('SVG text labels preserve literal comparison and ampersand characters', () => {
  const { logicDraw } = renderedModel();
  const output = logicDraw.T(0, 0, 'A < B & C > D');
  assert.ok(output.includes('A &lt; B &amp; C &gt; D'));
  assert.ok(!output.includes('A < B'));
});
