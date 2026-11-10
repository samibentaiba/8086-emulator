"""
Virtual Traffic Light Hardware Peripheral (I/O Port 4)
Standard EMU8086 Specification

Specification:
    Port: 4 (0x04)
    Size: 12-bit active word (16-bit register AX / 8-bit register AL)
    
    Bit Mapping:
        Bits 0-2:   Direction 1 (North / Top)
            Bit 0: Red
            Bit 1: Yellow
            Bit 2: Green
        Bits 3-5:   Direction 2 (West / Left)
            Bit 3: Red
            Bit 4: Yellow
            Bit 5: Green
        Bits 6-8:   Direction 3 (South / Bottom)
            Bit 6: Red
            Bit 7: Yellow
            Bit 8: Green
        Bits 9-11:  Direction 4 (East / Right)
            Bit 9: Red
            Bit 10: Yellow
            Bit 11: Green
        Bits 12-15: Reserved (Unused / 0)
"""

import os
import sys
import time
import multiprocessing as mp


def _run_traffic_light_gui(pipe):
    """Entry point for the isolated GUI process."""
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        return

    # Check for display
    if sys.platform != 'win32' and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        return

    class TrafficLightsWindow:
        def __init__(self, root, pipe):
            self.root = root
            self.pipe = pipe
            self.state = 0
            self.root.title("EMU8086 Virtual Hardware - Traffic Lights (Port 4)")
            self.root.geometry("540x620")
            self.root.resizable(False, False)
            self.root.configure(bg="#1E1E1E")

            self._create_widgets()
            self._update_display(0)
            self._poll_pipe()

        def _create_widgets(self):
            # Header Title Frame
            header_frame = tk.Frame(self.root, bg="#1E1E1E", pady=6)
            header_frame.pack(fill=tk.X)
            title_lbl = tk.Label(
                header_frame,
                text="4-WAY TRAFFIC LIGHT CONTROLLER",
                font=("Consolas", 14, "bold"),
                fg="#61AFEF",
                bg="#1E1E1E"
            )
            title_lbl.pack()
            subtitle = tk.Label(
                header_frame,
                text="I/O Port 4 (0x0004) - 12-Bit LED Array",
                font=("Consolas", 10),
                fg="#ABB2BF",
                bg="#1E1E1E"
            )
            subtitle.pack()

            # Canvas for intersection and traffic lights
            self.canvas_size = 440
            self.canvas = tk.Canvas(
                self.root,
                width=self.canvas_size,
                height=self.canvas_size,
                bg="#21252B",
                highlightthickness=1,
                highlightbackground="#3E4451"
            )
            self.canvas.pack(pady=4)

            self.led_ids = {} # (direction_idx, color_idx) -> canvas oval id
            self._draw_intersection()

            # Dashboard Info Frame
            dash = tk.Frame(self.root, bg="#282C34", padx=10, pady=8, bd=1, relief=tk.SOLID)
            dash.pack(fill=tk.X, padx=20, pady=6)

            # Row 1: Hex and binary status
            self.val_label = tk.Label(
                dash,
                text="Port 4 Value: 0x0000 (0)",
                font=("Consolas", 11, "bold"),
                fg="#98C379",
                bg="#282C34"
            )
            self.val_label.pack(anchor="w")

            self.bin_label = tk.Label(
                dash,
                text="Bits [11-0]: 000 000 000 000",
                font=("Consolas", 10),
                fg="#E5C07B",
                bg="#282C34"
            )
            self.bin_label.pack(anchor="w")

            # Row 2: Status badges for all 4 directions
            status_frame = tk.Frame(dash, bg="#282C34")
            status_frame.pack(fill=tk.X, pady=(4, 0))

            self.dir_labels = {}
            dirs = [("North", "N (0-2)"), ("West", "W (3-5)"), ("South", "S (6-8)"), ("East", "E (9-11)")]
            for idx, (name, tag) in enumerate(dirs):
                f = tk.Frame(status_frame, bg="#282C34")
                f.pack(side=tk.LEFT, expand=True)
                tag_lbl = tk.Label(f, text=tag, font=("Consolas", 9, "bold"), fg="#ABB2BF", bg="#282C34")
                tag_lbl.pack()
                state_lbl = tk.Label(f, text="OFF", font=("Consolas", 9, "bold"), fg="#5C6370", bg="#282C34")
                state_lbl.pack()
                self.dir_labels[idx] = state_lbl

        def _draw_intersection(self):
            c = self.canvas
            sz = self.canvas_size
            half = sz // 2
            rw = 130 # road width
            r_half = rw // 2

            # Grass corners
            c.create_rectangle(0, 0, half - r_half, half - r_half, fill="#2D4F36", outline="")
            c.create_rectangle(half + r_half, 0, sz, half - r_half, fill="#2D4F36", outline="")
            c.create_rectangle(0, half + r_half, half - r_half, sz, fill="#2D4F36", outline="")
            c.create_rectangle(half + r_half, half + r_half, sz, sz, fill="#2D4F36", outline="")

            # Roads (Asphalt)
            c.create_rectangle(half - r_half, 0, half + r_half, sz, fill="#1B1D23", outline="")
            c.create_rectangle(0, half - r_half, sz, half + r_half, fill="#1B1D23", outline="")

            # Lane markings (dashed yellow centerlines)
            c.create_line(half, 0, half, half - r_half, fill="#E5C07B", width=2, dash=(10, 6))
            c.create_line(half, half + r_half, half, sz, fill="#E5C07B", width=2, dash=(10, 6))
            c.create_line(0, half, half - r_half, half, fill="#E5C07B", width=2, dash=(10, 6))
            c.create_line(half + r_half, half, sz, half, fill="#E5C07B", width=2, dash=(10, 6))

            # Zebra crossings (White stripes)
            stripe_w = 4
            for x in range(half - r_half + 4, half + r_half - 4, 10):
                c.create_line(x, half - r_half - 2, x, half - r_half - 12, fill="#E6EDF3", width=stripe_w)
                c.create_line(x, half + r_half + 2, x, half + r_half + 12, fill="#E6EDF3", width=stripe_w)
            for y in range(half - r_half + 4, half + r_half - 4, 10):
                c.create_line(half - r_half - 2, y, half - r_half - 12, y, fill="#E6EDF3", width=stripe_w)
                c.create_line(half + r_half + 2, y, half + r_half + 12, y, fill="#E6EDF3", width=stripe_w)

            # Traffic Light Housings & LEDs
            # Dir 0: North (Top, facing traffic)
            self._create_light_box(
                dir_idx=0,
                bx=half - 50, by=half - r_half - 75,
                orientation="vertical",
                label="NORTH"
            )

            # Dir 1: West (Left)
            self._create_light_box(
                dir_idx=1,
                bx=half - r_half - 75, by=half + 20,
                orientation="horizontal",
                label="WEST"
            )

            # Dir 2: South (Bottom)
            self._create_light_box(
                dir_idx=2,
                bx=half + 26, by=half + r_half + 15,
                orientation="vertical",
                label="SOUTH"
            )

            # Dir 3: East (Right)
            self._create_light_box(
                dir_idx=3,
                bx=half + r_half + 15, by=half - 46,
                orientation="horizontal",
                label="EAST"
            )

        def _create_light_box(self, dir_idx, bx, by, orientation, label):
            c = self.canvas
            radius = 7
            spacing = 20

            if orientation == "vertical":
                box_w = 26
                box_h = 66
                c.create_rectangle(bx, by, bx + box_w, by + box_h, fill="#0F1012", outline="#4B5263", width=2)
                c.create_text(bx + box_w // 2, by - 8, text=label, fill="#61AFEF", font=("Consolas", 8, "bold"))
                # Red, Yellow, Green vertically
                colors = ["red", "yellow", "green"]
                for i, col in enumerate(colors):
                    cy = by + 12 + i * spacing
                    cx = bx + box_w // 2
                    oid = c.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#282C34", outline="#000000", width=1)
                    self.led_ids[(dir_idx, i)] = oid
            else: # horizontal
                box_w = 66
                box_h = 26
                c.create_rectangle(bx, by, bx + box_w, by + box_h, fill="#0F1012", outline="#4B5263", width=2)
                c.create_text(bx + box_w // 2, by - 8, text=label, fill="#61AFEF", font=("Consolas", 8, "bold"))
                # Red, Yellow, Green horizontally
                colors = ["red", "yellow", "green"]
                for i, col in enumerate(colors):
                    cx = bx + 12 + i * spacing
                    cy = by + box_h // 2
                    oid = c.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#282C34", outline="#000000", width=1)
                    self.led_ids[(dir_idx, i)] = oid

        def _update_display(self, value):
            self.state = value & 0x0FFF
            hex_str = f"0x{value:04X}"
            self.val_label.config(text=f"Port 4 Value: {hex_str} ({value})")

            # Binary string representation
            b_str = f"{self.state:012b}"
            # Format in groups of 3 (East, South, West, North)
            # b_str is [11..0]: East(11..9) South(8..6) West(5..3) North(2..0)
            e_bits = b_str[0:3]
            s_bits = b_str[3:6]
            w_bits = b_str[6:9]
            n_bits = b_str[9:12]
            self.bin_label.config(text=f"Bits [11-0]: E:{e_bits} S:{s_bits} W:{w_bits} N:{n_bits}")

            # Define ON / OFF colors
            # Color index 0: Red, 1: Yellow, 2: Green
            color_palettes = [
                ("#FF2020", "#380A0A", "#FF6B6B"), # Red ON, OFF, outline
                ("#FFD700", "#383008", "#FFE566"), # Yellow ON, OFF, outline
                ("#00E640", "#083310", "#5CFF8D")  # Green ON, OFF, outline
            ]

            # Update each direction
            dir_names = ["North", "West", "South", "East"]
            for d in range(4):
                d_status = []
                for c_idx in range(3):
                    bit_pos = d * 3 + c_idx
                    is_on = bool((self.state >> bit_pos) & 1)
                    on_col, off_col, out_col = color_palettes[c_idx]
                    oid = self.led_ids.get((d, c_idx))
                    if oid:
                        fill = on_col if is_on else off_col
                        outline = out_col if is_on else "#111111"
                        self.canvas.itemconfig(oid, fill=fill, outline=outline)

                    if is_on:
                        d_status.append(["RED", "YEL", "GRN"][c_idx])

                lbl = self.dir_labels.get(d)
                if lbl:
                    if d_status:
                        stat_text = "+".join(d_status)
                        stat_color = "#FF6B6B" if "RED" in d_status else ("#FFD700" if "YEL" in d_status else "#00E640")
                    else:
                        stat_text = "OFF"
                        stat_color = "#5C6370"
                    lbl.config(text=stat_text, fg=stat_color)

        def _poll_pipe(self):
            try:
                while self.pipe.poll():
                    cmd = self.pipe.recv()
                    if cmd == -1: # Termination signal
                        self.root.destroy()
                        return
                    elif isinstance(cmd, int):
                        self._update_display(cmd)
            except (EOFError, BrokenPipeError):
                self.root.destroy()
                return

            self.root.after(25, self._poll_pipe)

    try:
        root = tk.Tk()
        app = TrafficLightsWindow(root, pipe)
        root.mainloop()
    except Exception as e:
        pass


class TrafficLightsDevice(object):
    """
    Virtual Traffic Lights Hardware Device for EMU8086.
    Mapped to I/O Port 4.
    """
    PORT = 4

    def __init__(self, enable_gui=True):
        self.state = 0
        self.enable_gui = enable_gui
        self.process = None
        self.pipe = None
        if self.enable_gui:
            self._start_gui()

    def _start_gui(self):
        """Spawn the independent GUI process via pipe."""
        # Check if headless / no display
        if sys.platform != 'win32' and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            return

        try:
            parent_conn, child_conn = mp.Pipe()
            self.pipe = parent_conn
            self.process = mp.Process(target=_run_traffic_light_gui, args=(child_conn,), daemon=True)
            self.process.start()
        except Exception as e:
            print(f"[TrafficLightsDevice] Could not launch GUI: {e}", file=sys.stderr)
            self.process = None
            self.pipe = None

    def write(self, value, byte_size=2):
        """
        Handle OUT 4, AX or OUT 4, AL.
        Updates internal state and forwards to visual display.
        """
        if byte_size == 1:
            self.state = (self.state & 0xFF00) | (value & 0xFF)
        else:
            self.state = value & 0xFFFF

        if self.pipe:
            try:
                self.pipe.send(self.state)
            except (BrokenPipeError, OSError):
                self.pipe = None

    def read(self, byte_size=2):
        """
        Handle IN AL, 4 or IN AX, 4.
        Returns the current state register value.
        """
        if byte_size == 1:
            return self.state & 0xFF
        return self.state & 0xFFFF

    def close(self):
        """Close GUI process and clean up."""
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


# Interactive standalone demo
if __name__ == '__main__':
    print("Launching EMU8086 Virtual Traffic Lights Interactive Test...")
    dev = TrafficLightsDevice(enable_gui=True)
    time.sleep(0.5)

    # Standard EMU8086 traffic sequence demonstration
    test_patterns = [
        (0x0249, "All Red (0000 0010 0100 1001b)"),
        (0x020C, "North-South Green, East-West Red (0000 0010 0000 1100b)"),
        (0x0212, "North-South Yellow, East-West Red (0000 0010 0001 0010b)"),
        (0x0249, "All Red clearance (0000 0010 0100 1001b)"),
        (0x0849, "East-West Green, North-South Red (0000 1000 0100 1001b)"),
        (0x0449, "East-West Yellow, North-South Red (0000 0100 0100 1001b)"),
        (0x0FFF, "All 12 LEDs Lit (Test Pattern 0x0FFF)"),
        (0x0000, "All LEDs Dimmed / Off")
    ]

    try:
        for val, desc in test_patterns:
            print(f"Setting Port 4 = 0x{val:04X} -> {desc}")
            dev.write(val, byte_size=2)
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        dev.close()
        print("Demo completed.")
