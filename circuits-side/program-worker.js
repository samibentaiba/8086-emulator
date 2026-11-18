/* The assembly runs in a dedicated Python worker, isolated from the UI. */
let runtime;
async function initialize(configuration) {
  const base = configuration.base;
  const { loadPyodide } = await import(configuration.pyodideURL || new URL("runtime/pyodide.mjs", base).href);
  const py = await loadPyodide({
    indexURL: new URL("runtime/", base).href,
    stdout: () => {},
    stderr: () => {},
  });
  const bundled = configuration.sources || await fetch(new URL("python/repository.json", base)).then(r => {
    if (!r.ok) throw Error("Could not load the emulator source bundle.");
    return r.json();
  });
  for (const [name, content] of Object.entries(bundled)) {
    const path = "/home/pyodide/" + name;
    py.FS.mkdirTree(path.slice(0, path.lastIndexOf("/")));
    py.FS.writeFile(path, content);
  }
  for (const name of ["bytecode.py", "workflow.py"]) {
    const content = configuration.modules?.[name] || await fetch(new URL("python/" + name, base)).then(r => {
      if (!r.ok) throw Error("Could not load " + name);
      return r.text();
    });
    py.FS.writeFile("/home/pyodide/" + name, content);
  }
  py.runPython("from workflow import dispatch");
  return py;
}
self.onmessage = async event => {
  const { id, command, ...payload } = event.data;
  try {
    if (command === "initialize") {
      runtime = initialize(payload);
      await runtime;
      self.postMessage({ id, result: { ready: true } });
      return;
    }
    const py = await runtime;
    if (!py) throw Error("The code engine has not initialized.");
    py.globals.set("atlas_request", JSON.stringify({ command, ...payload }));
    const result = JSON.parse(py.runPython("dispatch(atlas_request)"));
    self.postMessage({ id, result });
  } catch (error) {
    self.postMessage({ id, error: String(error.message || error) });
  }
};

