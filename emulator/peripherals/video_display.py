"""
Virtual Text-Mode Video Display (CGA 80x25 Text Mode @ 0xB8000)
EMU8086 Compatible Video Memory Mirror

Specification:
    Memory Address: 0xB800:0000 (Physical address 0xB8000)
    Dimensions: 80 columns x 25 rows = 2,000 characters (4,000 bytes)
    Format:
        Even Byte (0xB8000 + 2*i):     ASCII character code (0-255)
        Odd Byte  (0xB8000 + 2*i + 1): Attribute byte
            Bits 0-3: Foreground Color (0-15)
            Bits 4-6: Background Color (0-7)
            Bit 7:    Blink / Bright Background
"""

import os
import sys
import time
import multiprocessing as mp

VIDEO_MEM_BASE = 0xB8000
VIDEO_COLS = 80
VIDEO_ROWS = 25
VIDEO_SIZE_BYTES = VIDEO_COLS * VIDEO_ROWS * 2 # 4000 bytes

# Standard IBM CGA 16-Color Palette
CGA_PALETTE = [
    "#000000",  # 0: Black
    "#0000AA",  # 1: Blue
    "#00AA00",  # 2: Green
    "#00AAAA",  # 3: Cyan
    "#AA0000",  # 4: Red
    "#AA00AA",  # 5: Magenta
    "#AA5500",  # 6: Brown
    "#AAAAAA",  # 7: Light Gray
    "#555555",  # 8: Dark Gray
    "#5555FF",  # 9: Light Blue
    "#55FF55",  # 10: Light Green
    "#55FFFF",  # 11: Light Cyan
    "#FF5555",  # 12: Light Red
    "#FF55FF",  # 13: Light Magenta
    "#FFFF55",  # 14: Yellow
    "#FFFFFF"   # 15: White
]


def _run_video_display_gui(pipe):
    """Entry point for isolated video display window."""
    try:
        import tkinter as tk
    except ImportError:
        return

    if sys.platform != 'win32' and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        return

    class VideoDisplayWindow:
        def __init__(self, root, pipe):
            self.root = root
            self.pipe = pipe
            self.cursor_row = 0
            self.cursor_col = 0
            self.cursor_visible = True
            self.char_w = 9
            self.char_h = 16

            self.root.title("EMU8086 Virtual Video Display (CGA 80x25 Text Mode - 0xB8000)")
            width = VIDEO_COLS * self.char_w + 20
            height = VIDEO_ROWS * self.char_h + 75
            self.root.geometry(f"{width}x{height}")
            self.root.resizable(False, False)
            self.root.configure(bg="#1E1E1E")

            self._create_widgets()
            self._poll_pipe()

        def _create_widgets(self):
            # Header
            hdr = tk.Frame(self.root, bg="#1E1E1E", pady=4)
            hdr.pack(fill=tk.X)
            t_lbl = tk.Label(
                hdr,
                text="VIRTUAL VIDEO DISPLAY - CGA TEXT MODE (0xB800:0000)",
                font=("Consolas", 11, "bold"),
                fg="#61AFEF",
                bg="#1E1E1E"
            )
            t_lbl.pack()

            # Main Display Canvas (80x25 characters)
            c_width = VIDEO_COLS * self.char_w
            c_height = VIDEO_ROWS * self.char_h
            self.canvas = tk.Canvas(
                self.root,
                width=c_width,
                height=c_height,
                bg="#000000",
                highlightthickness=2,
                highlightbackground="#3E4451"
            )
            self.canvas.pack(pady=4)

            # Footer / Status
            self.status_lbl = tk.Label(
                self.root,
                text=f"Resolution: 80x25 | Cursor: (Row: 0, Col: 0) | Buffer: 0xB8000-0xB8F9F",
                font=("Consolas", 9),
                fg="#98C379",
                bg="#1E1E1E"
            )
            self.status_lbl.pack(pady=2)

            # Initialize character text and background items on canvas
            self.text_ids = {} # (row, col) -> canvas text id
            self.bg_ids = {}   # (row, col) -> canvas rect id
            for r in range(VIDEO_ROWS):
                for c in range(VIDEO_COLS):
                    x1 = c * self.char_w
                    y1 = r * self.char_h
                    x2 = x1 + self.char_w
                    y2 = y1 + self.char_h
                    bid = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#000000", outline="")
                    tid = self.canvas.create_text(
                        x1 + self.char_w // 2,
                        y1 + self.char_h // 2,
                        text=" ",
                        fill="#AAAAAA",
                        font=("Consolas", 10)
                    )
                    self.bg_ids[(r, c)] = bid
                    self.text_ids[(r, c)] = tid

            # Cursor rectangle
            self.cursor_id = self.canvas.create_line(0, 0, 0, 0, fill="#FFFFFF", width=2)
            self._update_cursor(0, 0)

        def _update_cursor(self, row, col):
            self.cursor_row = max(0, min(VIDEO_ROWS - 1, row))
            self.cursor_col = max(0, min(VIDEO_COLS - 1, col))
            x1 = self.cursor_col * self.char_w
            y1 = (self.cursor_row + 1) * self.char_h - 2
            x2 = x1 + self.char_w
            y2 = y1
            self.canvas.coords(self.cursor_id, x1, y1, x2, y2)
            self.status_lbl.config(
                text=f"Resolution: 80x25 | Cursor: (Row: {self.cursor_row}, Col: {self.cursor_col}) | Buffer: 0xB8000-0xB8F9F"
            )

        def _render_buffer(self, buffer_data):
            """
            buffer_data: list of 2000 tuples: (char_code, attr_code)
            """
            for i, (char_code, attr) in enumerate(buffer_data):
                if i >= VIDEO_COLS * VIDEO_ROWS:
                    break
                row = i // VIDEO_COLS
                col = i % VIDEO_COLS

                # Decode character
                char_str = chr(char_code) if (32 <= char_code <= 126) else (' ' if char_code == 0 else chr(char_code) if char_code < 256 else '?')

                # Decode attribute
                fg_idx = attr & 0x0F
                bg_idx = (attr >> 4) & 0x07
                fg_color = CGA_PALETTE[fg_idx]
                bg_color = CGA_PALETTE[bg_idx]

                bid = self.bg_ids.get((row, col))
                if bid:
                    self.canvas.itemconfig(bid, fill=bg_color)
                tid = self.text_ids.get((row, col))
                if tid:
                    self.canvas.itemconfig(tid, text=char_str, fill=fg_color)

        def _poll_pipe(self):
            try:
                while self.pipe.poll():
                    msg = self.pipe.recv()
                    if msg == -1: # Exit
                        self.root.destroy()
                        return
                    elif isinstance(msg, dict):
                        if "cursor" in msg:
                            r, c = msg["cursor"]
                            self._update_cursor(r, c)
                        if "buffer" in msg:
                            self._render_buffer(msg["buffer"])
            except (EOFError, BrokenPipeError):
                self.root.destroy()
                return

            self.root.after(35, self._poll_pipe)

    try:
        root = tk.Tk()
        app = VideoDisplayWindow(root, pipe)
        root.mainloop()
    except Exception:
        pass


class VideoDisplayDevice(object):
    """
    Virtual Video Display Controller & Mirror for EMU8086.
    Watches memory from 0xB8000 to 0xB8F9F.
    """
    def __init__(self, memory=None, enable_gui=True):
        self.memory = memory
        self.enable_gui = enable_gui
        self.cursor_row = 0
        self.cursor_col = 0
        self.cursor_visible = True
        self.video_mode = 0x03 # Standard 80x25 Color Text Mode
        self.process = None
        self.pipe = None
        self.last_sync_time = 0

        if self.enable_gui:
            self._start_gui()

    def _start_gui(self):
        if sys.platform != 'win32' and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            return

        try:
            parent_conn, child_conn = mp.Pipe()
            self.pipe = parent_conn
            self.process = mp.Process(target=_run_video_display_gui, args=(child_conn,), daemon=True)
            self.process.start()
        except Exception as e:
            print(f"[VideoDisplayDevice] Could not launch GUI: {e}", file=sys.stderr)
            self.process = None
            self.pipe = None

    def set_memory(self, memory):
        self.memory = memory

    def set_cursor(self, row, col):
        self.cursor_row = max(0, min(VIDEO_ROWS - 1, row))
        self.cursor_col = max(0, min(VIDEO_COLS - 1, col))
        if self.pipe:
            try:
                self.pipe.send({"cursor": (self.cursor_row, self.cursor_col)})
            except (BrokenPipeError, OSError):
                self.pipe = None

    def get_cursor(self):
        return self.cursor_row, self.cursor_col

    def write_char_at(self, row, col, char_code, attr=0x07):
        """Write character and attribute directly to video memory."""
        if self.memory is None:
            return
        loc = VIDEO_MEM_BASE + 2 * (row * VIDEO_COLS + col)
        if loc + 1 < self.memory.max_space:
            self.memory.wb(loc, [hex(char_code)])
            self.memory.wb(loc + 1, [hex(attr)])

    def read_char_at(self, row, col):
        """Read character and attribute directly from video memory."""
        if self.memory is None:
            return 0, 0x07
        loc = VIDEO_MEM_BASE + 2 * (row * VIDEO_COLS + col)
        c_raw = self.memory.rb(loc)
        a_raw = self.memory.rb(loc + 1)
        try:
            c = int(c_raw[0], 16) if isinstance(c_raw, list) else int(c_raw, 16)
        except Exception:
            c = 0
        try:
            a = int(a_raw[0], 16) if isinstance(a_raw, list) else int(a_raw, 16)
        except Exception:
            a = 0x07
        return c, a

    def teletype_output(self, char_code, attr=0x07):
        """
        INT 10H / AH=0Eh: Teletype output.
        Writes character at current cursor, handles control chars, advances cursor, scrolls if needed.
        """
        if char_code == 0x0D: # Carriage Return '\r'
            self.cursor_col = 0
        elif char_code == 0x0A: # Line Feed '\n'
            self.cursor_row += 1
            if self.cursor_row >= VIDEO_ROWS:
                self.scroll_up(1, attr)
                self.cursor_row = VIDEO_ROWS - 1
        elif char_code == 0x08: # Backspace '\b'
            if self.cursor_col > 0:
                self.cursor_col -= 1
        else: # Printable character
            self.write_char_at(self.cursor_row, self.cursor_col, char_code, attr)
            self.cursor_col += 1
            if self.cursor_col >= VIDEO_COLS:
                self.cursor_col = 0
                self.cursor_row += 1
                if self.cursor_row >= VIDEO_ROWS:
                    self.scroll_up(1, attr)
                    self.cursor_row = VIDEO_ROWS - 1

        self.set_cursor(self.cursor_row, self.cursor_col)
        self.sync_display()

    def scroll_up(self, lines=1, attr=0x07):
        """Scroll the screen up by N lines."""
        if self.memory is None or lines <= 0:
            return
        row_bytes = VIDEO_COLS * 2
        for r in range(VIDEO_ROWS - lines):
            src = VIDEO_MEM_BASE + (r + lines) * row_bytes
            dst = VIDEO_MEM_BASE + r * row_bytes
            for offset in range(row_bytes):
                self.memory.wb(dst + offset, self.memory.space[src + offset])

        # Blank out bottom rows
        for r in range(VIDEO_ROWS - lines, VIDEO_ROWS):
            dst = VIDEO_MEM_BASE + r * row_bytes
            for c in range(VIDEO_COLS):
                self.memory.wb(dst + 2 * c, [hex(0x20)]) # Space
                self.memory.wb(dst + 2 * c + 1, [hex(attr)])

    def clear_screen(self, attr=0x07):
        """Clear entire 80x25 text buffer."""
        if self.memory is None:
            return
        for r in range(VIDEO_ROWS):
            for c in range(VIDEO_COLS):
                loc = VIDEO_MEM_BASE + 2 * (r * VIDEO_COLS + c)
                self.memory.wb(loc, [hex(0x20)]) # Space ' '
                self.memory.wb(loc + 1, [hex(attr)])
        self.set_cursor(0, 0)
        self.sync_display(force=True)

    def sync_display(self, force=False):
        """Mirror 0xB8000 memory buffer to GUI display."""
        if not self.pipe or not self.memory:
            return
        now = time.time()
        if not force and (now - self.last_sync_time) < 0.02: # Rate limit to 50 FPS
            return
        self.last_sync_time = now

        buffer_data = []
        for i in range(VIDEO_COLS * VIDEO_ROWS):
            loc = VIDEO_MEM_BASE + 2 * i
            c_raw = self.memory.rb(loc)
            a_raw = self.memory.rb(loc + 1)
            try:
                c = int(c_raw[0], 16) if isinstance(c_raw, list) else int(c_raw, 16)
            except Exception:
                c = 0x20
            try:
                a = int(a_raw[0], 16) if isinstance(a_raw, list) else int(a_raw, 16)
            except Exception:
                a = 0x07
            buffer_data.append((c, a))

        try:
            self.pipe.send({
                "cursor": (self.cursor_row, self.cursor_col),
                "buffer": buffer_data
            })
        except (BrokenPipeError, OSError):
            self.pipe = None

    def close(self):
        if self.pipe:
            try:
                self.pipe.send(-1)
                self.pipe.close()
            except Exception:
                pass
            self.pipe = None
        if self.process and self.process.is_alive():
            self.process.join(timeout=0.5)
            if self.process.is_alive():
                self.process.terminate()
            self.process = None


if __name__ == '__main__':
    print("Testing Video Display Device (0xB8000 Text Mode)...")
    from emulator.memory import Memory
    mem = Memory(0xFFFFF, 0x10000)
    dev = VideoDisplayDevice(memory=mem, enable_gui=True)
    time.sleep(0.5)

    dev.clear_screen(attr=0x1F) # White on Blue
    msg = "Welcome to EMU8086 Virtual Video Buffer @ 0xB8000!"
    for ch in msg:
        dev.teletype_output(ord(ch), attr=0x1F)
    dev.teletype_output(0x0D)
    dev.teletype_output(0x0A)
    dev.teletype_output(0x0A)

    colors = [0x0A, 0x0C, 0x0E, 0x0B] # Light Green, Light Red, Yellow, Light Cyan
    for i, col in enumerate(colors):
        line = f"Line {i+1}: Testing color attributes (Attr: 0x{col:02X})"
        for ch in line:
            dev.teletype_output(ord(ch), attr=col)
        dev.teletype_output(0x0D)
        dev.teletype_output(0x0A)

    dev.sync_display(force=True)
    time.sleep(2.0)
    dev.close()
    print("Video display test completed.")
