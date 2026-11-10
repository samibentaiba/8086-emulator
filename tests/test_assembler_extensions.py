import unittest
from emulator.assembler import Assembler, AssemblyError

SEG_INIT = {
    'DS': int('2000', 16),
    'CS': int('3000', 16),
    'SS': int('5000', 16),
    'ES': int('7000', 16)
}

class TestAssemblerExtensions(unittest.TestCase):
    def setUp(self):
        self.assembler = Assembler(SEG_INIT)

    def test_assembly_error_on_mismatched_ends(self):
        code = """
        CODE SEGMENT
            MOV AX, 1
        CODE WRONG_ENDS
        END
        """
        with self.assertRaises(AssemblyError) as ctx:
            self.assembler.compile(code)
        self.assertIn("Expected 'ENDS'", str(ctx.exception))

    def test_equ_directive_resolution(self):
        code = """
        CODE SEGMENT
        ASSUME CS:CODE
        BUFFER_SIZE EQU 1024
        START:
            MOV CX, BUFFER_SIZE
            MOV AH, 4CH
            INT 21H
        CODE ENDS
        END START
        """
        exe = self.assembler.compile(code)
        cs_instructions = exe.space['CS']
        # Check that BUFFER_SIZE was replaced with '1024'
        first_ins = cs_instructions[0]
        self.assertEqual(first_ins, ['MOV', 'CX', '1024'])

    def test_proc_endp_directive(self):
        code = """
        CODE SEGMENT
        ASSUME CS:CODE
        MY_PROC PROC
            MOV AX, 42
            RET
        MY_PROC ENDP

        START:
            CALL MY_PROC
            MOV AH, 4CH
            INT 21H
        CODE ENDS
        END START
        """
        exe = self.assembler.compile(code)
        self.assertIn('MY_PROC', exe.tags)
        # Entry point for MY_PROC is at offset 0
        self.assertEqual(exe.tags['MY_PROC']['offset'], '0x0')

    def test_hardware_demos_compile(self):
        import os
        demos = [
            "tests/Hardware/traffic_lights_demo.asm",
            "tests/Hardware/stepper_motor_demo.asm",
            "tests/Hardware/hello_video_demo.asm"
        ]
        for path in demos:
            self.assertTrue(os.path.exists(path), f"File {path} must exist")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            asm = Assembler(SEG_INIT)
            exe = asm.compile(content)
            self.assertIn('CS', exe.space)


if __name__ == '__main__':
    unittest.main()
