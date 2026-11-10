"""
Unit tests for Expanded BIOS INT 10H & DOS INT 21H Services
and Video Memory Buffer @ 0xB8000
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from emulator.memory import Memory
from emulator.assembler import Assembler
from emulator.pipeline_units import bus_interface_unit, execution_unit
from emulator.peripherals.video_display import (
    VideoDisplayDevice, VIDEO_MEM_BASE, VIDEO_COLS, VIDEO_ROWS
)

SEG_INIT = {
    'DS': int('2000', 16),
    'CS': int('3000', 16),
    'SS': int('5000', 16),
    'ES': int('7000', 16)
}


class TestVideoDisplayAndInterrupts(unittest.TestCase):
    def setUp(self):
        self.memory = Memory(0xFFFFF, 0x10000)
        self.assembler = Assembler(SEG_INIT)
        # Dummy exe file representation
        self.exe = self.assembler.compile("assume cs:codesg\ncodesg segment\nstart: nop\ncodesg ends\nend start")
        self.biu = bus_interface_unit.bus_interface_unit(6, self.exe, self.memory)
        self.eu = execution_unit.execution_unit(self.biu, int_msg=False)
        # Headless video display
        self.eu.video_display = VideoDisplayDevice(memory=self.memory, enable_gui=False)

    def tearDown(self):
        if self.eu.video_display:
            self.eu.video_display.close()
        for f in list(self.eu.file_handles.values()):
            try:
                f.close()
            except Exception:
                pass
        self.eu.file_handles.clear()

    def test_video_memory_direct_write(self):
        # Directly write 'A' (0x41) with attribute 0x1F (White on Blue) at 0xB8000
        self.eu.video_display.write_char_at(0, 0, 0x41, 0x1F)
        ch, attr = self.eu.video_display.read_char_at(0, 0)
        self.assertEqual(ch, 0x41)
        self.assertEqual(attr, 0x1F)

        # Check raw memory bytes in Memory space
        loc = VIDEO_MEM_BASE
        raw_c = self.memory.rb(loc)
        raw_a = self.memory.rb(loc + 1)
        self.assertEqual(raw_c, ['0x41'])
        self.assertEqual(raw_a, ['0x1f'])

    def test_bios_int_10h_cursor_and_teletype(self):
        # Set cursor to row 5, col 10 (AH=02h)
        self.eu.write_reg('AH', 0x02)
        self.eu.write_reg('DH', 5)
        self.eu.write_reg('DL', 10)
        self.eu.bios_isr_10h()
        self.assertEqual(self.eu.video.get_cursor(), (5, 10))

        # Read cursor position back (AH=03h)
        self.eu.write_reg('AH', 0x03)
        self.eu.bios_isr_10h()
        self.assertEqual(self.eu.read_reg('DH'), 5)
        self.assertEqual(self.eu.read_reg('DL'), 10)

        # Teletype write 'H' (AH=0Eh)
        self.eu.write_reg('AH', 0x0E)
        self.eu.write_reg('AL', ord('H'))
        self.eu.write_reg('BL', 0x0A) # Light Green
        self.eu.bios_isr_10h()
        # Cursor should advance to col 11
        self.assertEqual(self.eu.video.get_cursor(), (5, 11))
        # Char at (5, 10) should be 'H'
        ch, attr = self.eu.video.read_char_at(5, 10)
        self.assertEqual(ch, ord('H'))
        self.assertEqual(attr, 0x0A)

    def test_dos_int_21h_version(self):
        # AH=30h: Get DOS Version
        self.eu.write_reg('AH', 0x30)
        self.eu.dos_isr_21h()
        self.assertEqual(self.eu.read_reg('AL'), 5) # DOS 5.0

    def test_dos_int_21h_file_crud(self):
        test_file = "test_int21_file.tmp"
        if os.path.exists(test_file):
            os.remove(test_file)

        # Store ASCIIZ filename in memory at DS:0x0100
        ds = self.eu.read_reg('DS')
        addr = (ds << 4) + 0x0100
        for i, ch in enumerate(test_file):
            self.memory.wb(addr + i, [hex(ord(ch))])
        self.memory.wb(addr + len(test_file), ['0x00'])

        # 1. AH=3Ch: Create File
        self.eu.write_reg('AH', 0x3C)
        self.eu.write_reg('DX', 0x0100)
        self.eu.write_reg('CX', 0)
        self.eu.dos_isr_21h()
        self.assertEqual(self.eu.FR.carry, 0)
        handle = self.eu.read_reg('AX')
        self.assertGreaterEqual(handle, 5)

        # 2. AH=40h: Write 5 bytes "HELLO"
        payload = "HELLO"
        buf_addr = (ds << 4) + 0x0200
        for i, ch in enumerate(payload):
            self.memory.wb(buf_addr + i, [hex(ord(ch))])
        self.eu.write_reg('AH', 0x40)
        self.eu.write_reg('BX', handle)
        self.eu.write_reg('CX', len(payload))
        self.eu.write_reg('DX', 0x0200)
        self.eu.dos_isr_21h()
        self.assertEqual(self.eu.FR.carry, 0)
        self.assertEqual(self.eu.read_reg('AX'), 5)

        # 3. AH=3Eh: Close File
        self.eu.write_reg('AH', 0x3E)
        self.eu.write_reg('BX', handle)
        self.eu.dos_isr_21h()
        self.assertEqual(self.eu.FR.carry, 0)

        # 4. AH=3Dh: Open File (Read mode AL=0)
        self.eu.write_reg('AH', 0x3D)
        self.eu.write_reg('AL', 0)
        self.eu.write_reg('DX', 0x0100)
        self.eu.dos_isr_21h()
        self.assertEqual(self.eu.FR.carry, 0)
        read_handle = self.eu.read_reg('AX')

        # 5. AH=3Fh: Read 5 bytes into DS:0x0300
        read_buf = (ds << 4) + 0x0300
        self.eu.write_reg('AH', 0x3F)
        self.eu.write_reg('BX', read_handle)
        self.eu.write_reg('CX', 5)
        self.eu.write_reg('DX', 0x0300)
        self.eu.dos_isr_21h()
        self.assertEqual(self.eu.FR.carry, 0)
        self.assertEqual(self.eu.read_reg('AX'), 5)

        # Verify read content
        read_chars = [chr(int(self.memory.rb(read_buf + i)[0], 16)) for i in range(5)]
        self.assertEqual("".join(read_chars), "HELLO")

        # 6. Close file
        self.eu.write_reg('AH', 0x3E)
        self.eu.write_reg('BX', read_handle)
        self.eu.dos_isr_21h()

        # 7. AH=41h: Delete file
        self.eu.write_reg('AH', 0x41)
        self.eu.write_reg('DX', 0x0100)
        self.eu.dos_isr_21h()
        self.assertEqual(self.eu.FR.carry, 0)
        self.assertFalse(os.path.exists(test_file))


if __name__ == '__main__':
    unittest.main()
