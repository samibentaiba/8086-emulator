const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const path = require('node:path');
const { test } = require('node:test');

async function startServer(t) {
  const child = spawn(process.execPath, [path.join(__dirname, '..', 'tools', 'server.js')], {
    env: { ...process.env, PORT: '0' },
    stdio: ['ignore', 'pipe', 'pipe'],
    windowsHide: true,
  });
  let stderr = '';
  child.stderr.on('data', chunk => { stderr += chunk; });
  t.after(async () => {
    if (child.exitCode !== null) return;
    const closed = once(child, 'close');
    child.kill('SIGTERM');
    await closed;
  });
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`Server did not start: ${stderr}`)), 5000);
    let output = '';
    child.stdout.on('data', chunk => {
      output += chunk;
      const match = /Local: (http:\/\/127\.0\.0\.1:\d+\/)/.exec(output);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
    child.once('error', error => { clearTimeout(timer); reject(error); });
    child.once('exit', code => {
      clearTimeout(timer);
      reject(new Error(`Server exited before becoming ready (${code}): ${stderr}`));
    });
  });
}

test('preview server serves the complete browser entry point and isolates source files', { timeout: 15000 }, async t => {
  const base = await startServer(t);
  const index = await fetch(base);
  assert.equal(index.status, 200);
  assert.match(index.headers.get('content-type'), /^text\/html; charset=utf-8$/);
  const html = await index.text();
  assert.match(html, /8086 Circuit Workbench/);
  const assets = [...html.matchAll(/(?:src|href)="([^"#]+\.(?:js|css))"/g)].map(match => match[1]);
  assert.ok(assets.length >= 6, 'entry point should load the model, viewport renderer, diagrams, UI and styling');
  assert.ok(assets.includes('render-engine.js'), 'the viewport engine must be served as a browser asset');
  for (const asset of assets) {
    const response = await fetch(new URL(asset, base));
    assert.equal(response.status, 200, asset);
    assert.match(response.headers.get('content-type'), asset.endsWith('.js') ? /^text\/javascript/ : /^text\/css/);
    assert.equal(response.headers.get('x-content-type-options'), 'nosniff');
    assert.ok((await response.text()).length > 0, asset);
  }
  const head = await fetch(base, { method: 'HEAD' });
  assert.equal(head.status, 200);
  assert.ok(Number(head.headers.get('content-length')) > 0);
  assert.equal(await head.text(), '');
  for (const name of ['src/server.ts', 'src/model.ts', 'package.json', 'package-lock.json', '../AGENTS.md', '%2e%2e%2fAGENTS.md', '%00']) {
    const response = await fetch(new URL(name, base));
    assert.equal(response.status, 404, name);
  }
  const malformed = await fetch(base + '%not-an-escape');
  assert.equal(malformed.status, 400);
  const post = await fetch(base, { method: 'POST', body: 'ignored' });
  assert.equal(post.status, 405);
  assert.equal(post.headers.get('allow'), 'GET, HEAD');
});
