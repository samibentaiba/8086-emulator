"""
End-to-End "Student Learning Assembly" Comprehensive TUI Integration Test Suite.
Simulates a student using the 8086 TUI to learn assembly step by step, testing all
features, navigation, breakpoints, memory/stack/console inspection, and hardware peripherals.
"""

import os
import unittest
from ui.tui import EmulatorTUI
from emulator.assembler import to_decimal
from emulator.peripherals.manager import PeripheralManager


class TestStudentLearningWorkflow(unittest.TestCase):
    def setUp(self):
        PeripheralManager.reset_instance()
        self.bubble_sort_path = os.path.join(
            os.path.dirname(__file__), "Requirement", "bubble_sort.asm"
        )
        self.traffic_lights_path = os.path.join(
            os.path.dirname(__file__), "Hardware", "traffic_lights_demo.asm"
        )
        self.stepper_motor_path = os.path.join(
            os.path.dirname(__file__), "Hardware", "stepper_motor_demo.asm"
        )
        self.tui = EmulatorTUI(self.bubble_sort_path, enable_gui_windows=False)

    def tearDown(self):
        PeripheralManager.reset_instance()

    def test_01_student_inspects_initial_state(self):
        """Student opens bubble_sort.asm and inspects initial CPU/TUI state."""
        # Check initial IP and segment registers
        self.assertEqual(self.tui.BIU.reg.get('IP'), 0)
        self.assertEqual(self.tui.BIU.reg.get('CS'), 0x3000)
        self.assertEqual(self.tui.BIU.reg.get('DS'), 0x2000)

        # Check default UI state
        self.assertEqual(self.tui.focused_pane, 'disasm')
        self.assertTrue(self.tui.show_telemetry)
        self.assertIsNone(self.tui.zoomed_pane)
        self.assertFalse(self.tui.running)
        self.assertFalse(self.tui.show_leader_menu)
        self.assertFalse(self.tui.show_help)

        # Check that instructions are parsed cleanly
        self.assertGreater(len(self.tui.instructions), 10)
        first_offset, first_op, first_args = self.tui.instructions[0]
        self.assertEqual(first_offset, 0)
        self.assertEqual(first_op, 'MOV')
        self.assertIn('AX', first_args)

    def test_02_student_explores_which_key_menu(self):
        """Student presses <Space> to discover all commands via the Which-Key menu."""
        # Press Space: leader menu opens
        self.tui._handle_key(None, ord(' '))
        self.assertTrue(self.tui.show_leader_menu)

        # Press Space again: leader menu closes
        self.tui._handle_key(None, ord(' '))
        self.assertFalse(self.tui.show_leader_menu)

        # Press Space, then press a hotkey (e.g. 'p'): menu closes and executes pause
        self.tui._handle_key(None, ord(' '))
        self.assertTrue(self.tui.show_leader_menu)
        self.tui._handle_key(None, ord('p'))
        self.assertFalse(self.tui.show_leader_menu)
        self.assertFalse(self.tui.running)

    def test_03_student_single_steps_and_verifies_registers(self):
        """Student steps through setup code and checks that modified registers are detected."""
        # Step 1: MOV AX, DATA (DATA = 0x2000)
        self.tui._handle_key(None, ord('s'))
        self.assertEqual(self.tui.EU.reg.get('AX'), 0x2000)

        # Step 2: MOV DS, AX
        self.tui._handle_key(None, ord('s'))
        self.assertEqual(self.tui.BIU.reg.get('DS'), 0x2000)

        # Step 3: MOV CX, COUNT (COUNT = 6)
        self.tui._handle_key(None, ord('s'))
        self.assertEqual(self.tui.EU.reg.get('CX'), 6)

        # Step 4: DEC CX -> CX becomes 5
        self.tui._handle_key(None, ord('s'))
        self.assertEqual(self.tui.EU.reg.get('CX'), 5)

        # Check that change snapshot detects the current register values
        regs = self.tui._snapshot_regs()
        self.assertEqual(regs['AX'], 0x2000)
        self.assertEqual(regs['CX'], 5)

    def test_04_student_navigates_windows(self):
        """Student jumps directly to windows using 1, 2, 3, 4 and cycles with w / Tab."""
        # Direct jumps
        self.tui._handle_key(None, ord('2'))
        self.assertEqual(self.tui.focused_pane, 'registers')

        self.tui._handle_key(None, ord('3'))
        self.assertEqual(self.tui.focused_pane, 'telemetry')

        self.tui._handle_key(None, ord('4'))
        self.assertEqual(self.tui.focused_pane, 'memory')

        self.tui._handle_key(None, ord('1'))
        self.assertEqual(self.tui.focused_pane, 'disasm')

        # Cycling with 'w'
        self.tui._handle_key(None, ord('w'))
        self.assertEqual(self.tui.focused_pane, 'registers')
        self.tui._handle_key(None, ord('w'))
        self.assertEqual(self.tui.focused_pane, 'telemetry')
        self.tui._handle_key(None, ord('w'))
        self.assertEqual(self.tui.focused_pane, 'memory')
        self.tui._handle_key(None, ord('w'))
        self.assertEqual(self.tui.focused_pane, 'disasm')

    def test_05_student_sets_breakpoint_and_runs(self):
        """Student sets a breakpoint on the inner loop comparison and runs continuously."""
        # Find offset of CMP AL, DL instruction in bubble_sort
        cmp_offset = None
        for offset, opcode, opds in self.tui.instructions:
            if opcode == 'CMP' and 'AL' in opds and 'DL' in opds:
                cmp_offset = offset
                break
        self.assertIsNotNone(cmp_offset, "CMP AL, DL instruction must exist in bubble_sort.asm")

        # Set breakpoint
        self.tui.breakpoints.add(cmp_offset)
        self.assertIn(cmp_offset, self.tui.breakpoints)

        # Run continuously
        self.tui.running = True
        max_cycles = 200
        cycles = 0
        while self.tui.running and cycles < max_cycles:
            if not self.tui.step():
                break
            cycles += 1

        # Execution must have halted at the breakpoint!
        self.assertFalse(self.tui.running)
        self.assertEqual(self.tui.BIU.reg.get('IP'), cmp_offset)
        self.assertIn("Breakpoint hit", self.tui.status_msg)

    def test_06_student_zooms_active_window(self):
        """Student zooms the active window with 'z' to see more content, then restores."""
        self.tui.focused_pane = 'disasm'
        self.assertIsNone(self.tui.zoomed_pane)

        # Zoom window
        self.tui._handle_key(None, ord('z'))
        self.assertEqual(self.tui.zoomed_pane, 'disasm')

        # Unzoom window
        self.tui._handle_key(None, ord('z'))
        self.assertIsNone(self.tui.zoomed_pane)

    def test_07_student_toggles_hardware_telemetry(self):
        """Student hides the Hardware Telemetry panel with 't' to expand the memory pane."""
        self.assertTrue(self.tui.show_telemetry)

        # Hide telemetry
        self.tui._handle_key(None, ord('t'))
        self.assertFalse(self.tui.show_telemetry)

        # Show telemetry again
        self.tui._handle_key(None, ord('t'))
        self.assertTrue(self.tui.show_telemetry)

    def test_08_student_inspects_memory_and_cycles_segments(self):
        """Student inspects memory hex dump and cycles through DS, CS, SS, ES, VIDEO."""
        self.assertEqual(self.tui.mem_segments[self.tui.mem_seg_idx], 'DS')

        # Cycle segments
        expected = ['CS', 'SS', 'ES', 'VIDEO', 'DS']
        for seg in expected:
            self.tui._handle_key(None, ord('m'))
            self.assertEqual(self.tui.mem_segments[self.tui.mem_seg_idx], seg)

        # Scroll memory offset with 'j' and 'k'
        self.tui.focused_pane = 'memory'
        initial_offset = self.tui.mem_offset
        self.tui._handle_key(None, ord('j'))
        self.assertEqual(self.tui.mem_offset, initial_offset + 16)
        self.tui._handle_key(None, ord('k'))
        self.assertEqual(self.tui.mem_offset, initial_offset)

    def test_09_student_inspects_stack_view(self):
        """Student toggles to the live SS:SP Stack View using 'v'."""
        self.assertEqual(self.tui.mem_view_mode, 'hex')

        # Switch to stack view
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'stack')

        # Switch to console view
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'console')

        # Switch back to hex dump
        self.tui._handle_key(None, ord('v'))
        self.assertEqual(self.tui.mem_view_mode, 'hex')

    def test_10_student_inspects_console_output_view(self):
        """Student presses 'o' to inspect Program Console Output."""
        self.assertEqual(self.tui.mem_view_mode, 'hex')
        self.tui._handle_key(None, ord('o'))
        self.assertEqual(self.tui.mem_view_mode, 'console')

        # Pressing 'o' again returns to hex view
        self.tui._handle_key(None, ord('o'))
        self.assertEqual(self.tui.mem_view_mode, 'hex')

    def test_11_student_uses_vim_motions(self):
        """Student navigates using Vim motions: 'g' (top) and 'G' (bottom)."""
        self.tui.focused_pane = 'disasm'

        # Jump to bottom
        self.tui._handle_key(None, ord('G'))
        self.assertEqual(self.tui.disasm_cursor_idx, len(self.tui.instructions) - 1)

        # Jump to top
        self.tui._handle_key(None, ord('g'))
        self.assertEqual(self.tui.disasm_cursor_idx, 0)

    def test_12_student_adjusts_execution_speed(self):
        """Student increases speed with '+' and decreases with '-'."""
        init_delay = self.tui.step_delay
        self.tui._handle_key(None, ord('+'))
        self.assertLess(self.tui.step_delay, init_delay)

        self.tui._handle_key(None, ord('-'))
        self.assertGreater(self.tui.step_delay, init_delay * 0.7)

    def test_13_student_opens_and_closes_help(self):
        """Student opens help tooltip with '?' and closes it with any key."""
        self.assertFalse(self.tui.show_help)
        self.tui._handle_key(None, ord('?'))
        self.assertTrue(self.tui.show_help)

        self.tui._handle_key(None, ord('q'))
        self.assertFalse(self.tui.show_help)

    def test_14_student_resets_cpu(self):
        """Student steps several times then resets the CPU to Cycle 0 with 'r'."""
        for _ in range(5):
            self.tui.step()
        self.assertGreater(self.tui.cpu.cycle_count, 0)
        self.assertNotEqual(self.tui.BIU.reg.get('IP'), 0)

        # Reset CPU
        self.tui._handle_key(None, ord('r'))
        self.assertEqual(self.tui.cpu.cycle_count, 0)
        self.assertEqual(self.tui.BIU.reg.get('IP'), 0)
        self.assertEqual(self.tui.EU.reg.get('AX'), 0)

    def test_15_student_runs_bubble_sort_to_completion_and_checks_data(self):
        """Student runs bubble_sort.asm to completion and checks memory for sorted array."""
        # Run until done
        max_cycles = 1000
        cycles = 0
        while not self.tui.cpu.check_done() and cycles < max_cycles:
            self.tui.step()
            cycles += 1

        self.assertTrue(self.tui.cpu.check_done())

        # Physical address for DATA segment (DS=0x2000 => 0x20000)
        # Original array: [0xFE, 0x27, 0x10, 0xA2, 0x6C, 0x06]
        # Expected sorted: [0x06, 0x10, 0x27, 0x6C, 0xA2, 0xFE]
        ds_phys = self.tui.BIU.reg.get('DS') << 4
        sorted_vals = []
        for i in range(6):
            raw = self.tui.memory.rb(ds_phys + i)
            val = to_decimal(raw[0]) if isinstance(raw, list) else to_decimal(raw)
            sorted_vals.append(val)

        expected_sorted = [0x06, 0x10, 0x27, 0x6C, 0xA2, 0xFE]
        self.assertEqual(sorted_vals, expected_sorted, "Bubble sort must correctly sort the numbers in memory!")

        # Verify that all 6 sorted numbers were output to Port 0 and captured in output buffer
        for expected_num in expected_sorted:
            self.assertIn(str(expected_num), self.tui.EU.output)

    def test_16_student_tests_traffic_lights_hardware_demo(self):
        """Student tests the Port 4 Traffic Lights hardware demo in the TUI."""
        tui_tl = EmulatorTUI(self.traffic_lights_path, enable_gui_windows=False)
        self.assertIsNotNone(tui_tl.cpu)

        # Run several instructions
        for _ in range(20):
            if tui_tl.cpu.check_done():
                break
            tui_tl.step()

        # Check that Traffic Lights device on Port 4 is active
        tl_dev = tui_tl.EU.peripherals.get_device(4)
        self.assertIsNotNone(tl_dev)
        # Port 4 state should be non-zero after phase 1 write
        self.assertGreater(tl_dev.state, 0)

    def test_17_student_tests_stepper_motor_hardware_demo(self):
        """Student tests the Port 7 Stepper Motor hardware demo in the TUI."""
        tui_sm = EmulatorTUI(self.stepper_motor_path, enable_gui_windows=False)
        self.assertIsNotNone(tui_sm.cpu)

        # Run demo
        for _ in range(50):
            if tui_sm.cpu.check_done():
                break
            tui_sm.step()

        # Check Stepper Motor on Port 7
        sm_dev = tui_sm.EU.peripherals.get_device(7)
        self.assertIsNotNone(sm_dev)
        # Motor should have rotated and registered steps
        self.assertGreater(sm_dev.step_count, 0)
        self.assertGreater(sm_dev.angle, 0.0)


if __name__ == "__main__":
    unittest.main()
