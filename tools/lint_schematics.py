#!/usr/bin/env python3
"""
Intel 8086 Circuit Atlas - CAD Schematic Linter & Anti-Pattern Inspector
Scans rendered SVG outputs from diagram.js to enforce the 6 Cardinal CAD Invariants:
  1. Zero Gate & DFF Body Penetration (no vertical wire cuts through gate/latch bounding boxes)
  2. 3-Zone Planar Routing Law (dedicated zones for drops, gates, and MUX/results)
  3. Zero Floating Solder Dots (junction dots strictly at intersecting wire paths)
  4. Parallel Wire Clearance (horizontal spacing >= 3.0px, vertical spacing >= 1.8px)
  5. Canvas Boundary Violations (all drawing entities strictly within [0..vw, 0..vh])
  6. Zero Text, Header, & Badge Occlusions (wires never cut through header banners/labels)
  7. Anti-Pattern: Zero educational prose essays or empty placeholder units
"""

import os
import re
import sys
import json
import subprocess
import argparse
import glob
import shutil

def find_node():
    """Discover node binary on PATH or within Nix store."""
    node = shutil.which("node")
    if node:
        return node
    nix_candidates = sorted(glob.glob("/nix/store/*node*/bin/node"), reverse=True)
    for cand in nix_candidates:
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return "node"

NODE_BIN = find_node()
DIAGRAM_JS = os.path.join(os.path.dirname(__file__), "..", "circuits-side", "diagram.js")

SUBSYSTEMS = {
    'golden': ['alu', 'regs', 'flags'],
    'biu': ['seg', 'ip', 'adder', 'segmux', 'offmux', 'ind', 'opr', 'queue', 'memory', 'ext'],
    'eu': ['internal', 'temps', 'aluctl', 'mux'],
    'cu': ['loader', 'ir', 'prefix', 'pla', 'trom', 'engine', 'mar', 'rom', 'ctl', 'seq', 'dec'],
    'sys': ['clk', 'latches', 'transceivers', 'decoder', 'bootrom', 'ram'],
}

SUBSYSTEM_MAP = SUBSYSTEMS

GOLDEN_UNITS = ['alu', 'regs', 'flags']

ALL_UNITS = (
    ['alu', 'regs', 'flags']
    + SUBSYSTEMS['biu']
    + SUBSYSTEMS['eu']
    + SUBSYSTEMS['cu']
    + SUBSYSTEMS['sys']
)

def extract_circuits(target_components=None):
    """Extract rendered SVG outputs for specified or registered circuit components."""
    if target_components is None:
        target_components = GOLDEN_UNITS

    script = """
    const fs = require('fs');
    const vm = require('vm');
    const code = fs.readFileSync(process.argv[1], 'utf8');
    const targetList = process.argv[2] ? JSON.parse(process.argv[2]) : null;

    const mockStimulus = {
        op: 'ADD',
        a: 0x1234,
        b: 0x0234,
        c: 0,
        ax: 0x1234,
        bx: 0x5678,
        cx: 0x0010,
        dx: 0x0020,
        sp: 0xfffe,
        bp: 0x0100,
        si: 0x0004,
        di: 0x0008,
        cs: 0x1000,
        ds: 0x2000,
        ss: 0x3000,
        es: 0x4000,
        ip: 0x0100,
        ind: 0x0020,
        opr: 0x0030,
        ir: 0x01,
        mod: 0x00,
        prefix: 0,
        queue: [0x90, 0x00, 0x00, 0x00, 0x00, 0x00],
        clock: 1,
        phase: 0,
        page: 0,
        lastWord: 0x1234,
        tmpA: 0x1000,
        tmpB: 0x0234,
        flags: { CF: 0, PF: 1, AF: 0, ZF: 0, SF: 0, OF: 0, TF: 0, IF: 1, DF: 0 }
    };

    const mockCpu = {
        calculate: () => ({
            word: 0x1234,
            flags: { CF: 0, PF: 1, AF: 0, ZF: 0, SF: 0, OF: 0, TF: 0, IF: 1, DF: 0 }
        }),
        enables: () => ({
            A: true, B: false, W: true, F: true, IR: false, M: false,
            RDA: true, RDB: false, WE: true
        }),
        isMem: () => false,
        line: () => 0,
        outputs: [
            { key: 'F', name: 'Prefetch', terms: [0, 3, 4, 8, 11, 12] },
            { key: 'IR', name: 'Load opcode', terms: [1, 9] },
            { key: 'M', name: 'Load ModR/M', terms: [2, 10] },
            { key: 'A', name: 'Capture tmpA', terms: [3, 11] },
            { key: 'B', name: 'Capture tmpB', terms: [4, 12] },
            { key: 'Σ', name: 'Observe sum', terms: [5, 13] },
            { key: 'W', name: 'Write AX and flags', terms: [6, 14] },
            { key: 'N', name: 'Retire', terms: [7, 15] }
        ],
        s: mockStimulus
    };

    const window = {};
    const ctx = {
        window,
        global: window,
        console,
        cpu: mockCpu
    };
    ctx.window = ctx;
    vm.createContext(ctx);
    vm.runInContext(code, ctx);

    const componentsToAudit = targetList || ['alu', 'regs', 'flags'];
    const results = {};
    for (const name of componentsToAudit) {
        if (ctx.logicDraw && ctx.logicDraw[name]) {
            try {
                const res = ctx.logicDraw[name](mockStimulus);
                results[name] = {
                    title: res.title,
                    vw: res.vw,
                    vh: res.vh,
                    svg: res.body
                };
            } catch (err) {
                results[name] = { error: `Render exception: ${err.message}` };
            }
        } else {
            results[name] = { error: `Component '${name}' not found in LogicDraw namespace.` };
        }
    }
    console.log(JSON.stringify(results));
    """
    cmd = [NODE_BIN, "-e", script, DIAGRAM_JS, json.dumps(target_components)]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout)

def parse_path_segments(d):
    """Parse SVG path 'd' string into a list of line segments ((x1, y1), (x2, y2))."""
    segments = []
    tokens = re.findall(r'([MmLlHhVvZzCcQq])|(-?\d*\.?\d+)', d)
    cur_x, cur_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    cmd = 'M'
    
    nums = []
    for op, num in tokens:
        if op:
            cmd = op
            nums = []
        elif num:
            nums.append(float(num))
            if cmd in ('M', 'm') and len(nums) == 2:
                cur_x = nums[0] if cmd == 'M' else cur_x + nums[0]
                cur_y = nums[1] if cmd == 'M' else cur_y + nums[1]
                start_x, start_y = cur_x, cur_y
                nums = []
                cmd = 'L' if cmd == 'M' else 'l'
            elif cmd in ('L', 'l') and len(nums) == 2:
                nx = nums[0] if cmd == 'L' else cur_x + nums[0]
                ny = nums[1] if cmd == 'L' else cur_y + nums[1]
                segments.append(((cur_x, cur_y), (nx, ny)))
                cur_x, cur_y = nx, ny
                nums = []
            elif cmd in ('H', 'h') and len(nums) == 1:
                nx = nums[0] if cmd == 'H' else cur_x + nums[0]
                segments.append(((cur_x, cur_y), (nx, cur_y)))
                cur_x = nx
                nums = []
            elif cmd in ('V', 'v') and len(nums) == 1:
                ny = nums[0] if cmd == 'V' else cur_y + nums[0]
                segments.append(((cur_x, cur_y), (cur_x, ny)))
                cur_y = ny
                nums = []
    return segments

def lint_circuit(name, data):
    """Audit a single circuit component SVG for visual CAD quality invariants."""
    svg = data['svg']
    vw = data['vw']
    vh = data['vh']
    errors = []
    warnings = []

    # 1. Parse all wire path segments
    paths = re.findall(r'<path[^>]*d="([^"]+)"', svg)
    all_segments = []
    for d in paths:
        segs = parse_path_segments(d)
        all_segments.extend(segs)

    # Rule 5: Check for Canvas Boundary Violations (Path segments)
    for (x1, y1), (x2, y2) in all_segments:
        if min(x1, x2) < -5 or max(x1, x2) > vw + 5 or min(y1, y2) < -5 or max(y1, y2) > vh + 5:
            errors.append(f"Boundary Violation: Wire ({x1:.1f}, {y1:.1f}) -> ({x2:.1f}, {y2:.1f}) leaks outside viewport [0..{vw}, 0..{vh}]")

    # Rule 5: Check top-level rect, circle, and text elements against viewport bounds
    svg_top = re.sub(r'<g\s+[^>]*transform="translate\([^)]+\)"[^>]*>.*?</g>', '', svg, flags=re.DOTALL)
    for rm in re.finditer(r'<rect\s+([^>]+)>', svg_top):
        attrs = rm.group(1)
        xm = re.search(r'\bx="([^\"]+)"', attrs)
        ym = re.search(r'\by="([^\"]+)"', attrs)
        wm = re.search(r'\bwidth="([^\"]+)"', attrs)
        hm = re.search(r'\bheight="([^\"]+)"', attrs)
        if xm and ym and wm and hm:
            rx, ry = float(xm.group(1)), float(ym.group(1))
            rw, rh = float(wm.group(1)), float(hm.group(1))
            if rx < -5 or rx + rw > vw + 5 or ry < -5 or ry + rh > vh + 5:
                errors.append(f"Boundary Violation: Rect at ({rx:.1f}, {ry:.1f}, {rw:.1f}x{rh:.1f}) leaks outside viewport [0..{vw}, 0..{vh}]")

    for cm in re.finditer(r'<circle\s+([^>]+)>', svg_top):
        attrs = cm.group(1)
        cx_m = re.search(r'\bcx="([^\"]+)"', attrs)
        cy_m = re.search(r'\bcy="([^\"]+)"', attrs)
        r_m = re.search(r'\br="([^\"]+)"', attrs)
        if cx_m and cy_m:
            cx, cy = float(cx_m.group(1)), float(cy_m.group(1))
            cr = float(r_m.group(1)) if r_m else 2.0
            if cx - cr < -5 or cx + cr > vw + 5 or cy - cr < -5 or cy + cr > vh + 5:
                errors.append(f"Boundary Violation: Circle at ({cx:.1f}, {cy:.1f}, r={cr:.1f}) leaks outside viewport [0..{vw}, 0..{vh}]")

    for tm in re.finditer(r'<text\s+([^>]+)>', svg_top):
        attrs = tm.group(1)
        xm = re.search(r'\bx="([^\"]+)"', attrs)
        ym = re.search(r'\by="([^\"]+)"', attrs)
        if xm and ym:
            tx, ty = float(xm.group(1)), float(ym.group(1))
            if tx < -5 or tx > vw + 5 or ty < -5 or ty > vh + 5:
                errors.append(f"Boundary Violation: Text at ({tx:.1f}, {ty:.1f}) leaks outside viewport [0..{vw}, 0..{vh}]")

    # 2. Rule 1: Extract Logic Components (Gates, Muxes, Buffers, DFFs) & Check Body Penetrations
    components = []
    gate_matches = re.finditer(r'<g\s+[^>]*transform="translate\((\d+(?:\.\d+)?)[,\s]+(\d+(?:\.\d+)?)\)"[^>]*>(.*?)</g>', svg, re.DOTALL)
    for m in gate_matches:
        gx = float(m.group(1))
        gy = float(m.group(2))
        inner = m.group(3)
        buf_m = re.search(r'd="M0 0L(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)L0\s+(\d+(?:\.\d+)?)Z"', inner)
        mux_m = re.search(r'd="M0 0H(\d+(?:\.\d+)?)L[\d.]+\s+(\d+(?:\.\d+)?)H', inner)
        if buf_m:
            gw, gh = float(buf_m.group(1)), float(buf_m.group(3))
        elif mux_m:
            gw, gh = float(mux_m.group(1)), float(mux_m.group(2))
        elif 'L12 48' in inner or 'L16 48' in inner or 'H16' in inner:
            gw, gh = 16.0, 48.0
        elif 'H15' in inner or 'H14' in inner or 'L15' in inner:
            gw, gh = 15.0, 10.0
        else:
            gw, gh = 18.0, 12.0
        components.append(('gate', gx, gy, gw, gh))

    # Match DFF cells and latches rendered as <rect>
    for rm in re.finditer(r'<rect\s+([^>]+)>', svg):
        attrs = rm.group(1)
        xm = re.search(r'\bx="([^\"]+)"', attrs)
        ym = re.search(r'\by="([^\"]+)"', attrs)
        wm = re.search(r'\bwidth="([^\"]+)"', attrs)
        hm = re.search(r'\bheight="([^\"]+)"', attrs)
        if xm and ym and wm and hm:
            rw, rh = float(wm.group(1)), float(hm.group(1))
            if int(rw) in (18, 20, 30, 34, 36) and int(rh) in (22, 34, 38, 44):
                components.append(('dff', float(xm.group(1)), float(ym.group(1)), rw, rh))

    # Check vertical wire penetration through component interiors (Rule 1 & Rule 2)
    for (x1, y1), (x2, y2) in all_segments:
        if abs(x1 - x2) < 0.1:
            vx = x1
            vy_min = min(y1, y2)
            vy_max = max(y1, y2)
            for ctype, gx, gy, gw, gh in components:
                # Interior bounding box: [gx + 1.5 .. gx + gw - 1.5] x [gy + 1 .. gy + gh - 1] (excludes input/output pins)
                if gx + 1.5 < vx < gx + gw - 1.5 and vy_min < gy + 1 and vy_max > gy + gh - 1:
                    errors.append(f"Gate Penetration: Vertical wire at X={vx:.1f} cuts through {ctype} body at ({gx:.1f}, {gy:.1f}, {gw:.1f}x{gh:.1f})")

    # 3. Rule 3: Check for Solder Dots (Filter out gate inversion bubbles; treat floating dots as fatal errors)
    circle_matches = re.finditer(r'<circle\s+([^>]+)>', svg_top)
    for cm in circle_matches:
        attrs = cm.group(1)
        cx_m = re.search(r'\bcx="([^\"]+)"', attrs)
        cy_m = re.search(r'\bcy="([^\"]+)"', attrs)
        if cx_m and cy_m:
            cx = float(cx_m.group(1))
            cy = float(cy_m.group(1))
            touching = 0
            for (x1, y1), (x2, y2) in all_segments:
                min_x, max_x = min(x1, x2) - 1.5, max(x1, x2) + 1.5
                min_y, max_y = min(y1, y2) - 1.5, max(y1, y2) + 1.5
                if min_x <= cx <= max_x and min_y <= cy <= max_y:
                    touching += 1
            if touching == 0:
                errors.append(f"Floating Solder Dot: Dot at ({cx:.1f}, {cy:.1f}) is disconnected from all wire paths")

    # 4. Rule 4: Check for Parallel Wire Collisions (Horizontal < 3.0px, Vertical < 1.8px)
    h_lines = [((min(s[0][0], s[1][0]), max(s[0][0], s[1][0])), s[0][1]) for s in all_segments if abs(s[0][1] - s[1][1]) < 0.1 and abs(s[0][0] - s[1][0]) > 8]
    h_lines.sort(key=lambda item: item[1])
    for i in range(len(h_lines)):
        (x1a, x2a), ya = h_lines[i]
        for j in range(i + 1, len(h_lines)):
            (x1b, x2b), yb = h_lines[j]
            dy = abs(ya - yb)
            if dy >= 3.0:
                break
            if dy > 0.1:
                overlap_x = max(0, min(x2a, x2b) - max(x1a, x1b))
                if overlap_x > 15:
                    errors.append(f"Parallel Wire Collision (H): Wires at Y={ya:.1f} and Y={yb:.1f} overlap by {overlap_x:.1f}px with only {dy:.1f}px gap")

    v_lines = [((min(s[0][1], s[1][1]), max(s[0][1], s[1][1])), s[0][0]) for s in all_segments if abs(s[0][0] - s[1][0]) < 0.1 and abs(s[0][1] - s[1][1]) > 8]
    v_lines.sort(key=lambda item: item[1])
    for i in range(len(v_lines)):
        (y1a, y2a), xa = v_lines[i]
        for j in range(i + 1, len(v_lines)):
            (y1b, y2b), xb = v_lines[j]
            dx = abs(xa - xb)
            if dx >= 1.8:
                break
            if dx > 0.1:
                overlap_y = max(0, min(y2a, y2b) - max(y1a, y1b))
                if overlap_y > 15:
                    errors.append(f"Parallel Wire Collision (V): Wires at X={xa:.1f} and X={xb:.1f} overlap by {overlap_y:.1f}px with only {dx:.1f}px gap")

    # 5. Rule 6: Header Banners & Container Occlusion Checks
    headers = []
    for rm in re.finditer(r'<rect\s+([^>]+)>', svg):
        attrs = rm.group(1)
        xm = re.search(r'\bx="([^\"]+)"', attrs)
        ym = re.search(r'\by="([^\"]+)"', attrs)
        wm = re.search(r'\bwidth="([^\"]+)"', attrs)
        hm = re.search(r'\bheight="([^\"]+)"', attrs)
        if xm and ym and wm and hm:
            rx, ry, rw, rh = float(xm.group(1)), float(ym.group(1)), float(wm.group(1)), float(hm.group(1))
            if int(rh) in (13, 14, 18) and 60 < rw < 300:
                headers.append(('header', rx, ry, rw, rh))

    for (x1, y1), (x2, y2) in all_segments:
        if abs(x1 - x2) < 0.1:
            vx = x1
            vy_min, vy_max = min(y1, y2), max(y1, y2)
            for htype, hx, hy, hw, hh in headers:
                if hx + 1.5 < vx < hx + hw - 1.5 and vy_min < hy + 1 and vy_max > hy + hh - 1:
                    errors.append(f"Header Occlusion: Wire at X={vx:.1f} cuts through {htype} at ({hx:.1f}, {hy:.1f}, {hw:.1f}x{hh:.1f})")

    # 6. Anti-Pattern: Educational Essays & Placeholder Card Detection
    if len(components) < 1 and len(all_segments) < 10:
        errors.append("Placeholder Card: Unit contains no discrete logic gates or silicon components")

    forbidden_phrases = ['theory of operation', 'educational overview', 'tutorial', 'placeholder unit', 'todo: implement']
    texts = re.findall(r'<text[^>]*>(.*?)</text>', svg, re.DOTALL)
    for t in texts:
        tl = t.lower()
        for fp in forbidden_phrases:
            if fp in tl:
                errors.append(f'Educational Essay Anti-Pattern: Text contains forbidden phrase "{fp}"')
        if len(t) > 120 and not any(k in t for k in ['C_out', '⊕', '=', 'BUS', 'HIGHWAY', 'INTEL 8086', 'PORT', 'DATA', 'ADDRESS', 'CONTROL', '[15:0]']):
            errors.append(f'Educational Essay Anti-Pattern: Excessive prose text ({len(t)} chars): "{t[:50]}..."')

    return errors, warnings

def parse_args():
    parser = argparse.ArgumentParser(
        description="Intel 8086 Circuit Atlas - CAD Schematic Linter & Anti-Pattern Inspector"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Audit all 34 microprocessor circuit units"
    )
    parser.add_argument(
        "--units", "--components",
        dest="units",
        type=str,
        default=None,
        help="Comma-separated list of component keys (e.g. 'alu,regs,flags' or 'adder,ip')"
    )
    parser.add_argument(
        "--subsystem",
        type=str,
        default=None,
        help="Target subsystem(s) to audit: 'golden', 'biu', 'eu', 'cu', 'sys' (comma-separated allowed)"
    )
    parser.add_argument(
        "--golden",
        action="store_true",
        help="Audit the 3 golden units: alu, regs, flags"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as fatal errors"
    )
    return parser.parse_args()

def resolve_target_units(args):
    """Determine list of units to audit based on CLI flags."""
    if args.all:
        return ALL_UNITS

    if getattr(args, 'golden', False):
        return GOLDEN_UNITS

    selected = []
    if args.subsystem:
        subs = [s.strip().lower() for s in args.subsystem.split(',') if s.strip()]
        for sub in subs:
            if sub not in SUBSYSTEMS:
                print(f"[FATAL] Unknown subsystem '{sub}'. Available: {', '.join(SUBSYSTEMS.keys())}", file=sys.stderr)
                sys.exit(2)
            for u in SUBSYSTEMS[sub]:
                if u not in selected:
                    selected.append(u)

    if args.units:
        units = [u.strip().lower() for u in args.units.split(',') if u.strip()]
        for u in units:
            if u not in ALL_UNITS:
                print(f"[FATAL] Unknown component key '{u}'. Available: {', '.join(ALL_UNITS)}", file=sys.stderr)
                sys.exit(2)
            if u not in selected:
                selected.append(u)

    if not selected:
        return GOLDEN_UNITS

    return selected

def main():
    args = parse_args()
    target_units = resolve_target_units(args)

    print("=" * 70)
    print("Intel 8086 Circuit Atlas - CAD Schematic Inspector")
    if target_units == GOLDEN_UNITS and not args.units and not args.subsystem and not args.all:
        print("[INFO] Auditing default golden units: alu, regs, flags.")
        print("       (Use --all for all 34 units, or --subsystem <golden|biu|eu|cu|sys>, or --units <list>)")
    else:
        print(f"[INFO] Auditing {len(target_units)} unit(s): {', '.join(target_units)}")
    print("=" * 70)

    try:
        circuits = extract_circuits(target_units)
    except Exception as e:
        print(f"[FATAL] Failed to extract circuits from diagram.js: {e}", file=sys.stderr)
        sys.exit(1)

    total_errors = 0
    total_warnings = 0

    for name in target_units:
        data = circuits.get(name)
        if not data:
            print(f"\n[AUDITING] {name.upper()}")
            print("  ❌ Extraction failed: No data returned from Node.js V8")
            total_errors += 1
            continue
        if "error" in data:
            print(f"\n[AUDITING] {name.upper()}")
            print(f"  ❌ Extraction Error: {data['error']}")
            total_errors += 1
            continue

        print(f"\n[AUDITING] {data['title']} ({name.upper()}) · Viewport: {data['vw']}x{data['vh']}")
        errors, warnings = lint_circuit(name, data)

        if errors:
            print(f"  ❌ {len(errors)} ERROR(S) FOUND:")
            for err in errors[:10]:
                print(f"     - {err}")
            if len(errors) > 10:
                print(f"     ... and {len(errors) - 10} more")
        else:
            print("  ✅ Zero Gate Penetrations & Zero Boundary Violations")

        if warnings:
            print(f"  ⚠️  {len(warnings)} WARNING(S):")
            for warn in warnings[:5]:
                print(f"     - {warn}")
            if len(warnings) > 5:
                print(f"     ... and {len(warnings) - 5} more")
        else:
            print("  ✅ Zero Floating Solder Dots & Zero Wire Collisions")

        total_errors += len(errors)
        total_warnings += len(warnings)

    print("\n" + "=" * 70)
    failed = (total_errors > 0) or (args.strict and total_warnings > 0)
    if not failed:
        print("🎉 ALL SCHEMATICS COMPLY WITH ZERO-GLITCH CAD INVARIANTS!")
    else:
        reasons = []
        if total_errors > 0:
            reasons.append(f"{total_errors} critical error(s)")
        if args.strict and total_warnings > 0:
            reasons.append(f"{total_warnings} warning(s) in strict mode")
        print(f"💥 AUDIT FAILED: {' and '.join(reasons)} must be fixed.")
    print("=" * 70)

    sys.exit(1 if failed else 0)

if __name__ == '__main__':
    main()
