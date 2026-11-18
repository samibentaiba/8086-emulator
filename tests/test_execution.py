import unittest

from emulator.assembler import Assembler
from emulator.cpu import CPU
from emulator.memory import Memory
from emulator.peripherals import PeripheralManager
from emulator.pipeline_units.bus_interface_unit import bus_interface_unit
from emulator.pipeline_units.execution_unit import execution_unit


class TestInstructionExecution(unittest.TestCase):
    def run_program(self, instructions, steps=None):
        source = f"CODE SEGMENT\nSTART:\n{instructions}\nHLT\nCODE ENDS\nEND START"
        exe = Assembler(dict(CS=0x3000, DS=0x2000, SS=0x5000, ES=0x7000)).compile(source)
        memory = Memory(1 << 20, 1 << 16)
        memory.load(exe)
        PeripheralManager.get_instance(enable_gui=False)
        self.addCleanup(PeripheralManager.reset_instance)
        bus = bus_interface_unit(6, exe, memory)
        eu = execution_unit(bus, int_msg=False)
        eu.mute_stdout = True
        cpu = CPU(bus, eu, gui_mode=False)
        for _ in range(steps or 64):
            if cpu.check_done():
                break
            cpu.iterate()
        if steps is None:
            self.assertTrue(eu.shutdown)
        return eu

    def test_unsigned_multiply_and_divide_widths(self):
        eu = self.run_program("""
            MOV AL, 10h
            MOV BL, 10h
            MUL BL
            MOV SI, AX
            MOV AX, 8100h
            MOV BX, 2
            MUL BX
            MOV DI, DX
            MOV CX, AX
            PUSHF
            POP BP
            DIV BX
        """)
        self.assertEqual(eu.reg['SI'], 0x100)
        self.assertEqual((eu.reg['DI'], eu.reg['CX']), (1, 0x200))
        self.assertEqual((eu.reg['AX'], eu.reg['DX']), (0x8100, 0))
        self.assertEqual(eu.reg['BP'] & 0x801, 0x801)

    def test_signed_multiply_and_divide(self):
        eu = self.run_program("""
            MOV AX, -7
            MOV BX, 3
            IMUL BX
            MOV SI, DX
            MOV DI, AX
            MOV AX, -7
            CWD
            IDIV BX
            MOV CX, AX
            MOV BX, DX
            MOV AX, -7
            MOV DL, -3
            IDIV DL
        """)
        self.assertEqual((eu.reg['SI'], eu.reg['DI']), (0xffff, 0xffeb))
        self.assertEqual((eu.reg['CX'], eu.reg['BX']), (0xfffe, 0xffff))
        self.assertEqual(eu.reg['AX'], 0xff02)

    def test_divide_overflow_saves_word_context_and_leaves_dividend(self):
        eu = self.run_program("""
            MOV SP, 1234h
            MOV AX, 100h
            MOV BL, 1
            DIV BL
        """, steps=4)
        self.assertEqual(eu.reg['AX'], 0x100)
        self.assertEqual(eu.reg['SP'], 0x122e)
        self.assertEqual(eu.get_int_from_adr(eu.ss_sp), 4)
        self.assertEqual(eu.get_int_from_adr(eu.ss_sp + 2), 0x3000)
        self.assertEqual((eu.read_reg('CS'), eu.read_reg('IP')), (0x1000, 0))

    def test_carry_overflow_parity_and_signed_branch_aliases(self):
        eu = self.run_program("""
            MOV AX, 0ffffh
            ADD AX, 1
            PUSHF
            POP DX
            MOV AX, 7fffh
            ADC AX, 0
            PUSHF
            POP SI
            MOV AL, 1
            CMP AL, 2
            JBE below
            INC BX
        below: CMP AL, 1
            JNG equal
            INC BX
        equal: MOV AX, 100h
            TEST AX, AX
        """)
        self.assertEqual(eu.reg['DX'] & 0x8d5, 0x55)   # CF, AF, ZF, PF
        self.assertEqual(eu.reg['SI'] & 0x8d5, 0x894)  # OF, SF, AF, PF
        self.assertEqual(eu.reg['BX'], 0)
        self.assertEqual(eu.FR.parity, 1)

    def test_byte_string_indices_and_count_remain_16_bit(self):
        eu = self.run_program("""
            MOV AL, 5ah
            MOV DI, 1200h
            MOV CX, 101h
            REP STOSB
            MOV SI, 2300h
            STD
            MOVSB
        """)
        self.assertEqual((eu.reg['SI'], eu.reg['DI'], eu.reg['CX']), (0x22ff, 0x1300, 0))
        for offset in (0x1200, 0x1300):
            self.assertEqual(eu.bus.read_byte((eu.read_reg('ES') << 4) + offset), ['0x5a'])

    def test_word_copy_addresses_and_negative_displacements(self):
        eu = self.run_program("""
            MOV AX, 1234h
            MOV [0], AX
            MOVSW
            MOV DX, ES:[0]
            MOV BP, 2
            MOV [BP-4], AX
            MOV CX, SS:[0fffeh]
            MOV BX, [BP+4]
            LEA SI, [BP-4]
            MOV DI, 0ffffh
            MOV AL, [DI+1]
        """)
        self.assertEqual((eu.reg['DX'], eu.reg['CX']), (0x1234, 0x1234))
        self.assertEqual((eu.reg['BX'], eu.reg['SI'], eu.read_reg('AL')), (0, 0xfffe, 0x34))

    def test_shift_with_cl_uses_destination_width_and_sets_flags(self):
        eu = self.run_program("""
            MOV AX, 100h
            MOV CL, 1
            SHL AX, CL
            MOV BX, AX
            MOV AX, 1
            SHR AX, CL
            MOV CL, 0
            SHL BX, CL
        """)
        self.assertEqual((eu.reg['AX'], eu.reg['BX']), (0, 0x200))
        self.assertEqual((eu.FR.carry, eu.FR.zero, eu.FR.parity), (1, 1, 1))

    def test_bracket_character_immediate(self):
        eu = self.run_program("MOV AL, '['")
        self.assertEqual(eu.read_reg('AL'), ord('['))

    def test_aam_splits_decimal_digits_and_sets_flags_from_al(self):
        eu = self.run_program("MOV AL, 99\nAAM\nMOV BX, AX\nMOV AL, 10\nAAM")
        self.assertEqual((eu.reg['BX'], eu.reg['AX']), (0x0909, 0x0100))
        self.assertEqual((eu.FR.sign, eu.FR.zero, eu.FR.parity), (0, 1, 1))

    def test_near_and_far_return_with_stack_arguments(self):
        eu = self.run_program("""
            MOV SP, 1000h
            PUSH AX
            CALL inner
            MOV SI, SP
            PUSH BX
            CALL FAR PTR outer
            HLT
        inner: INC AX
            RET 2
        outer: INC AX
            RETF 2
        """)
        self.assertEqual(eu.reg['AX'], 2)
        self.assertEqual((eu.reg['SI'], eu.reg['SP']), (0x1000, 0x1000))
        self.assertEqual(eu.read_reg('CS'), 0x3000)

    def test_segment_loads_and_indirect_far_call(self):
        eu = self.run_program("""
            MOV AX, OFFSET callee
            MOV DS:[10h], AX
            MOV DS:[12h], CS
            MOV SP, 2000h
            CALL DWORD PTR DS:[10h]
            MOV SI, SP
            MOV AX, 1234h
            MOV DS:[10h], AX
            MOV AX, 5678h
            MOV DS:[12h], AX
            LES BX, DWORD PTR [10h]
            LDS DX, [10h]
            HLT
        callee: INC DI
            RETF
        """)
        self.assertEqual((eu.reg['SI'], eu.reg['DI']), (0x2000, 1))
        self.assertEqual((eu.reg['BX'], eu.reg['DX']), (0x1234, 0x1234))
        self.assertEqual((eu.read_reg('ES'), eu.read_reg('DS')), (0x5678, 0x5678))
