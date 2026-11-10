"""
Unit Tests for 8086 Time-Travel Debugging & Reverse Execution
Verifies single-step rewind (reverse-step) and continuous run backward (reverse-continue).
"""

import os
import unittest
import tempfile
from emulator.assembler import Assembler
from emulator.memory import Memory
from emulator.pipeline_units import bus_interface_unit, execution_unit
from emulator.cpu import CPU
from emulator.peripherals import PeripheralManager
from ui.tui import EmulatorTUI

MEMORY_SIZE = int('FFFFF', 16)
SEGMENT_SIZE = int('10000', 16)
SEG_INIT = {
    'DS': 0x2000,
    'CS': 0x3000,
    'SS': 0x5000,
    'ES': 0x7000
}


class TestReverseExecution(unittest.TestCase):

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

    def _create_cpu(self, asm_code):
        asm = Assembler(SEG_INIT)
        exe = asm.compile(asm_code)
        mem = Memory(MEMORY_SIZE, SEGMENT_SIZE)
        mem.load(exe, verbose=False)
        biu = bus_interface_unit.bus_interface_unit(6, exe, mem)
        eu = execution_unit.execution_unit(biu, int_msg=False)
        eu.mute_stdout = True
        cpu = CPU(biu, eu, gui_mode=False)
        cpu.tui_mode = True
        return cpu, mem, biu, eu

    def test_01_single_step_reverse_registers_and_cycle(self):
        """Verify registers and cycle counts rewind accurately across multiple instructions."""
        code = """
        CODE SEGMENT
        START:
            MOV AX, 01234H
            MOV BX, 05678H
            ADD AX, BX
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)

        # Initially at Cycle 0
        self.assertEqual(cpu.cycle_count, 0)
        self.assertEqual(eu.reg['AX'], 0)
        self.assertEqual(eu.reg['BX'], 0)
        self.assertFalse(cpu.can_step_back())
        self.assertFalse(cpu.step_back())

        # Step 1: MOV AX, 1234H
        cpu.iterate()
        self.assertEqual(eu.reg['AX'], 0x1234)
        self.assertEqual(eu.reg['BX'], 0)
        self.assertEqual(len(cpu.history), 1)

        # Step 2: MOV BX, 5678H
        cpu.iterate()
        self.assertEqual(eu.reg['AX'], 0x1234)
        self.assertEqual(eu.reg['BX'], 0x5678)
        self.assertEqual(len(cpu.history), 2)

        # Step 3: ADD AX, BX
        cpu.iterate()
        self.assertEqual(eu.reg['AX'], 0x1234 + 0x5678)
        self.assertEqual(eu.reg['BX'], 0x5678)
        self.assertEqual(len(cpu.history), 3)

        # REWIND Step 3 -> returns AX to 0x1234
        success = cpu.step_back()
        self.assertTrue(success)
        self.assertEqual(eu.reg['AX'], 0x1234)
        self.assertEqual(eu.reg['BX'], 0x5678)
        self.assertEqual(len(cpu.history), 2)

        # REWIND Step 2 -> returns BX to 0
        success = cpu.step_back()
        self.assertTrue(success)
        self.assertEqual(eu.reg['AX'], 0x1234)
        self.assertEqual(eu.reg['BX'], 0)
        self.assertEqual(len(cpu.history), 1)

        # REWIND Step 1 -> returns AX to 0, cycle to 0
        success = cpu.step_back()
        self.assertTrue(success)
        self.assertEqual(eu.reg['AX'], 0)
        self.assertEqual(eu.reg['BX'], 0)
        self.assertEqual(cpu.cycle_count, 0)
        self.assertEqual(len(cpu.history), 0)

        # Trying to rewind past beginning returns False cleanly
        self.assertFalse(cpu.step_back())

    def test_02_memory_write_rollback(self):
        """Verify memory writes via [address] are tracked and rolled back on step_back."""
        code = """
        DATA SEGMENT
            NUM DW 01111H
        DATA ENDS
        CODE SEGMENT
        ASSUME CS:CODE, DS:DATA
        START:
            MOV AX, DATA
            MOV DS, AX
            MOV AX, 09999H
            MOV [0], AX
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)

        # Physical address for DATA segment: 0x20000
        data_addr = 0x20000
        # Initially NUM is 0x1111 (little endian: 0x11, 0x11)
        self.assertEqual(mem.rb(data_addr), ['0x11'])
        self.assertEqual(mem.rb(data_addr + 1), ['0x11'])

        # Step until after MOV [0], AX
        cpu.iterate() # MOV AX, DATA
        cpu.iterate() # MOV DS, AX
        cpu.iterate() # MOV AX, 09999H
        cpu.iterate() # MOV [0], AX

        # Verify memory changed to 0x9999 (0x99, 0x99)
        self.assertEqual(mem.rb(data_addr), ['0x99'])
        self.assertEqual(mem.rb(data_addr + 1), ['0x99'])

        # Step back: MOV [0], AX is undone!
        cpu.step_back()
        self.assertEqual(mem.rb(data_addr), ['0x11'])
        self.assertEqual(mem.rb(data_addr + 1), ['0x11'])

    def test_03_flags_rollback(self):
        """Verify flag registers (ZF, CF, SF, OF) roll back to previous values."""
        code = """
        CODE SEGMENT
        START:
            MOV AX, 05H
            CMP AX, 05H
            CMP AX, 010H
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)

        cpu.iterate() # MOV AX, 5
        self.assertEqual(eu.FR.zero, 0)

        cpu.iterate() # CMP AX, 5 -> equal, ZF=1, CF=0
        self.assertEqual(eu.FR.zero, 1)
        self.assertEqual(eu.FR.carry, 0)

        cpu.iterate() # CMP AX, 10 -> less, ZF=0, CF=1
        self.assertEqual(eu.FR.zero, 0)
        self.assertEqual(eu.FR.carry, 1)

        # Rewind CMP AX, 10 -> ZF should be 1 again, CF should be 0
        cpu.step_back()
        self.assertEqual(eu.FR.zero, 1)
        self.assertEqual(eu.FR.carry, 0)

        # Rewind CMP AX, 5 -> ZF should be 0
        cpu.step_back()
        self.assertEqual(eu.FR.zero, 0)

    def test_04_stack_push_pop_rollback(self):
        """Verify SP and stack memory locations revert correctly on rewind."""
        code = """
        CODE SEGMENT
        START:
            MOV AX, 0ABCDH
            PUSH AX
            POP BX
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)
        init_sp = eu.reg['SP']

        cpu.iterate() # MOV AX, 0ABCDH
        cpu.iterate() # PUSH AX (SP decreases by 2)
        self.assertEqual(eu.reg['SP'], (init_sp - 2) & 0xFFFF)

        # Rewind PUSH AX
        cpu.step_back()
        self.assertEqual(eu.reg['SP'], init_sp)

    def test_05_loop_instruction_rewind(self):
        """Verify execution pointer and loop counter restore cleanly across loop cycles."""
        code = """
        CODE SEGMENT
        START:
            MOV CX, 03H
        AGAIN:
            DEC CX
            JNZ AGAIN
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)

        cpu.iterate() # MOV CX, 3
        self.assertEqual(eu.reg['CX'], 3)

        cpu.iterate() # DEC CX -> 2
        self.assertEqual(eu.reg['CX'], 2)

        cpu.iterate() # JNZ AGAIN (loops)
        cpu.iterate() # DEC CX -> 1
        self.assertEqual(eu.reg['CX'], 1)

        # Rewind back across loop
        cpu.step_back()
        self.assertEqual(eu.reg['CX'], 2)

    def test_06_tui_step_back_and_run_backward(self):
        """Verify TUI integration with 'u' (step back) and 'C' (run backward)."""
        code = """
        CODE SEGMENT
        START:
            MOV AX, 1
            MOV BX, 2
            MOV CX, 3
            MOV DX, 4
            HLT
        CODE ENDS
        END START
        """
        with tempfile.NamedTemporaryFile('w', suffix='.asm', delete=False) as tf:
            tf.write(code)
            temp_path = tf.name
        self.temp_files.append(temp_path)

        tui = EmulatorTUI(temp_path, enable_gui_windows=False)
        self.assertEqual(tui.cpu.cycle_count, 0)
        self.assertEqual(len(tui.cpu.history), 0)

        # Step forward 3 times
        tui.step()
        tui.step()
        tui.step()
        self.assertEqual(len(tui.cpu.history), 3)
        self.assertEqual(tui.EU.reg['AX'], 1)
        self.assertEqual(tui.EU.reg['BX'], 2)
        self.assertEqual(tui.EU.reg['CX'], 3)

        # Step backward via TUI
        tui.step_back()
        self.assertEqual(len(tui.cpu.history), 2)
        self.assertEqual(tui.EU.reg['CX'], 0) # CX was reverted
        self.assertEqual(tui.EU.reg['BX'], 2)

        # Test 'u' key handler
        tui._handle_key(None, ord('u'))
        self.assertEqual(len(tui.cpu.history), 1)
        self.assertEqual(tui.EU.reg['BX'], 0) # BX was reverted

        # Test 'C' key handler (Run backward / rewind)
        tui._handle_key(None, ord('C'))
        self.assertTrue(tui.running)
        self.assertEqual(tui.running_direction, -1)
        self.assertIn("Rewinding", tui.status_msg)

        # Step backward to 0
        tui.step_back()
        self.assertEqual(len(tui.cpu.history), 0)
        self.assertFalse(tui.step_back())
        self.assertIn("Already at start", tui.status_msg)

    def test_07_peripheral_state_rollback(self):
        """Verify I/O port writes to Traffic Lights and Stepper Motor rollback state."""
        code = """
        CODE SEGMENT
        START:
            MOV AX, 00249H
            OUT 4, AX
            MOV AL, 006H
            OUT 7, AL
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)
        pm = PeripheralManager.get_instance()
        traffic = pm.get_device(4)
        stepper = pm.get_device(7)

        init_traffic_state = traffic.state
        init_stepper_state = stepper.state

        cpu.iterate() # MOV AX, 0249H
        cpu.iterate() # OUT 4, AX
        self.assertEqual(traffic.state, 0x0249)

        cpu.iterate() # MOV AL, 06H
        cpu.iterate() # OUT 7, AL
        self.assertEqual(stepper.state, 0x06)

        # Rewind OUT 7, AL
        cpu.step_back()
        self.assertEqual(stepper.state, init_stepper_state)

        # Rewind OUT 4, AX
        cpu.step_back() # rewind MOV AL, 6
        cpu.step_back() # rewind OUT 4, AX
        self.assertEqual(traffic.state, init_traffic_state)

    def test_08_reverse_breakpoint(self):
        """Verify that reverse execution halts when hitting a breakpoint while rewinding."""
        code = """
        CODE SEGMENT
        START:
            MOV AX, 1
            MOV BX, 2
            MOV CX, 3
            MOV DX, 4
            HLT
        CODE ENDS
        END START
        """
        with tempfile.NamedTemporaryFile('w', suffix='.asm', delete=False) as tf:
            tf.write(code)
            temp_path = tf.name
        self.temp_files.append(temp_path)

        tui = EmulatorTUI(temp_path, enable_gui_windows=False)
        # Advance 4 steps
        for _ in range(4):
            tui.step()
        self.assertEqual(len(tui.cpu.history), 4)

        # Set breakpoint at IP=1 (which corresponds to MOV BX, 2)
        tui.breakpoints.add(1)
        tui.running = True
        tui.running_direction = -1

        # Simulate running backward
        while tui.running:
            tui.step_back()

        # Should have stopped at breakpoint IP=1
        self.assertFalse(tui.running)
        self.assertEqual(tui.BIU.reg['IP'], 1)
        self.assertIn("Reverse breakpoint hit", tui.status_msg)

    def test_09_console_output_rollback(self):
        """Verify that character console output via INT 21H AH=02H is restored on rewind."""
        code = """
        CODE SEGMENT
        START:
            MOV AH, 02H
            MOV DL, 'A'
            INT 21H
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)

        cpu.iterate() # MOV AH, 02H
        cpu.iterate() # MOV DL, 'A'
        cpu.iterate() # INT 21H (outputs 'A')
        self.assertIn("A", eu.output)

        # Rewind INT 21H
        cpu.step_back()
        self.assertNotIn("A", eu.output)

    def test_10_reverse_execution_on_terminated_cpu(self):
        """Verify that a terminated/halted CPU can step back and resume execution."""
        code = """
        CODE SEGMENT
        START:
            MOV AX, 042H
            HLT
        CODE ENDS
        END START
        """
        cpu, mem, biu, eu = self._create_cpu(code)

        cpu.iterate() # MOV AX, 42H
        cpu.iterate() # HLT
        self.assertTrue(cpu.check_done())

        # Step back before HLT
        success = cpu.step_back()
        self.assertTrue(success)
        self.assertFalse(cpu.check_done())
        self.assertEqual(eu.reg['AX'], 0x42)


if __name__ == '__main__':
    unittest.main()
