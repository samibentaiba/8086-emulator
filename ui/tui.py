"""
Antigravity 8086 Full-Featured Terminal User Interface (TUI)
LazyVim-style modular interactive debugger, in-TUI modal code editor, and virtual hardware monitor.
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
from emulator.instructions import all_ins
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
        self.source_lines = []
        self.instructions = []
        self.breakpoints = set()
        self.disasm_cursor_idx = 0
        self.follow_ip = True
        self.running = False
        self.show_help = False
        self.show_leader_menu = False
        self.step_delay = 0.05  # seconds between steps in run mode
        self.last_step_time = 0
        self.running_direction = 1  # 1 for forward, -1 for backward (rewind)
        self.status_msg = "NORMAL mode. Press [i] to Edit, [s] to Step, [u] to Step Back, [c] to Run, [C] to Rewind."

        # LazyVim Modal Editor state
        self.mode = 'NORMAL'          # 'NORMAL' or 'INSERT'
        self.edit_row = 0             # 0-indexed line in source_lines
        self.edit_col = 0             # 0-indexed column within line
        self.source_scroll_y = 0      # viewport vertical scroll offset
        self.source_scroll_x = 0      # viewport horizontal scroll offset
        self.modified = False         # unsaved changes flag

        # LazyVim Window Manager state
        self.focused_pane = 'disasm'  # 'disasm', 'registers', 'telemetry', 'memory'
        self.show_telemetry = True     # toggle with 't'
        self.zoomed_pane = None        # toggle with 'z' (None or pane name)

        # Memory inspector & Console state
        self.mem_segments = ['DS', 'CS', 'SS', 'ES', 'VIDEO']
        self.mem_seg_idx = 0
        self.mem_offset = 0
        self.mem_view_mode = 'hex'     # 'hex', 'stack', 'console'
        self.console_scroll_offset = 0

        # Previous register state for change highlighting
        self.prev_regs = {}

        # Debug Symbol Mapping (1-to-1 IP <-> Source Line)
        self.ip_to_source_line = {}
        self.source_line_to_ip = {}
        self.need_full_clear = False

        # Load and initialize CPU
        self._load_file()
        self._init_cpu()

    def _load_file(self):
        with open(self.asm_filepath, 'r', encoding='utf-8') as f:
            self.asm_code = f.read()
        self.source_lines = self.asm_code.splitlines() if self.asm_code else [""]
        self.edit_row = 0
        self.edit_col = 0
        self.source_scroll_y = 0
        self.source_scroll_x = 0
        self._build_source_mapping()

    def _build_source_mapping(self):
        """Build exact 1-to-1 mapping between physical IP offsets and source lines."""
        self.ip_to_source_line = {}
        self.source_line_to_ip = {}
        has_code_seg = any('CODE' in l.upper() and 'SEGMENT' in l.upper() for l in self.source_lines)
        in_code = not has_code_seg
        ip = 0
        for idx, raw in enumerate(self.source_lines):
            line = raw.split(';')[0].strip()
            if not line:
                continue
            tokens = [t for t in re.split(r'[\s,:]+', line.upper()) if t]
            if not tokens:
                continue
            if 'CODE' in tokens and 'SEGMENT' in tokens:
                in_code = True
                continue
            if in_code and has_code_seg and ('ENDS' in tokens or 'END' in tokens):
                if 'ENDS' in tokens:
                    in_code = False
                    continue
            if in_code:
                if line.endswith(':'):
                    continue
                if ':' in line:
                    parts = line.split(':', 1)
                    after = parts[1].strip()
                    if not after:
                        continue
                    first_tok = re.split(r'[\s,]+', after.upper())[0]
                else:
                    first_tok = tokens[0]
                if first_tok in all_ins or any(first_tok.startswith(ins) for ins in all_ins):
                    self.ip_to_source_line[ip] = idx
                    self.source_line_to_ip[idx] = ip
                    ip += 1

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
        self.EU.mute_stdout = True  # Mute raw stdout to prevent screen tearing/glitches
        self.cpu = CPU(self.BIU, self.EU, gui_mode=False)
        self.cpu.tui_mode = True   # Suppress interactive debug() prompt in TUI mode

        self._cache_instructions()
        self.prev_regs = self._snapshot_regs()
        self.running = False
        self.running_direction = 1
        self.disasm_cursor_idx = 0
        self.follow_ip = True

    def _cache_instructions(self):
        cs_space = self.exe_file.space.get('CS', [])
        cs_len = self.exe_file.seg_len.get('CS', len(cs_space))
        self.instructions = []
        for idx in range(cs_len):
            item = cs_space[idx]
            if item != ['0']:
                opcode = item[0]
                opds = ", ".join(item[1:]) if len(item) > 1 else ""
                self.instructions.append((idx, opcode, opds))

    def _recompile_code(self):
        """On-the-fly reassembly when exiting INSERT mode (<Esc>)."""
        new_code = "\n".join(self.source_lines)
        try:
            new_asm = Assembler(SEG_INIT)
            new_exe = new_asm.compile(new_code)
            self.assembler = new_asm
            self.exe_file = new_exe
            self.memory.load(self.exe_file)
            if hasattr(self, 'BIU') and self.BIU:
                self.BIU.flush_pipeline()
            self._cache_instructions()
            self._build_source_mapping()
            self.need_full_clear = True
            self.status_msg = f"Assembled successfully ({len(self.source_lines)} lines)."
            self.modified = True
        except Exception as err:
            self.status_msg = f"AssemblyError: {err} (press 'i' to fix)"

    def save_to_disk(self):
        """Save source code changes back to the .asm file."""
        try:
            with open(self.asm_filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.source_lines) + "\n")
            self.modified = False
            self.status_msg = f"Saved '{os.path.basename(self.asm_filepath)}' to disk."
        except Exception as err:
            self.status_msg = f"Error saving file: {err}"

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
                for idx, (offset, opc, _) in enumerate(self.instructions):
                    if offset == current_ip:
                        self.disasm_cursor_idx = idx
                        break
                if current_ip in self.ip_to_source_line:
                    self.edit_row = self.ip_to_source_line[current_ip]
            if current_ip in self.breakpoints:
                self.running = False
                self.status_msg = f"Breakpoint hit at IP={current_ip:04X}h!"
            return True
        else:
            self.running = False
            self.status_msg = f"Program terminated. Cycles: {self.cpu.cycle_count}."
            return False

    def step_back(self):
        """Rewind CPU state by 1 instruction, reverting registers, memory, and flags."""
        if not self.cpu.can_step_back():
            self.running = False
            self.status_msg = "Already at start of execution (Cycle 0)."
            return False

        old_regs = self._snapshot_regs()
        if self.cpu.step_back():
            self.prev_regs = old_regs  # Reverted registers and flags will highlight in yellow!
            current_ip = self.BIU.reg.get('IP', 0)
            if self.follow_ip:
                for idx, (offset, opc, _) in enumerate(self.instructions):
                    if offset == current_ip:
                        self.disasm_cursor_idx = idx
                        break
                if current_ip in self.ip_to_source_line:
                    self.edit_row = self.ip_to_source_line[current_ip]

            if current_ip in self.breakpoints:
                self.running = False
                self.status_msg = f"Reverse breakpoint hit at IP={current_ip:04X}h!"
            else:
                undone_line = self.source_lines[self.edit_row].strip() if self.edit_row < len(self.source_lines) else ""
                self.status_msg = f"⏪ Stepped back to IP={current_ip:04X}h (Cycle {self.cpu.cycle_count}): {undone_line}"
            return True
        else:
            self.running = False
            self.status_msg = "Already at start of execution (Cycle 0)."
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
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Success / Active / Values / Insert
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Warning / Changes / Focused
        curses.init_pair(4, curses.COLOR_RED, -1)      # Breakpoints / Errors / Halt
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Highlight Cursor Current IP
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Status Bar / Headers
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)  # Segment / Registers / Directives
        curses.init_pair(8, curses.COLOR_BLUE, -1)     # Dim labels / Comments
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Selected Row Cursor

    def _safe_addstr(self, win, y, x, text, attr=0, max_w=None):
        try:
            max_y, max_x = win.getmaxyx()
            if 0 <= y < max_y and 0 <= x < max_x:
                avail = max_x - x - 1
                if max_w is not None:
                    avail = min(avail, max(0, max_w))
                if avail > 0:
                    win.addstr(y, x, text[:avail], attr)
        except curses.error:
            pass

    def _draw_box(self, win, y, x, h, w, title="", is_focused=False):
        border_attr = (curses.color_pair(3) | curses.A_BOLD) if is_focused else curses.color_pair(1)

        # Blank the interior of the box to guarantee no ghost artifacts or glitches
        inner_w = max(0, w - 2)
        blank = " " * inner_w
        for row in range(y + 1, y + h - 1):
            self._safe_addstr(win, row, x + 1, blank, max_w=inner_w)

        for row in range(y, y + h):
            self._safe_addstr(win, row, x, "│", border_attr, max_w=1)
            self._safe_addstr(win, row, x + w - 1, "│", border_attr, max_w=1)
        for col in range(x, x + w):
            self._safe_addstr(win, y, col, "─", border_attr, max_w=1)
            self._safe_addstr(win, y + h - 1, col, "─", border_attr, max_w=1)
        # Corners
        self._safe_addstr(win, y, x, "┌", border_attr, max_w=1)
        self._safe_addstr(win, y, x + w - 1, "┐", border_attr, max_w=1)
        self._safe_addstr(win, y + h - 1, x, "└", border_attr, max_w=1)
        self._safe_addstr(win, y + h - 1, x + w - 1, "┘", border_attr, max_w=1)

        if title:
            focused_indicator = " [FOCUSED]" if is_focused else ""
            title_text = f" {title}{focused_indicator} "
            avail_title_w = max(0, w - 4)
            self._safe_addstr(win, y, x + 2, title_text[:avail_title_w], border_attr | curses.A_BOLD, max_w=avail_title_w)

    def _main_loop(self, stdscr):
        import io
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            self._init_colors()
            curses.curs_set(0) # Default cursor
            stdscr.nodelay(True) # Non-blocking input
            stdscr.timeout(30)   # 30ms timeout for smooth execution

            while True:
                max_y, max_x = stdscr.getmaxyx()
                if self.need_full_clear:
                    stdscr.clear()
                    self.need_full_clear = False
                else:
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
                main_h = max_y - 4

                if self.zoomed_pane:
                    # Zoomed single-pane view (LazyVim <C-w>m / 'z' style)
                    if self.zoomed_pane == 'disasm':
                        self._render_disassembly(stdscr, 1, 0, main_h, max_x)
                    elif self.zoomed_pane == 'registers':
                        self._render_registers(stdscr, 1, 0, main_h, max_x)
                    elif self.zoomed_pane == 'telemetry':
                        self._render_telemetry(stdscr, 1, 0, main_h, max_x)
                    else:
                        if self.mem_view_mode == 'console':
                            self._render_console_view(stdscr, 1, 0, main_h, max_x)
                        elif self.mem_view_mode == 'stack':
                            self._render_stack_view(stdscr, 1, 0, main_h, max_x)
                        else:
                            self._render_memory(stdscr, 1, 0, main_h, max_x)
                else:
                    left_w = min(50, int(max_x * 0.44))
                    right_w = max_x - left_w
                    disasm_h = main_h

                    if self.show_telemetry:
                        reg_h = min(10, max(8, main_h // 3))
                        telem_h = min(9, max(7, main_h // 3))
                        mem_h = main_h - reg_h - telem_h
                    else:
                        telem_h = 0
                        reg_h = min(11, max(8, main_h // 3))
                        mem_h = main_h - reg_h

                    self._render_disassembly(stdscr, 1, 0, disasm_h, left_w)
                    self._render_registers(stdscr, 1, left_w, reg_h, right_w)

                    if self.show_telemetry:
                        self._render_telemetry(stdscr, 1 + reg_h, left_w, telem_h, right_w)

                    mem_y = 1 + reg_h + telem_h
                    if self.mem_view_mode == 'console':
                        self._render_console_view(stdscr, mem_y, left_w, mem_h, right_w)
                    elif self.mem_view_mode == 'stack':
                        self._render_stack_view(stdscr, mem_y, left_w, mem_h, right_w)
                    else:
                        self._render_memory(stdscr, mem_y, left_w, mem_h, right_w)

                # Footer
                self._render_footer(stdscr, max_y, max_x)

                # Overlays: Floating Help Modal or LazyVim Which-Key Menu
                if self.show_help:
                    self._render_help_modal(stdscr, max_y, max_x)
                elif self.show_leader_menu:
                    self._render_leader_menu(stdscr, max_y, max_x)

                stdscr.refresh()

                # Handle Continuous Running (Forward or Backward)
                if self.running and self.mode == 'NORMAL':
                    now = time.time()
                    if now - self.last_step_time >= self.step_delay:
                        if getattr(self, 'running_direction', 1) == -1:
                            if not self.step_back():
                                self.running = False
                        else:
                            if not self.step():
                                self.running = False
                        self.last_step_time = now

                # Process User Input Keybindings
                key = stdscr.getch()
                if key != -1:
                    if not self._handle_key(stdscr, key):
                        break
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def _render_header(self, win, max_x):
        if self.running:
            if getattr(self, 'running_direction', 1) == -1:
                state_str = "REWIND ◀◀"
                state_color = curses.color_pair(3)
            else:
                state_str = "RUNNING ▶▶"
                state_color = curses.color_pair(2)
        else:
            state_str = "HALTED" if self.cpu.check_done() else "PAUSED"
            state_color = curses.color_pair(4) if self.cpu.check_done() else curses.color_pair(3)

        parts = self.asm_filepath.replace('\\', '/').split('/')
        filename = '/'.join(parts[-2:]) if len(parts) > 2 else self.asm_filepath
        mod_str = " [+]" if self.modified else ""
        speed_str = f"{1.0/self.step_delay:.0f} steps/s" if self.step_delay > 0 else "Max"
        cs = self.BIU.reg.get('CS', 0)
        ip = self.BIU.reg.get('IP', 0)
        zoom_str = f" [ZOOM:{self.zoomed_pane.upper()}]" if self.zoomed_pane else ""
        mode_badge = f" [{self.mode}] "
        mode_attr = curses.color_pair(2) if self.mode == 'INSERT' else curses.color_pair(5)

        hdr_text = f" 8086 TUI │ {filename}{mod_str}{zoom_str} │ CS:IP={cs:04X}:{ip:04X}h │ ⚡{speed_str} │ "
        self._safe_addstr(win, 0, 0, hdr_text, curses.color_pair(6) | curses.A_BOLD)
        cur_x = len(hdr_text)
        self._safe_addstr(win, 0, cur_x, mode_badge, mode_attr | curses.A_BOLD)
        cur_x += len(mode_badge)
        self._safe_addstr(win, 0, cur_x, f" [{state_str}] ", state_color | curses.A_BOLD)
        cur_x += len(state_str) + 4

        if max_x > cur_x:
            self._safe_addstr(win, 0, cur_x, " " * (max_x - cur_x), curses.color_pair(6))

    def _render_disassembly(self, win, y, x, h, w):
        is_focused = (self.focused_pane == 'disasm')
        mode_tag = f" [{self.mode}]"
        mod_mark = " [+]" if self.modified else ""
        cur_line_len = len(self.source_lines[self.edit_row]) if self.source_lines else 0
        self.edit_col = max(0, min(cur_line_len, self.edit_col))
        title = f"CODE{mode_tag}{mod_mark} (Ln {self.edit_row + 1}, Col {self.edit_col + 1})"
        self._draw_box(win, y, x, h, w, title, is_focused)

        content_h = max(1, h - 2)
        if not self.source_lines:
            self._safe_addstr(win, y + 1, x + 2, "(Empty file)", curses.color_pair(8), max_w=w - 4)
            return

        self.edit_row = max(0, min(len(self.source_lines) - 1, self.edit_row))

        current_ip = self.BIU.reg.get('IP', 0)
        exec_line_idx = self.ip_to_source_line.get(current_ip, -1)

        # Viewport vertical scrolling: follow executing line when follow_ip is True, else edit_row
        target_row = exec_line_idx if (self.follow_ip and exec_line_idx >= 0) else self.edit_row
        if target_row < self.source_scroll_y:
            self.source_scroll_y = target_row
        elif target_row >= self.source_scroll_y + content_h:
            self.source_scroll_y = target_row - content_h + 1

        inner_w = max(0, w - 2)
        prefix_len = 6  # "01│  " is 6 characters
        avail_w = max(5, inner_w - prefix_len)

        # Horizontal viewport auto-scrolling to follow cursor when focused
        if is_focused:
            if self.edit_col < self.source_scroll_x:
                self.source_scroll_x = self.edit_col
            elif self.edit_col >= self.source_scroll_x + avail_w:
                self.source_scroll_x = self.edit_col - avail_w + 1

        for row_idx in range(content_h):
            line_idx = self.source_scroll_y + row_idx
            if line_idx >= len(self.source_lines):
                break

            line_text = self.source_lines[line_idx]
            is_cursor_line = (line_idx == self.edit_row and is_focused)
            is_exec_line = (line_idx == exec_line_idx)

            line_ip = self.source_line_to_ip.get(line_idx, -1)
            is_bp = (line_ip in self.breakpoints) if line_ip >= 0 else False
            bp_mark = "●" if is_bp else " "
            ptr_mark = "▶" if is_exec_line else " "

            num_str = f"{line_idx + 1:02d}"
            prefix = f"{num_str}│{bp_mark}{ptr_mark} "
            row_y = y + 1 + row_idx

            # Draw line number prefix
            prefix_attr = (curses.color_pair(3) | curses.A_BOLD) if is_cursor_line else curses.color_pair(8)
            self._safe_addstr(win, row_y, x + 1, prefix, prefix_attr, max_w=len(prefix))

            # Syntax highlighting base attribute
            base_attr = curses.A_NORMAL
            if is_exec_line:
                base_attr = curses.color_pair(5) | curses.A_BOLD
            elif is_bp:
                base_attr = curses.color_pair(4) | curses.A_BOLD
            else:
                stripped = line_text.strip()
                if stripped.startswith(';'):
                    base_attr = curses.color_pair(8)
                elif 'SEGMENT' in stripped or 'ENDS' in stripped or stripped.endswith(':'):
                    base_attr = curses.color_pair(7) | curses.A_BOLD
                else:
                    base_attr = curses.color_pair(2) if line_idx % 2 == 0 else curses.A_NORMAL

            # Slice line based on horizontal scroll offset
            disp_line = line_text[self.source_scroll_x : self.source_scroll_x + avail_w]
            cur_draw_x = x + 1 + len(prefix)

            if is_cursor_line:
                # Active line with Character-Level Inverted Block Cursor
                rel_cursor = self.edit_col - self.source_scroll_x

                # 1. Text before cursor
                before = disp_line[:max(0, rel_cursor)]
                if before:
                    self._safe_addstr(win, row_y, cur_draw_x, before, base_attr, max_w=len(before))
                    cur_draw_x += len(before)

                # 2. Exact Character Under Cursor
                if 0 <= rel_cursor < avail_w:
                    cursor_char = disp_line[rel_cursor] if rel_cursor < len(disp_line) else " "
                    if self.mode == 'INSERT':
                        # High-visibility bright green inverted block in INSERT mode
                        cursor_attr = curses.color_pair(2) | curses.A_REVERSE | curses.A_BOLD
                    else:
                        # Solid blue/white inverted block in NORMAL mode
                        cursor_attr = curses.color_pair(9) | curses.A_REVERSE | curses.A_BOLD

                    self._safe_addstr(win, row_y, cur_draw_x, cursor_char, cursor_attr, max_w=1)
                    cur_draw_x += 1

                # 3. Text after cursor
                after = disp_line[rel_cursor + 1:] if (rel_cursor + 1 < len(disp_line)) else ""
                if after:
                    self._safe_addstr(win, row_y, cur_draw_x, after, base_attr, max_w=len(after))
                    cur_draw_x += len(after)

                # 4. Fill remainder with blanks
                rem = (x + 1 + inner_w) - cur_draw_x
                if rem > 0:
                    self._safe_addstr(win, row_y, cur_draw_x, " " * rem, curses.A_NORMAL, max_w=rem)
            else:
                # Inactive line: draw sliced text and pad
                self._safe_addstr(win, row_y, cur_draw_x, disp_line, base_attr, max_w=avail_w)
                cur_draw_x += len(disp_line)
                rem = (x + 1 + inner_w) - cur_draw_x
                if rem > 0:
                    self._safe_addstr(win, row_y, cur_draw_x, " " * rem, curses.A_NORMAL, max_w=rem)

        # Position terminal cursor precisely on the active character cell
        if is_focused and (0 <= (self.edit_row - self.source_scroll_y) < content_h):
            curs_y = y + 1 + (self.edit_row - self.source_scroll_y)
            rel_col = self.edit_col - self.source_scroll_x
            curs_x = x + 1 + len(prefix) + max(0, min(rel_col, avail_w - 1))
            try:
                if self.mode == 'INSERT':
                    curses.curs_set(1)
                else:
                    curses.curs_set(0)
                win.move(curs_y, curs_x)
            except curses.error:
                pass
        else:
            try:
                curses.curs_set(0)
            except curses.error:
                pass

    def _render_registers(self, win, y, x, h, w):
        is_focused = (self.focused_pane == 'registers')
        self._draw_box(win, y, x, h, w, "CPU REGISTERS & FLAGS", is_focused)

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
            avail = max(0, (x + w - 1) - col)
            if avail <= 0:
                break
            self._safe_addstr(win, y + 1, col, text, attr, max_w=avail)
            col += len(text) + 1

        # Row 2: Sub-registers (AH/AL, BH/BL, etc.)
        r2 = f" AH:{ax>>8:02X} AL:{ax&0xFF:02X}  BH:{bx>>8:02X} BL:{bx&0xFF:02X}  CH:{cx>>8:02X} CL:{cx&0xFF:02X}  DH:{dx>>8:02X} DL:{dx&0xFF:02X}"
        self._safe_addstr(win, y + 2, x + 2, r2, curses.color_pair(8), max_w=max(0, w - 4))

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
            avail = max(0, (x + w - 1) - col)
            if avail <= 0:
                break
            self._safe_addstr(win, y + 4, col, text, attr, max_w=avail)
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
            avail = max(0, (x + w - 1) - col)
            if avail <= 0:
                break
            self._safe_addstr(win, y + 5, col, text, attr, max_w=avail)
            col += len(text) + 2

        # Row 5: Flags Register
        fr = self.EU.FR
        flags = [
            ("CF", fr.carry), ("ZF", fr.zero), ("SF", fr.sign),
            ("OF", fr.overflow), ("PF", fr.parity), ("AF", fr.auxiliary),
            ("IF", fr.interrupt), ("DF", fr.direction)
        ]
        col_x = x + 2
        self._safe_addstr(win, y + 7, col_x, "FLAGS: ", curses.color_pair(1) | curses.A_BOLD, max_w=max(0, (x + w - 1) - col_x))
        col_x += 7
        for name, val in flags:
            avail = max(0, (x + w - 1) - col_x)
            if avail <= 0:
                break
            changed = (name in self.prev_regs and self.prev_regs[name] != val)
            if changed:
                flag_attr = curses.color_pair(3) | curses.A_BOLD
            elif val:
                flag_attr = curses.color_pair(2) | curses.A_BOLD
            else:
                flag_attr = curses.color_pair(8)
            f_str = f"[{name}:{val}] "
            self._safe_addstr(win, y + 7, col_x, f_str, flag_attr, max_w=avail)
            col_x += len(f_str)

    def _render_telemetry(self, win, y, x, h, w):
        is_focused = (self.focused_pane == 'telemetry')
        self._draw_box(win, y, x, h, w, "VIRTUAL HARDWARE PERIPHERALS", is_focused)

        # Port 4: Traffic Lights
        tl_dev = self.EU.peripherals.get_device(4) if hasattr(self.EU, 'peripherals') else None
        tl_val = tl_dev.state if tl_dev else 0

        dirs = ["North", "West", "South", "East"]
        lamps = []
        for d in range(4):
            r = (tl_val >> (d * 3)) & 1
            y_l = (tl_val >> (d * 3 + 1)) & 1
            g = (tl_val >> (d * 3 + 2)) & 1
            st = ("R" if r else ".") + ("Y" if y_l else ".") + ("G" if g else ".")
            lamps.append(f"{dirs[d][0]}:[{st}]")

        tl_text = f" [Port 4 Traffic Lights]  Val: 0x{tl_val:04X} ({tl_val})  " + "  ".join(lamps)
        self._safe_addstr(win, y + 1, x + 2, tl_text, curses.color_pair(2) | curses.A_BOLD, max_w=max(0, w - 4))

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
        self._safe_addstr(win, y + 3, x + 2, sm_text, curses.color_pair(3) | curses.A_BOLD, max_w=max(0, w - 4))

        # Video Buffer 0xB8000
        vid_dev = self.EU.video_display
        vid_r, vid_c = vid_dev.get_cursor() if vid_dev else (0, 0)
        vid_text = f" [Video Display 0xB8000]  Mode: 80x25 Color Text  Cursor: (Row: {vid_r:02d}, Col: {vid_c:02d})  Status: Mirror Active"
        self._safe_addstr(win, y + 5, x + 2, vid_text, curses.color_pair(1), max_w=max(0, w - 4))

        # Console log output preview
        out_lines = [l for l in self.EU.output.splitlines() if l.strip()]
        if out_lines:
            out1 = out_lines[-1] if len(out_lines) >= 1 else ""
            out2 = out_lines[-2] if len(out_lines) >= 2 else ""
            if out2:
                clean_out2 = out2.replace("> " * 16, "").strip()
                self._safe_addstr(win, y + 6, x + 2, f" ▸ {clean_out2}", curses.color_pair(8), max_w=max(0, w - 4))
            clean_out1 = out1.replace("> " * 16, "").strip()
            self._safe_addstr(win, y + 7, x + 2, f" ▸ {clean_out1}", curses.color_pair(2) | curses.A_BOLD, max_w=max(0, w - 4))
        else:
            self._safe_addstr(win, y + 7, x + 2, " Console: (no output yet)", curses.color_pair(8), max_w=max(0, w - 4))

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
        inner_w = max(0, w - 2)

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
            self._safe_addstr(win, y + 1 + row, x + 1, row_text[:inner_w], curses.color_pair(2) if row % 2 == 0 else curses.A_NORMAL, max_w=inner_w)

    def _render_stack_view(self, win, y, x, h, w):
        """Render the SS:SP stack view in the memory inspector area."""
        is_focused = (self.focused_pane == 'memory')
        ss = self.BIU.reg.get('SS', 0)
        sp = self.EU.reg.get('SP', 0)
        title = f"STACK VIEW [SS:{ss:04X}h SP:{sp:04X}h]"
        self._draw_box(win, y, x, h, w, title, is_focused)

        content_h = max(1, h - 2)
        inner_w = max(0, w - 2)
        ss_phys = ss << 4
        num_entries = min(content_h, 12)

        self._safe_addstr(win, y + 1, x + 2,
            "  Offset    Physical   Value    (last pushed → top)",
            curses.color_pair(1) | curses.A_BOLD, max_w=max(0, w - 4))

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
                self._safe_addstr(win, row, x + 1, row_text.ljust(inner_w)[:inner_w], attr, max_w=inner_w)
            else:
                self._safe_addstr(win, row, x + 2, f"  (address {phys:05X}h out of range)", curses.color_pair(8), max_w=max(0, w - 4))

    def _render_console_view(self, win, y, x, h, w):
        """Render full scrollable program output (OUT commands, DOS strings)."""
        is_focused = (self.focused_pane == 'memory')
        title = "PROGRAM CONSOLE OUTPUT (OUT / DOS INT 21H)"
        self._draw_box(win, y, x, h, w, title, is_focused)

        content_h = max(1, h - 2)
        inner_w = max(0, w - 2)
        lines = [l for l in self.EU.output.splitlines() if l.strip()]

        if not lines:
            self._safe_addstr(win, y + 1, x + 2, "No program output generated yet.", curses.color_pair(8), max_w=max(0, w - 4))
            self._safe_addstr(win, y + 2, x + 2, "Any 'OUT <port>, AL' or DOS 'INT 21H' output displays here cleanly.", curses.color_pair(8), max_w=max(0, w - 4))
            return

        total_lines = len(lines)
        if total_lines <= content_h:
            start_idx = 0
        else:
            if self.console_scroll_offset == 0:
                start_idx = total_lines - content_h
            else:
                start_idx = max(0, min(total_lines - content_h, self.console_scroll_offset))

        visible = lines[start_idx:start_idx + content_h]
        for idx, line in enumerate(visible):
            line_no = start_idx + idx + 1
            clean_line = line.replace("> " * 16, "").strip()
            row_text = f" {line_no:02d} │ {clean_line}"
            self._safe_addstr(win, y + 1 + idx, x + 1, row_text.ljust(inner_w)[:inner_w], curses.color_pair(2) | curses.A_BOLD, max_w=inner_w)

    def _render_footer(self, win, max_y, max_x):
        if self.mode == 'INSERT':
            hotkeys = " -- INSERT --  [<Esc>] Normal Mode  [Enter] Split Line  [Bksp] Delete  [Arrows] Move"
            self._safe_addstr(win, max_y - 2, 0, f"{hotkeys}".ljust(max_x), curses.color_pair(2) | curses.A_BOLD)
            status_line = f" INSERT │ Ln {self.edit_row + 1}, Col {self.edit_col + 1} │ MSG: {self.status_msg}"
            self._safe_addstr(win, max_y - 1, 0, status_line.ljust(max_x), curses.color_pair(3))
        else:
            hist_count = len(self.cpu.history) if hasattr(self.cpu, 'history') else 0
            hist_tag = f" [Rev:{hist_count}]" if hist_count > 0 else ""
            hotkeys = " [Space] Which-Key  [i] Edit  [s] Step  [u] Step Back  [c] Run  [C] Rewind  [p] Pause  [z] Zoom  [?] Help  [q] Quit"
            self._safe_addstr(win, max_y - 2, 0, f"{hotkeys}".ljust(max_x), curses.color_pair(6) | curses.A_BOLD)
            status_line = f" NORMAL │ [{self.focused_pane.upper()}] Ln {self.edit_row + 1}, Col {self.edit_col + 1}{hist_tag} │ MSG: {self.status_msg}"
            self._safe_addstr(win, max_y - 1, 0, status_line.ljust(max_x), curses.color_pair(3))

    def _render_leader_menu(self, win, max_y, max_x):
        """LazyVim-style Which-Key floating menu overlay at the bottom."""
        menu_h = 7
        menu_w = min(88, max_x - 2)
        start_y = max_y - menu_h - 2
        start_x = max(1, (max_x - menu_w) // 2)

        # Clear background of menu
        for r in range(start_y, start_y + menu_h):
            self._safe_addstr(win, r, start_x, " " * menu_w, curses.color_pair(6))

        self._draw_box(win, start_y, start_x, menu_h, menu_w, "WHICH-KEY (Space Leader)", True)

        commands = [
            [("s", "Step Fwd"), ("u", "Step Back"), ("c", "Run Fwd"), ("C", "Run Back")],
            [("p", "Pause"), ("b", "Toggle Break"), ("w", "Save to Disk"), ("z", "Zoom Window")],
            [("t", "Toggle Telem"), ("o", "Console Output"), ("v", "Stack View"), ("r", "Reset CPU")]
        ]

        for row_idx, row_items in enumerate(commands):
            curr_y = start_y + 1 + row_idx * 2
            col_x = start_x + 3
            for key_str, desc in row_items:
                self._safe_addstr(win, curr_y, col_x, f"[{key_str}]", curses.color_pair(3) | curses.A_BOLD)
                self._safe_addstr(win, curr_y, col_x + len(key_str) + 3, desc, curses.color_pair(2))
                col_x += 21

    def _render_help_modal(self, win, max_y, max_x):
        modal_w = min(74, max_x - 4)
        modal_h = min(22, max_y - 4)
        start_y = max(1, (max_y - modal_h) // 2)
        start_x = max(1, (max_x - modal_w) // 2)

        for r in range(start_y, start_y + modal_h):
            self._safe_addstr(win, r, start_x, " " * modal_w, curses.color_pair(6))

        self._draw_box(win, start_y, start_x, modal_h, modal_w, "KEYBOARD SHORTCUTS & HELP", True)

        help_lines = [
            ("LazyVim Modal Code Editing:", True),
            ("  [i]               Enter INSERT mode at cursor (edit code)", False),
            ("  [a]               Enter INSERT mode (append after cursor)", False),
            ("  [o] / [O]         Open new line below / above in insert mode", False),
            ("  [<Esc>]           Exit INSERT mode and re-compile assembly", False),
            ("  [<Space>w]        Save modified code to file on disk", False),
            ("  [x] / [d]         Delete character / line under cursor", False),
            ("", False),
            ("LazyVim Window Management:", True),
            ("  [Space]           Open LazyVim Which-Key floating menu", False),
            ("  [z]               Zoom / Maximize active window to full screen", False),
            ("  [t]               Toggle Hardware Telemetry window on / off", False),
            ("  [1] [2] [3] [4]   Jump directly to Disasm / Regs / Telem / Memory", False),
            ("  [w] / [Tab]       Cycle active window forward ([W] backward)", False),
            ("  [o] / [v]         Cycle inspector: Hex Dump <-> Stack <-> Console", False),
            ("", False),
            ("Execution & Time-Travel Debugging:", True),
            ("  [s] / [Enter]     Single-step 1 instruction forward", False),
            ("  [u] / [Bksp]      Single-step 1 instruction backward (Undo step)", False),
            ("  [c]               Run forward continuously", False),
            ("  [C] / [U]         Run backward continuously (Rewind to break/start)", False),
            ("  [p]               Pause forward or backward execution", False),
            ("  [b] / [r]         Toggle breakpoint / Reset CPU to Cycle 0", False),
            ("  [k] / [j]         Move up / down line by line", False),
            ("  [g] / [G]         Jump to top / bottom of code", False),
            ("  [q]               Quit TUI", False)
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
            self.need_full_clear = True
            return True

        # =============================================================
        # INSERT MODE KEY HANDLING
        # =============================================================
        if self.mode == 'INSERT':
            cur_line = self.source_lines[self.edit_row] if self.source_lines else ""

            if key in [27]:  # <Esc>: Exit insert mode and re-compile
                self.mode = 'NORMAL'
                self._recompile_code()
                return True

            elif key in [curses.KEY_BACKSPACE, ord('\b'), 127, 8]:
                if self.edit_col > 0:
                    new_line = cur_line[:self.edit_col - 1] + cur_line[self.edit_col:]
                    self.source_lines[self.edit_row] = new_line
                    self.edit_col -= 1
                    self.modified = True
                elif self.edit_row > 0:
                    prev_line = self.source_lines[self.edit_row - 1]
                    new_col = len(prev_line)
                    self.source_lines[self.edit_row - 1] = prev_line + cur_line
                    del self.source_lines[self.edit_row]
                    self.edit_row -= 1
                    self.edit_col = new_col
                    self.modified = True
                return True

            elif key in [curses.KEY_DC]:  # Delete key
                if self.edit_col < len(cur_line):
                    new_line = cur_line[:self.edit_col] + cur_line[self.edit_col + 1:]
                    self.source_lines[self.edit_row] = new_line
                    self.modified = True
                return True

            elif key in [ord('\n'), 10, 13]:  # Enter: split line
                left = cur_line[:self.edit_col]
                right = cur_line[self.edit_col:]
                self.source_lines[self.edit_row] = left
                self.source_lines.insert(self.edit_row + 1, right)
                self.edit_row += 1
                self.edit_col = 0
                self.modified = True
                return True

            elif key in [curses.KEY_LEFT]:
                self.edit_col = max(0, self.edit_col - 1)
                return True

            elif key in [curses.KEY_RIGHT]:
                self.edit_col = min(len(cur_line), self.edit_col + 1)
                return True

            elif key in [curses.KEY_HOME]:
                self.edit_col = 0
                return True

            elif key in [curses.KEY_END]:
                self.edit_col = len(cur_line)
                return True

            elif key == curses.KEY_UP:
                self.edit_row = max(0, self.edit_row - 1)
                self.edit_col = min(len(self.source_lines[self.edit_row]), self.edit_col)
                return True

            elif key == curses.KEY_DOWN:
                self.edit_row = min(len(self.source_lines) - 1, self.edit_row + 1)
                self.edit_col = min(len(self.source_lines[self.edit_row]), self.edit_col)
                return True

            elif 32 <= key <= 126:  # Printable character
                char = chr(key)
                new_line = cur_line[:self.edit_col] + char + cur_line[self.edit_col:]
                self.source_lines[self.edit_row] = new_line
                self.edit_col += 1
                self.modified = True
                return True

            return True

        # =============================================================
        # NORMAL MODE KEY HANDLING
        # =============================================================

        # If Leader menu is open, handle hotkey or dismiss
        if self.show_leader_menu:
            self.show_leader_menu = False
            self.need_full_clear = True
            if key in [ord(' '), 27]: # Space or Esc closes menu
                return True
            if key in [ord('w'), ord('W')]: # <Space>w: Save file
                self.save_to_disk()
                return True
            # Otherwise proceed to execute the command corresponding to `key`!

        # Leader key trigger
        if key == ord(' '):
            self.show_leader_menu = True
            self.need_full_clear = True
            return True

        if key in [ord('q'), ord('Q')]:
            return False

        elif key in [ord('?'), curses.KEY_F1]:
            self.show_help = True
            self.need_full_clear = True
            return True

        # LazyVim Modal Editor triggers: i, a, O, x, d
        elif key in [ord('i'), ord('I')]:
            self.mode = 'INSERT'
            self.focused_pane = 'disasm'
            cur_line = self.source_lines[self.edit_row] if self.source_lines else ""
            self.edit_col = max(0, min(len(cur_line), self.edit_col))
            self.status_msg = "-- INSERT -- (Press <Esc> to return to NORMAL mode)"
            return True

        elif key in [ord('a'), ord('A')]:
            self.mode = 'INSERT'
            self.focused_pane = 'disasm'
            cur_line = self.source_lines[self.edit_row] if self.source_lines else ""
            self.edit_col = min(len(cur_line), self.edit_col + 1)
            self.status_msg = "-- INSERT (Append) -- (Press <Esc> to return to NORMAL mode)"
            return True

        elif key == ord('O'):
            if self.focused_pane == 'disasm':
                self.source_lines.insert(self.edit_row + 1, "    ")
                self.edit_row += 1
                self.edit_col = 4
                self.mode = 'INSERT'
                self.modified = True
                self.status_msg = "-- INSERT (Open Line) -- (Press <Esc> to return)"
                return True

        elif key in [ord('x'), ord('X')]:
            if self.focused_pane == 'disasm' and self.source_lines:
                cur_line = self.source_lines[self.edit_row]
                if self.edit_col < len(cur_line):
                    self.source_lines[self.edit_row] = cur_line[:self.edit_col] + cur_line[self.edit_col + 1:]
                    self.modified = True
                    self._recompile_code()
            return True

        elif key in [ord('d'), ord('D')]:
            if self.focused_pane == 'disasm' and len(self.source_lines) > 1:
                del self.source_lines[self.edit_row]
                self.edit_row = min(len(self.source_lines) - 1, self.edit_row)
                self.modified = True
                self._recompile_code()
            return True

        # Vim cursor motions within line: h (left), l (right), 0/^ (start), $ (end)
        elif key in [ord('h'), curses.KEY_LEFT]:
            if self.focused_pane == 'disasm':
                self.edit_col = max(0, self.edit_col - 1)
            return True

        elif key in [ord('l'), curses.KEY_RIGHT]:
            if self.focused_pane == 'disasm':
                cur_line = self.source_lines[self.edit_row] if self.source_lines else ""
                self.edit_col = min(len(cur_line), self.edit_col + 1)
            return True

        elif key in [ord('0'), ord('^')]:
            if self.focused_pane == 'disasm':
                self.edit_col = 0
            return True

        elif key in [ord('$')]:
            if self.focused_pane == 'disasm':
                cur_line = self.source_lines[self.edit_row] if self.source_lines else ""
                self.edit_col = len(cur_line)
            return True

        # Window navigation: 1, 2, 3, 4
        elif key == ord('1'):
            self.focused_pane = 'disasm'
            self.status_msg = "Window [1: CODE EDITOR] focused."
        elif key == ord('2'):
            self.focused_pane = 'registers'
            self.status_msg = "Window [2: REGISTERS] focused."
        elif key == ord('3'):
            if self.show_telemetry:
                self.focused_pane = 'telemetry'
                self.status_msg = "Window [3: TELEMETRY] focused."
            else:
                self.status_msg = "Telemetry window is hidden (press [t] to show)."
        elif key == ord('4'):
            self.focused_pane = 'memory'
            self.status_msg = f"Window [4: {self.mem_view_mode.upper()}] focused."

        # Window cycle: w or Tab
        elif key in [9, ord('w'), ord('W')]:  # Tab or w
            panes = ['disasm', 'registers']
            if self.show_telemetry:
                panes.append('telemetry')
            panes.append('memory')
            idx = panes.index(self.focused_pane) if self.focused_pane in panes else 0
            if key == ord('W'):
                self.focused_pane = panes[(idx - 1) % len(panes)]
            else:
                self.focused_pane = panes[(idx + 1) % len(panes)]
            self.status_msg = f"Active window: [{self.focused_pane.upper()}]."

        # Window toggles: t (telemetry), z (zoom)
        elif key in [ord('t'), ord('T')]:
            self.show_telemetry = not self.show_telemetry
            if not self.show_telemetry and self.focused_pane == 'telemetry':
                self.focused_pane = 'memory'
            self.need_full_clear = True
            self.status_msg = f"Hardware telemetry window: {'SHOWN' if self.show_telemetry else 'HIDDEN'}."

        elif key in [ord('z'), ord('Z')]:
            if self.zoomed_pane:
                self.zoomed_pane = None
                self.status_msg = "Restored split window layout."
            else:
                self.zoomed_pane = self.focused_pane
                self.status_msg = f"Zoomed window [{self.zoomed_pane.upper()}] to full screen."
            self.need_full_clear = True

        # Inspector view modes: o (console output), v (stack/hex/console toggle)
        elif key == ord('o'):
            self.mem_view_mode = 'console' if self.mem_view_mode != 'console' else 'hex'
            self.focused_pane = 'memory'
            self.need_full_clear = True
            self.status_msg = f"Inspector mode: [{self.mem_view_mode.upper()}]."

        elif key in [ord('v'), ord('V')]:
            modes = ['hex', 'stack', 'console']
            cur_idx = modes.index(self.mem_view_mode) if self.mem_view_mode in modes else 0
            self.mem_view_mode = modes[(cur_idx + 1) % len(modes)]
            self.focused_pane = 'memory'
            self.need_full_clear = True
            self.status_msg = f"Inspector mode: [{self.mem_view_mode.upper()}]."

        # Step and run forward / backward
        elif key in [ord('s'), ord('S'), ord('\n'), 10]:
            self.running = False
            self.follow_ip = True
            self.step()

        elif key in [ord('u'), curses.KEY_BACKSPACE, ord('\b'), 127, 8]:
            self.running = False
            self.follow_ip = True
            self.step_back()

        elif key in [ord('c')]:
            self.running = True
            self.running_direction = 1
            self.status_msg = "▶ Running continuously forward... Press [p] to pause."

        elif key in [ord('C'), ord('U')]:
            self.running = True
            self.running_direction = -1
            self.status_msg = "◀ Running continuously backward (Rewinding)... Press [p] to pause."

        elif key in [ord('p'), ord('P')]:
            self.running = False
            self.status_msg = "Execution paused."

        elif key in [ord('r'), ord('R')]:
            self.running = False
            self._load_file()
            self._init_cpu()
            self.need_full_clear = True
            self.status_msg = "CPU reset and reloaded to initial state."

        elif key in [ord('b'), ord('B')]:
            if self.focused_pane == 'disasm' and self.edit_row in self.source_line_to_ip:
                target_ip = self.source_line_to_ip[self.edit_row]
            elif self.focused_pane == 'disasm' and self.instructions:
                target_ip = self.instructions[min(self.disasm_cursor_idx, len(self.instructions) - 1)][0]
            else:
                target_ip = self.BIU.reg.get('IP', 0)

            if target_ip in self.breakpoints:
                self.breakpoints.remove(target_ip)
                self.status_msg = f"Removed breakpoint at IP={target_ip:04X}h"
            else:
                self.breakpoints.add(target_ip)
                self.status_msg = f"Added breakpoint at IP={target_ip:04X}h"

        # Directional navigation: j / k / Down / Up
        elif key in [ord('k'), ord('K'), curses.KEY_UP]:
            if self.focused_pane == 'disasm':
                self.follow_ip = False
                self.disasm_cursor_idx = max(0, self.disasm_cursor_idx - 1)
                self.edit_row = max(0, self.edit_row - 1)
                cur_line = self.source_lines[self.edit_row] if self.source_lines else ""
                self.edit_col = min(len(cur_line), self.edit_col)
            elif self.focused_pane == 'memory':
                if self.mem_view_mode == 'console':
                    self.console_scroll_offset = max(0, self.console_scroll_offset - 1)
                else:
                    self.mem_offset = max(0, self.mem_offset - 16)

        elif key in [ord('j'), ord('J'), curses.KEY_DOWN]:
            if self.focused_pane == 'disasm':
                self.follow_ip = False
                self.disasm_cursor_idx = min(len(self.instructions) - 1, self.disasm_cursor_idx + 1)
                self.edit_row = min(len(self.source_lines) - 1, self.edit_row + 1)
                cur_line = self.source_lines[self.edit_row] if self.source_lines else ""
                self.edit_col = min(len(cur_line), self.edit_col)
            elif self.focused_pane == 'memory':
                if self.mem_view_mode == 'console':
                    self.console_scroll_offset += 1
                else:
                    self.mem_offset = min(0xFFFF, self.mem_offset + 16)

        # Vim jump to top / bottom: g / G
        elif key in [ord('g'), curses.KEY_HOME]:
            if self.focused_pane == 'disasm':
                self.disasm_cursor_idx = 0
                self.edit_row = 0
                self.edit_col = 0
            elif self.focused_pane == 'memory':
                self.mem_offset = 0
                self.console_scroll_offset = 0
            self.status_msg = "Jumped to beginning."

        elif key in [ord('G'), curses.KEY_END]:
            if self.focused_pane == 'disasm':
                self.disasm_cursor_idx = max(0, len(self.instructions) - 1)
                self.edit_row = max(0, len(self.source_lines) - 1)
                self.edit_col = 0
            elif self.focused_pane == 'memory':
                self.mem_offset = 0xFF00
            self.status_msg = "Jumped to end."

        elif key in [curses.KEY_PPAGE]:  # Page Up
            if self.focused_pane == 'disasm':
                self.disasm_cursor_idx = max(0, self.disasm_cursor_idx - 10)
                self.edit_row = max(0, self.edit_row - 10)
            elif self.focused_pane == 'memory':
                self.mem_offset = max(0, self.mem_offset - 128)

        elif key in [curses.KEY_NPAGE]:  # Page Down
            if self.focused_pane == 'disasm':
                self.disasm_cursor_idx = min(len(self.instructions) - 1, self.disasm_cursor_idx + 10)
                self.edit_row = min(len(self.source_lines) - 1, self.edit_row + 10)
            elif self.focused_pane == 'memory':
                self.mem_offset = min(0xFFFF, self.mem_offset + 128)

        elif key in [ord('m'), ord('M')]:
            self.mem_seg_idx = (self.mem_seg_idx + 1) % len(self.mem_segments)
            self.mem_offset = 0
            self.status_msg = f"Memory segment: [{self.mem_segments[self.mem_seg_idx]}]."

        elif key in [ord('+'), ord('=')]:
            self.step_delay = max(0.005, self.step_delay * 0.7)
            self.status_msg = f"Speed increased (delay: {self.step_delay*1000:0.1f}ms)."

        elif key in [ord('-'), ord('_')]:
            self.step_delay = min(1.0, self.step_delay * 1.4)
            self.status_msg = f"Speed decreased (delay: {self.step_delay*1000:0.1f}ms)."

        return True
