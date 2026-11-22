#!/usr/bin/env python3
"""
8086 Circuit Atlas — Standalone Server & Visualization Launcher
Serves the full 100% interactive Intel 8086 microprocessor circuit workbench in the browser.
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import threading

REPO_DIR = os.path.abspath(os.path.dirname(__file__))
CIRCUITS_DIR = os.path.join(REPO_DIR, "circuits-side")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Keep console output clean
        pass


def launch_circuit(port=8086, open_browser=True):
    if not os.path.exists(CIRCUITS_DIR):
        sys.exit(f"Error: Circuits directory not found at {CIRCUITS_DIR}")

    actual_port = port
    httpd = None

    class CustomServer(socketserver.TCPServer):
        allow_reuse_address = True

    for p in range(port, port + 100):
        try:
            httpd = CustomServer(("", p), lambda *args, **kwargs: QuietHandler(*args, directory=CIRCUITS_DIR, **kwargs))
            actual_port = p
            break
        except OSError:
            continue

    if not httpd:
        sys.exit(f"Error: Could not bind to any port in range {port}-{port + 100}")

    url = f"http://localhost:{actual_port}/"
    print("\n" + "=" * 68)
    print("  ★ Intel 8086 Microprocessor Circuit Atlas & Workbench ★")
    print(f"  Live Interactive Schematic: {url}")
    print("  Press Ctrl+C to stop.")
    print("=" * 68 + "\n")

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped 8086 Circuit Atlas server.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    port_arg = 8086
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_arg = int(sys.argv[1])
    launch_circuit(port=port_arg)
