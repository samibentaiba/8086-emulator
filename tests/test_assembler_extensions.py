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

    def test_quoted_instruction_operands(self):
        code = """
        code segment
        start: mov\tdl,'a' ; the lowercase character
               mov dl,','
               mov dl,' '
               mov dl,";"
               mov dl,'?'
        code ends
        end start
        """
        exe = self.assembler.compile(code)
        operands = [instruction[2] for instruction in exe.space['CS'][:5]]
        self.assertEqual(operands, ["'a'", "','", "' '", '";"', "'?'"])

    def test_data_strings_and_dup_keep_literal_contents(self):
        code = """
        data segment
        msg db 'Ready?; 0Ah, it''s fine', 0Ah, ? ; this is a comment
        db 2 dup("a;B,", '?')
        data ends
        """
        exe = self.assembler.compile(code)
        stored = bytes(int(cell[0], 16) for cell in exe.space['DS'][:exe.seg_len['DS']])
        self.assertEqual(stored, b"Ready?; 0Ah, it's fine\n\0a;B,?a;B,?")

    def test_unterminated_literal_reports_original_line(self):
        code = "\n; comment\ndata segment\nmsg db 'oops; still open\ndata ends"
        with self.assertRaises(AssemblyError) as ctx:
            self.assembler.compile(code)
        self.assertEqual(ctx.exception.line, 4)
        self.assertEqual(ctx.exception.source, "msg db 'oops; still open")

    def test_source_mapping_uses_emitted_code_offsets(self):
        code = "\n".join([
            "; comment", "assume cs:text", "text segment", "org 100h",
            "entry:mov al, es:[di]", "even", "proc1 proc near", "  nop",
            "proc1 endp", "dup_label: db 2 dup(?)", "  hlt",
            "org 102h", "db 0", "text ends", "end entry"
        ])
        exe = self.assembler.compile(code)
        self.assertEqual(exe.ip_to_source_line, {0x100: 4, 0x105: 10})
        self.assertEqual(exe.seg_len['CS'], 0x106)

    def test_incomplete_segment_reports_assembly_error(self):
        for end in ('', 'end start', 'data segment'):
            with self.subTest(end=end), self.assertRaises(AssemblyError) as ctx:
                self.assembler.compile("\ncode segment\nstart: hlt\n" + end)
            self.assertIn('CODE ENDS', str(ctx.exception))
            self.assertEqual(ctx.exception.line, 4 if end else 2)

    def test_incomplete_offset_operand_reports_source_line(self):
        code = "\ncode segment\n; comment\nstart: mov bx, offset\ncode ends\nend start"
        with self.assertRaises(AssemblyError) as ctx:
            self.assembler.compile(code)
        self.assertEqual(ctx.exception.line, 4)
        self.assertEqual(ctx.exception.source, "start: mov bx, offset")

    def test_invalid_data_reports_original_declaration(self):
        code = "\n; comment\ndata segment\nvalue db bad\ndata ends"
        with self.assertRaises(AssemblyError) as ctx:
            self.assembler.compile(code)
        self.assertEqual(ctx.exception.line, 4)
        self.assertEqual(ctx.exception.source, "value db bad")

    def test_invalid_directives_and_opcodes_report_the_source_line(self):
        for instruction in ("ALIGN 0", "ALIGN 3", "ORG 10000h", "MOOV AX, 1"):
            with self.subTest(instruction=instruction), self.assertRaises(AssemblyError) as ctx:
                self.assembler.compile(f"; example\nCODE SEGMENT\n{instruction}\nCODE ENDS")
            self.assertEqual(ctx.exception.line, 3)
            self.assertEqual(ctx.exception.source, instruction)

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
