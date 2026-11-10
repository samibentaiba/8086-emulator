"""
Antigravity 8086 Full-Featured Terminal User Interface (TUI)
Neovim / GDB TUI style interactive debugger and virtual hardware monitor.
"""

import os
import re
import sys
import time

try:
    import curses
except ImportError:
    curses = None

from emulator.assembler import Assembler, to_decimal
from emulator.cpu import CPU
from emulator.memory import Memory
from emulator.pipeline_units import bus_interface_unit, execution_unit
from emulator.peripherals.video_display import VIDEO_MEM_BASE
from emulator.peripherals.manager import PeripheralManager

MEMORY_SIZE = int('FFFFF', 16)
SEGMENT_SIZE = int('10000', 16)
INSTRUCTION_QUEUE_SIZE = 6

SEG_INIT = {
    'DS': int('2000', 16),
    'CS': int('3000', 16),
    'SS': int('5000', 16),
    'ES': int('7000', 16)
}


class EmulatorTUI:
    def __init__(self, asm_filepath, enable_gui_windows=False):
        self.asm_filepath = asm_filepath
        self.enable_gui_windows = enable_gui_windows
        self.asm_code = ""
        self.instructions = []
        self.breakpoints = set()
        self.disasm_cursor_idx = 0
        self.follow_ip = True
        self.running = False
        self.show_help = False
        self.step_delay = 0.05  # seconds between steps in run mode
        self.last_step_time = 0
        self.status_msg = "Initialized. Press [s] to step, [c] to run, [Tab] to switch pane, [?] for help."

        # Active pane: 'disasm' or 'memory'
        self.focused_pane = 'disasm'

        # Memory inspector state
        self.mem_segments = ['DS', 'CS', 'SS', 'ES', 'VIDEO']
        self.mem_seg_idx = 0
        self.mem_offset = 0
        self.mem_view_mode = 'hex'  # 'hex' or 'stack'

        # Previous register state for change highlighting
        self.prev_regs = {}

        # Load and initialize CPU
        self._load_file()
        self._init_cpu()

    def _load_file(self):
        with open(self.asm_filepath, 'r', encoding='utf-8') as f:
            self.asm_code = f.read()

    def _init_cpu(self):
        # Reset peripheral manager singleton to ensure clean state
        PeripheralManager.reset_instance()
        PeripheralManager.get_instance(enable_gui=self.enable_gui_windows)

        # Reset and compile
        self.assembler = Assembler(SEG_INIT)
        try:
            self.exe_file = self.assembler.compile(self.asm_code)
        except Exception as err:
            print(f"\n{err}\n")
            sys.exit(1)
        self.memory = Memory(MEMORY_SIZE, SEGMENT_SIZE)
        self.memory.load(self.exe_file)

        self.BIU = bus_interface_unit.bus_interface_unit(INSTRUCTION_QUEUE_SIZE, self.exe_file, self.memory)
        self.EU = execution_unit.execution_unit(self.BIU, int_msg=False)
        self.cpu = CPU(self.BIU, self.EU, gui_mode=False)
        self.cpu.tui_mode = True  # Suppress interactive debug() prompt in TUI mode

        # Cache instructions list with clean formatting
        cs_space = self.exe_file.space.get('CS', [])
        cs_len = self.exe_file.seg_len.get('CS', len(cs_space))
        self.instructions = []
        for idx in range(cs_len):
            item = cs_space[idx]
            if item != ['0']:
                opcode = item[0]
                opds = ", ".join(item[1:]) if len(item) > 1 else ""
                self.instructions.append((idx, opcode, opds))

        self.prev_regs = self._snapshot_regs()
        self.running = False
        self.disasm_cursor_idx = 0
        self.follow_ip = True

    def _snapshot_regs(self):
        snap = {}
        for k, v in self.EU.reg.items():
            snap[k] = v
        for k, v in self.BIU.reg.items():
            snap[k] = v
        snap['CF'] = self.EU.FR.carry
        snap['ZF'] = self.EU.FR.zero
        snap['SF'] = self.EU.FR.sign
        snap['OF'] = self.EU.FR.overflow
        snap['PF'] = self.EU.FR.parity
        snap['AF'] = self.EU.FR.auxiliary
        snap['IF'] = self.EU.FR.interrupt
        snap['DF'] = self.EU.FR.direction
        return snap

    def step(self):
        if not self.cpu.check_done():
            self.prev_regs = self._snapshot_regs()
            self.cpu.iterate(debug=False)
            current_ip = self.BIU.reg.get('IP', 0)
            if self.follow_ip:
                for idx, (offset, _, _) in enumerate(self.instructions):
                    if offset == current_ip:
                        self.disasm_cursor_idx = idx
                        break
            if current_ip in self.breakpoints:
                self.running = False
                self.status_msg = f"Breakpoint hit at IP={current_ip:04X}h!"
            return True
        else:
            self.running = False
            self.status_msg = f"Program terminated. Cycles: {self.cpu.cycle_count}."
            return False

    def run(self):
        if curses is None:
            print("\nError: The 'curses' library is required to run the Terminal User Interface.")
            if sys.platform == 'win32':
                print("On Windows, please install windows-curses via:")
                print("    pip install windows-curses\n")
            else:
                print("Please install curses or use a Python distribution with curses support.\n")
            sys.exit(1)
        try:
            curses.wrapper(self._main_loop)
        finally:
            PeripheralManager.reset_instance()

    def _init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        # Pair definitions
        curses.init_pair(1, curses.COLOR_CYAN, -1)     # Borders & Headers
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Success / Active / Values
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Warning / Changes / Addresses
        curses.init_pair(4, curses.COLOR_RED, -1)      # Breakpoints / Errors / Halt
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Highlight Cursor Current IP
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Status Bar / Headers
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)  # Segment / Registers
        curses.init_pair(8, curses.COLOR_BLUE, -1)     # Dim labels
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Selected Row Cursor

    def _safe_addstr(self, win, y, x, text, attr=0):
        try:
            max_y, max_x = win.getmaxyx()
            if 0 <= y < max_y and 0 <= x < max_x:
                avail = max_x - x - 1
                if avail > 0:
                    win.addstr(y, x, text[:avail], attr)
        except curses.error:
            pass

    def _draw_box(self, win, y, x, h, w, title="", is_focused=False):
        border_attr = (curses.color_pair(3) | curses.A_BOLD) if is_focused else curses.color_pair(1)
        for row in range(y, y + h):
            self._safe_addstr(win, row, x, "│", border_attr)
            self._safe_addstr(win, row, x + w - 1, "│", border_attr)
        for col in range(x, x + w):
            self._safe_addstr(win, y, col, "─", border_attr)
            self._safe_addstr(win, y + h - 1, col, "─", border_attr)
        # Corners
        self._safe_addstr(win, y, x, "┌", border_attr)
        self._safe_addstr(win, y, x + w - 1, "┐", border_attr)
        self._safe_addstr(win, y + h - 1, x, "└", border_attr)
        self._safe_addstr(win, y + h - 1, x + w - 1, "┘", border_attr)

        if title:
            focused_indicator = " [FOCUSED]" if is_focused else ""
            title_text = f" {title}{focused_indicator} "
            self._safe_addstr(win, y, x + 2, title_text, border_attr | curses.A_BOLD)

    def _main_loop(self, stdscr):
        self._init_colors()
        curses.curs_set(0) # Hide blinking cursor
        stdscr.nodelay(True) # Non-blocking input
        stdscr.timeout(30)   # 30ms timeout for smooth execution

        while True:
            max_y, max_x = stdscr.getmaxyx()
            stdscr.erase()

            if max_y < 22 or max_x < 80:
                self._safe_addstr(
                    stdscr, 1, 1,
                    f"Terminal too small ({max_x}x{max_y}). Please resize to at least 80x24.",
                    curses.color_pair(4) | curses.A_BOLD
                )
                stdscr.refresh()
                key = stdscr.getch()
                if key in [ord('q'), ord('Q')]:
                    break
                time.sleep(0.05)
                continue

            # Header
            self._render_header(stdscr, max_x)

            # Pane Dimensions
            left_w = min(50, int(max_x * 0.44))
            right_w = max_x - left_w - 1
            main_h = max_y - 4

            disasm_h = main_h
            reg_h = min(10, max(8, main_h // 3))
            telem_h = min(9, max(7, main_h // 3))
            mem_h = main_h - reg_h - telem_h

            # Render Panes
            self._render_disassembly(stdscr, 1, 0, disasm_h, left_w)
            self._render_registers(stdscr, 1, left_w, reg_h, right_w)
            self._render_telemetry(stdscr, 1 + reg_h, left_w, telem_h, right_w)
            if self.mem_view_mode == 'stack':
                self._render_stack_view(stdscr, 1 + reg_h + telem_h, left_w, mem_h, right_w)
            else:
                self._render_memory(stdscr, 1 + reg_h + telem_h, left_w, mem_h, right_w)

            # Footer
            self._render_footer(stdscr, max_y, max_x)

            # Floating Help Modal (if active)
            if self.show_help:
                self._render_help_modal(stdscr, max_y, max_x)

            stdscr.refresh()

            # Handle Continuous Running
            if self.running:
                now = time.time()
                if now - self.last_step_time >= self.step_delay:
                    self.step()
                    self.last_step_time = now

            # Process User Input Keybindings
            key = stdscr.getch()
            if key != -1:
                if not self._handle_key(stdscr, key):
                    break

    def _render_header(self, win, max_x):
        state_str = "RUNNING" if self.running else ("HALTED" if self.cpu.check_done() else "PAUSED")
        state_color = curses.color_pair(2) if self.running else (curses.color_pair(4) if self.cpu.check_done() else curses.color_pair(3))
        
        # Truncate long paths: show up to last 2 path components
        parts = self.asm_filepath.replace('\\', '/').split('/')
        filename = '/'.join(parts[-2:]) if len(parts) > 2 else self.asm_filepath
        # Add execution speed to header
        speed_str = f"{1.0/self.step_delay:.0f} steps/s" if self.step_delay > 0 else "Max"
        cs = self.BIU.reg.get('CS', 0)
        ip = self.BIU.reg.get('IP', 0)
        hdr_text = f" 8086 TUI │ {filename} │ CS:IP={cs:04X}:{ip:04X}h │ ⚡{speed_str} │ Cycles:{self.cpu.cycle_count} │ "
        self._safe_addstr(win, 0, 0, hdr_text, curses.color_pair(6) | curses.A_BOLD)
        self._safe_addstr(win, 0, len(hdr_text), f"[{state_str}] ", state_color | curses.A_BOLD)

        used = len(hdr_text) + len(state_str) + 3
        if max_x > used:
            self._safe_addstr(win, 0, used, " " * (max_x - used), curses.color_pair(6))

    def _render_disassembly(self, win, y, x, h, w):
        is_focused = (self.focused_pane == 'disasm')
        self._draw_box(win, y, x, h, w, "DISASSEMBLY (CS:IP)", is_focused)
        current_ip = self.BIU.reg.get('IP', 0)
        content_h = max(1, h - 2)

        if not self.instructions:
            self._safe_addstr(win, y + 1, x + 2, "No instructions loaded.", curses.color_pair(8))
            return

        cursor_idx = max(0, min(len(self.instructions) - 1, self.disasm_cursor_idx))
        start_idx = max(0, cursor_idx - content_h // 2)
        end_idx = min(len(self.instructions), start_idx + content_h)

        for line_row, i in enumerate(range(start_idx, end_idx)):
            offset, opcode, opds = self.instructions[i]
            is_current = (offset == current_ip)
            is_selected = (i == cursor_idx and is_focused)
            is_break = (offset in self.breakpoints)

            bp_mark = "●" if is_break else " "
            ptr_mark = "▶" if is_current else " "

            line_text = f"{bp_mark}{ptr_mark} {offset:04X}: {opcode:<6} {opds}"

            attr = curses.A_NORMAL
            if is_current and is_selected:
                attr = curses.color_pair(5) | curses.A_BOLD | curses.A_UNDERLINE
            elif is_current:
                attr = curses.color_pair(5) | curses.A_BOLD
            elif is_selected:
                attr = curses.color_pair(9) | curses.A_BOLD
            elif is_break:
                attr = curses.color_pair(4) | curses.A_BOLD
            else:
                attr = curses.color_pair(2) if i % 2 == 0 else curses.A_NORMAL

            self._safe_addstr(win, y + 1 + line_row, x + 1, line_text.ljust(w - 2), attr)

    def _render_registers(self, win, y, x, h, w):
        self._draw_box(win, y, x, h, w, "CPU REGISTERS & FLAGS")

        eu_reg = self.EU.reg
        ax = eu_reg.get('AX', 0)
        bx = eu_reg.get('BX', 0)
        cx = eu_reg.get('CX', 0)
        dx = eu_reg.get('DX', 0)

        def get_reg_attr(name, val):
            if name in self.prev_regs and self.prev_regs[name] != val:
                return curses.color_pair(3) | curses.A_BOLD  # Yellow changed
            return curses.color_pair(2) | curses.A_BOLD       # Green normal

        # Row 1: General Data Registers
        col = x + 2
        for rname, rval in [('AX', ax), ('BX', bx), ('CX', cx), ('DX', dx)]:
            attr = get_reg_attr(rname, rval)
            text = f" {rname}: 0x{rval:04X} "
            self._safe_addstr(win, y + 1, col, text, attr)
            col += len(text) + 1

        # Row 2: Sub-registers (AH/AL, BH/BL, etc.)
        r2 = f" AH:{ax>>8:02X} AL:{ax&0xFF:02X}  BH:{bx>>8:02X} BL:{bx&0xFF:02X}  CH:{cx>>8:02X} CL:{cx&0xFF:02X}  DH:{dx>>8:02X} DL:{dx&0xFF:02X}"
        self._safe_addstr(win, y + 2, x + 2, r2, curses.color_pair(8))

        # Row 3: Pointer & Index Registers
        sp = eu_reg.get('SP', 0)
        bp = eu_reg.get('BP', 0)
        si = eu_reg.get('SI', 0)
        di = eu_reg.get('DI', 0)
        ip = self.BIU.reg.get('IP', 0)

        col = x + 2
        for rname, rval in [('SP', sp), ('BP', bp), ('SI', si), ('DI', di), ('IP', ip)]:
            attr = get_reg_attr(rname, rval)
            text = f"{rname}:0x{rval:04X} "
            self._safe_addstr(win, y + 4, col, text, attr)
            col += len(text) + 1

        # Row 4: Segment Registers
        cs = self.BIU.reg.get('CS', 0)
        ds = self.BIU.reg.get('DS', 0)
        ss = self.BIU.reg.get('SS', 0)
        es = self.BIU.reg.get('ES', 0)
        col = x + 2
        for rname, rval in [('CS', cs), ('DS', ds), ('SS', ss), ('ES', es)]:
            attr = get_reg_attr(rname, rval)
            text = f"{rname}:0x{rval:04X} "
            self._safe_addstr(win, y + 5, col, text, attr)
            col += len(text) + 2

        # Row 5: Flags Register
        fr = self.EU.FR
        flags = [
            ("CF", fr.carry), ("ZF", fr.zero), ("SF", fr.sign),
            ("OF", fr.overflow), ("PF", fr.parity), ("AF", fr.auxiliary),
            ("IF", fr.interrupt), ("DF", fr.direction)
        ]
        col_x = x + 2
        self._safe_addstr(win, y + 7, col_x, "FLAGS: ", curses.color_pair(1) | curses.A_BOLD)
        col_x += 7
        for name, val in flags:
            changed = (name in self.prev_regs and self.prev_regs[name] != val)
            if changed:
                flag_attr = curses.color_pair(3) | curses.A_BOLD
            elif val:
                flag_attr = curses.color_pair(2) | curses.A_BOLD
            else:
                flag_attr = curses.color_pair(8)
            f_str = f"[{name}:{val}] "
            self._safe_addstr(win, y + 7, col_x, f_str, flag_attr)
            col_x += len(f_str)

    def _render_telemetry(self, win, y, x, h, w):
        self._draw_box(win, y, x, h, w, "VIRTUAL HARDWARE PERIPHERALS")

        # Port 4: Traffic Lights
        tl_dev = self.EU.peripherals.get_device(4) if hasattr(self.EU, 'peripherals') else None
        tl_val = tl_dev.state if tl_dev else 0

        # Bit parsing: 0-2 N, 3-5 W, 6-8 S, 9-11 E
        dirs = ["North", "West", "South", "East"]
        lamps = []
        for d in range(4):
            r = (tl_val >> (d * 3)) & 1
            y_l = (tl_val >> (d * 3 + 1)) & 1
            g = (tl_val >> (d * 3 + 2)) & 1
            st = ("R" if r else ".") + ("Y" if y_l else ".") + ("G" if g else ".")
            lamps.append(f"{dirs[d][0]}:[{st}]")

        tl_text = f" [Port 4 Traffic Lights]  Val: 0x{tl_val:04X} ({tl_val})  " + "  ".join(lamps)
        self._safe_addstr(win, y + 1, x + 2, tl_text, curses.color_pair(2) | curses.A_BOLD)

        # Port 7: Stepper Motor
        sm_dev = self.EU.peripherals.get_device(7) if hasattr(self.EU, 'peripherals') else None
        sm_angle = sm_dev.angle if sm_dev else 0.0
        sm_dir = sm_dev.direction_str if sm_dev else "IDLE"
        sm_steps = sm_dev.step_count if sm_dev else 0
        sm_coils = sm_dev.state if sm_dev else 0

        needles = ["↑", "↗", "→", "↘", "↓", "↙", "←", "↖"]
        needle_idx = int(((sm_angle + 22.5) % 360) / 45)
        needle_char = needles[needle_idx % 8]

        c_str = f"D:{(sm_coils>>3)&1} C:{(sm_coils>>2)&1} B:{(sm_coils>>1)&1} A:{sm_coils&1}"
        sm_text = f" [Port 7 Stepper Motor ]  Needle: [{needle_char}]  Angle: {sm_angle:05.1f}° [{sm_dir:<4}]  Steps: {sm_steps:<3}  Coils: [{c_str}]"
        self._safe_addstr(win, y + 3, x + 2, sm_text, curses.color_pair(3) | curses.A_BOLD)

        # Video Buffer 0xB8000
        vid_dev = self.EU.video_display
        vid_r, vid_c = vid_dev.get_cursor() if vid_dev else (0, 0)
        vid_text = f" [Video Display 0xB8000]  Mode: 80x25 Color Text  Cursor: (Row: {vid_r:02d}, Col: {vid_c:02d})  Status: Mirror Active"
        self._safe_addstr(win, y + 5, x + 2, vid_text, curses.color_pair(1))

        # Console log output — show last 2 lines of program output
        out_lines = [l for l in self.EU.output.split("\n") if l.strip()]
        if out_lines:
            out1 = out_lines[-1] if len(out_lines) >= 1 else ""
            out2 = out_lines[-2] if len(out_lines) >= 2 else ""
            if out2:
                self._safe_addstr(win, y + 6, x + 2, f" ▸ {out2[:w-6]}", curses.color_pair(8))
            self._safe_addstr(win, y + 7, x + 2, f" ▸ {out1[:w-6]}", curses.color_pair(2) | curses.A_BOLD)
        else:
            self._safe_addstr(win, y + 7, x + 2, " Console: (no output yet)", curses.color_pair(8))

    def _render_memory(self, win, y, x, h, w):
        is_focused = (self.focused_pane == 'memory')
        cur_seg_name = self.mem_segments[self.mem_seg_idx]
        title = f"MEMORY INSPECTOR [{cur_seg_name}:{self.mem_offset:04X}h]"
        self._draw_box(win, y, x, h, w, title, is_focused)

        if cur_seg_name == 'VIDEO':
            base_addr = VIDEO_MEM_BASE + self.mem_offset
        else:
            seg_val = self.BIU.reg.get(cur_seg_name, 0)
            base_addr = (seg_val << 4) + self.mem_offset

        content_h = max(1, h - 2)
        bytes_per_row = 16 if w >= 70 else 8

        for row in range(content_h):
            row_addr = base_addr + row * bytes_per_row
            if row_addr >= MEMORY_SIZE:
                break

            hex_bytes = []
            ascii_chars = []
            for b_idx in range(bytes_per_row):
                addr = row_addr + b_idx
                if addr < MEMORY_SIZE:
                    val_raw = self.memory.rb(addr)
                    val = to_decimal(val_raw[0]) if isinstance(val_raw, list) else to_decimal(val_raw)
                    hex_bytes.append(f"{val:02X}")
                    ascii_chars.append(chr(val) if (32 <= val <= 126) else ".")
                else:
                    hex_bytes.append("..")
                    ascii_chars.append(" ")

            hex_str = " ".join(hex_bytes[:8])
            if bytes_per_row == 16:
                hex_str += "  " + " ".join(hex_bytes[8:])
            ascii_str = "".join(ascii_chars)

            row_text = f" {row_addr:05X}:  {hex_str:<49} │ {ascii_str}"
            self._safe_addstr(win, y + 1 + row, x + 1, row_text, curses.color_pair(2) if row % 2 == 0 else curses.A_NORMAL)

    def _render_stack_view(self, win, y, x, h, w):
        """Render the SS:SP stack view in the memory inspector area."""
        is_focused = (self.focused_pane == 'memory')
        ss = self.BIU.reg.get('SS', 0)
        sp = self.EU.reg.get('SP', 0)
        title = f"STACK VIEW [SS:{ss:04X}h SP:{sp:04X}h]"
        self._draw_box(win, y, x, h, w, title, is_focused)

        content_h = max(1, h - 2)
        ss_phys = ss << 4
        # SS:SP points to current top of stack; show 8 word entries going upward
        num_entries = min(content_h, 12)

        self._safe_addstr(win, y + 1, x + 2,
            "  Offset    Physical   Value    (last pushed → top)",
            curses.color_pair(1) | curses.A_BOLD)

        for i in range(num_entries - 1):
            row = y + 2 + i
            if row >= y + h - 1:
                break
            word_offset = sp + (i * 2)
            phys = ss_phys + word_offset
            if phys + 1 < MEMORY_SIZE:
                raw_lo = self.memory.rb(phys)
                raw_hi = self.memory.rb(phys + 1)
                lo = to_decimal(raw_lo[0]) if isinstance(raw_lo, list) else to_decimal(raw_lo)
                hi = to_decimal(raw_hi[0]) if isinstance(raw_hi, list) else to_decimal(raw_hi)
                word_val = (hi << 8) | lo
                is_top = (i == 0)
                prefix = "▶ SP+%02X" % (i * 2) if is_top else "  SP+%02X" % (i * 2)
                row_text = f" {prefix}  {phys:05X}h   {word_val:04X}h = {word_val}"
                attr = (curses.color_pair(3) | curses.A_BOLD) if is_top else curses.color_pair(2)
                self._safe_addstr(win, row, x + 1, row_text.ljust(w - 2), attr)
            else:
                self._safe_addstr(win, row, x + 2, f"  (address {phys:05X}h out of range)", curses.color_pair(8))

    def _render_footer(self, win, max_y, max_x):
        hotkeys = "[s] Step  [c] Run  [p] Pause  [b] Break  [Tab] Pane  [k/j] Nav  [m] MemSeg  [v] StackView  [?] Help  [q] Quit"
        self._safe_addstr(win, max_y - 2, 0, f" {hotkeys}".ljust(max_x), curses.color_pair(6) | curses.A_BOLD)

        status_line = f" MSG: {self.status_msg}"
        self._safe_addstr(win, max_y - 1, 0, status_line.ljust(max_x), curses.color_pair(3))

    def _render_help_modal(self, win, max_y, max_x):
        modal_w = min(72, max_x - 4)
        modal_h = min(20, max_y - 4)
        start_y = max(1, (max_y - modal_h) // 2)
        start_x = max(1, (max_x - modal_w) // 2)

        # Clear background area of modal with spaces
        for r in range(start_y, start_y + modal_h):
            self._safe_addstr(win, r, start_x, " " * modal_w, curses.color_pair(6))

        self._draw_box(win, start_y, start_x, modal_h, modal_w, "KEYBOARD SHORTCUTS & HELP", True)

        help_lines = [
            ("Execution Controls:", True),
            ("  [s] / [Space]     Single-step one instruction forward", False),
            ("  [c]               Continue running continuously", False),
            ("  [p]               Pause continuous execution", False),
            ("  [b]               Toggle breakpoint at current/selected IP", False),
            ("  [r]               Reset CPU and reload program", False),
            ("  [+] / [-]         Increase / decrease execution speed", False),
            ("", False),
            ("Navigation & Inspection:", True),
            ("  [Tab]             Switch focus (Disassembly <-> Memory)", False),
            ("  [k] / [↑]         Move cursor up / scroll memory up", False),
            ("  [j] / [↓]         Move cursor down / scroll memory down", False),
            ("  [PgUp] / [PgDn]   Scroll memory by 128 bytes", False),
            ("  [m]               Cycle memory segment (DS, CS, SS, ES, VIDEO)", False),
            ("", False),
            ("  [?] / [h]         Toggle this help window", False),
            ("  [q]               Quit TUI", False),
            ("", False),
            ("               Press any key to close this help window", True)
        ]

        for idx, (line, is_header) in enumerate(help_lines):
            row = start_y + 1 + idx
            if row >= start_y + modal_h - 1:
                break
            attr = (curses.color_pair(3) | curses.A_BOLD) if is_header else curses.color_pair(2)
            self._safe_addstr(win, row, start_x + 2, line[:modal_w - 4], attr)

    def _handle_key(self, win, key):
        if self.show_help:
            self.show_help = False
            return True

        if key in [ord('q'), ord('Q')]:
            return False

        elif key in [ord('?'), ord('h'), ord('H')]:
            self.show_help = True
            return True

        elif key in [9]:  # Tab key
            self.focused_pane = 'memory' if self.focused_pane == 'disasm' else 'disasm'
            self.status_msg = f"Active pane switched to [{self.focused_pane.upper()}]."

        elif key in [ord('s'), ord('S'), ord(' '), ord('\n'), 10]:
            self.running = False
            self.follow_ip = True
            self.step()

        elif key in [ord('c'), ord('C')]:
            self.running = True
            self.status_msg = "Running continuously... Press [p] to pause."

        elif key in [ord('p'), ord('P')]:
            self.running = False
            self.status_msg = "Execution paused."

        elif key in [ord('r'), ord('R')]:
            self.running = False
            self._init_cpu()
            self.status_msg = "CPU reset and reloaded to initial state."

        elif key in [ord('b'), ord('B')]:
            if self.focused_pane == 'disasm' and self.instructions:
                target_ip = self.instructions[self.disasm_cursor_idx][0]
            else:
                target_ip = self.BIU.reg.get('IP', 0)

            if target_ip in self.breakpoints:
                self.breakpoints.remove(target_ip)
                self.status_msg = f"Removed breakpoint at IP={target_ip:04X}h"
            else:
                self.breakpoints.add(target_ip)
                self.status_msg = f"Added breakpoint at IP={target_ip:04X}h"

        elif key in [ord('k'), ord('K'), curses.KEY_UP]:
            if self.focused_pane == 'disasm':
                self.follow_ip = False
                self.disasm_cursor_idx = max(0, self.disasm_cursor_idx - 1)
            else:
                self.mem_offset = max(0, self.mem_offset - 16)

        elif key in [ord('j'), ord('J'), curses.KEY_DOWN]:
            if self.focused_pane == 'disasm':
                self.follow_ip = False
                self.disasm_cursor_idx = min(len(self.instructions) - 1, self.disasm_cursor_idx + 1)
            else:
                self.mem_offset = min(0xFFFF, self.mem_offset + 16)

        elif key in [curses.KEY_PPAGE]:  # Page Up
            if self.focused_pane == 'disasm':
                self.disasm_cursor_idx = max(0, self.disasm_cursor_idx - 10)
            else:
                self.mem_offset = max(0, self.mem_offset - 128)

        elif key in [curses.KEY_NPAGE]:  # Page Down
            if self.focused_pane == 'disasm':
                self.disasm_cursor_idx = min(len(self.instructions) - 1, self.disasm_cursor_idx + 10)
            else:
                self.mem_offset = min(0xFFFF, self.mem_offset + 128)

        elif key in [ord('m'), ord('M')]:
            self.mem_seg_idx = (self.mem_seg_idx + 1) % len(self.mem_segments)
            self.mem_offset = 0
            self.status_msg = f"Memory inspector switched to segment [{self.mem_segments[self.mem_seg_idx]}]."

        elif key in [ord('v'), ord('V')]:
            self.mem_view_mode = 'stack' if self.mem_view_mode == 'hex' else 'hex'
            self.status_msg = f"Memory view mode: {self.mem_view_mode.upper()}."

        elif key in [ord('+'), ord('=')]:
            self.step_delay = max(0.005, self.step_delay * 0.7)
            self.status_msg = f"Speed increased (delay: {self.step_delay*1000:0.1f}ms)."

        elif key in [ord('-'), ord('_')]:
            self.step_delay = min(1.0, self.step_delay * 1.4)
            self.status_msg = f"Speed decreased (delay: {self.step_delay*1000:0.1f}ms)."

        return True
