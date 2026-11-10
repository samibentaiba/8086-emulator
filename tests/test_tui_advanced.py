"""
Advanced & Complex End-to-End TUI Test Suite for 8086 Emulator.
Exercises student workflows, canvas boundary clipping, window management,
reverse debugging collision, stack viewer, hardware telemetry, and editing stress.
"""

import os
import unittest
import tempfile
from unittest.mock import patch

from ui.tui import EmulatorTUI, SEG_INIT
from emulator.peripherals.manager import PeripheralManager


class MockCursesWindow:
    """Mock curses window recording all draw calls and enforcing boundary limits."""
    def __init__(self, h=24, w=80):
        self.h = h
        self.w = w
        self.calls = []

    def getmaxyx(self):
        return (self.h, self.w)

    def addstr(self, y, x, text, attr=0):
        self.calls.append((y, x, str(text), attr))

    def move(self, y, x):
        pass

    def clear(self):
        pass

    def erase(self):
        pass

    def refresh(self):
        pass


class TestTUIAdvancedScenarios(unittest.TestCase):

    def setUp(self):
        PeripheralManager.reset_instance()
        self.temp_files = []

    def tearDown(self):
        PeripheralManager.reset_instance()
        for f in self.temp_files:
            try:
                os.remove(f)
            except OSError:
                pass

    def _create_temp_asm(self, code):
        tf = tempfile.NamedTemporaryFile('w', suffix='.asm', delete=False)
        tf.write(code)
        tf.close()
        self.temp_files.append(tf.name)
        return tf.name

    def test_01_student_live_patching_and_reverse_debugging_workflow(self):
        """
        Complex student scenario:
        1. Student starts program with an erroneous value.
        2. Steps forward into execution.
        3. Realizes the mistake, steps backward to the exact line.
        4. Enters INSERT mode, fixes the bug, hits <Esc> to reassemble on the fly.
        5. Continues execution forward to verify the corrected machine state.
        6. Reverses all the way back to cycle 0 cleanly.
        """
        buggy_code = """
        DATA SEGMENT
            RESULT DW 0
        DATA ENDS
        CODE SEGMENT
        ASSUME CS:CODE, DS:DATA
        START:
            MOV AX, DATA
            MOV DS, AX
            MOV AX, 10
            ADD AX, 99 ; Error: student intended ADD AX, 5
            MOV [0], AX
            HLT
        CODE ENDS
        END START
        """
        filepath = self._create_temp_asm(buggy_code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Step 4 instructions forward: MOV AX, DATA -> MOV DS, AX -> MOV AX, 10 -> ADD AX, 99
        for _ in range(4):
            tui.step()

        self.assertEqual(tui.EU.reg['AX'], 109)
        self.assertEqual(len(tui.cpu.history), 4)

        # Student realizes 109 is wrong! Rewinds 1 instruction back before ADD AX, 99
        tui.step_back()
        self.assertEqual(tui.EU.reg['AX'], 10)
        self.assertEqual(len(tui.cpu.history), 3)

        # Student enters INSERT mode to patch the line
        # Find line with 'ADD AX, 99'
        add_line_idx = None
        for idx, line in enumerate(tui.source_lines):
            if "ADD AX, 99" in line.upper():
                add_line_idx = idx
                break
        self.assertIsNotNone(add_line_idx)

        tui.focused_pane = 'disasm'
        tui.edit_row = add_line_idx
        tui._handle_key(None, ord('i'))
        self.assertEqual(tui.mode, 'INSERT')

        # Replace 'ADD AX, 99' with 'ADD AX, 5'
        tui.source_lines[add_line_idx] = "            ADD AX, 5"
        tui.modified = True

        # Press <Esc> to trigger on-the-fly reassembly and memory reload
        tui._handle_key(None, 27)
        self.assertEqual(tui.mode, 'NORMAL')
        self.assertIn("Assembled successfully", tui.status_msg)

        # Save to disk
        tui.save_to_disk()
        self.assertFalse(tui.modified)

        # Now step forward through the patched instruction and store to memory
        tui.step()
        self.assertEqual(tui.EU.reg['AX'], 15) # Successfully patched!

        tui.step() # MOV [0], AX
        data_addr = 0x20000
        # 15 is 0x000F in memory (little endian: 0x0F, 0x00)
        self.assertEqual(tui.memory.rb(data_addr), ['0xf'])
        self.assertEqual(tui.memory.rb(data_addr + 1), ['0x0'])

        # Rewind all the way back to start
        while tui.cpu.can_step_back():
            tui.step_back()

        self.assertEqual(tui.cpu.cycle_count, 0)
        self.assertFalse(tui.step_back())
        self.assertIn("Already at start", tui.status_msg)

    @patch('curses.color_pair', return_value=0)
    def test_02_strict_canvas_boundary_clipping_mathematical_guarantee(self, mock_cp):
        """
        Zero-Glitch Verification:
        Renders every pane with ultra-long strings (500+ chars) under 80x24 constraints.
        Mathematically asserts that NO curses string exceeds bounds or writes out-of-range.
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Inject extreme strings
        long_comment = "    ; " + "VERY_LONG_COMMENT_" * 35
        tui.source_lines[0] = long_comment
        tui.EU.output = "OUTPUT_" * 80 + "\n" + "ANOTHER_LONG_LINE_" * 40
        tui.status_msg = "STATUS_" * 50

        mock_win = MockCursesWindow(h=24, w=80)

        # Render all UI panes
        tui._render_header(mock_win, 80)
        tui._render_disassembly(mock_win, 1, 0, 20, 40)
        tui._render_registers(mock_win, 1, 40, 7, 40)
        tui._render_telemetry(mock_win, 8, 40, 7, 40)
        tui._render_memory(mock_win, 15, 40, 6, 40)
        tui._render_stack_view(mock_win, 15, 40, 6, 40)
        tui._render_console_view(mock_win, 15, 40, 6, 40)
        tui._render_footer(mock_win, 24, 80)
        tui._render_leader_menu(mock_win, 24, 80)
        tui._render_help_modal(mock_win, 24, 80)

        # Verify every single call to addstr satisfies bounding requirements
        self.assertGreater(len(mock_win.calls), 100)
        for y, x, text, attr in mock_win.calls:
            self.assertGreaterEqual(y, 0, f"Negative Y coordinate: {y}")
            self.assertLess(y, 24, f"Y coordinate out of bounds: {y} >= 24")
            self.assertGreaterEqual(x, 0, f"Negative X coordinate: {x}")
            self.assertLess(x, 80, f"X coordinate out of bounds: {x} >= 80")
            # Text must not spill past screen width
            self.assertLessEqual(x + len(text), 80, f"Spillover: x({x}) + len({len(text)}) > 80: '{text}'")

    def test_03_bidirectional_multi_breakpoint_stepping(self):
        """
        Verify multiple breakpoints stop execution accurately in both forward and reverse runs.
        """
        code = """
        CODE SEGMENT
        START:
            MOV AX, 10
            MOV BX, 20
            MOV CX, 30
            MOV DX, 40
            HLT
        CODE ENDS
        END START
        """
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Set breakpoints at IP=1 (MOV BX, 20) and IP=3 (MOV DX, 40)
        tui.breakpoints.add(1)
        tui.breakpoints.add(3)

        # Run forward continuously -> should hit breakpoint at IP=1
        tui._handle_key(None, ord('c'))
        self.assertTrue(tui.running)
        while tui.running:
            tui.step()
        self.assertEqual(tui.BIU.reg['IP'], 1)
        self.assertEqual(tui.EU.reg['AX'], 10)
        self.assertEqual(tui.EU.reg['BX'], 0) # Hasn't executed yet

        # Run forward again -> should hit breakpoint at IP=3
        tui._handle_key(None, ord('c'))
        while tui.running:
            tui.step()
        self.assertEqual(tui.BIU.reg['IP'], 3)
        self.assertEqual(tui.EU.reg['AX'], 10)
        self.assertEqual(tui.EU.reg['BX'], 20)
        self.assertEqual(tui.EU.reg['CX'], 30)
        self.assertEqual(tui.EU.reg['DX'], 0) # Hasn't executed yet

        # Step one more to execute MOV DX, 40
        tui.step()
        self.assertEqual(tui.EU.reg['DX'], 40)

        # Now run backward (rewind) -> should hit reverse breakpoint at IP=3
        tui._handle_key(None, ord('C'))
        self.assertTrue(tui.running)
        self.assertEqual(tui.running_direction, -1)
        while tui.running:
            tui.step_back()
        self.assertEqual(tui.BIU.reg['IP'], 3)
        self.assertEqual(tui.EU.reg['DX'], 0) # DX was reverted
        self.assertIn("Reverse breakpoint hit", tui.status_msg)

        # Run backward again -> should hit reverse breakpoint at IP=1
        tui._handle_key(None, ord('C'))
        while tui.running:
            tui.step_back()
        self.assertEqual(tui.BIU.reg['IP'], 1)
        self.assertEqual(tui.EU.reg['BX'], 0) # BX was reverted
        self.assertIn("Reverse breakpoint hit", tui.status_msg)

    def test_04_window_manager_zoom_and_pane_focus_matrix(self):
        """
        Verify LazyVim window layout management:
        - Direct jump (1, 2, 3, 4)
        - Window cycling (Tab/w and W)
        - Telemetry toggle (t) skipping hidden panes
        - Zoom toggle (z)
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Direct jumps
        tui._handle_key(None, ord('2'))
        self.assertEqual(tui.focused_pane, 'registers')
        tui._handle_key(None, ord('3'))
        self.assertEqual(tui.focused_pane, 'telemetry')
        tui._handle_key(None, ord('4'))
        self.assertEqual(tui.focused_pane, 'memory')
        tui._handle_key(None, ord('1'))
        self.assertEqual(tui.focused_pane, 'disasm')

        # Window zoom toggle ('z')
        tui._handle_key(None, ord('z'))
        self.assertEqual(tui.zoomed_pane, 'disasm')
        self.assertTrue(tui.need_full_clear)
        tui._handle_key(None, ord('z')) # unzoom
        self.assertIsNone(tui.zoomed_pane)

        # Hide telemetry window with 't'
        self.assertTrue(tui.show_telemetry)
        tui._handle_key(None, ord('t'))
        self.assertFalse(tui.show_telemetry)

        # Cycling with Tab should only cycle: disasm -> registers -> memory -> disasm
        tui.focused_pane = 'disasm'
        tui._handle_key(None, 9) # Tab
        self.assertEqual(tui.focused_pane, 'registers')
        tui._handle_key(None, 9) # Tab
        self.assertEqual(tui.focused_pane, 'memory') # Skips telemetry!
        tui._handle_key(None, 9) # Tab
        self.assertEqual(tui.focused_pane, 'disasm')

        # Reverse cycling with 'W'
        tui._handle_key(None, ord('W'))
        self.assertEqual(tui.focused_pane, 'memory')
        tui._handle_key(None, ord('W'))
        self.assertEqual(tui.focused_pane, 'registers')

        # Re-enable telemetry with 't'
        tui._handle_key(None, ord('t'))
        self.assertTrue(tui.show_telemetry)

    def test_05_interactive_code_editor_multiline_split_and_merge(self):
        """
        Verify multi-line code splitting with Enter and line merging with Backspace in INSERT mode.
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        init_line_count = len(tui.source_lines)
        tui.focused_pane = 'disasm'
        tui.edit_row = 2 # 'MOV AX, 1'
        tui.edit_col = 4 # between 'MOV ' and 'AX, 1'
        tui.mode = 'INSERT'

        # Press Enter: should split line
        tui._handle_key(None, ord('\n'))
        self.assertEqual(len(tui.source_lines), init_line_count + 1)
        self.assertEqual(tui.source_lines[2], "MOV ")
        self.assertEqual(tui.source_lines[3], "AX, 1")
        self.assertEqual(tui.edit_row, 3)
        self.assertEqual(tui.edit_col, 0)

        # Press Backspace at column 0 of line 3: should merge back with line 2
        tui._handle_key(None, 127) # Backspace
        self.assertEqual(len(tui.source_lines), init_line_count)
        self.assertEqual(tui.source_lines[2], "MOV AX, 1")
        self.assertEqual(tui.edit_row, 2)
        self.assertEqual(tui.edit_col, 4)

    @patch('curses.color_pair', return_value=0)
    def test_06_stack_viewer_call_stack_telemetry(self, mock_cp):
        """
        Verify stack inspection displays SS:SP address, word hex values, and follows pushes/pops.
        """
        code = """
        CODE SEGMENT
        START:
            MOV AX, 01234H
            MOV BX, 05678H
            PUSH AX
            PUSH BX
            POP CX
            HLT
        CODE ENDS
        END START
        """
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)
        tui.mem_view_mode = 'stack'

        mock_win = MockCursesWindow(h=15, w=40)
        tui._render_stack_view(mock_win, 1, 0, 10, 40)

        # Step through PUSH AX and PUSH BX
        tui.step() # MOV AX
        tui.step() # MOV BX
        tui.step() # PUSH AX
        tui.step() # PUSH BX

        mock_win.calls.clear()
        tui._render_stack_view(mock_win, 1, 0, 10, 40)
        rendered_texts = " ".join(call[2] for call in mock_win.calls)

        # Stack top (SP+0) should contain 5678H (BX), SP+2 should contain 1234H (AX)
        self.assertIn("5678", rendered_texts)
        self.assertIn("1234", rendered_texts)

        # Rewind PUSH BX
        tui.step_back()
        mock_win.calls.clear()
        tui._render_stack_view(mock_win, 1, 0, 10, 40)
        rendered_after_rewind = " ".join(call[2] for call in mock_win.calls)
        # 1234 is now at top of stack
        self.assertIn("1234", rendered_after_rewind)

    @patch('curses.color_pair', return_value=0)
    def test_07_console_output_inspector_scrolling_and_navigation(self, mock_cp):
        """
        Verify program console output viewer correctly decodes and scrolls large output.
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Inject 30 lines of console output
        output_lines = [f"Program Output Line #{i}" for i in range(1, 31)]
        tui.EU.output = "\n".join(output_lines)
        tui.mem_view_mode = 'console'
        tui.focused_pane = 'memory'

        mock_win = MockCursesWindow(h=12, w=40)
        tui._render_console_view(mock_win, 1, 0, 10, 40)

        # Test scroll navigation with 'j' and 'k'
        tui._handle_key(None, ord('j'))
        self.assertGreaterEqual(tui.console_scroll_offset, 1)

        tui._handle_key(None, ord('k'))
        self.assertEqual(tui.console_scroll_offset, 0)

        # Test jump to end with 'G' and start with 'g'
        tui._handle_key(None, ord('G'))
        tui._handle_key(None, ord('g'))
        self.assertEqual(tui.console_scroll_offset, 0)

    def test_08_speed_throttling_and_dynamic_direction_flip(self):
        """
        Verify execution speed adjustments with '+' / '-' and on-the-fly direction reversal.
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        init_delay = tui.step_delay

        # Speed up with '+'
        tui._handle_key(None, ord('+'))
        self.assertLess(tui.step_delay, init_delay)
        self.assertIn("Speed increased", tui.status_msg)

        # Slow down with '-'
        tui._handle_key(None, ord('-'))
        tui._handle_key(None, ord('-'))
        self.assertGreater(tui.step_delay, init_delay * 0.7)
        self.assertIn("Speed decreased", tui.status_msg)

        # Start running forward
        tui._handle_key(None, ord('c'))
        self.assertTrue(tui.running)
        self.assertEqual(tui.running_direction, 1)

        # Flip direction to backward while in motion
        tui._handle_key(None, ord('C'))
        self.assertTrue(tui.running)
        self.assertEqual(tui.running_direction, -1)
        self.assertIn("Rewinding", tui.status_msg)

        # Pause
        tui._handle_key(None, ord('p'))
        self.assertFalse(tui.running)
        self.assertIn("Execution paused", tui.status_msg)

    def test_09_which_key_and_help_modal_navigation(self):
        """
        Verify Which-Key palette (<Space>) and Help modal (?) event loop handling.
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Open Which-Key menu with Space
        tui._handle_key(None, ord(' '))
        self.assertTrue(tui.show_leader_menu)
        self.assertTrue(tui.need_full_clear)

        # Press 's' to execute step through Which-Key
        tui._handle_key(None, ord('s'))
        self.assertFalse(tui.show_leader_menu)
        self.assertEqual(tui.cpu.cycle_count, 2)

        # Open Which-Key menu and dismiss with <Esc>
        tui._handle_key(None, ord(' '))
        self.assertTrue(tui.show_leader_menu)
        tui._handle_key(None, 27) # Esc
        self.assertFalse(tui.show_leader_menu)

        # Open Help modal with '?'
        tui._handle_key(None, ord('?'))
        self.assertTrue(tui.show_help)
        self.assertTrue(tui.need_full_clear)

        # Dismiss help with any key
        tui._handle_key(None, ord('x'))
        self.assertFalse(tui.show_help)
        self.assertTrue(tui.need_full_clear)

    def test_10_memory_segment_cycling_and_offset_navigation(self):
        """
        Verify cycling memory segments with 'm' and scrolling address offsets.
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Default is 'DS'
        self.assertEqual(tui.mem_segments[tui.mem_seg_idx], 'DS')

        # Cycle through segments: DS -> CS -> SS -> ES -> VIDEO -> DS
        expected_order = ['CS', 'SS', 'ES', 'VIDEO', 'DS']
        for seg in expected_order:
            tui._handle_key(None, ord('m'))
            self.assertEqual(tui.mem_segments[tui.mem_seg_idx], seg)
            self.assertEqual(tui.mem_offset, 0)

        # In memory pane, test scrolling offsets with j, k, PageDown, PageUp
        tui.focused_pane = 'memory'
        tui.mem_view_mode = 'hex'

        # Scroll down with 'j' (+16 bytes)
        tui._handle_key(None, ord('j'))
        self.assertEqual(tui.mem_offset, 16)

        # Scroll down with PageDown (+128 bytes)
        tui._handle_key(None, 338) # KEY_NPAGE
        self.assertEqual(tui.mem_offset, 16 + 128)

        # Scroll up with 'k' (-16 bytes)
        tui._handle_key(None, ord('k'))
        self.assertEqual(tui.mem_offset, 128)

        # Jump to start with 'g'
        tui._handle_key(None, ord('g'))
        self.assertEqual(tui.mem_offset, 0)

    @patch('curses.color_pair', return_value=0)
    def test_11_hardware_telemetry_rendering_accuracy(self, mock_cp):
        """
        Verify live rendering of Virtual Traffic Lights and Stepper Motor inside Telemetry pane.
        """
        code = """
        CODE SEGMENT
        START:
            MOV AX, 00924H
            OUT 4, AX
            MOV AL, 003H
            OUT 7, AL
            HLT
        CODE ENDS
        END START
        """
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Step past OUT 4, AX and OUT 7, AL
        tui.step() # MOV AX
        tui.step() # OUT 4
        tui.step() # MOV AL
        tui.step() # OUT 7

        mock_win = MockCursesWindow(h=12, w=80)
        tui._render_telemetry(mock_win, 1, 0, 10, 80)
        rendered = " ".join(call[2] for call in mock_win.calls)

        # Verify North/West/South/East and Stepper motor keywords are present
        self.assertIn("N:", rendered)
        self.assertIn("W:", rendered)
        self.assertIn("S:", rendered)
        self.assertIn("E:", rendered)
        self.assertIn("Stepper", rendered)

    def test_12_syntax_error_correction_and_resilient_state_recovery(self):
        """
        Verify that typing a syntax error displays AssemblyError without crashing,
        and fixing it allows immediate execution forward.
        """
        code = "CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n"
        filepath = self._create_temp_asm(code)
        tui = EmulatorTUI(filepath, enable_gui_windows=False)

        # Enter INSERT mode
        tui._handle_key(None, ord('i'))
        self.assertEqual(tui.mode, 'INSERT')

        # Introduce broken data definition: 'VAL DB NOT_A_NUM'
        tui.source_lines.insert(2, "    VAL DB NOT_A_NUM")
        tui.modified = True
        tui._handle_key(None, 27) # <Esc> exits insert mode and recompiles

        # Should show error message and NOT crash
        self.assertIn("AssemblyError", tui.status_msg)

        # Now enter INSERT mode again and fix it: remove the bad line and change MOV AX, 1 to MOV AX, 042H
        tui._handle_key(None, ord('i'))
        del tui.source_lines[2] # remove the bad line
        tui.source_lines[2] = "    MOV AX, 042H"
        tui._handle_key(None, 27) # <Esc> exits insert mode and recompiles
        self.assertIn("Assembled successfully", tui.status_msg)

        # Can now execute cleanly
        tui.step()
        self.assertEqual(tui.EU.reg['AX'], 0x42)


if __name__ == '__main__':
    unittest.main()
