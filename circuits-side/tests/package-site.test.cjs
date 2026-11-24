const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const { spawnSync } = require('node:child_process');

const browserAssets = ['index.html', 'style.css', 'model.js', 'diagram.js',
  'render-engine.js', 'architecture.js', 'app.js'];

async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), '8086-site-package-'));
  t.after(async () => {
    assert.equal(path.dirname(root), os.tmpdir());
    assert.ok(path.basename(root).startsWith('8086-site-package-'));
    await fs.rm(root, { recursive: true, force: true });
  });
  await fs.mkdir(path.join(root, 'tools'));
  await Promise.all(['package-site.js', 'public-assets.js'].map(name =>
    fs.copyFile(path.join(__dirname, '..', 'tools', name), path.join(root, 'tools', name))));
  await Promise.all(browserAssets.map(name => fs.writeFile(path.join(root, name), `asset:${name}`)));
  return root;
}

test('static package includes only public assets and removes stale build contents', async t => {
  const root = await fixture(t);
  const output = path.join(root, 'dist');
  await fs.mkdir(path.join(output, 'old-private-directory'), { recursive: true });
  await fs.writeFile(path.join(output, 'old-private-directory', 'obsolete.txt'), 'stale');
  await fs.mkdir(path.join(root, 'src'));
  await fs.writeFile(path.join(root, 'src', 'private.ts'), 'must not publish');
  const result = spawnSync(process.execPath, [path.join(root, 'tools', 'package-site.js')], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  assert.deepEqual((await fs.readdir(output)).sort(), [...browserAssets, '.nojekyll'].sort());
  for (const name of browserAssets) assert.equal(await fs.readFile(path.join(output, name), 'utf8'), `asset:${name}`);
  assert.equal(await fs.readFile(path.join(output, '.nojekyll'), 'utf8'), '');
  assert.equal(await fs.readFile(path.join(root, 'src', 'private.ts'), 'utf8'), 'must not publish');
});

test('missing browser assets fail before replacing the previous static build', async t => {
  const root = await fixture(t);
  const output = path.join(root, 'dist');
  await fs.mkdir(output);
  await fs.writeFile(path.join(output, 'index.html'), 'previous successful build');
  await fs.unlink(path.join(root, 'app.js'));
  const result = spawnSync(process.execPath, [path.join(root, 'tools', 'package-site.js')], { encoding: 'utf8' });
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /app\.js/);
  assert.equal(await fs.readFile(path.join(output, 'index.html'), 'utf8'), 'previous successful build');
});
