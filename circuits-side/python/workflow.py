"""Run encoded assembly with the user's execution unit and capture real effects.

Events expose functional transfers. Their order is an explanatory trace and
does not claim the original chip's microcode clocks or electrical netlist.
"""
import copy
import json
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

from bytecode import Program, SUPPORTED, SEG_PREFIX, WORD_REGS, BYTE_REGS
from emulator.memory import Memory, ADDRESS_MASK
from emulator.register import Flag_register
from emulator.peripherals import PeripheralManager
from emulator.pipeline_units.bus_interface_unit import bus_interface_unit
from emulator.pipeline_units.execution_unit import execution_unit

FLAG_ATTRIBUTES = dict(CF="carry", PF="parity", AF="auxiliary", ZF="zero",
                       SF="sign", OF="overflow", TF="trap", IF="interrupt", DF="direction")
ARITHMETIC = {"ADD", "ADC", "SUB", "SBB", "CMP", "INC", "DEC", "NEG"}
LOGICAL = {"AND", "OR", "XOR", "TEST", "NOT"}


def h(value, width=4):
    return f"{value:0{width}X}h"


class Flags8086(Flag_register):
    def get_int(self):
        return super().get_int() | 0xF002


class TraceBus(bus_interface_unit):
    def attach(self, trace):
        self.trace = trace

    def read_byte(self, loc):
        value = super().read_byte(loc)
        if getattr(self, "trace", None) and self.trace.capturing:
            self.trace.bus_access("read", loc, [int(value[0], 16)])
        return value

    def read_word(self, loc):
        low = super().read_byte(loc)
        high = super().read_byte(loc + 1)
        if self.trace.capturing:
            self.trace.bus_access("read", loc, [int(low[0], 16), int(high[0], 16)])
        return high + low

    def read_dword(self, loc):
        return self.read_word(loc + 2) + self.read_word(loc)

    def write_byte(self, loc, value):
        old = super().read_byte(loc)
        self.trace.changes.setdefault(loc & ADDRESS_MASK, old)
        super().write_byte(loc, value)
        if self.trace.capturing:
            self.trace.bus_access("write", loc, [int(super().read_byte(loc)[0], 16)])

    def write_word(self, loc, value):
        data = [value & 255, (value >> 8) & 255] if isinstance(value, int) else [int(v,16) for v in value]
        for n, byte in enumerate(data):
            address = (loc + n) & ADDRESS_MASK
            self.trace.changes.setdefault(address, super().read_byte(address))
            super().write_byte(address, byte)
        if self.trace.capturing:
            self.trace.bus_access("write", loc, data)


class TraceEU(execution_unit):
    def attach(self, trace):
        self.trace = trace
        self.FR = Flags8086()
        self.mute_stdout = True

    def write_reg(self, register, value):
        before = self.read_reg(register)
        super().write_reg(register, value)
        if getattr(self, "trace", None) and self.trace.capturing:
            if register in ("IP", "CS"):
                self.trace.branched = True
            current = self.read_reg(register)
            kind = "branch" if register in ("IP", "CS") else "write"
            self.trace.event(kind, f"{register} ← {h(current)}",
                             f"{register} changes from {h(before)} to {h(current)}.",
                             register=register, value=current)

    def get_address(self, operand):
        address = super().get_address(operand) & ADDRESS_MASK
        if self.trace.capturing:
            prefix, separator, _ = operand.partition(":")
            segment = prefix if separator else ("SS" if "BP" in operand else "DS")
            offset = self.get_offset(operand)
            self.trace.ind = offset
            self.trace.selected_segment = segment
            self.trace.event("address", f"Address {h(address,5)}",
                             f"{segment}={h(self.read_reg(segment))}, offset={h(offset)}. "
                             f"(segment × 16 + offset) mod 2²⁰ = {h(address,5)}.",
                             address=address, offset=offset, segment=segment)
        return address

    def get_int(self, operand):
        value = super().get_int(operand)
        if self.trace.capturing and self.opcode in ARITHMETIC | LOGICAL | {"MOV", "XCHG", "PUSH", "OUT"}:
            if len(self.trace.operands) < 2:
                self.trace.operands.append(value)
                self.trace.event("operand", f"Read {operand}",
                                 f"{operand} supplies {h(value, self.opbyte*2)} "
                                 f"as a {self.opbyte*8}-bit operand.",
                                 operand=operand, value=value)
        return value

    def _add_subtract(self, left, right, *, subtract=False, carry=0, preserve_carry=False):
        before = self.trace.flags()
        result = super()._add_subtract(left, right, subtract=subtract,
                                       carry=carry, preserve_carry=preserve_carry)
        if self.trace.capturing:
            width = self.opbyte * 8
            self.trace.alu = dict(a=left & ((1 << width)-1), b=right & ((1 << width)-1),
                                  width=width, subtract=subtract, carry=carry,
                                  operation=self.opcode, result=result,
                                  preserveCarry=preserve_carry)
            operation = "−" if subtract else "+"
            self.trace.event("alu", f"ALU · {self.opcode}",
                             f"{h(left & ((1<<width)-1),width//4)} {operation} "
                             f"{h(right & ((1<<width)-1),width//4)}"
                             + (f" {operation} carry {carry}" if carry else "")
                             + f" → {h(result,width//4)}. Flags update for this operation.",
                             beforeFlags=before, result=result)
        return result

    def record_logic(self, result):
        if self.trace.capturing and self.opcode in LOGICAL:
            values = self.trace.operands
            left = values[0] if values else 0
            right = values[1] if len(values)>1 else 0
            mask = (1 << (self.opbyte*8))-1
            result &= mask
            self.trace.alu = dict(a=left,b=right,width=self.opbyte*8,operation=self.opcode,
                                  result=result,subtract=False,carry=0,preserveCarry=False)
            if self.opcode != "NOT":
                self.trace.undefined_flags = ["AF"]
            self.trace.event("alu", "ALU · "+self.opcode,
                             f"{self.opcode} produces {h(result,self.opbyte*2)}. "
                             + ("The destination keeps its value." if self.opcode=="TEST" else ""),
                             result=result)

    def put_int(self, operand, value):
        self.record_logic(value)
        super().put_int(operand, value)

    def logical_ins(self):
        super().logical_ins()
        if self.opcode == "TEST":
            self.record_logic(self.trace.operands[0] & self.trace.operands[1])

    def stack_related_ins(self):
        if self.opcode == "POP" and self.opd == ["SP"]:
            value = self.get_int_from_adr(self.ss_sp)
            self.inc_reg("SP", 2)
            self.write_reg("SP", value)
        else:
            super().stack_related_ins()

    def interrupt_handler(self, int_type):
        raise ValueError(f"CPU interrupt {int_type} occurred. Execution stopped before committing this instruction.")

    def miscellaneous_ins(self):
        if self.opcode == "XLAT":
            self.opbyte = 1
            offset = (self.read_reg("BX") + self.read_reg("AL")) & 65535
            address = ((self.read_reg("DS") << 4) + offset) & ADDRESS_MASK
            value = int(self.bus.read_byte(address)[0], 16)
            self.write_reg("AL", value)
            return
        if self.opcode == "INT":
            vector = int(self.opd[0],0) if self.opd[0].lower().startswith("0x") else int(self.opd[0][:-1],16) if self.opd[0].upper().endswith("H") else int(self.opd[0])
            service = self.read_reg("AH")
            if vector != 0x21 or service not in (0,2,9,0x4c):
                raise ValueError("The browser trace implements INT 21h services 00h, 02h, 09h and 4Ch")
        super().miscellaneous_ins()


class Workflow:
    def __init__(self, source):
        self.program = Program(source)
        self.memory = Memory(1 << 20, 1 << 16)
        self.capturing = False
        self.events = []
        self.changes = {}
        self.operands = []
        self.alu = None
        self.prefix = None
        self.ir = None
        self.modrm = None
        self.ind = None
        self.opr = None
        self.selected_segment = None
        self.last_address = None
        self.last_word = None
        self.current = None
        self.completed = 0
        self.undefined_flags = []
        self.console = ""
        self.halted = False
        self.history = []
        self.truncated = 0
        self.branched = False
        exe = self.program.exe
        for segment, cells in exe.space.items():
            if segment != "CS":
                self.memory.load_segment(self.program.segments[segment] << 4, cells[:exe.seg_len[segment]])
        for instruction in self.program.instructions.values():
            for offset, value in enumerate(instruction.data):
                self.memory.wb(((self.program.segments["CS"] << 4) + instruction.address + offset) & ADDRESS_MASK,
                               [hex(value)])
        PeripheralManager.reset_instance()
        PeripheralManager.get_instance(enable_gui=False)
        self.bus = TraceBus(6, exe, self.memory)
        self.bus.attach(self)
        self.bus.reg["IP"] = self.program.entry
        self.bus.pre_fetch_ip = self.program.entry
        self.eu = TraceEU(self.bus, int_msg=False)
        self.eu.attach(self)
        self.eu.reg["SP"] = 0xFFFE

    def flags(self):
        return {key: getattr(self.eu.FR, value) for key,value in FLAG_ATTRIBUTES.items()}

    def state(self):
        registers = dict(self.eu.reg, **self.bus.reg)
        return dict(registers=registers,flags=self.flags(),
                    queue=list(self.bus.instruction_queue.queue),
                    fetchIP=self.bus.pre_fetch_ip,ir=self.ir,mod=self.modrm,
                    prefix=self.prefix,ind=self.ind,opr=self.opr,
                    selectedSegment=self.selected_segment,physical=self.last_address,
                    lastWord=self.last_word,operands=list(self.operands),alu=copy.deepcopy(self.alu),
                    retired=self.completed,halted=self.halted,undefinedFlags=self.undefined_flags[:],
                    sourceLine=self.current.line if self.current else None,
                    instruction=self.current.text.strip() if self.current else "",
                    instructionAddress=self.current.address if self.current else self.program.entry)

    def event(self, kind, title, description, **values):
        if not self.capturing:
            return
        if len(self.events) >= 1024 and kind not in ("retire", "halt"):
            self.truncated += 1
            return
        self.events.append(dict(kind=kind,title=title,description=description,
                               state=self.state(),**values))

    def bus_access(self, kind, address, data):
        self.last_address = address & ADDRESS_MASK
        if kind == "read":
            self.opr = sum(byte << (8*i) for i,byte in enumerate(data))
        # Odd word accesses consume two bus transfers, one byte lane at a time.
        pieces = [(address,data)]
        if len(data)==2 and address&1:
            pieces = [(address,data[:1]),(address+1,data[1:])]
        for location, part in pieces:
            a0 = location & 1
            bhe = 0 if len(part)==2 or a0 else 1
            self.event("memory-"+kind, f"Memory {kind} · {h(location & ADDRESS_MASK,5)}",
                       f"{len(part)} byte(s), A0={a0}, BHE#={bhe}. "
                       + " ".join(h(value,2) for value in part)
                       + (" enter OPR." if kind=="read" else " enter memory."),
                       address=location & ADDRESS_MASK,bytes=part,a0=a0,bhe=bhe)

    def refill(self):
        queue = self.bus.instruction_queue
        if queue.qsize() > 4:
            return
        offset = self.bus.pre_fetch_ip
        count = 1 if offset&1 else 2
        address = ((self.bus.reg["CS"] << 4) + offset) & ADDRESS_MASK
        values = [int(self.memory.rb((address+i)&ADDRESS_MASK)[0],16) for i in range(count)]
        for value in values:
            queue.put_nowait(value)
        self.bus.pre_fetch_ip = (offset+count)&65535
        self.last_address = address
        self.last_word = sum(value << (8*i) for i,value in enumerate(values))
        self.event("fetch", "BIU prefetch · "+h(address,5),
                   f"CS:{h(offset)} selects {h(address,5)}. Append "
                   + " ".join(h(v,2) for v in values)
                   + f". FIFO now holds {queue.qsize()} of 6 bytes.",
                   address=address,bytes=values,a0=offset&1,bhe=0)

    def consume(self, instruction):
        prefixes = set(SEG_PREFIX.values()) | {0xf2,0xf3}
        opcode_index = next((i for i,b in enumerate(instruction.data) if b not in prefixes),0)
        for index, expected in enumerate(instruction.data):
            if self.bus.instruction_queue.empty():
                self.refill()
            actual = self.bus.instruction_queue.get_nowait()
            if actual != expected:
                raise ValueError("Code bytes changed after assembly. Reassemble before tracing modified code.")
            self.bus.reg["IP"] = (self.bus.reg["IP"]+1)&65535
            if index < opcode_index:
                self.prefix = actual
                title = "Prefix latch"
                description = f"Consume prefix {h(actual,2)} for this instruction."
            elif index == opcode_index:
                self.ir = actual
                title = "Opcode → IR"
                description = f"Consume {h(actual,2)} from Q and latch the 8-bit opcode."
            else:
                title = "Operand encoding byte"
                description = f"Consume {h(actual,2)} from Q as ModR/M, displacement or immediate data."
                if index == opcode_index+1 and has_modrm(self.ir):
                    self.modrm = actual
                    title = "ModR/M latch"
                    description = f"{h(actual,2)} = {actual>>6:02b} | {(actual>>3)&7:03b} | {actual&7:03b}."
            self.event("prefix" if index<opcode_index else "decode",title,description,byte=actual)

    def save(self):
        return dict(registers=dict(self.eu.reg),bus=dict(self.bus.reg),
                    prefetch=self.bus.pre_fetch_ip,queue=list(self.bus.instruction_queue.queue),
                    flags=self.eu.FR.get_int(),shutdown=self.eu.shutdown,
                    output=self.eu.output,extras=copy.deepcopy({
                        name:getattr(self,name) for name in (
                            "alu","prefix","ir","modrm","ind","opr","selected_segment",
                            "last_address","last_word","completed","undefined_flags","halted","operands")
                    }))

    def restore(self, saved, changes):
        self.eu.reg = dict(saved["registers"])
        self.bus.reg = dict(saved["bus"])
        self.bus.pre_fetch_ip = saved["prefetch"]
        self.bus.instruction_queue.queue.clear()
        for byte in saved["queue"]:
            self.bus.instruction_queue.put_nowait(byte)
        self.eu.FR.set_int(saved["flags"])
        self.eu.shutdown = saved["shutdown"]
        self.eu.output = saved["output"]
        for name,value in saved["extras"].items():
            setattr(self,name,copy.deepcopy(value))
        for address,old in changes.items():
            self.memory.space[address] = old

    def step(self):
        if self.halted:
            return dict(events=[],state=self.state(),halted=True,output="")
        offset = self.bus.reg["IP"]
        instruction = self.program.instructions.get(offset)
        if self.bus.reg["CS"] != self.program.segments["CS"] or instruction is None:
            raise ValueError(f"No assembled instruction at {h(self.bus.reg['CS'])}:{h(offset)}")
        saved = self.save()
        self.current = instruction
        self.events = []
        self.changes = {}
        self.operands = []
        self.prefix = None
        self.modrm = None
        self.truncated = 0
        self.branched = False
        self.capturing = True
        output_start = len(self.eu.output)
        try:
            self.refill()
            self.consume(instruction)
            self.eu.IR = list(instruction.tokens)
            self.eu.opcode = instruction.tokens[0]
            self.eu.opd = list(instruction.tokens[1:])
            self.eu.get_opbyte()
            self.event("control", "Decode · "+self.eu.opcode.replace("LANF","LAHF").replace("SANF","SAHF"),
                       "Select the instruction's operand transfers and architectural operation.")
            sequential = self.bus.reg["IP"]
            cs = self.bus.reg["CS"]
            if self.eu.opcode in ARITHMETIC:
                self.undefined_flags = ["CF"] if self.eu.opcode in ("INC","DEC") and "CF" in self.undefined_flags else []
            self.eu.control_circuit()
            if self.eu.opcode in ("MUL","IMUL"):
                self.undefined_flags = ["PF","AF","ZF","SF"]
            elif self.eu.opcode in ("DIV","IDIV"):
                self.undefined_flags = ["CF","PF","AF","ZF","SF","OF"]
            if self.branched or self.bus.reg["IP"] != sequential or self.bus.reg["CS"] != cs:
                self.bus.flush_pipeline()
                self.event("flush","Branch flush",
                           "Discard prefetched bytes and restart BIU fetching at "
                           f"{h(self.bus.reg['CS'])}:{h(self.bus.reg['IP'])}.")
            self.completed += 1
            self.halted = self.eu.shutdown
            self.prefix = None
            self.event("halt" if self.halted else "retire",
                       "Processor halted" if self.halted else "Instruction complete",
                       f"{instruction.text.strip()} completed. "
                       f"Architectural IP={h(self.bus.reg['IP'])}, next fetch IP={h(self.bus.pre_fetch_ip)}.")
        except (Exception, SystemExit) as error:
            self.restore(saved,self.changes)
            raise ValueError(str(error)) from None
        finally:
            self.capturing = False
        self.history.append((saved,dict(self.changes)))
        if len(self.history)>1000:
            self.history.pop(0)
        return dict(events=self.events,state=self.state(),halted=self.halted,
                    output=self.eu.output[output_start:],omittedEvents=self.truncated)

    def back(self):
        if self.history:
            saved,changes = self.history.pop()
            self.restore(saved,changes)
            self.current = self.program.instructions.get(self.bus.reg["IP"])
        return dict(state=self.state(),output=self.eu.output,canBack=bool(self.history))

    def memory_window(self, address, length=64):
        address &= ADDRESS_MASK
        return dict(address=address,bytes=[int(self.memory.rb((address+i)&ADDRESS_MASK)[0],16)
                                         for i in range(min(length,256))])


def has_modrm(opcode):
    return ((opcode & 0xC4)==0 and opcode <0x40
            or 0x80<=opcode<=0x8F
            or opcode in (0xC4,0xC5,0xC6,0xC7,0xD0,0xD1,0xD2,0xD3,0xF6,0xF7,0xFE,0xFF))


_instance = None

def dispatch(payload_json):
    global _instance
    message = json.loads(payload_json)
    command = message["command"]
    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
        if command == "assemble":
            candidate = Workflow(message["source"])
            _instance = candidate
            return json.dumps(dict(state=candidate.state(),listing=candidate.program.listing(),
                                   supported=SUPPORTED,segments=candidate.program.segments))
        if _instance is None:
            raise ValueError("Assemble a program first")
        if command == "step":
            return json.dumps(_instance.step())
        if command == "back":
            return json.dumps(_instance.back())
        if command == "memory":
            return json.dumps(_instance.memory_window(message.get("address",0x20000)))
    raise ValueError("Unknown workbench command")

