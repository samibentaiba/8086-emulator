/* Study views share the circuit model used by the workbench. */
(() => {
  'use strict';

  const practice = new Map();
  const number = value => Number(value.toFixed(4)).toString();
  const frequencyOf = (state, hz) => Number(hz || state.hz) > 0 ? Number(hz || state.hz) : 1;
  const word = (state, names) => names.map(name => Number(Boolean(state[name]))).join('');
  const periodOf = hz => number(1 / hz) + ' s';

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function action(text, className, handler) {
    const button = element('button', className, text);
    button.type = 'button';
    button.addEventListener('click', handler);
    return button;
  }

  function guides(lesson, state, hz) {
    const lab = window.CircuitLab;
    const output = lab.evaluate(lesson.id, state);
    switch (lesson.id) {
      case 'boolean':
        return [
          ['Read the inputs', 'Each switch is one bit. Follow its wire from left to right. A dot joins wires at a crossing.', 'A = ' + state.A + '   M = ' + state.M + '   C = ' + state.C],
          ['Evaluate the AND gates', 'A product is 1 only when every input to that gate is 1. Find the gate fed by A and C.', 'A · C = ' + (state.A & state.C)],
          ['Combine with OR', 'M already covers every term containing M. The independent A · C path can also switch on X.', 'X = M + A · C = ' + output.X]
        ];
      case 'decoder': {
        const bits = word(state, lesson.inputs);
        const index = parseInt(bits, 2);
        const active = lesson.outputs.filter(name => output[name]).join(', ') || 'none';
        return [
          ['Read the address', 'Read BA through BD from left to right. The four bit positions have weights 8, 4, 2 and 1.', bits + '₂ = ' + index],
          ['Select one line', 'The decoder raises one of sixteen lines. Every other decoder line stays at 0.', 'S' + index + ' = 1'],
          ['Follow its taps', 'Each dot feeds an OR gate below the decoder. A selected line can activate several outputs, or none.', 'Active outputs: ' + active]
        ];
      }
      case 'sequential': {
        const q = word(state, lesson.outputs);
        const next = word(lab.step(lesson.id, { ...state }), lesson.outputs);
        return [
          ['Read the stored bits', 'The three flip-flops hold C, B and A between clock edges. A barred letter is the opposite of that bit.', 'C B A = ' + q],
          ['Work out J and K', 'For each flip-flop, JK = 00 holds, 01 clears, 10 sets and 11 toggles the stored bit.', 'Jₐ = B · C̄ = ' + (state.B & (1 - state.C))],
          ['Apply one falling edge', 'All three flip-flops sample the old state together. Step the clock and compare the new word.', q + ' → ' + next]
        ];
      }
      default:
        return [
          ['Count complete cycles', 'A cycle runs from one rising edge to the next. Hertz counts complete cycles per second.', 'f = ' + number(hz) + ' Hz'],
          ['Find the period', 'Divide one second by the frequency to find how long one complete cycle takes.', 'T = 1 / f = ' + periodOf(hz)],
          ['Follow the edges', 'In this square wave, high and low last equally long. Each half-period moves the signal to the other level.', 'T / 2 = ' + number(0.5 / hz) + ' s']
        ];
    }
  }

  function drawGuide(root, lesson, state, hz) {
    const grid = element('ol', 'nb-guide');
    guides(lesson, state, hz).forEach(([title, body, value], i) => {
      const step = element('li', 'nb-step');
      const head = element('div', 'nb-step-head');
      head.append(element('span', 'nb-number', String(i + 1)), element('h3', '', title));
      step.append(head, element('p', '', body), element('code', 'nb-reading', value));
      grid.append(step);
    });
    root.append(grid);
  }

  function allRows(names) {
    return Array.from({ length: 2 ** names.length }, (_, i) => {
      const bits = i.toString(2).padStart(names.length, '0');
      return Object.fromEntries(names.map((name, j) => [name, Number(bits[j])]));
    });
  }

  function drawTable(root, lesson, state, onInput, selectState) {
    const sequential = lesson.id === 'sequential';
    const names = sequential ? lesson.outputs : lesson.inputs;
    const rows = allRows(names);
    const hasActions = !sequential && Boolean(selectState || onInput);
    const table = element('table', 'nb-table');
    const caption = element('caption', '', sequential
      ? 'Read CBA before and after one falling edge. The highlighted row is the current state.'
      : 'Choose an input combination to trace it on the schematic.');
    table.append(caption);
    const thead = document.createElement('thead');
    const head = document.createElement('tr');
    const labels = sequential ? ['C', 'B', 'A', 'Next C', 'Next B', 'Next A'] : [...names, ...lesson.outputs];
    if (hasActions) labels.push('Inputs');
    labels.forEach((label, i) => {
      const th = element('th', i === names.length ? 'nb-split' : '', label);
      th.scope = 'col';
      head.append(th);
    });
    thead.append(head);
    table.append(thead);
    const body = document.createElement('tbody');
    rows.forEach(row => {
      const tr = document.createElement('tr');
      const active = names.every(k => Number(state[k]) === row[k]);
      if (active) tr.classList.add('nb-current');
      const result = sequential
        ? window.CircuitLab.step(lesson.id, { ...state, ...row })
        : window.CircuitLab.evaluate(lesson.id, row);
      [...names.map(k => row[k]), ...lesson.outputs.map(k => result[k])].forEach((bit, i) => {
        const cell = element('td', i === names.length ? 'nb-split' : '');
        cell.append(element('span', 'nb-bit ' + (bit ? 'nb-high' : 'nb-low'), String(bit)));
        tr.append(cell);
      });
      if (hasActions) {
        const cell = document.createElement('td');
        const apply = action(active ? 'Selected' : 'Apply', 'nb-apply', () => {
          if (selectState) selectState({ ...row });
          else names.forEach(k => { if (Number(state[k]) !== row[k]) onInput(k, row[k]); });
        });
        apply.disabled = active;
        apply.setAttribute('aria-label', (active ? 'Selected inputs ' : 'Apply inputs ') + word(row, names));
        cell.append(apply);
        tr.append(cell);
      }
      body.append(tr);
    });
    table.append(body);
    const scroll = element('div', 'nb-table-scroll');
    scroll.append(table);
    root.append(scroll);
    if (lesson.id === 'decoder') {
      root.append(element('p', 'nb-footnote', Object.entries(window.CircuitLab.terms).map(([name, indices]) =>
        name + ' = Σ(' + indices.join(', ') + ')').join('    ·    ')));
    }
  }

  const exercises = {
    boolean: [
      ['A = 1, M = 0, C = 1. What value reaches X?', ['0', '1'], 1, 'The A · C term is 1, so the final OR gate outputs 1.'],
      ['Which expression gives the same X for every input?', ['M + A · C', 'M · A · C', 'A + M + C'], 0, 'The direct M wire already covers A · M, M · C and A · M · C. Only A · C adds another way to reach 1.'],
      ['With M = 1, which input can turn X off by itself?', ['A', 'C', 'Neither'], 2, 'The direct M wire holds one input of the OR network at 1 regardless of A and C.']
    ],
    decoder: [
      ['BA BR BG BD = 0100. Which decoder line is active?', ['S2', 'S4', 'S8'], 1, 'The BR position has weight 4. The decoder selects S4.'],
      ['Which outputs rise when S4 is active?', ['MGA and MDA', 'MGR and MDR', 'MGR only'], 1, 'The dots on S4 connect it to the OR gates for MGR and MDR.'],
      ['What happens at address 1111?', ['MDR rises', 'All four outputs rise', 'All four outputs stay low'], 2, 'S15 is selected, but it has no taps feeding the four output gates.']
    ],
    sequential: [
      ['Starting at CBA = 000, what is stored after one falling edge?', ['000', '001', '010'], 2, 'Jᵦ = Ā · C̄ + A · C is 1. With Kᵦ = 1, B toggles from 0 to 1; C and A stay at 0.'],
      ['What does a JK flip-flop do with J = 1 and K = 1 at its active edge?', ['Holds its bit', 'Toggles its bit', 'Always stores 1'], 1, 'On that edge, a stored 0 becomes 1 and a stored 1 becomes 0.'],
      ['When the clock falls, which values feed the three state updates?', ['The bits just before the edge', 'The new bits from left to right'], 0, 'All three flip-flops sample together, so every next bit is computed from the same previous state.']
    ],
    clock: [
      ['A clock runs at 4 Hz. How long is a complete cycle?', ['4 s', '0.5 s', '0.25 s'], 2, 'The period is 1 / 4 s, or 0.25 s.'],
      ['At 2 Hz, how many falling edges occur in three full seconds of cycles?', ['3', '6', '12'], 1, 'There is one falling edge per complete cycle. Two cycles per second times three seconds gives six.'],
      ['For a symmetric 1 Hz square wave, how long does it stay high?', ['0.25 s', '0.5 s', '1 s'], 1, 'One cycle lasts 1 s, with one half high and the other half low.']
    ]
  };

  function drawPractice(root, lesson) {
    const deck = exercises[lesson.id];
    const progress = practice.get(lesson.id) || { index: 0, choice: null, revealed: false };
    practice.set(lesson.id, progress);
    const [prompt, choices, answer, explanation] = deck[progress.index];
    const finished = progress.revealed || progress.choice === answer;
    const panel = element('section', 'nb-practice');
    panel.setAttribute('aria-label', 'Practice question');
    const refresh = selector => {
      root.replaceChildren();
      drawPractice(root, lesson);
      const target = root.querySelector(selector);
      if (target) target.focus({ preventScroll: true });
    };
    panel.append(element('span', 'nb-counter', 'Question ' + (progress.index + 1) + ' of ' + deck.length));
    const title = element('h3', '', prompt);
    title.tabIndex = -1;
    panel.append(title);
    const group = element('div', 'nb-answers');
    choices.forEach((label, idx) => {
      const button = action(label, 'nb-answer', () => {
        progress.choice = idx;
        refresh('.nb-feedback');
      });
      if (finished && idx === answer) button.classList.add('nb-correct');
      if (!finished && progress.choice === idx) button.classList.add('nb-incorrect');
      button.disabled = finished;
      group.append(button);
    });
    panel.append(group);
    if (finished || progress.choice !== null) {
      const summary = finished ? (progress.revealed ? 'Answer: ' + choices[answer] + '. ' : 'Correct. ') + explanation
                               : 'Try again. Trace the inputs or check the table, then choose another answer.';
      const feedback = element('p', 'nb-feedback', summary);
      feedback.tabIndex = -1;
      feedback.setAttribute('role', 'status');
      panel.append(feedback);
    }
    const controls = element('div', 'nb-practice-actions');
    if (!finished) controls.append(action('Reveal answer', 'nb-link', () => {
      progress.revealed = true;
      refresh('.nb-feedback');
    }));
    else {
      controls.append(action('Try again', 'nb-link', () => {
        Object.assign(progress, { choice: null, revealed: false });
        refresh('h3');
      }), action(progress.index + 1 === deck.length ? 'Start again' : 'Next question', 'nb-next', () => {
        Object.assign(progress, { index: (progress.index + 1) % deck.length, choice: null, revealed: false });
        refresh('h3');
      }));
    }
    panel.append(controls);
    root.append(panel);
  }

  function svgNode(name, attrs, value) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', name);
    Object.entries(attrs).forEach(([key, v]) => node.setAttribute(key, v));
    if (value !== undefined) node.textContent = value;
    return node;
  }

  function drawTiming(root, lesson, state, hz) {
    const seq = lesson.id === 'sequential';
    const phases = [];
    const traces = seq ? ['CLK', 'C', 'B', 'A'] : ['CLK'];
    let current = { ...state };
    for (let i = 0; i < 9; i++) {
      const clock = (Number(state.phase ?? 1) + i) % 2;
      if (seq && i && !clock) current = window.CircuitLab.step(lesson.id, { ...current });
      phases.push({ CLK: clock, C: current.C, B: current.B, A: current.A });
    }
    const height = 35 + traces.length * 40;
    const graph = svgNode('svg', { viewBox:'0 0 670 ' + height, class:'nb-wave', role:'img',
      'aria-label':'Timing diagram showing four cycles at ' + number(hz) + ' Hz' });
    for (let i = 0; i <= 8; i++) {
      const x = 50 + i * 74;
      graph.append(svgNode('path', { d:'M' + x + ' 9V' + (height-24), class:'nb-gridline' }));
      if (!(i%2)) graph.append(svgNode('text', { x, y:height-5, 'text-anchor':'middle', class:'nb-time-label' }, number(i * 0.5/hz) + ' s'));
    }
    traces.forEach((name, row) => {
      const y = 11 + 40 * row;
      const yOf = i => y + (phases[i][name] ? 0 : 22);
      let d = 'M50 ' + yOf(0);
      for (let i = 1; i <= 8; i++) d += 'H' + (50 + i * 74) + 'V' + yOf(i);
      graph.append(svgNode('text', { x:9, y:y+15, class:'nb-wave-label' }, name), svgNode('path', { d, class:'nb-trace' }));
    });
    root.append(element('p', 'nb-timing-summary', 'Four cycles at ' + number(hz) + ' Hz · Period ' + periodOf(hz) +
      (seq ? ' · Falling edges update CBA' : ' · High and low each last ' + number(0.5/hz) + ' s')), graph);
  }

  function renderTab(container, tab, lesson, state, onInput, clockHz, onSelectState) {
    const view = String(tab).toLowerCase();
    const hz = frequencyOf(state, clockHz);
    // Changing input or clock state should not discard an in-progress answer or its focus.
    if (view === 'practice' && container.dataset.notebook === 'practice-' + lesson.id) return;
    container.dataset.notebook = view + '-' + lesson.id;
    container.replaceChildren();
    const root = element('div', 'nb-content');
    container.append(root);
    if (view === 'practice') drawPractice(root, lesson);
    else if (view === 'timing' || (view.includes('table') && lesson.id === 'clock')) drawTiming(root, lesson, state, hz);
    else if (view.includes('table')) drawTable(root, lesson, state, onInput, onSelectState);
    else drawGuide(root, lesson, state, hz);
  }

  window.Notebook = { renderTab };
})();
