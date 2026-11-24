#!/usr/bin/env python3
"""
Compatibility entry point for the TypeScript workbench build.
"""
import glob
import os
import shutil
import subprocess
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
CIRCUITS_DIR = os.path.join(REPO_DIR, "circuits-side")
TSCONFIG_PATH = os.path.join(CIRCUITS_DIR, "tsconfig.json")


def find_tsc():
    # Prefer the lockfile-pinned compiler. Invoke Node directly on Windows rather
    # than trying to execute npm's .cmd shim as an executable.
    node = shutil.which("node")
    local = os.path.join(CIRCUITS_DIR, "node_modules", "typescript", "bin", "tsc")
    if node and os.path.isfile(local):
        return [node, local]

    # System PATH (also supports the existing Nix development environment).
    tsc = shutil.which("tsc")
    if tsc:
        return tsc

    # 2. Nix store pattern
    nix_candidates = sorted(glob.glob("/nix/store/*-typescript-*/bin/tsc"), reverse=True)
    if nix_candidates:
        return nix_candidates[0]

    return None


def main():
    tsc_cmd = find_tsc()
    if not tsc_cmd:
        print("[ERROR] TypeScript compiler (tsc) not found on PATH or in /nix/store/.", file=sys.stderr)
        print("Run npm ci in circuits-side, or use nix-shell.", file=sys.stderr)
        return 1

    for config in ("tsconfig.json", "tsconfig.app.json", "tsconfig.server.json"):
        cmd = [tsc_cmd] if isinstance(tsc_cmd, str) else list(tsc_cmd)
        cmd.extend(["-p", os.path.join(CIRCUITS_DIR, config)])
        print(f"[INFO] Compiling {config}")
        result = subprocess.run(cmd, cwd=CIRCUITS_DIR)
        if result.returncode:
            return result.returncode
    print("[SUCCESS] Built schematic engine, browser UI, and preview server.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
