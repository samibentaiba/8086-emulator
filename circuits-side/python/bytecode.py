"""Encode the supported original-8086 forms produced by the repository assembler.

Lengths and relative branches use byte addresses. The original interpreter's
one-cell instruction storage is translated here without changing its interfaces.
"""
import re
from dataclasses import dataclass
from emulator.assembler import Assembler, AssemblyError, to_decimal

WORD_REGS = "AX CX DX BX SP BP SI DI".split()
BYTE_REGS = "AL CL DL BL AH CH DH BH".split()
SEG_REGS = "ES CS SS DS".split()
SEG_PREFIX = dict(ES=0x26, CS=0x2E, SS=0x36, DS=0x3E)
ALU = dict(ADD=0, OR=1, ADC=2, SBB=3, AND=4, SUB=5, XOR=6, CMP=7)
CONDITION_GROUPS = [
    "JO", "JNO", "JB JC JNAE", "JAE JNB JNC", "JE JZ", "JNE JNZ",
    "JBE JNA", "JA JNBE", "JS", "JNS", "JP JPE", "JNP JPO",
    "JL JNGE", "JGE JNL", "JLE JNG", "JG JNLE",
]
JCC = {name: 0x70 + n for n, aliases in enumerate(CONDITION_GROUPS)
       for name in aliases.split()}
LOOPS = dict(LOOPNE=0xE0, LOOPNZ=0xE0, LOOPE=0xE1, LOOPZ=0xE1, LOOP=0xE2, JCXZ=0xE3)
SINGLE = dict(NOP=0x90, HLT=0xF4, CBW=0x98, CWD=0x99,
              PUSHF=0x9C, POPF=0x9D, LAHF=0x9F, SAHF=0x9E,
              LANF=0x9F, SANF=0x9E, CLC=0xF8, STC=0xF9,
              CMC=0xF5, CLD=0xFC, STD=0xFD, CLI=0xFA, STI=0xFB,
              XLAT=0xD7, WAIT=0x9B)
STRINGS = dict(MOVSB=0xA4, MOVSW=0xA5, CMPSB=0xA6, CMPSW=0xA7,
               STOSB=0xAA, STOSW=0xAB, LODSB=0xAC, LODSW=0xAD,
               SCASB=0xAE, SCASW=0xAF)
SHIFTS = dict(ROL=0, ROR=1, RCL=2, RCR=3, SHL=4, SAL=4, SHR=5, SAR=7)
UNARY = dict(NOT=2, NEG=3, MUL=4, IMUL=5, DIV=6, IDIV=7)
SUPPORTED = sorted(set(SINGLE) | set(STRINGS) | set(ALU) | set(JCC) |
                   set(LOOPS) | set(SHIFTS) | set(UNARY) |
                   {"MOV", "XCHG", "LEA", "LDS", "LES", "TEST", "INC", "DEC",
                    "PUSH", "POP", "CALL", "JMP", "RET", "RETF", "AAM", "INT",
                    "IN", "OUT", "REP", "REPE", "REPZ", "REPNE", "REPNZ"})


def number(value):
    try:
        return to_decimal(value)
    except (ValueError, IndexError, TypeError):
        raise ValueError(f"Expected an integer, got {value!r}") from None


def immediate(value, width):
    value = number(value) if isinstance(value, str) else value
    if not -(1 << (width - 1)) <= value < (1 << width):
        raise ValueError(f"Immediate {value} does not fit {width} bits")
    return [(value >> shift) & 255 for shift in range(0, width, 8)]


def register_code(operand, width):
    registers = WORD_REGS if width == 16 else BYTE_REGS
    if operand not in registers:
        raise ValueError(f"Expected a {width}-bit register, got {operand}")
    return registers.index(operand)


def is_memory(operand):
    return "[" in operand


def is_register(operand):
    return operand in WORD_REGS or operand in BYTE_REGS or operand in SEG_REGS


def addressing(operand, field, width):
    """Return segment prefix and ModR/M + displacement bytes."""
    if is_register(operand):
        return [], [0xC0 | (field << 3) | register_code(operand, width)]
    if not is_memory(operand):
        raise ValueError(f"Expected a register or memory operand, got {operand}")
    prefix = []
    address = operand
    if ":" in address:
        segment, address = address.split(":", 1)
        if segment not in SEG_PREFIX:
            raise ValueError("Memory segment override must name CS, DS, SS or ES")
        prefix = [SEG_PREFIX[segment]]
    compact = address.replace("[", "+").replace("]", "").replace(" ", "")
    registers = []
    displacement = 0
    for sign, item in re.findall(r"([+-]?)([A-Z0-9_]+)", compact.upper()):
        if item in ("BX", "BP", "SI", "DI"):
            if sign == "-" or item in registers:
                raise ValueError("Invalid 8086 effective-address register expression")
            registers.append(item)
        else:
            displacement += (-1 if sign == "-" else 1) * number(item)
    if not registers:
        return prefix, [(field << 3) | 6] + immediate(displacement, 16)
    pairs = {frozenset(v.split()): i for i, v in enumerate(
        ["BX SI", "BX DI", "BP SI", "BP DI", "SI", "DI", "BP", "BX"])}
    key = frozenset(registers)
    if key not in pairs:
        raise ValueError("8086 addressing permits BX/BP with SI/DI, or a single BX/BP/SI/DI")
    rm = pairs[key]
    if displacement == 0 and rm != 6:
        return prefix, [(field << 3) | rm]
    if -128 <= displacement <= 127:
        return prefix, [0x40 | (field << 3) | rm, displacement & 255]
    return prefix, [0x80 | (field << 3) | rm] + immediate(displacement, 16)


def operands(tokens):
    """Keep operand width explicit when memory has no register partner."""
    requested = 8 if "BYTE" in tokens else 16 if "WORD" in tokens else 32 if "DWORD" in tokens else None
    clean = [v for v in tokens if v not in ("BYTE", "WORD", "DWORD", "PTR", "SHORT", "NEAR")]
    registers = [v for v in clean if v in WORD_REGS + BYTE_REGS]
    width = requested or (8 if any(v in BYTE_REGS for v in registers) else 16)
    if any(v in WORD_REGS for v in registers) and width == 8:
        raise ValueError("Byte memory operand cannot be paired with a word register")
    if any(v in BYTE_REGS for v in registers) and width != 8:
        raise ValueError("Word memory operand cannot be paired with a byte register")
    return clean, width


def encode(tokens, address=0, validate_branch=True):
    opcode = tokens[0]
    args, width = operands(tokens[1:-1] if opcode in SHIFTS else tokens[1:])
    if opcode in SHIFTS:
        args.append(tokens[-1])
    w = int(width == 16)

    def rmop(byte, operand, field, tail=(), use_width=None):
        prefix, encoded = addressing(operand, field, use_width or width)
        return prefix + [byte] + encoded + list(tail)

    def require_count(count):
        if len(args) != count:
            raise ValueError(f"{opcode} expects {count} operand(s)")

    if opcode in SINGLE or opcode in STRINGS:
        require_count(0)
        return [SINGLE.get(opcode, STRINGS.get(opcode))]
    if opcode in ("REP", "REPE", "REPZ", "REPNE", "REPNZ"):
        require_count(1)
        if args[0] not in STRINGS:
            raise ValueError("REP prefixes require a string instruction")
        return [0xF2 if opcode in ("REPNE", "REPNZ") else 0xF3, STRINGS[args[0]]]
    if opcode in JCC or opcode in LOOPS:
        require_count(1)
        delta = (number(args[0]) - (address + 2)) & 65535
        signed = delta - 65536 if delta & 0x8000 else delta
        if validate_branch and not -128 <= signed <= 127:
            raise ValueError(f"{opcode} target is outside the signed 8-bit branch range")
        return [JCC.get(opcode, LOOPS.get(opcode)), delta & 255]
    if opcode in ("CALL", "JMP"):
        require_count(1)
        target = args[0]
        if is_register(target) or is_memory(target):
            far = width == 32
            return rmop(0xFF, target, (3 if far else 2) + (2 if opcode == "JMP" else 0), use_width=16)
        if ":" in target:
            segment, offset = target.split(":")
            return [0x9A if opcode == "CALL" else 0xEA] + immediate(offset, 16) + immediate(segment, 16)
        delta = (number(target) - (address + 3)) & 65535
        return [0xE8 if opcode == "CALL" else 0xE9] + immediate(delta, 16)
    if opcode in ("RET", "RETF"):
        if len(args) > 1:
            raise ValueError("RET accepts at most one stack adjustment")
        return ([0xC2 if opcode == "RET" else 0xCA] + immediate(args[0], 16)
                if args else [0xC3 if opcode == "RET" else 0xCB])
    if opcode in ("PUSH", "POP"):
        require_count(1)
        operand = args[0]
        if operand in SEG_REGS:
            if opcode == "POP" and operand == "CS":
                raise ValueError("POP CS is outside the documented instruction set")
            return [6 + 8 * SEG_REGS.index(operand) + int(opcode == "POP")]
        if operand in WORD_REGS:
            return [(0x50 if opcode == "PUSH" else 0x58) + WORD_REGS.index(operand)]
        if not is_memory(operand) or width != 16:
            raise ValueError("8086 PUSH/POP requires a word register, segment or word memory operand")
        return rmop(0xFF if opcode == "PUSH" else 0x8F, operand, 6 if opcode == "PUSH" else 0)
    if opcode == "INT":
        require_count(1)
        return [0xCD] + immediate(args[0], 8)
    if opcode == "AAM":
        require_count(0)
        return [0xD4, 10]
    if opcode in ("IN", "OUT"):
        require_count(2)
        accumulator, port = args if opcode == "IN" else args[::-1]
        if accumulator not in ("AL", "AX"):
            raise ValueError("8086 IN/OUT uses AL or AX")
        base = 0xE4 if opcode == "IN" else 0xE6
        return [base + int(accumulator == "AX") + (8 if port == "DX" else 0)] + (
            [] if port == "DX" else immediate(port, 8))
    if opcode in SHIFTS:
        require_count(2)
        if args[1] not in ("1", "CL"):
            raise ValueError("8086 shift counts are 1 or CL")
        # CL controls the count, not the width of a word destination.
        width = 8 if args[0] in BYTE_REGS or "BYTE" in tokens else 16
        w = int(width == 16)
        return rmop(0xD0 + w + (2 if args[1] == "CL" else 0), args[0], SHIFTS[opcode])
    if opcode in UNARY or opcode in ("INC", "DEC"):
        require_count(1)
        if opcode in ("INC", "DEC"):
            if args[0] in WORD_REGS:
                return [0x40 + (8 if opcode == "DEC" else 0) + WORD_REGS.index(args[0])]
            return rmop(0xFE + w, args[0], int(opcode == "DEC"))
        return rmop(0xF6 + w, args[0], UNARY[opcode])

    require_count(2)
    destination, source = args
    if is_memory(destination) and is_memory(source):
        raise ValueError("This instruction cannot use two memory operands")
    if opcode == "MOV":
        if destination == "CS":
            raise ValueError("MOV cannot load CS")
        if destination in SEG_REGS:
            if source in SEG_REGS or not (source in WORD_REGS or is_memory(source)):
                raise ValueError("MOV into a segment register requires r/m16")
            return rmop(0x8E, source, SEG_REGS.index(destination), use_width=16)
        if source in SEG_REGS:
            return rmop(0x8C, destination, SEG_REGS.index(source), use_width=16)
        if destination in WORD_REGS + BYTE_REGS:
            if is_register(source) or is_memory(source):
                return rmop(0x8A + w, source, register_code(destination, width))
            return [0xB0 + 8 * w + register_code(destination, width)] + immediate(source, width)
        if is_memory(destination):
            if is_register(source):
                return rmop(0x88 + w, destination, register_code(source, width))
            if not any(v in tokens for v in ("BYTE", "WORD")):
                raise ValueError("Use BYTE PTR or WORD PTR for an immediate memory write")
            return rmop(0xC6 + w, destination, 0, immediate(source, width))
        raise ValueError("MOV needs a register or memory destination")
    if opcode in ("LEA", "LDS", "LES"):
        if destination not in WORD_REGS or not is_memory(source):
            raise ValueError(f"{opcode} requires a word register and memory operand")
        return rmop({"LEA":0x8D,"LDS":0xC5,"LES":0xC4}[opcode], source, WORD_REGS.index(destination), use_width=16)
    if opcode == "XCHG":
        if source not in WORD_REGS + BYTE_REGS:
            destination, source = source, destination
        return rmop(0x86 + w, destination, register_code(source, width))
    if opcode in ALU:
        base = ALU[opcode] * 8
        if source in WORD_REGS + BYTE_REGS:
            return rmop(base + w, destination, register_code(source, width))
        if is_memory(source):
            return rmop(base + 2 + w, source, register_code(destination, width))
        if destination == ("AX" if width == 16 else "AL"):
            return [base + 4 + w] + immediate(source, width)
        return rmop(0x80 + w, destination, ALU[opcode], immediate(source, width))
    if opcode == "TEST":
        if source in WORD_REGS + BYTE_REGS:
            return rmop(0x84 + w, destination, register_code(source, width))
        if destination in ("AL", "AX"):
            return [0xA8 + w] + immediate(source, width)
        return rmop(0xF6 + w, destination, 0, immediate(source, width))
    raise ValueError(f"{opcode} has no verified encoding in this workbench")


@dataclass
class Instruction:
    address: int
    tokens: list
    data: list
    line: int
    text: str


class Program:
    def __init__(self, source):
        self.source = source
        rows = source.splitlines()
        wrapped = not re.search(r"\bSEGMENT\b", source, flags=re.I)
        input_source = "CODE SEGMENT\nATLAS_ENTRY:\n" + source + "\nCODE ENDS\nEND ATLAS_ENTRY" if wrapped else source
        # The supplied interpreter uses the older misspellings internally.
        input_source = re.sub(r"\bLAHF\b", "LANF", input_source, flags=re.I)
        input_source = re.sub(r"\bSAHF\b", "SANF", input_source, flags=re.I)
        try:
            exe = Assembler(dict(CS=0x3000, DS=0x2000, SS=0x5000, ES=0x7000)).compile(input_source)
        except AssemblyError as error:
            line = error.line - 2 if wrapped and error.line else error.line
            raise AssemblyError(error.message, line, error.source) from None
        if not exe.ip_to_source_line:
            raise ValueError("The program contains no instructions")
        self.exe = exe
        offsets = sorted(exe.ip_to_source_line)
        start = offsets[0]
        if offsets != list(range(start, start + len(offsets))):
            raise ValueError("Use one contiguous code region; keep DB/DW values in a data segment")
        self.mapping = {}
        position = start
        raw = {}
        for offset in offsets:
            tokens = list(exe.space["CS"][offset])
            source_row = exe.ip_to_source_line[offset] - (2 if wrapped else 0)
            line = source_row + 1
            try:
                encoded = encode(tokens, position, validate_branch=False)
            except (ValueError, KeyError, IndexError) as error:
                raise AssemblyError(str(error), line, rows[source_row] if 0 <= source_row < len(rows) else "") from None
            self.mapping[offset] = position
            raw[offset] = (tokens, source_row, len(encoded))
            position += len(encoded)
        self.mapping[offsets[-1] + 1] = position
        if position > 65536:
            raise ValueError("Encoded code exceeds the 64 KiB code segment")
        self.instructions = {}
        for offset, (tokens, row, length) in raw.items():
            position = self.mapping[offset]
            if tokens[0] in set(JCC) | set(LOOPS) | {"JMP", "CALL"}:
                operand = tokens[-1]
                if not is_register(operand) and not is_memory(operand):
                    if ":" in operand:
                        segment, target = operand.split(":")
                        if number(segment) != int(exe.seg_adr["CS"],16):
                            raise AssemblyError("Far branch target must belong to the assembled code segment", row+1)
                        tokens[-1] = segment + ":" + hex(self.mapping.get(number(target),number(target)))
                    else:
                        tokens[-1] = hex(self.mapping.get(number(operand), number(operand)))
            encoded = encode(tokens, position)
            if len(encoded) != length:
                raise ValueError("Instruction length changed during branch relocation")
            self.instructions[position] = Instruction(position, tokens, encoded, row + 1, rows[row] if row < len(rows) else "")
        self.entry = self.mapping[number(exe.ip)]
        self.end = position + length
        self.segments = {name: int(value,16) for name,value in exe.seg_adr.items()}

    def listing(self):
        return [dict(address=i.address, bytes=i.data, line=i.line, text=i.text,
                     instruction=" ".join(i.tokens).replace("LANF","LAHF").replace("SANF","SAHF"))
                for i in self.instructions.values()]

