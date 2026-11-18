import unittest

from emulator.assembler import Assembler
from emulator.memory import MEMORY_SIZE, Memory
from emulator.pipeline_units.bus_interface_unit import bus_interface_unit


class TestPhysicalMemory(unittest.TestCase):
    def test_load_and_read_across_twenty_bit_address_limit(self):
        exe = Assembler(dict(CS=0x3000, DS=0xffff, ES=0, SS=0x5000)).compile("""
            DATA SEGMENT
                ORG 0fh
                DB 12h
                ORG 410h
                DB 34h
            DATA ENDS
        """)
        memory = Memory(MEMORY_SIZE, 0x10000)
        memory.load(exe)
        bus = bus_interface_unit(6, exe, memory)
        self.assertEqual(len(memory.space), 0x100000)
        self.assertEqual(memory.rb(0xfffff), ['0x12'])
        self.assertEqual(memory.rb(0x400), ['0x34'])
        bus.write_word(0xfffff, 0xabcd)
        self.assertEqual(memory.rb(0), ['0xab'])
        self.assertEqual(bus.read_word(0xfffff), ['0xab', '0xcd'])

    def test_instruction_prefetch_wraps_within_code_segment(self):
        exe = Assembler(dict(CS=0xffff, DS=0x2000, ES=0, SS=0x5000)).compile("""
            CODE SEGMENT
                ORG 0ffffh
                START: NOP
                ORG 0
                HLT
            CODE ENDS
            END START
        """)
        memory = Memory(MEMORY_SIZE, 0x10000)
        memory.load(exe)
        bus = bus_interface_unit(6, exe, memory)
        self.assertEqual(bus.cs_ip, 0xffef)
        bus.run()
        self.assertEqual(list(bus.instruction_queue.queue), [['NOP'], ['HLT']])
