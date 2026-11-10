"""
Virtual Stepper Motor Hardware Peripheral (I/O Port 7)
Standard EMU8086 Specification

Specification:
    Port: 7 (0x07)
    Size: 8-bit register AL
    
    Bit Mapping:
        Bits 0-3: Coil Excitation Phases (A, B, C, D)
            Bit 0: Coil 1 (Phase A)
            Bit 1: Coil 2 (Phase B)
            Bit 2: Coil 3 (Phase C)
            Bit 3: Coil 4 (Phase D)
        Bits 4-6: Reserved
        Bit 7:    Ready Flag (1 = Ready to accept new command)
        
    Step Mechanics:
        Full Revolution = 32 half-steps (11.25 degrees per step).
        Rotation direction (CW / CCW) is determined by phase sequence transitions.
"""

import math
import os
import sys
import time
import multiprocessing as mp

# Comprehensive Stepper Motor Transition Map (Supports EMU8086 sequences & standard 4/8-phase unipolar/bipolar)
CW_TRANSITIONS = {
    # EMU8086 datcw half-step
    (0b0110, 0b0100): 1,
    (0b0100, 0b0011): 1,
    (0b0011, 0b0010): 1,
    (0b0010, 0b0110): 1,
    # EMU8086 datcw full-step
    (0b0001, 0b0011): 1,
    (0b0011, 0b0110): 1,
    (0b0110, 0b0000): 1,
    (0b0000, 0b0001): 1,
    # Standard 4-phase wave drive (CW)
    (0b0001, 0b0010): 1,
    (0b0010, 0b0100): 1,
    (0b0100, 0b1000): 1,
    (0b1000, 0b0001): 1,
    # Standard 4-phase full-step (CW)
    (0b0011, 0b0110): 1,
    (0b0110, 0b1100): 1,
    (0b1100, 0b1001): 1,
    (0b1001, 0b0011): 1,
    # Standard 8-phase half-step (CW)
    (0b0001, 0b0011): 1,
    (0b0011, 0b0010): 1,
    (0b0010, 0b0110): 1,
    (0b0110, 0b0100): 1,
    (0b0100, 0b1100): 1,
    (0b1100, 0b1000): 1,
    (0b1000, 0b1001): 1,
    (0b1001, 0b0001): 1,
}

CCW_TRANSITIONS = {
    # EMU8086 datccw half-step
    (0b0011, 0b0001): -1,
    (0b0001, 0b0110): -1,
    (0b0110, 0b0010): -1,
    (0b0010, 0b0011): -1,
    # EMU8086 datccw full-step
    (0b0100, 0b0110): -1,
    (0b0110, 0b0011): -1,
    (0b0011, 0b0000): -1,
    (0b0000, 0b0100): -1,
    # Standard 4-phase wave drive (CCW)
    (0b0001, 0b1000): -1,
    (0b1000, 0b0100): -1,
    (0b0100, 0b0010): -1,
    (0b0010, 0b0001): -1,
    # Standard 4-phase full-step (CCW)
    (0b0011, 0b1001): -1,
    (0b1001, 0b1100): -1,
    (0b1100, 0b0110): -1,
    (0b0110, 0b0011): -1,
    # Standard 8-phase half-step (CCW)
    (0b0001, 0b1001): -1,
    (0b1001, 0b1000): -1,
    (0b1000, 0b1100): -1,
    (0b1100, 0b0100): -1,
    (0b0100, 0b0110): -1,
    (0b0110, 0b0010): -1,
    (0b0010, 0b0011): -1,
    (0b0011, 0b0001): -1,
}


def _run_stepper_motor_gui(pipe):
    """Entry point for the isolated Stepper Motor GUI process."""
    try:
        import tkinter as tk
    except ImportError:
        return

    # Check for display environment
    if sys.platform != 'win32' and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
        return

    class StepperMotorWindow:
        def __init__(self, root, pipe):
            self.root = root
            self.pipe = pipe
            self.angle = 0.0
            self.direction_str = "IDLE"
            self.step_count = 0
            self.coils = 0

            self.root.title("EMU8086 Virtual Hardware - Stepper Motor (Port 7)")
            self.root.geometry("480x570")
            self.root.resizable(False, False)
            self.root.configure(bg="#1E1E1E")

            self._create_widgets()
            self._update_display(0, 0.0, "IDLE", 0)
            self._poll_pipe()

        def _create_widgets(self):
            # Header
            hdr = tk.Frame(self.root, bg="#1E1E1E", pady=6)
            hdr.pack(fill=tk.X)
            t_lbl = tk.Label(
                hdr,
                text="VIRTUAL STEPPER MOTOR",
                font=("Consolas", 14, "bold"),
                fg="#61AFEF",
                bg="#1E1E1E"
            )
            t_lbl.pack()
            sub_lbl = tk.Label(
                hdr,
                text="I/O Port 7 (0x0007) - 4-Phase Stepper Controller",
                font=("Consolas", 10),
                fg="#ABB2BF",
                bg="#1E1E1E"
            )
            sub_lbl.pack()

            # Canvas for Stepper Motor Dial & Rotor
            self.canvas_size = 380
            self.canvas = tk.Canvas(
                self.root,
                width=self.canvas_size,
                height=self.canvas_size,
                bg="#21252B",
                highlightthickness=1,
                highlightbackground="#3E4451"
            )
            self.canvas.pack(pady=4)

            # Dashboard
            dash = tk.Frame(self.root, bg="#282C34", padx=12, pady=8, bd=1, relief=tk.SOLID)
            dash.pack(fill=tk.X, padx=20, pady=6)

            self.status_lbl = tk.Label(
                dash,
                text="Angle: 0.0° | Direction: IDLE | Total Steps: 0",
                font=("Consolas", 10, "bold"),
                fg="#98C379",
                bg="#282C34"
            )
            self.status_lbl.pack(anchor="w")

            self.coils_lbl = tk.Label(
                dash,
                text="Active Coils: [D:0 C:0 B:0 A:0] (0x00) | Ready: 1",
                font=("Consolas", 10),
                fg="#E5C07B",
                bg="#282C34"
            )
            self.coils_lbl.pack(anchor="w")

            # Coil Indicator Pills
            pills_frame = tk.Frame(dash, bg="#282C34")
            pills_frame.pack(fill=tk.X, pady=(4, 0))

            self.coil_pills = {}
            for i, name in enumerate(["Coil A (b0)", "Coil B (b1)", "Coil C (b2)", "Coil D (b3)"]):
                f = tk.Frame(pills_frame, bg="#282C34")
                f.pack(side=tk.LEFT, expand=True)
                lbl = tk.Label(f, text=name, font=("Consolas", 8, "bold"), fg="#5C6370", bg="#282C34")
                lbl.pack()
                self.coil_pills[i] = lbl

            self._draw_static_dial()

        def _draw_static_dial(self):
            c = self.canvas
            sz = self.canvas_size
            cx, cy = sz // 2, sz // 2
            r_outer = 160
            r_inner = 135

            # Outer Motor Frame (Stator)
            c.create_oval(cx - r_outer - 12, cy - r_outer - 12, cx + r_outer + 12, cy + r_outer + 12, fill="#181A1F", outline="#3E4451", width=3)
            c.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer, fill="#282C34", outline="#4B5263", width=2)

            # Degree ticks and labels
            for deg in range(0, 360, 45):
                rad = math.radians(deg)
                x1 = cx + (r_inner + 5) * math.cos(rad)
                y1 = cy - (r_inner + 5) * math.sin(rad)
                x2 = cx + (r_outer - 5) * math.cos(rad)
                y2 = cy - (r_outer - 5) * math.sin(rad)
                c.create_line(x1, y1, x2, y2, fill="#ABB2BF", width=2)
                # Label
                lx = cx + (r_inner - 14) * math.cos(rad)
                ly = cy - (r_inner - 14) * math.sin(rad)
                c.create_text(lx, ly, text=f"{deg}°", fill="#5C6370", font=("Consolas", 8))

            # Small 11.25 deg ticks (32 steps)
            for step_idx in range(32):
                deg = step_idx * 11.25
                rad = math.radians(deg)
                x1 = cx + (r_inner + 12) * math.cos(rad)
                y1 = cy - (r_inner + 12) * math.sin(rad)
                x2 = cx + (r_outer - 8) * math.cos(rad)
                y2 = cy - (r_outer - 8) * math.sin(rad)
                c.create_line(x1, y1, x2, y2, fill="#3E4451", width=1)

            # Stator Poles (Coils A, B, C, D)
            # Coil A: Right (0°)
            # Coil B: Top (90°)
            # Coil C: Left (180°)
            # Coil D: Bottom (270°)
            self.coil_ovals = {}
            coil_positions = [
                (0, cx + 110, cy, "COIL A"),
                (1, cx, cy - 110, "COIL B"),
                (2, cx - 110, cy, "COIL C"),
                (3, cx, cy + 110, "COIL D")
            ]
            for idx, px, py, tag in coil_positions:
                oid = c.create_oval(px - 14, py - 14, px + 14, py + 14, fill="#1B1D23", outline="#4B5263", width=2)
                self.coil_ovals[idx] = oid
                c.create_text(px, py, text=str(idx), fill="#ABB2BF", font=("Consolas", 9, "bold"))

        def _update_display(self, coils, angle, direction_str, step_count):
            self.coils = coils & 0x0F
            self.angle = angle % 360.0
            self.direction_str = direction_str
            self.step_count = step_count

            # Update labels
            self.status_lbl.config(
                text=f"Angle: {self.angle:0.1f}° | Direction: {self.direction_str} | Steps: {self.step_count}"
            )
            b3 = (self.coils >> 3) & 1
            b2 = (self.coils >> 2) & 1
            b1 = (self.coils >> 1) & 1
            b0 = (self.coils >> 0) & 1
            self.coils_lbl.config(
                text=f"Active Coils: [D:{b3} C:{b2} B:{b1} A:{b0}] (0x{self.coils:02X}) | Ready: 1"
            )

            # Update coil pills and canvas pole glows
            active_color = "#E5C07B"
            for i in range(4):
                is_active = bool((self.coils >> i) & 1)
                pill = self.coil_pills.get(i)
                if pill:
                    pill.config(fg="#98C379" if is_active else "#5C6370")
                oid = self.coil_ovals.get(i)
                if oid:
                    fill = "#FF9800" if is_active else "#1B1D23"
                    outline = "#FFE082" if is_active else "#4B5263"
                    self.canvas.itemconfig(oid, fill=fill, outline=outline)

            # Redraw Rotor and Needle Arrow
            self._draw_rotor()

        def _draw_rotor(self):
            c = self.canvas
            sz = self.canvas_size
            cx, cy = sz // 2, sz // 2
            r_rotor = 65

            # Delete old dynamic items
            c.delete("rotor_dynamic")

            # Rotor Body
            c.create_oval(
                cx - r_rotor, cy - r_rotor, cx + r_rotor, cy + r_rotor,
                fill="#2C313C", outline="#61AFEF", width=2,
                tags="rotor_dynamic"
            )

            # Arrow Pointer
            # Angle: 0 deg = Up (North), rotating clockwise
            # Standard screen math: angle from top:
            rad = math.radians(90 - self.angle)
            tip_x = cx + (r_rotor + 35) * math.cos(rad)
            tip_y = cy - (r_rotor + 35) * math.sin(rad)

            # Tail points for triangular arrow
            rad_left = math.radians(90 - self.angle + 140)
            rad_right = math.radians(90 - self.angle - 140)
            tail_l_x = cx + 22 * math.cos(rad_left)
            tail_l_y = cy - 22 * math.sin(rad_left)
            tail_r_x = cx + 22 * math.cos(rad_right)
            tail_r_y = cy - 22 * math.sin(rad_right)

            # Draw arrow polygon
            c.create_polygon(
                tip_x, tip_y, tail_l_x, tail_l_y, cx, cy, tail_r_x, tail_r_y,
                fill="#E06C75", outline="#BE5046", width=2,
                tags="rotor_dynamic"
            )

            # Center cap
            c.create_oval(
                cx - 15, cy - 15, cx + 15, cy + 15,
                fill="#1E1E1E", outline="#98C379", width=2,
                tags="rotor_dynamic"
            )
            c.create_oval(
                cx - 5, cy - 5, cx + 5, cy + 5,
                fill="#98C379", outline="",
                tags="rotor_dynamic"
            )

        def _poll_pipe(self):
            try:
                while self.pipe.poll():
                    msg = self.pipe.recv()
                    if msg == -1: # Exit
                        self.root.destroy()
                        return
                    elif isinstance(msg, dict):
                        self._update_display(
                            coils=msg.get("coils", 0),
                            angle=msg.get("angle", 0.0),
                            direction_str=msg.get("direction", "IDLE"),
                            step_count=msg.get("step_count", 0)
                        )
            except (EOFError, BrokenPipeError):
                self.root.destroy()
                return

            self.root.after(25, self._poll_pipe)

    try:
        root = tk.Tk()
        app = StepperMotorWindow(root, pipe)
        root.mainloop()
    except Exception:
        pass


class StepperMotorDevice(object):
    """
    Virtual Stepper Motor Hardware Device for EMU8086.
    Mapped to I/O Port 7.
    """
    PORT = 7
    DEGREES_PER_STEP = 11.25 # 32 steps per 360 deg

    def __init__(self, enable_gui=True):
        self.enable_gui = enable_gui
        self.state = 0 # Current coil excitation byte
        self.prev_coils = None
        self.angle = 0.0
        self.step_count = 0
        self.direction_str = "IDLE"
        self.process = None
        self.pipe = None

        if self.enable_gui:
            self._start_gui()

    def _start_gui(self):
        """Start isolated visualizer process."""
        if sys.platform != 'win32' and not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            return

        try:
            parent_conn, child_conn = mp.Pipe()
            self.pipe = parent_conn
            self.process = mp.Process(target=_run_stepper_motor_gui, args=(child_conn,), daemon=True)
            self.process.start()
        except Exception as e:
            print(f"[StepperMotorDevice] Could not launch GUI: {e}", file=sys.stderr)
            self.process = None
            self.pipe = None

    def write(self, value, byte_size=1):
        """
        Handle 'OUT 7, AL'.
        Parses 4-bit coil excitation, calculates step rotation, updates visualizer.
        """
        coils = value & 0x0F
        self.state = coils

        if self.prev_coils is not None:
            trans = (self.prev_coils, coils)
            if trans in CW_TRANSITIONS:
                step_delta = 1
                self.angle = (self.angle + self.DEGREES_PER_STEP) % 360.0
                self.step_count += 1
                self.direction_str = "CW"
            elif trans in CCW_TRANSITIONS:
                step_delta = -1
                self.angle = (self.angle - self.DEGREES_PER_STEP) % 360.0
                self.step_count += 1
                self.direction_str = "CCW"
            elif self.prev_coils != coils:
                # Fallback to CW if non-zero change
                self.angle = (self.angle + self.DEGREES_PER_STEP) % 360.0
                self.step_count += 1
                self.direction_str = "CW"

        self.prev_coils = coils

        if self.pipe:
            try:
                self.pipe.send({
                    "coils": self.state,
                    "angle": self.angle,
                    "direction": self.direction_str,
                    "step_count": self.step_count
                })
            except (BrokenPipeError, OSError):
                self.pipe = None

    def read(self, byte_size=1):
        """
        Handle 'IN AL, 7'.
        Bit 7 is the Ready flag: always set to 1 when ready.
        Lower bits return the current coil excitation status.
        """
        return 0x80 | (self.state & 0x0F)

    def close(self):
        """Clean up process."""
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


# Standalone demonstration
if __name__ == '__main__':
    print("Launching EMU8086 Virtual Stepper Motor Interactive Test...")
    dev = StepperMotorDevice(enable_gui=True)
    time.sleep(0.5)

    # Standard EMU8086 clockwise half-step sequence
    cw_half_steps = [0b0110, 0b0100, 0b0011, 0b0010]
    # Standard counter-clockwise half-step sequence
    ccw_half_steps = [0b0011, 0b0001, 0b0110, 0b0010]

    try:
        print("\n1. Rotating Clockwise (CW) for 16 steps...")
        for i in range(16):
            coil = cw_half_steps[i % len(cw_half_steps)]
            dev.write(coil)
            print(f"Step {i+1}: Coil=0b{coil:04b} -> Angle={dev.angle:0.1f}° [{dev.direction_str}]")
            time.sleep(0.15)

        time.sleep(0.5)

        print("\n2. Rotating Counter-Clockwise (CCW) for 16 steps...")
        for i in range(16):
            coil = ccw_half_steps[i % len(ccw_half_steps)]
            dev.write(coil)
            print(f"Step {i+1}: Coil=0b{coil:04b} -> Angle={dev.angle:0.1f}° [{dev.direction_str}]")
            time.sleep(0.15)

    except KeyboardInterrupt:
        pass
    finally:
        dev.close()
        print("\nStepper motor demonstration finished.")
