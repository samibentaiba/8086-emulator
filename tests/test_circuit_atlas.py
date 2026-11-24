import os
import re
import sys
import json
import subprocess
import unittest
import socket

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CIRCUITS_DIR = os.path.join(REPO_DIR, "circuits-side")
TOOLS_DIR = os.path.join(REPO_DIR, "tools")
sys.path.insert(0, TOOLS_DIR)

import lint_schematics


class TestCircuitAtlas(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "index.html",
            "style.css",
            "model.js",
            "diagram.js",
            "render-engine.js",
            "architecture.js",
            "app.js",
        ]
        for fname in required:
            path = os.path.join(CIRCUITS_DIR, fname)
            self.assertTrue(os.path.exists(path), f"Missing required circuit file: {fname}")
            self.assertGreater(os.path.getsize(path), 100, f"File {fname} is unexpectedly empty or too small")

    def test_index_html_structure(self):
        index_path = os.path.join(CIRCUITS_DIR, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn('id="map"', content)
        self.assertIn('id="world"', content)
        self.assertIn('id="workbench"', content)
        self.assertIn('diagram.js', content)
        self.assertLess(content.index('render-engine.js'), content.index('architecture.js'))

    def test_all_circuit_modules_render_via_node(self):
        node_bin = lint_schematics.find_node()
        if not node_bin:
            self.skipTest("Node.js binary not available for executing JS verification test")

        js_script = """
        global.window = global;
        global.document = { getElementById: () => ({ setAttribute: () => {}, textContent: '' }) };
        require('./circuits-side/model.js');
        require('./circuits-side/diagram.js');
        const s = global.cpu.s;
        const components = [
          'regs', 'internal', 'temps', 'aluctl', 'mux', 'alu', 'flags',
          'seg', 'ip', 'ind', 'segmux', 'offmux', 'adder', 'opr', 'memory',
          'ext', 'queue', 'loader', 'ir', 'prefix', 'pla', 'trom', 'engine',
          'mar', 'rom', 'ctl', 'clk', 'dec', 'seq', 'ram', 'latches',
          'transceivers', 'decoder', 'bootrom'
        ];
        let count = 0;
        for (const id of components) {
          if (!global.logicDraw.hasLogic(id)) {
            process.stderr.write('Missing logic: ' + id);
            process.exit(1);
          }
          const res = global.logicDraw.getComponentLogic(id, s, 0);
          if (!res || !res.body || res.body.length < 10) {
            process.stderr.write('Invalid output: ' + id);
            process.exit(2);
          }
          count++;
        }
        process.stdout.write(String(count));
        """
        proc = subprocess.run([node_bin, "-e", js_script], cwd=REPO_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node script failed: {proc.stderr}")
        self.assertEqual(proc.stdout.strip(), "34")

    def test_architecture_board_render_via_node(self):
        node_bin = lint_schematics.find_node()
        if not node_bin:
            self.skipTest("Node.js binary not available")

        js_script = """
        global.window = global;
        global.document = { getElementById: () => ({ setAttribute: () => {}, textContent: '' }) };
        require('./circuits-side/model.js');
        require('./circuits-side/diagram.js');
        require('./circuits-side/render-engine.js');
        require('./circuits-side/architecture.js');
        const svg = global.board.render(1, 'alu', 0);
        if (!svg || svg.length < 1000) {
          process.stderr.write('SVG render output too small or empty');
          process.exit(1);
        }
        const keys = Object.keys(global.board.N);
        if (keys.length !== 34) {
          process.stderr.write('Expected 34 nodes, found ' + keys.length);
          process.exit(2);
        }
        for (const k of keys) {
          if (!svg.includes('data-node="' + k + '"')) {
            process.stderr.write('Missing node in SVG: ' + k);
            process.exit(3);
          }
        }
        process.stdout.write(String(keys.length));
        """
        proc = subprocess.run([node_bin, "-e", js_script], cwd=REPO_DIR, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"Node script failed: {proc.stderr}")
        self.assertEqual(proc.stdout.strip(), "34")

    def test_circuit_server_module_import(self):
        import circuit_server
        self.assertTrue(hasattr(circuit_server, "launch_circuit"))
        self.assertTrue(os.path.exists(circuit_server.CIRCUITS_DIR))


class TestSchematicLinter(unittest.TestCase):
    """Systematic verification of schematic linter CLI, CAD invariant detection, and golden units."""

    # ------------------------------------------------------------------------
    # 1. CLI Argument Handling Tests
    # ------------------------------------------------------------------------
    def test_linter_cli_help(self):
        """Verify linter --help outputs usage information and options."""
        cmd = [sys.executable, os.path.join(TOOLS_DIR, "lint_schematics.py"), "--help"]
        res = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("--all", res.stdout)
        self.assertIn("--subsystem", res.stdout)

    def test_linter_cli_default_runs_golden_units(self):
        """Verify default linter run without args audits golden units and exits 0."""
        cmd = [sys.executable, os.path.join(TOOLS_DIR, "lint_schematics.py")]
        res = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Default linter run failed:\n{res.stdout}\n{res.stderr}")
        self.assertIn("ALL SCHEMATICS COMPLY", res.stdout)

    def test_linter_cli_units_flag(self):
        """Verify --units flag restricts audit to specified units."""
        cmd = [sys.executable, os.path.join(TOOLS_DIR, "lint_schematics.py"), "--units", "alu,flags"]
        res = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("ALU", res.stdout)
        self.assertIn("FLAGS", res.stdout)
        self.assertNotIn("REGS", res.stdout)

    def test_linter_cli_invalid_unit_flag(self):
        """Verify invalid unit key produces a non-zero exit code or error output."""
        cmd = [sys.executable, os.path.join(TOOLS_DIR, "lint_schematics.py"), "--units", "invalid_nonexistent_unit"]
        res = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        self.assertNotEqual(res.returncode, 0)

    # ------------------------------------------------------------------------
    # 2. Negative CAD Invariant Tests (Synthetic Defect Detection)
    # ------------------------------------------------------------------------
    def test_detect_gate_body_penetration(self):
        """Verify Rule 1: A wire cutting through a gate body triggers an error."""
        # Gate at (100, 100) with size 14x10; vertical wire at X=105 spanning Y=90..120
        svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
          <g transform="translate(100 100)">
            <path d="M0 0 H14 V10 H0 Z" fill="#fff" stroke="#000"/>
          </g>
          <path d="M 105 90 V 120" stroke="#000" stroke-width="1.5"/>
        </svg>
        """
        data = {"svg": svg, "vw": 400, "vh": 200, "title": "TEST_GATE_PEN"}
        errors, warnings = lint_schematics.lint_circuit("test_gate", data)
        self.assertTrue(
            any("Gate Penetration" in e or "cuts through gate" in e for e in errors),
            f"Expected gate penetration error, got: {errors}"
        )

    def test_detect_boundary_violation(self):
        """Verify Rule 5: Wires leaking outside viewport bounds trigger an error."""
        # Canvas bounds: 0..400, 0..200. Wire extends to X=450
        svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
          <path d="M 380 100 H 450" stroke="#000" stroke-width="1.5"/>
        </svg>
        """
        data = {"svg": svg, "vw": 400, "vh": 200, "title": "TEST_BOUNDARY"}
        errors, warnings = lint_schematics.lint_circuit("test_bound", data)
        self.assertTrue(
            any("Boundary Violation" in e or "leaks outside" in e for e in errors),
            f"Expected boundary violation error, got: {errors}"
        )

    def test_detect_floating_solder_dot(self):
        """Verify Rule 3: Solder dot not touching any wire triggers a defect."""
        svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
          <circle cx="150" cy="150" r="2.5" fill="#000"/>
        </svg>
        """
        data = {"svg": svg, "vw": 400, "vh": 200, "title": "TEST_FLOATING_DOT"}
        errors, warnings = lint_schematics.lint_circuit("test_dot", data)
        has_dot_defect = any("Floating Solder Dot" in str(x) for x in (errors + warnings))
        self.assertTrue(has_dot_defect, f"Expected floating dot defect, got errors={errors}, warnings={warnings}")

    def test_valid_solder_dot_at_junction(self):
        """Verify Rule 3: Solder dot at a genuine wire intersection produces zero dot defects."""
        svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
          <path d="M 100 150 H 200" stroke="#000" stroke-width="1.5"/>
          <path d="M 150 100 V 200" stroke="#000" stroke-width="1.5"/>
          <circle cx="150" cy="150" r="2.5" fill="#000"/>
        </svg>
        """
        data = {"svg": svg, "vw": 400, "vh": 200, "title": "TEST_VALID_DOT"}
        errors, warnings = lint_schematics.lint_circuit("test_valid_dot", data)
        dot_defects = [x for x in (errors + warnings) if "Floating Solder Dot" in x]
        self.assertEqual(len(dot_defects), 0, f"Valid dot falsely flagged: {dot_defects}")

    def test_detect_parallel_wire_collision(self):
        """Verify Rule 4: Parallel wires spaced < 3px apart trigger a collision defect."""
        # Two horizontal wires at Y=100 and Y=102 overlapping by 50px
        svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 200">
          <path d="M 50 100 H 150" stroke="#000" stroke-width="1.5"/>
          <path d="M 60 102 H 160" stroke="#000" stroke-width="1.5"/>
        </svg>
        """
        data = {"svg": svg, "vw": 400, "vh": 200, "title": "TEST_COLLISION"}
        errors, warnings = lint_schematics.lint_circuit("test_collision", data)
        has_collision = any("Parallel Wire Collision" in str(x) for x in (errors + warnings))
        self.assertTrue(has_collision, f"Expected parallel wire collision defect, got: {errors}, {warnings}")

    # ------------------------------------------------------------------------
    # 3. Golden Module Immutability & Positive Compliance Tests
    # ------------------------------------------------------------------------
    def test_golden_units_pass_cad_invariants_with_zero_defects(self):
        """Verify that golden units (alu, regs, flags) pass the linter with 0 errors and 0 warnings."""
        circuits = lint_schematics.extract_circuits()
        self.assertIn("alu", circuits)
        self.assertIn("regs", circuits)
        self.assertIn("flags", circuits)

        for name in ["alu", "regs", "flags"]:
            data = circuits[name]
            errors, warnings = lint_schematics.lint_circuit(name, data)
            self.assertEqual(len(errors), 0, f"Golden unit {name} has errors: {errors}")
            self.assertEqual(len(warnings), 0, f"Golden unit {name} has warnings: {warnings}")

    # ------------------------------------------------------------------------
    # 4. Macro Architecture Pin Bridge Alignment Tests
    # ------------------------------------------------------------------------
    def test_macro_pin_bridge_alignment(self):
        """Board wires terminate on the rendered named ports after layout."""
        script = """
        global.window = global;
        require('./circuits-side/model.js');
        require('./circuits-side/diagram.js');
        require('./circuits-side/render-engine.js');
        require('./circuits-side/architecture.js');
        console.log(JSON.stringify({nodes: board.N, ...board.layout()}));
        """
        proc = subprocess.run(
            [lint_schematics.find_node(), "-e", script], cwd=REPO_DIR,
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        layout = json.loads(proc.stdout)
        self.assertEqual(len(layout["connections"]), 53)
        for connection in layout["connections"]:
            net, points = connection["net"], connection["points"]
            for endpoint, name, owner in (
                (points[0], net[4], net[1]), (points[-1], net[5], net[2]),
            ):
                pin = layout["pins"][name]
                self.assertEqual(pin["owner"], owner)
                self.assertEqual(endpoint, {"x": pin["x"], "y": pin["y"]})
                x, y, width, height = layout["nodes"][owner][:4]
                self.assertIn(pin["x"], (x, x + width))
                self.assertGreater(pin["y"], y + 20, "Ports must clear the title")
                self.assertLess(pin["y"], y + height)
            for start, end in zip(points, points[1:]):
                self.assertTrue(start["x"] == end["x"] or start["y"] == end["y"])
                for owner, box in layout["nodes"].items():
                    x, y, width, height = box[:4]
                    if start["y"] == end["y"]:
                        crosses = y < start["y"] < y + height and (
                            max(start["x"], end["x"]) > x
                            and min(start["x"], end["x"]) < x + width
                        )
                    else:
                        crosses = x < start["x"] < x + width and (
                            max(start["y"], end["y"]) > y
                            and min(start["y"], end["y"]) < y + height
                        )
                    self.assertFalse(crosses, f"{net[0]} crosses {owner}")



if __name__ == "__main__":
    unittest.main()
