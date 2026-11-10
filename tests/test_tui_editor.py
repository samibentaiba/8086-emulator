"""
Unit Tests for LazyVim Modal Code Editor & 1-to-1 Instruction Execution Tracking in 8086 Curses TUI.
"""

import io
import os
import sys
import tempfile
import unittest

from ui.tui import EmulatorTUI, SEG_INIT
from emulator.peripherals.manager import PeripheralManager
from emulator.memory import Memory
from emulator.assembler import Assembler


class TestTUIModalEditor(unittest.TestCase):
    def setUp(self):
        PeripheralManager.reset_instance()
        self.bubble_sort_path = os.path.join(
            os.path.dirname(__file__), "Requirement", "bubble_sort.asm"
        )
        self.tui = EmulatorTUI(self.bubble_sort_path, enable_gui_windows=False)

    def tearDown(self):
        PeripheralManager.reset_instance()

    def test_01_exact_one_to_one_execution_tracking(self):
        """Verify that at every clock cycle, exactly ONE line is executing and marked."""
        # Check that symbol table has mapped all instructions
        self.assertGreater(len(self.tui.ip_to_source_line), 20)
        self.assertEqual(len(self.tui.ip_to_source_line), len(self.tui.instructions))

        # At IP=0: exactly one line should match
        ip0_line = self.tui.ip_to_source_line[0]
        self.assertIn("MOV AX", self.tui.source_lines[ip0_line].upper())

        # Step 1: MOV AX, DATA -> IP becomes 1
        self.tui.step()
        self.assertEqual(self.tui.BIU.reg.get('IP'), 1)
        ip1_line = self.tui.ip_to_source_line[1]
        self.assertIn("MOV DS", self.tui.source_lines[ip1_line].upper())
        self.assertEqual(self.tui.edit_row, ip1_line)
        self.assertNotEqual(ip0_line, ip1_line)

        # Step 2: MOV DS, AX -> IP becomes 2
        self.tui.step()
        self.assertEqual(self.tui.BIU.reg.get('IP'), 2)
        ip2_line = self.tui.ip_to_source_line[2]
        self.assertIn("MOV CX", self.tui.source_lines[ip2_line].upper())
        self.assertEqual(self.tui.edit_row, ip2_line)

        # Step 3: MOV CX, COUNT -> IP becomes 3 (DEC CX)
        self.tui.step()
        self.assertEqual(self.tui.BIU.reg.get('IP'), 3)
        ip3_line = self.tui.ip_to_source_line[3]
        self.assertIn("DEC CX", self.tui.source_lines[ip3_line].upper())
        self.assertEqual(self.tui.edit_row, ip3_line)

        # Ensure that ip2_line is distinct from ip0_line and ip1_line (no multi-MOV collision)
        self.assertNotEqual(ip0_line, ip2_line)
        self.assertNotEqual(ip1_line, ip2_line)

    def test_02_breakpoint_line_mapping(self):
        """Verify that toggling breakpoints on a source line maps to the exact IP."""
        # Find line for CMP AL,DL
        cmp_line = None
        for idx, line in enumerate(self.tui.source_lines):
            clean = line.replace(" ", "").upper()
            if "CMPAL,DL" in clean:
                cmp_line = idx
                break
        self.assertIsNotNone(cmp_line)
        expected_ip = self.tui.source_line_to_ip[cmp_line]

        # Move cursor to that line and press 'b'
        self.tui.focused_pane = 'disasm'
        self.tui.edit_row = cmp_line
        self.tui._handle_key(None, ord('b'))
        self.assertIn(expected_ip, self.tui.breakpoints)
        self.assertIn(f"IP={expected_ip:04X}h", self.tui.status_msg)

        # Press 'b' again to toggle off
        self.tui._handle_key(None, ord('b'))
        self.assertNotIn(expected_ip, self.tui.breakpoints)

    def test_03_modal_editor_normal_and_insert_modes(self):
        """Verify entering INSERT mode with 'i', editing, and exiting with <Esc>."""
        self.assertEqual(self.tui.mode, 'NORMAL')

        # Press 'i': enters INSERT mode
        self.tui._handle_key(None, ord('i'))
        self.assertEqual(self.tui.mode, 'INSERT')
        self.assertIn("INSERT", self.tui.status_msg)

        # Type some characters in insert mode: 'NOP'
        init_line = self.tui.source_lines[self.tui.edit_row]
        for ch in "; testing insert mode":
            self.tui._handle_key(None, ord(ch))
        self.assertTrue(self.tui.modified)
        self.assertIn("; testing insert mode", self.tui.source_lines[self.tui.edit_row])

        # Press <Esc> (27): returns to NORMAL mode and recompiles
        self.tui._handle_key(None, 27)
        self.assertEqual(self.tui.mode, 'NORMAL')
        self.assertTrue(self.tui.need_full_clear)
        self.assertIn("Assembled successfully", self.tui.status_msg)

    def test_04_modal_editor_open_line_and_append(self):
        """Verify 'a' (append) and 'O' (open line)."""
        # Test 'a'
        init_col = self.tui.edit_col
        self.tui._handle_key(None, ord('a'))
        self.assertEqual(self.tui.mode, 'INSERT')
        self.assertEqual(self.tui.edit_col, init_col + 1)
        self.tui._handle_key(None, 27) # Return to normal

        # Test 'O' (open line)
        init_lines_count = len(self.tui.source_lines)
        init_row = self.tui.edit_row
        self.tui._handle_key(None, ord('O'))
        self.assertEqual(self.tui.mode, 'INSERT')
        self.assertEqual(len(self.tui.source_lines), init_lines_count + 1)
        self.assertEqual(self.tui.edit_row, init_row + 1)
        self.tui._handle_key(None, 27)

    def test_05_modal_editor_deletion_and_navigation(self):
        """Verify 'x' (delete char), 'd' (delete line), 'h'/'l' (col motions)."""
        self.tui.source_lines[0] = "ABCDEF"
        self.tui.edit_row = 0
        self.tui.edit_col = 2  # on 'C'

        # Press 'h' to move left
        self.tui._handle_key(None, ord('h'))
        self.assertEqual(self.tui.edit_col, 1)

        # Press 'l' to move right
        self.tui._handle_key(None, ord('l'))
        self.assertEqual(self.tui.edit_col, 2)

        # Press 'x' to delete 'C'
        self.tui._handle_key(None, ord('x'))
        self.assertEqual(self.tui.source_lines[0], "ABDEF")

        # Press 'd' to delete the line
        init_count = len(self.tui.source_lines)
        self.tui._handle_key(None, ord('d'))
        self.assertEqual(len(self.tui.source_lines), init_count - 1)

    def test_06_assembly_error_recovery(self):
        """Verify syntax error in INSERT mode displays AssemblyError on <Esc> without losing text."""
        self.tui._handle_key(None, ord('i'))
        # Insert an invalid data definition that triggers compile error
        self.tui.source_lines.insert(7, "    VAL_BAD DB INVALID_NOT_A_NUM")
        self.tui._handle_key(None, 27)  # <Esc>

        self.assertEqual(self.tui.mode, 'NORMAL')
        self.assertIn("AssemblyError", self.tui.status_msg)
        # Verify text was preserved so user can fix it
        self.assertIn("    VAL_BAD DB INVALID_NOT_A_NUM", self.tui.source_lines)

    def test_07_save_to_disk(self):
        """Verify save_to_disk() writes changes to the source file."""
        with tempfile.NamedTemporaryFile('w', suffix='.asm', delete=False) as tf:
            tf.write("CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n")
            temp_path = tf.name

        try:
            tui = EmulatorTUI(temp_path, enable_gui_windows=False)
            tui.source_lines.append("; appended comment")
            tui.modified = True
            tui.save_to_disk()
            self.assertFalse(tui.modified)
            self.assertIn("Saved", tui.status_msg)

            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("; appended comment", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_08_stdout_isolation_and_silence(self):
        """Verify Memory.load(verbose=False) produces zero output on stdout."""
        assembler = Assembler(SEG_INIT)
        exe = assembler.compile("CODE SEGMENT\nSTART:\nMOV AX, 1\nCODE ENDS\nEND START\n")
        mem = Memory(0xFFFF, 0x1000)

        captured_stdout = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured_stdout
        try:
            mem.load(exe, verbose=False)
        finally:
            sys.stdout = old_stdout

        output = captured_stdout.getvalue()
        self.assertEqual(output.strip(), "")


if __name__ == '__main__':
    unittest.main()
