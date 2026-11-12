{ pkgs ? import <nixpkgs> {} }:

let
  pythonEnv = pkgs.python3.withPackages (ps: with ps; [
    pyqt5
  ]);
in
pkgs.mkShell {
  name = "8086-emulator-devshell";

  buildInputs = [
    pythonEnv
    pkgs.desktop-file-utils
  ];

  shellHook = ''
    export PYTHONPATH="$PWD:$PYTHONPATH"
    export PATH="$PWD/bin:$PATH"
    echo "======================================================================"
    echo "  8086 Emulator NixOS Environment"
    echo "======================================================================"
    echo "  Available Commands:"
    echo "    emu8086-tui [file.asm]  - Neovim-style terminal debugger & modal editor"
    echo "    emu8086-gui [file.asm]  - PyQt5 graphical microprocessor workbench"
    echo "    emu8086 [file.asm] -n   - Headless automated runner / CLI"
    echo "======================================================================"
  '';
}
