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
    pkgs.libsForQt5.qtbase
    pkgs.libsForQt5.qtwayland
  ];

  shellHook = ''
    export PYTHONPATH="$PWD:$PYTHONPATH"
    export PATH="$PWD/bin:$PATH"
    export QT_PLUGIN_PATH="${pkgs.libsForQt5.qtbase.bin}/lib/qt-5.15.19/plugins:${pkgs.libsForQt5.qtwayland.bin}/lib/qt-5.15.19/plugins:$QT_PLUGIN_PATH"
    export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.libsForQt5.qtbase.bin}/lib/qt-5.15.19/plugins/platforms"
    if [ -n "$WAYLAND_DISPLAY" ] && [ -z "$QT_QPA_PLATFORM" ]; then
      export QT_QPA_PLATFORM="wayland;xcb"
    fi
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
