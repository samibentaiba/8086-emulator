"""
Unit and Integration Tests for Antigravity 8086 TUI (Terminal User Interface).
Verifies initialization, instruction caching, stepping, breakpoints, and key handlers.
"""

import os
import unittest
from ui.tui import EmulatorTUI


class TestEmulatorTUI(unittest.TestCase):
    def setUp(self):
        self.asm_path = os.path.join(os.path.dirname(__file__), "Requirement", "bubble_sort.asm")
        self.tui = EmulatorTUI(self.asm_path, enable_gui_windows=False)

    def tearDown(self):
        from emulator.peripherals.manager import PeripheralManager
        PeripheralManager.reset_instance()

    def test_tui_initialization(self):
        self.assertIsNotNone(self.tui.cpu)
        self.assertIsNotNone(self.tui.instructions)
        self.assertGreater(len(self.tui.instructions), 0)
        self.assertEqual(self.tui.BIU.reg.get('IP'), 0)
        self.assertEqual(self.tui.focused_pane, 'disasm')
        self.assertFalse(self.tui.running)

    def test_instructions_cached(self):
        # First instruction should be MOV AX, 0x2000
        idx, opcode, opds = self.tui.instructions[0]
        self.assertEqual(idx, 0)
        self.assertEqual(opcode, "MOV")
        self.assertIn("AX", opds)

    def test_step_execution(self):
        initial_ip = self.tui.BIU.reg.get('IP', 0)
        self.assertEqual(initial_ip, 0)

        # Step 1: MOV AX, 0x2000
        stepped = self.tui.step()
        self.assertTrue(stepped)
        self.assertEqual(self.tui.EU.reg.get('AX'), 0x2000)
        self.assertNotEqual(self.tui.BIU.reg.get('IP'), initial_ip)

    def test_breakpoint_toggle_and_hit(self):
        # Set breakpoint at offset 2 (MOV CX, DS:[0x10])
        self.tui.breakpoints.add(2)
        self.assertIn(2, self.tui.breakpoints)

        # Run until breakpoint
        self.tui.running = True
        max_steps = 100
        steps = 0
        while self.tui.running and steps < max_steps:
            if not self.tui.step():
                break
            steps += 1

        self.assertFalse(self.tui.running)
        self.assertEqual(self.tui.BIU.reg.get('IP'), 2)
        self.assertIn("Breakpoint hit", self.tui.status_msg)

    def test_key_handling_navigation(self):
        # Test Tab to switch pane
        ret = self.tui._handle_key(None, 9)  # Tab key
        self.assertTrue(ret)
        self.assertEqual(self.tui.focused_pane, 'memory')

        ret = self.tui._handle_key(None, 9)
        self.assertTrue(ret)
        self.assertEqual(self.tui.focused_pane, 'disasm')

        # Test cursor move down 'j'
        init_cursor = self.tui.disasm_cursor_idx
        self.tui._handle_key(None, ord('j'))
        self.assertEqual(self.tui.disasm_cursor_idx, init_cursor + 1)

        # Test cursor move up 'k'
        self.tui._handle_key(None, ord('k'))
        self.assertEqual(self.tui.disasm_cursor_idx, init_cursor)

        # Test memory segment cycle 'm'
        init_seg_idx = self.tui.mem_seg_idx
        self.tui._handle_key(None, ord('m'))
        self.assertEqual(self.tui.mem_seg_idx, (init_seg_idx + 1) % len(self.tui.mem_segments))

        # Test help modal toggle '?'
        self.assertFalse(self.tui.show_help)
        self.tui._handle_key(None, ord('?'))
        self.assertTrue(self.tui.show_help)
        # Any key closes help
        self.tui._handle_key(None, ord('x'))
        self.assertFalse(self.tui.show_help)

        # Test quit key 'q'
        ret = self.tui._handle_key(None, ord('q'))
        self.assertFalse(ret)

    def test_register_snapshot_and_change_detection(self):
        snap1 = self.tui._snapshot_regs()
        self.assertEqual(snap1['AX'], 0)

        self.tui.step() # MOV AX, 0x2000
        snap2 = self.tui._snapshot_regs()
        self.assertEqual(snap2['AX'], 0x2000)
        self.assertNotEqual(snap1['AX'], snap2['AX'])

    def test_stack_view_toggle(self):
        self.assertEqual(self.tui.mem_view_mode, 'hex')
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'stack')
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'hex')


if __name__ == "__main__":
    unittest.main()
