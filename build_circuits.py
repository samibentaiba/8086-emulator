#!/usr/bin/env python3
"""
Build helper script to compile circuits-side TypeScript sources to circuits-side/diagram.js
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
    # 1. System PATH
    tsc = shutil.which("tsc")
    if tsc:
        return tsc

    # 2. Nix store pattern
    nix_candidates = sorted(glob.glob("/nix/store/*-typescript-*/bin/tsc"), reverse=True)
    if nix_candidates:
        return nix_candidates[0]

    # 3. Node modules or npx
    npx = shutil.which("npx")
    if npx:
        return [npx, "tsc"]

    return None


def main():
    tsc_cmd = find_tsc()
    if not tsc_cmd:
        print("[ERROR] TypeScript compiler (tsc) not found on PATH or in /nix/store/.", file=sys.stderr)
        print("Please install TypeScript (e.g., npm install -g typescript) or use nix-shell.", file=sys.stderr)
        return 1

    cmd = [tsc_cmd] if isinstance(tsc_cmd, str) else list(tsc_cmd)
    cmd.extend(["-p", TSCONFIG_PATH])

    print(f"[INFO] Compiling TypeScript: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=CIRCUITS_DIR)
    if result.returncode == 0:
        print("[SUCCESS] Successfully compiled circuits-side/src/ -> circuits-side/diagram.js")
    else:
        print(f"[FAIL] tsc exited with error code {result.returncode}", file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
