"""
Unit and Integration Tests for Antigravity 8086 TUI (Terminal User Interface).
Verifies initialization, instruction caching, stepping, breakpoints, LazyVim window management,
Which-Key leader menu, and key handlers.
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
        self.assertTrue(self.tui.EU.mute_stdout)
        self.assertTrue(self.tui.cpu.tui_mode)

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
        # Test Tab to cycle window: disasm -> registers -> telemetry -> memory -> disasm
        self.assertEqual(self.tui.focused_pane, 'disasm')
        self.tui._handle_key(None, 9)  # Tab key
        self.assertEqual(self.tui.focused_pane, 'registers')
        self.tui._handle_key(None, 9)
        self.assertEqual(self.tui.focused_pane, 'telemetry')
        self.tui._handle_key(None, 9)
        self.assertEqual(self.tui.focused_pane, 'memory')
        self.tui._handle_key(None, 9)
        self.assertEqual(self.tui.focused_pane, 'disasm')

        # Test direct window jump keys: 1, 2, 3, 4
        self.tui._handle_key(None, ord('3'))
        self.assertEqual(self.tui.focused_pane, 'telemetry')
        self.tui._handle_key(None, ord('1'))
        self.assertEqual(self.tui.focused_pane, 'disasm')
        self.tui._handle_key(None, ord('4'))
        self.assertEqual(self.tui.focused_pane, 'memory')

        # Test cursor move down 'j'
        self.tui.focused_pane = 'disasm'
        init_cursor = self.tui.disasm_cursor_idx
        self.tui._handle_key(None, ord('j'))
        self.assertEqual(self.tui.disasm_cursor_idx, init_cursor + 1)

        # Test cursor move up 'k'
        self.tui._handle_key(None, ord('k'))
        self.assertEqual(self.tui.disasm_cursor_idx, init_cursor)

        # Test Vim motions: 'G' (bottom) and 'g' (top)
        self.tui._handle_key(None, ord('G'))
        self.assertEqual(self.tui.disasm_cursor_idx, len(self.tui.instructions) - 1)
        self.tui._handle_key(None, ord('g'))
        self.assertEqual(self.tui.disasm_cursor_idx, 0)

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

    def test_space_leader_which_key_menu(self):
        self.assertFalse(self.tui.show_leader_menu)
        # Space opens Which-Key palette
        self.tui._handle_key(None, ord(' '))
        self.assertTrue(self.tui.show_leader_menu)

        # Pressing Space again closes Which-Key palette
        self.tui._handle_key(None, ord(' '))
        self.assertFalse(self.tui.show_leader_menu)

        # Space then a command key executes command and closes menu
        self.tui._handle_key(None, ord(' '))
        self.assertTrue(self.tui.show_leader_menu)
        self.tui._handle_key(None, ord('p'))
        self.assertFalse(self.tui.show_leader_menu)
        self.assertFalse(self.tui.running)

    def test_lazyvim_window_toggles(self):
        # Test Telemetry toggle 't'
        self.assertTrue(self.tui.show_telemetry)
        self.tui._handle_key(None, ord('t'))
        self.assertFalse(self.tui.show_telemetry)
        self.tui._handle_key(None, ord('t'))
        self.assertTrue(self.tui.show_telemetry)

        # Test Window Zoom 'z'
        self.assertIsNone(self.tui.zoomed_pane)
        self.tui.focused_pane = 'disasm'
        self.tui._handle_key(None, ord('z'))
        self.assertEqual(self.tui.zoomed_pane, 'disasm')
        self.tui._handle_key(None, ord('z'))
        self.assertIsNone(self.tui.zoomed_pane)

    def test_view_modes_stack_and_console(self):
        self.assertEqual(self.tui.mem_view_mode, 'hex')

        # 'v' cycles view modes: hex -> stack -> console -> hex
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'stack')
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'console')
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'hex')

        # 'o' jumps to console output view directly
        self.tui._handle_key(None, ord('o'))
        self.assertEqual(self.tui.mem_view_mode, 'console')
        self.tui._handle_key(None, ord('o'))
        self.assertEqual(self.tui.mem_view_mode, 'hex')

    def test_register_snapshot_and_change_detection(self):
        snap1 = self.tui._snapshot_regs()
        self.assertEqual(snap1['AX'], 0)

        self.tui.step() # MOV AX, 0x2000
        snap2 = self.tui._snapshot_regs()
        self.assertEqual(snap2['AX'], 0x2000)
        self.assertNotEqual(snap1['AX'], snap2['AX'])


if __name__ == "__main__":
    unittest.main()
