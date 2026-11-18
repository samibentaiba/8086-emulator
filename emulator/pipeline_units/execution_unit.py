import os
import sys
import re
import datetime
from emulator.register import *
from emulator.instructions import *
from emulator.assembler import to_decimal




class execution_unit(object):

    def __init__(self, BIU, int_msg):
        self.IR = []                 # Instruction register
        self.opcode = ''             # Opcode
        self.opd = []                # Operands
        self.opbyte = 2              # Default operand bytes: 1, 2, 4
        self.eo = [0] * 5            # Evaluated opds
        self.bus = BIU               # Internal bus connection to BIU
        # Flag Register
        self.interrupt = False       # External interrupt request
        self.shutdown = False        # CPU shutdown / halt
        self.int_msg = int_msg       # Print interrupt messages flag
        self.FR = Flag_register()
        self.reg = {
            # Data Register
            'AX': 0,
            'BX': 0,
            'CX': 0,
            'DX': 0,
            # Pointer Register
            'SP': 0,
            'BP': 0,
            # Index Register
            'SI': 0,
            'DI': 0
        }
        self.eu_regs = list(self.reg.keys()) + ['AL', 'AH', 'BL', 'BH', 'CL', 'CH', 'DL', 'DH']
        self.biu_regs = list(BIU.reg.keys()) # 'DS', 'CS', 'SS', 'ES', 'IP'
        self.output = ''
        self.mute_stdout = False
        from emulator.peripherals import PeripheralManager
        self.peripherals = PeripheralManager.get_instance()
        self.file_handles = {}
        self.next_handle = 5
        self.video_display = None

    @property
    def video(self):
        if self.video_display is None:
            from emulator.peripherals.video_display import VideoDisplayDevice
            self.video_display = VideoDisplayDevice(memory=self.bus.memory, enable_gui=self.peripherals.enable_gui)
        return self.video_display

    def read_asciiz_from_mem(self, seg, offset):
        """Read a null-terminated string from memory at seg:offset."""
        addr = (seg << 4) + offset
        chars = []
        for _ in range(256):
            b_list = self.bus.read_byte(addr)
            val = to_decimal(b_list[0]) if isinstance(b_list, list) else to_decimal(b_list)
            if val == 0:
                break
            chars.append(chr(val))
            addr += 1
        return "".join(chars)

    def print(self, string):
        # emulator print
        if not getattr(self, 'mute_stdout', False):
            print(string, end='')

        self.output += string

    def run(self):
        self.IR = self.bus.instruction_queue.get()
        self.opcode = self.IR[0]
        self.inc_reg('IP', 1)
        self.opd = []
        if len(self.IR) > 1:
            self.opd = self.IR[1:]
        self.get_opbyte()
        self.control_circuit()

    def get_opbyte(self):
        self.opbyte = 2
        width_operands = self.opd[:1] if self.opcode in rotate_shift_ins else self.opd
        for pr in width_operands:
            if pr in ['AL', 'AH', 'BL', 'BH', 'CL', 'CH', 'DL', 'DH']:
                self.opbyte = 1
        if 'PTR' in self.opd:
            self.opd.remove('PTR')
            if 'BYTE' in self.opd:
                self.opbyte = 1
                self.opd.remove('BYTE')
            elif 'WORD' in self.opd:
                self.opbyte = 2
                self.opd.remove('WORD')
            elif 'DWORD' in self.opd:
                self.opbyte = 4
                self.opd.remove('DWORD')
            else:
                sys.exit("Runtime Error: Unexpected PTR")
        if self.opcode in string_manipulation_ins:
            if 'B' in self.opcode:
                self.opbyte = 1
            else:
                self.opbyte = 2

    def read_reg(self, reg):
        if reg in self.biu_regs:
            res = self.bus.reg[reg]
        elif reg[1] == 'H':
            res = (self.reg[reg.replace('H', 'X')] >> 8) & 0xff
        elif reg[1] == 'L':
            res = self.reg[reg.replace('L', 'X')] & 0xff
        else:
            res = self.reg[reg]
        return res

    def write_reg(self, reg, num):
        # self.print(f"writing {hex(num)} => {num} to {reg} ...\n")

        num &= 0xffff
        if reg in self.biu_regs:
            self.bus.reg[reg] = num
        elif reg[1] == 'H':
            reg = reg.replace('H', 'X')
            self.reg[reg] = (self.reg[reg] & 0xff) + ((num & 0xff) << 8)
        elif reg[1] == 'L':
            reg = reg.replace('L', 'X')
            self.reg[reg] = (self.reg[reg] & 0xff00) + (num & 0xff)
        else:
            self.reg[reg] = num

    def inc_reg(self, reg, val):
        # Increment or decrement register value
        self.write_reg(reg, self.read_reg(reg) + val)

    def get_address(self, opd):
        prefix, separator, _ = opd.partition(':')
        if separator:
            segment = self.read_reg(prefix) if prefix in self.biu_regs else to_decimal(prefix)
        else:
            segment = self.read_reg('SS' if re.search(r'\bBP\b', opd) else 'DS')
        return (segment << 4) + self.get_offset(opd)

    def get_offset(self, opd):
        expression = opd.split(':')[-1]
        offset = 0
        for sign, term in re.findall(r'([+-]?)\s*(\w+)', expression):
            value = self.read_reg(term) if term in ('BX', 'BP', 'SI', 'DI') else to_decimal(term)
            offset += -value if sign == '-' else value
        return offset & 0xffff

    def __get_byte(self, opd):
        # Memory addressing containing '[]'
        address = self.get_address(opd)
        content = self.bus.read_byte(address)
        # self.print("Get Byte content: " + content + " from " + hex(address) + '\n)
        return content

    def __get_word(self, opd):
        # Memory addressing containing '[]'
        address = self.get_address(opd)
        content = self.bus.read_word(address)
        return content

    def __get_dword(self, opd):
        # Memory addressing containing '[]'
        address = self.get_address(opd)
        content = self.bus.read_dword(address)
        return content

    def __get_char(self, address):
        # Get ASCII character at memory address
        return chr(to_decimal(self.bus.read_byte(address)[0]))

    def get_int(self, opd):
        # Automatically get operand value
        # If opd is int, access as memory address
        if isinstance(opd, int):
            return self.get_int_from_adr(opd)
        # Register
        if self.is_reg(opd):
            res = self.read_reg(opd)
        # Memory
        elif self.is_mem(opd):
            if self.opbyte == 1:
                res_list = self.__get_byte(opd)
            elif self.opbyte == 2:
                res_list = self.__get_word(opd)
            elif self.opbyte == 4:
                res_list = self.__get_dword(opd)
            else:
                sys.exit("Opbyte Error")
            res = 0
            assert res_list, "Empty memory space"
            # print("res_list", res_list)

            for num in res_list:
                res = (res << 8) + (int(num, 16) & 0xff)
        # Immediate
        else:
            res = to_decimal(opd)
        # self.print("get_int " + hex(res) + " from " + opd)
        return res

    def get_int_from_adr(self, adr):
        # Absolute address
        if self.opbyte == 1:
            res_list = self.bus.read_byte(adr)
        elif self.opbyte == 2:
            res_list = self.bus.read_word(adr)
        elif self.opbyte == 4:
            res_list = self.bus.read_dword(adr)
        else:
            sys.exit("Opbyte Error")
        res = 0
        assert res_list, "Empty memory space"
        for num in res_list:
            res = (res << 8) + (int(num, 16) & 0xff)
        return res

    def put_int(self, opd, num):
        # Automatically store num to opd (register or memory)
        if self.is_reg(opd):
            self.write_reg(opd, num)
        elif self.is_mem(opd):
            adr = self.get_address(opd)
            self.write_mem(adr, num)

    def is_reg(self, opd):
        return opd in (self.eu_regs + self.biu_regs)

    def is_mem(self, opd):
        return '[' in opd and not opd.startswith(("'", '"'))

    def write_mem(self, loc, content):
        # Automatically write to memory
        if self.opbyte == 1:
            self.bus.write_byte(loc, content)
        elif self.opbyte == 2:
            self.bus.write_word(loc, content)
        elif self.opbyte == 4:
            self.bus.write_dword(loc, content)
        else:
            sys.exit("Opbyte Error")

    def control_circuit(self):
        old_cs_ip = self.bus.cs_ip
        if self.opcode in data_transfer_ins:
            self.data_transfer_ins()
        elif self.opcode in arithmetic_ins:
            self.arithmetic_ins()
        elif self.opcode in logical_ins:
            self.logical_ins()
        elif self.opcode in rotate_shift_ins:
            self.rotate_shift_ins()
        elif self.opcode in transfer_control_ins:
            self.transfer_control_ins()
        elif self.opcode in string_manipulation_ins:
            self.string_manipulation_ins()
        elif self.opcode in flag_manipulation_ins:
            self.flag_manipulation_ins()
        elif self.opcode in stack_related_ins:
            self.stack_related_ins()
        elif self.opcode in input_output_ins:
            self.input_output_ins()
        elif self.opcode in miscellaneous_ins:
            self.miscellaneous_ins()
        else:
            sys.exit("operation code not support")
        # print(f"old_cs_ip: {hex(old_cs_ip)}, new_cs_ip: {hex(self.bus.cs_ip)})")
        if old_cs_ip != self.bus.cs_ip:
            self.bus.flush_pipeline()

    def data_transfer_ins(self):
        self.opd[1] = ''.join(self.opd[1:])
        if self.opcode == 'MOV':
            res = self.get_int(self.opd[1])
            self.put_int(self.opd[0], res)

        elif self.opcode == 'XCHG':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            self.put_int(self.opd[0], res2)
            self.put_int(self.opd[1], res1)

        elif self.opcode == 'LEA':
            adr = self.get_offset(self.opd[1])
            self.put_int(self.opd[0], adr)

        elif self.opcode in ('LDS', 'LES'):
            adr = self.get_address(self.opd[1])
            self.opbyte = 2  # Both fields of the far pointer are 16-bit words.
            self.write_reg(self.opd[0], self.get_int(adr))
            self.write_reg('DS' if self.opcode == 'LDS' else 'ES', self.get_int(adr + 2))
        else:
            pass

    # Count set bits (popcount) in binary representation
    def popcount(self, num):
        cnt = 0
        while num > 0:
            cnt += 1
            num &= num - 1
        return cnt

    # Convert num to signed decimal based on opbyte
    def to_signed(self, num):
        unsigned = self.to_unsigned(num)
        sign_bit = 1 << (self.opbyte * 8 - 1)
        return (unsigned ^ sign_bit) - sign_bit

    def to_unsigned(self, num):
        return num & ((1 << (self.opbyte * 8)) - 1)

    def is_overflow(self, num):
        limit = 1 << (self.opbyte * 8 - 1)
        return not -limit <= num < limit

    def set_pf(self, result):
        self.FR.parity = int(self.popcount(result & 0xff) % 2 == 0)

    def set_of(self, result):
        self.FR.overflow = int(self.is_overflow(result))

    def set_sf(self, result):
        if self.to_signed(result) < 0:
            self.FR.sign = 1
        else:
            self.FR.sign = 0

    def set_zf(self, result):
        if result == 0:
            self.FR.zero = 1
        else:
            self.FR.zero = 0

    def set_cf(self, result):
        if result == True:
            self.FR.carry = 1
        else:
            self.FR.carry = 0

    def _add_subtract(self, left, right, *, subtract=False, carry=0, preserve_carry=False):
        left = self.to_unsigned(left)
        right = self.to_unsigned(right)
        if subtract:
            value = left - right - carry
            signed_value = self.to_signed(left) - self.to_signed(right) - carry
        else:
            value = left + right + carry
            signed_value = self.to_signed(left) + self.to_signed(right) + carry
        result = self.to_unsigned(value)
        self.set_of(signed_value)
        if not preserve_carry:
            self.set_cf(value != result)
        self.FR.auxiliary = ((left ^ right ^ result) >> 4) & 1
        self.set_pf(result)
        self.set_zf(result)
        self.set_sf(result)
        return result

    def arithmetic_ins(self):
        if self.opcode in ('ADD', 'ADC', 'SUB', 'SBB'):
            left = self.get_int(self.opd[0])
            right = self.get_int(self.opd[1])
            carry = self.FR.carry if self.opcode in ('ADC', 'SBB') else 0
            result = self._add_subtract(left, right, subtract=self.opcode in ('SUB', 'SBB'), carry=carry)
            self.put_int(self.opd[0], result)

        elif self.opcode in ('MUL', 'IMUL'):
            left = self.read_reg('AL' if self.opbyte == 1 else 'AX')
            right = self.get_int(self.opd[0])
            if self.opcode == 'IMUL':
                product = self.to_signed(left) * self.to_signed(right)
                overflow = self.is_overflow(product)
            else:
                product = left * right
                overflow = product != self.to_unsigned(product)
            self.write_reg('AX', product)
            if self.opbyte == 2:
                self.write_reg('DX', product >> 16)
            self.FR.overflow = self.FR.carry = int(overflow)

        elif self.opcode in ('DIV', 'IDIV'):
            bits = self.opbyte * 8
            divisor = self.to_unsigned(self.get_int(self.opd[0]))
            dividend = self.read_reg('AX')
            if self.opbyte == 2:
                dividend |= self.read_reg('DX') << 16
            if divisor == 0:
                self.interrupt_handler(0)
                return
            if self.opcode == 'IDIV':
                divisor = self.to_signed(divisor)
                sign_bit = 1 << (2 * bits - 1)
                dividend = (dividend ^ sign_bit) - sign_bit
                # Signed division truncates toward zero and preserves the dividend's remainder sign.
                quotient = abs(dividend) // abs(divisor)
                if (dividend < 0) != (divisor < 0):
                    quotient = -quotient
                remainder = dividend - quotient * divisor
                overflow = self.is_overflow(quotient)
            else:
                quotient, remainder = divmod(dividend, divisor)
                overflow = quotient != self.to_unsigned(quotient)
            if overflow:
                self.interrupt_handler(0)
                return
            self.write_reg('AL' if self.opbyte == 1 else 'AX', quotient)
            self.write_reg('AH' if self.opbyte == 1 else 'DX', remainder)

        elif self.opcode == 'AAM':
            radix = self.get_int(self.opd[0]) & 0xff if self.opd else 10
            if radix == 0:
                self.interrupt_handler(0)
                return
            high, low = divmod(self.read_reg('AL'), radix)
            self.write_reg('AX', (high << 8) | low)
            self.FR.sign = low >> 7
            self.set_zf(low)
            self.set_pf(low)

        elif self.opcode in ('INC', 'DEC'):
            value = self.get_int(self.opd[0])
            result = self._add_subtract(value, 1, subtract=self.opcode == 'DEC', preserve_carry=True)
            self.put_int(self.opd[0], result)

        elif self.opcode == 'CBW':
            res = self.read_reg('AL')
            if res >> 7 & 1:
                self.write_reg('AH', 255)
            else:
                self.write_reg('AH', 0)

        elif self.opcode == 'CWD':
            res = self.read_reg('AX')
            if res >> 15 & 1:
                self.write_reg('DX', 65535)
            else:
                self.write_reg('DX', 0)

        else:
            sys.exit("operation code not support")

    def logical_ins(self):
        if self.opcode == 'AND':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = res1 & res2

            self.FR.carry = self.FR.overflow = 0

            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'OR':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = res1 | res2

            self.FR.carry = self.FR.overflow = 0

            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'XOR':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = res1 ^ res2

            self.FR.carry = self.FR.overflow = 0

            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'NOT':
            res1 = self.get_int(self.opd[0])
            self.put_int(self.opd[0], ~res1)

        elif self.opcode == 'NEG':
            value = self.get_int(self.opd[0])
            self.put_int(self.opd[0], self._add_subtract(0, value, subtract=True))

        elif self.opcode == 'CMP':
            self._add_subtract(self.get_int(self.opd[0]), self.get_int(self.opd[1]), subtract=True)

        elif self.opcode == 'TEST':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = res1 & res2

            self.FR.carry = self.FR.overflow = 0

            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

        else:
            sys.exit("operation code not support")

    def rotate_shift_ins(self):
        if self.opcode == 'RCL':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                temp = (res << 1) + self.FR.carry
                self.FR.carry = temp >> (self.opbyte * 8) & 1
                if (temp >> (self.opbyte * 8 - 1) & 1) == (res >> (self.opbyte * 8 - 1) & 1):
                    self.FR.overflow = 0
                else:
                    self.FR.overflow = 1
                res = temp & int('1' * self.opbyte * 8, 2)
            self.put_int(self.opd[0], res)

        elif self.opcode == 'RCR':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                temp = (res >> 1) + (self.FR.carry << (self.opbyte * 8 - 1))
                self.FR.carry = res & 1
                if (temp >> (self.opbyte * 8 - 1) & 1) == (res >> (self.opbyte * 8 - 1) & 1):
                    self.FR.overflow = 0
                else:
                    self.FR.overflow = 1
                res = temp
            self.put_int(self.opd[0], res)

        elif self.opcode == 'ROL':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                temp = (res << 1) + (res >> (self.opbyte * 8 - 1) & 1)
                self.FR.carry = res >> (self.opbyte * 8 - 1) & 1
                if (temp >> (self.opbyte * 8 - 1) & 1) == (res >> (self.opbyte * 8 - 1) & 1):
                    self.FR.overflow = 0
                else:
                    self.FR.overflow = 1
                res = temp & int('1' * self.opbyte * 8, 2)
            self.put_int(self.opd[0], res)

        elif self.opcode == 'ROR':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                temp = (res >> 1) + ((res & 1) << (self.opbyte * 8 - 1))
                self.FR.carry = res & 1
                if (temp >> (self.opbyte * 8 - 1) & 1) == (res >> (self.opbyte * 8 - 1) & 1):
                    self.FR.overflow = 0
                else:
                    self.FR.overflow = 1
                res = temp
            self.put_int(self.opd[0], res)

        elif self.opcode in ('SAL', 'SHL', 'SAR', 'SHR'):
            count = self.get_int(self.opd[1])
            if count == 0:
                return
            value = self.get_int(self.opd[0])
            sign_bit = 1 << (self.opbyte * 8 - 1)
            for _ in range(count):
                original_sign = value & sign_bit
                if self.opcode in ('SAL', 'SHL'):
                    self.FR.carry = int(bool(original_sign))
                    value = self.to_unsigned(value << 1)
                    self.FR.overflow = int((value & sign_bit) != original_sign)
                else:
                    self.FR.carry = value & 1
                    value >>= 1
                    if self.opcode == 'SAR':
                        value |= original_sign
                        self.FR.overflow = 0
                    else:
                        self.FR.overflow = int(bool(original_sign))
            self.set_sf(value)
            self.set_zf(value)
            self.set_pf(value)
            self.put_int(self.opd[0], value)

        else:
            sys.exit("operation code not support")

    @property
    def ss_sp(self):
        return self.bus.reg['SS'] * 16 + self.reg['SP']

    def stack_related_ins(self):
        if self.opcode == 'PUSH':
            self.inc_reg('SP', -2)
            self.write_mem(self.ss_sp, self.get_int(self.opd[0]))
        elif self.opcode == 'POP':
            res_list = self.bus.read_word(self.ss_sp)
            res = 0
            for num in res_list:
                res = (res << 8) + int(num, 16)
            if self.is_mem(self.opd[0]):
                ad = self.get_address(self.opd[0])
                self.write_mem(ad,res)
            elif self.is_reg(self.opd[0]):
                self.write_reg(self.opd[0], res)
            self.inc_reg('SP', 2)
        elif self.opcode == 'PUSHF':
            self.inc_reg('SP', -2)
            self.write_mem(self.ss_sp, self.FR.get_int())
        elif self.opcode == 'POPF':
            res_list = self.bus.read_word(self.ss_sp)
            res = 0
            for num in res_list:
                res = (res << 8) + int(num, 16)
            self.FR.set_int(res)
            self.inc_reg('SP', 2)
        else:
            sys.exit("operation code not support")

    def transfer_control_ins(self):
        
        if self.opcode in ('JMP', 'CALL'):
            target = self.opd[0]
            segment = None
            if self.is_mem(target):
                address = self.get_address(target)
                far_pointer = self.opbyte == 4
                self.opbyte = 2
                offset = self.get_int_from_adr(address)
                if far_pointer:
                    segment = self.get_int_from_adr(address + 2)
            elif ':' in target:
                segment_operand, offset_operand = target.split(':')
                segment = self.get_int(segment_operand)
                offset = self.get_int(offset_operand)
            else:
                offset = self.get_int(target)

            if self.opcode == 'CALL':
                if segment is not None:
                    self.inc_reg('SP', -2)
                    self.bus.write_word(self.ss_sp, self.read_reg('CS'))
                self.inc_reg('SP', -2)
                self.bus.write_word(self.ss_sp, self.read_reg('IP'))
            if segment is not None:
                self.write_reg('CS', segment)
            self.write_reg('IP', offset)

        elif self.opcode == 'LOOP':
            self.inc_reg('CX', -1)
            if self.reg['CX'] != 0:
                self.write_reg('IP', self.get_int(self.opd[0]))

        elif self.opcode in ['LOOPE', 'LOOPZ']:
            self.inc_reg('CX', -1)
            if self.reg['CX'] != 0 and self.FR.zero == 1:
                self.write_reg('IP', self.get_int(self.opd[0]))

        elif self.opcode in ['LOOPNE', 'LOOPNZ']:
            self.inc_reg('CX', -1)
            if self.reg['CX'] != 0 and self.FR.zero == 0:
                self.write_reg('IP', self.get_int(self.opd[0]))

        elif self.opcode in ('RET', 'RETF'):
            self.write_reg('IP', self.get_int_from_adr(self.ss_sp))
            self.inc_reg('SP', 2)
            if self.opcode == 'RETF':
                self.write_reg('CS', self.get_int_from_adr(self.ss_sp))
                self.inc_reg('SP', 2)
            if self.opd:
                self.inc_reg('SP', self.get_int(self.opd[0]))

        elif self.opcode in conditional_jump_ins:
            # All conditional jumps are short jumps
            jmp_map = {
                'JA':  self.FR.carry == 0 and self.FR.zero == 0,
                'JAE': self.FR.carry == 0,
                'JB': self.FR.carry == 1,
                'JBE': self.FR.carry == 1 or self.FR.zero == 1,
                'JC': self.FR.carry == 1,
                'JCXZ': self.reg['CX'] == 0,
                'JE': self.FR.zero == 1,
                'JG': self.FR.zero == 0 and self.FR.sign == self.FR.overflow,
                'JGE': self.FR.sign == self.FR.overflow,
                'JL': self.FR.sign != self.FR.overflow,
                'JLE': self.FR.sign != self.FR.overflow or self.FR.zero == 1,
                'JNA': self.FR.carry == 1 or self.FR.zero == 1,
                'JNAE': self.FR.carry == 1,
                'JNB': self.FR.carry == 0,
                'JNBE': self.FR.carry == 0 and self.FR.zero == 0,
                'JNC': self.FR.carry == 0,
                'JNE': self.FR.zero == 0,
                'JNG': self.FR.zero == 1 or self.FR.sign != self.FR.overflow,
                'JNGE': self.FR.sign != self.FR.overflow,
                'JNL': self.FR.sign == self.FR.overflow,
                'JNLE': self.FR.sign == self.FR.overflow and self.FR.zero == 0,
                'JNO': self.FR.overflow == 0,
                'JNP': self.FR.parity == 0,
                'JNS': self.FR.sign == 0,
                'JNZ': self.FR.zero == 0,
                'JO': self.FR.overflow == 1,
                'JP': self.FR.parity == 1,
                'JPE': self.FR.parity == 1,
                'JPO': self.FR.parity == 0,
                'JS': self.FR.sign == 1,
                'JZ': self.FR.zero == 1
            }
            if jmp_map[self.opcode]:
                self.write_reg('IP', self.get_int(self.opd[0]))

        else:
            sys.exit("operation code not support")

    def string_manipulation_ins(self):
        if self.opcode == 'MOVSB':
            src_adr = self.bus.reg['DS'] * 16 + self.reg['SI']
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            res_list = self.bus.read_byte(src_adr)
            self.write_mem(dst_adr, res_list)
            if self.FR.direction == 0:
                self.inc_reg('SI', 1)
                self.inc_reg('DI', 1)
            else:
                self.inc_reg('SI', -1)
                self.inc_reg('DI', -1)

        elif self.opcode == 'MOVSW':
            src_adr = self.bus.reg['DS'] * 16 + self.reg['SI']
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            self.bus.write_word(dst_adr, self.get_int_from_adr(src_adr))
            if self.FR.direction == 0:
                self.inc_reg('SI', 2)
                self.inc_reg('DI', 2)
            else:
                self.inc_reg('SI', -2)
                self.inc_reg('DI', -2)

        elif self.opcode == 'CMPSB':
            src_adr = self.bus.reg['DS'] * 16 + self.reg['SI']
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            res1_list = self.bus.read_byte(src_adr)
            res1 = 0
            for num in res1_list:
                res1 = (res1 << 8) + int(num, 16)
            res2_list = self.bus.read_byte(dst_adr)
            res2 = 0
            for num in res2_list:
                res2 = (res2 << 8) + int(num, 16)

            self._add_subtract(res1, res2, subtract=True)

            if self.FR.direction == 0:
                self.inc_reg('SI', 1)
                self.inc_reg('DI', 1)
            else:
                self.inc_reg('SI', -1)
                self.inc_reg('DI', -1)

        elif self.opcode == 'CMPSW':
            src_adr = self.bus.reg['DS'] * 16 + self.reg['SI']
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            res1_list = self.bus.read_word(src_adr)
            res1 = 0
            for num in res1_list:
                res1 = (res1 << 8) + int(num, 16)
            res2_list = self.bus.read_word(dst_adr)
            res2 = 0
            for num in res2_list:
                res2 = (res2 << 8) + int(num, 16)

            self._add_subtract(res1, res2, subtract=True)

            if self.FR.direction == 0:
                self.inc_reg('SI', 2)
                self.inc_reg('DI', 2)
            else:
                self.inc_reg('SI', -2)
                self.inc_reg('DI', -2)

        elif self.opcode == 'LODSB':
            src_adr = self.bus.reg['DS'] * 16 + self.reg['SI']
            res_list = self.bus.read_byte(src_adr)
            res = 0
            for num in res_list:
                res = (res << 8) + int(num, 16)
            self.write_reg('AL', res)
            if self.FR.direction == 0:
                self.inc_reg('SI', 1)
            else:
                self.inc_reg('SI', -1)

        elif self.opcode == 'LODSW':
            src_adr = self.bus.reg['DS'] * 16 + self.reg['SI']
            res_list = self.bus.read_word(src_adr)
            res = 0
            for num in res_list:
                res = (res << 8) + int(num, 16)
            self.write_reg('AX', res)
            if self.FR.direction == 0:
                self.inc_reg('SI', 2)
            else:
                self.inc_reg('SI', -2)

        elif self.opcode == 'STOSB':
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            res = self.read_reg('AL')
            self.bus.write_byte(dst_adr, res)
            if self.FR.direction == 0:
                self.inc_reg('DI', 1)
            else:
                self.inc_reg('DI', -1)

        elif self.opcode == 'STOSW':
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            res = self.read_reg('AX')
            self.bus.write_word(dst_adr, res)
            if self.FR.direction == 0:
                self.inc_reg('DI', 2)
            else:
                self.inc_reg('DI', -2)

        elif self.opcode == 'SCASB':
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            res1 = self.read_reg('AL')
            res2_list = self.bus.read_byte(dst_adr)
            res2 = 0
            for num in res2_list:
                res2 = (res2 << 8) + int(num, 16)

            self._add_subtract(res1, res2, subtract=True)

            if self.FR.direction == 0:
                self.inc_reg('DI', 1)
            else:
                self.inc_reg('DI', -1)

        elif self.opcode == 'SCASW':
            dst_adr = self.bus.reg['ES'] * 16 + self.reg['DI']
            res1 = self.read_reg('AX')
            res2_list = self.bus.read_word(dst_adr)
            res2 = 0
            for num in res2_list:
                res2 = (res2 << 8) + int(num, 16)

            self._add_subtract(res1, res2, subtract=True)

            if self.FR.direction == 0:
                self.inc_reg('DI', 2)
            else:
                self.inc_reg('DI', -2)

        elif self.opcode == 'REP':
            self.opcode = self.opd[0]
            if len(self.opd) > 1:
                self.opd = self.opd[1:]
            else:
                self.opd = []
            self.get_opbyte()
            
            while self.read_reg('CX') != 0:
                self.control_circuit()
                res = self.read_reg('CX')
                self.write_reg('CX', res - 1)

        elif self.opcode == 'REPE':
            self.opcode = self.opd[0]
            if len(self.opd) > 1:
                self.opd = self.opd[1:]
            else:
                self.opd = []
            self.get_opbyte()
            while self.read_reg('CX') != 0:
                self.control_circuit()
                res = self.read_reg('CX')
                self.write_reg('CX', res - 1)
                if self.FR.zero == 0:
                    break

        elif self.opcode == 'REPZ':
            self.opcode = self.opd[0]
            if len(self.opd) > 1:
                self.opd = self.opd[1:]
            else:
                self.opd = []
            self.get_opbyte()
            while self.read_reg('CX') != 0:
                self.control_circuit()
                res = self.read_reg('CX')
                self.write_reg('CX', res - 1)
                if self.FR.zero == 0:
                    break

        elif self.opcode == 'REPNE':
            self.opcode = self.opd[0]
            if len(self.opd) > 1:
                self.opd = self.opd[1:]
            else:
                self.opd = []
            self.get_opbyte()
            while self.read_reg('CX') != 0:
                self.control_circuit()
                res = self.read_reg('CX')
                self.write_reg('CX', res - 1)
                if self.FR.zero == 1:
                    break

        elif self.opcode == 'REPNZ':
            self.opcode = self.opd[0]
            if len(self.opd) > 1:
                self.opd = self.opd[1:]
            else:
                self.opd = []
            self.get_opbyte()
            while self.read_reg('CX') != 0:
                self.control_circuit()
                res = self.read_reg('CX')
                self.write_reg('CX', res - 1)
                if self.FR.zero == 1:
                    break

        else:
            sys.exit("operation code not support")

    # execution_unit methods
    def flag_manipulation_ins(self):
        if self.opcode == 'STC':
            self.FR.carry = 1
        elif self.opcode == 'CLC':
            self.FR.carry = 0
        elif self.opcode == 'CMC':
            self.FR.carry ^= 1
        elif self.opcode == 'STD':
            self.FR.direction = 1
        elif self.opcode == 'CLD':
            self.FR.direction = 0
        elif self.opcode == 'STI':
            self.FR.interrupt = 1
        elif self.opcode == 'CLI':
            self.FR.interrupt = 0
        elif self.opcode == 'LANF':
            self.write_reg('AH', self.FR.get_low())
        elif self.opcode == 'SANF':
            self.FR.set_low(self.read_reg('AH'))
        else:
            sys.exit("Operation code not supported")

    def input_output_ins(self):
        if self.opcode == 'IN':
            # Input from port into AL or AX. IN AX, 4; IN AL, 7;
            # Supports all registers. Port can be immediate or DX.
            port = self.get_int(self.opd[1]) if self.is_reg(self.opd[1]) else to_decimal(self.opd[1])
            val = None
            if hasattr(self, 'peripherals') and self.peripherals.has_device(port):
                val = self.peripherals.read_port(port, self.opbyte)
            if val is None:
                try:
                    val = to_decimal(input(f"Input to Port {port}: "))
                except (EOFError, OSError, ValueError):
                    val = 0
            self.write_reg(self.opd[0], val)
        elif self.opcode == 'OUT':
            # Output from AL or AX to port. OUT 4, AX; OUT DX, AX
            # If port > 255, DX is used.
            port = self.get_int(self.opd[0])
            val = self.read_reg(self.opd[1])
            if hasattr(self, 'peripherals'):
                self.peripherals.write_port(port, val, self.opbyte)
            self.print("> " * 16 + "@Port {}: 0x{:<4x} => {}\n".format(port, val, val))
        else:
            sys.exit("Operation code not supported")

    def dos_isr_21h(self):
        ah = self.read_reg('AH')
        al = self.read_reg('AL')
        if self.int_msg:
            self.print(f"\nInvoking DOS Interrupt 21H, AH={hex(ah)}\n")
        if ah == 0x0:
            if self.int_msg:
                self.print("Interrupt Routine: Program Terminate\n")
            self.print("> " * 16 + "Exit to operating system")
            self.shutdown = True

        elif ah == 0x01:
            if self.int_msg:
                self.print("Interrupt Routine: Keyboard Input with Echo\n")
            try:
                char_in = input()
                char = char_in[0] if char_in else '\r'
            except (EOFError, OSError):
                char = '\r'
            self.write_reg('AL', ord(char)) # Store ASCII
        
        elif ah == 0x02:
            if self.int_msg:
                self.print("Interrupt Routine: Character Output\n")
            char = chr(self.read_reg('DL'))
            self.print('> '+ char + '\n')

        elif ah == 0x9: # Display string DS:DX=string address, '$' terminated
            if self.int_msg:
                self.print("Interrupt Routine: Display String\n")
            address = (self.read_reg('DS') << 4) + self.read_reg('DX')
            count = 0
            self.print("> " * 16)     # '>' prompt for CPU output

            while True:
                char = self.__get_char(address)
                if char == '$' or count == 500: # Stop if '$' or 500 character limit reached
                    break
                # print(address)
                self.print(char)
                address += 1
                count += 1
            self.print('\n')

        elif ah == 0x06: # Direct console I/O
            dl = self.read_reg('DL')
            if dl == 0xFF:
                # Direct non-blocking input
                # Return AL = 0, ZF = 1 if no input
                self.write_reg('AL', 0)
                self.FR.zero = 1
            else:
                self.print(chr(dl))
                if self.video_display:
                    self.video.teletype_output(dl)

        elif ah in [0x07, 0x08]: # Console input without echo
            if self.int_msg:
                self.print("Interrupt Routine: Console Input without Echo\n")
            try:
                char = input()
                ch_code = ord(char[0]) if char else 0x0D
            except Exception:
                ch_code = 0x0D
            self.write_reg('AL', ch_code)

        elif ah == 0x0A: # Buffered keyboard input (DS:DX points to buffer)
            if self.int_msg:
                self.print("Interrupt Routine: Buffered Keyboard Input\n")
            buf_addr = (self.read_reg('DS') << 4) + self.read_reg('DX')
            b_max = self.bus.read_byte(buf_addr)
            max_len = to_decimal(b_max[0]) if isinstance(b_max, list) else to_decimal(b_max)
            try:
                line = input()
            except Exception:
                line = ""
            chars = line[:max(0, max_len - 1)]
            # Write actual length at buffer + 1
            self.bus.write_byte(buf_addr + 1, len(chars))
            # Write characters starting at buffer + 2
            for idx, ch in enumerate(chars):
                self.bus.write_byte(buf_addr + 2 + idx, ord(ch))
            # Terminate with CR (0x0D)
            self.bus.write_byte(buf_addr + 2 + len(chars), 0x0D)

        elif ah == 0x0B: # Get stdin status
            self.write_reg('AL', 0xFF) # Ready

        elif ah == 0x25: # Set interrupt vector (AL=int_type, DS:DX=vector)
            int_type = self.read_reg('AL')
            dx = self.read_reg('DX')
            ds = self.read_reg('DS')
            self.bus.write_word(int_type * 4, dx)
            self.bus.write_word(int_type * 4 + 2, ds)

        elif ah == 0x2a: # Get date: CX:DH:DL=Year:Month:Day
            if self.int_msg:
                self.print("Interrupt Routine: Read System Date\n")
            now = datetime.datetime.now()
            self.write_reg('CX', now.year)
            self.write_reg('DH', now.month)
            self.write_reg('DL', now.day)

        elif ah == 0x2c: # Get time: CH:CL=Hour:Minute, DH:DL=Second:1/100 Second
            if self.int_msg:
                self.print("Interrupt Routine: Read System Time\n")
            now = datetime.datetime.now()
            self.write_reg('CH', now.hour)
            self.write_reg('CL', now.minute)
            self.write_reg('DH', now.second)
            self.write_reg('DL', now.microsecond // 10_000)
        
        elif ah == 0x30: # Get DOS Version (AL=major=5, AH=minor=0)
            self.write_reg('AL', 5)
            self.write_reg('AH', 0)
            self.write_reg('BH', 0xFF)
            self.write_reg('BL', 0)

        elif ah == 0x35:
            if self.int_msg:
                self.print("Interrupt Routine: Get Interrupt Vector\n")
            int_type = self.read_reg('AL')
            self.write_reg('BX', self.get_int_from_adr(int_type * 4))
            self.write_reg('ES', self.get_int_from_adr(int_type * 4 + 2))
        
        # File Operations
        elif ah == 0x3C: # Create / Truncate file (DS:DX=ASCIIZ filename, CX=attribute)
            filename = self.read_asciiz_from_mem(self.read_reg('DS'), self.read_reg('DX'))
            try:
                f = open(filename, 'w+b')
                handle = self.next_handle
                self.next_handle += 1
                self.file_handles[handle] = f
                self.write_reg('AX', handle)
                self.FR.carry = 0
            except Exception:
                self.write_reg('AX', 3) # Path not found / access denied
                self.FR.carry = 1

        elif ah == 0x3D: # Open file (DS:DX=ASCIIZ filename, AL=mode: 0=R, 1=W, 2=RW)
            filename = self.read_asciiz_from_mem(self.read_reg('DS'), self.read_reg('DX'))
            mode_flag = al & 0x03
            mode_str = 'rb' if mode_flag == 0 else ('wb' if mode_flag == 1 else 'r+b')
            try:
                f = open(filename, mode_str)
                handle = self.next_handle
                self.next_handle += 1
                self.file_handles[handle] = f
                self.write_reg('AX', handle)
                self.FR.carry = 0
            except Exception:
                self.write_reg('AX', 2) # File not found
                self.FR.carry = 1

        elif ah == 0x3E: # Close file (BX=handle)
            bx = self.read_reg('BX')
            if bx in self.file_handles:
                try:
                    self.file_handles[bx].close()
                except Exception:
                    pass
                del self.file_handles[bx]
                self.FR.carry = 0
            else:
                self.write_reg('AX', 6) # Invalid handle
                self.FR.carry = 1

        elif ah == 0x3F: # Read from file or device (BX=handle, CX=count, DS:DX=buffer)
            bx = self.read_reg('BX')
            cx = self.read_reg('CX')
            buf_addr = (self.read_reg('DS') << 4) + self.read_reg('DX')
            if bx == 0: # Stdin
                try:
                    data = sys.stdin.buffer.read(cx)
                except Exception:
                    data = b""
                for idx, byte_val in enumerate(data):
                    self.bus.write_byte(buf_addr + idx, byte_val)
                self.write_reg('AX', len(data))
                self.FR.carry = 0
            elif bx in self.file_handles:
                try:
                    data = self.file_handles[bx].read(cx)
                    for idx, byte_val in enumerate(data):
                        self.bus.write_byte(buf_addr + idx, byte_val)
                    self.write_reg('AX', len(data))
                    self.FR.carry = 0
                except Exception:
                    self.write_reg('AX', 5) # Access denied
                    self.FR.carry = 1
            else:
                self.write_reg('AX', 6) # Invalid handle
                self.FR.carry = 1

        elif ah == 0x40: # Write to file or device (BX=handle, CX=count, DS:DX=buffer)
            bx = self.read_reg('BX')
            cx = self.read_reg('CX')
            buf_addr = (self.read_reg('DS') << 4) + self.read_reg('DX')
            byte_list = []
            for idx in range(cx):
                b = self.bus.read_byte(buf_addr + idx)
                val = to_decimal(b[0]) if isinstance(b, list) else to_decimal(b)
                byte_list.append(val & 0xFF)
            data_bytes = bytes(byte_list)

            if bx in (1, 2): # Stdout / Stderr
                text = data_bytes.decode('latin1', errors='replace')
                self.print(text)
                if self.video_display:
                    for ch in text:
                        self.video.teletype_output(ord(ch))
                self.write_reg('AX', cx)
                self.FR.carry = 0
            elif bx in self.file_handles:
                try:
                    self.file_handles[bx].write(data_bytes)
                    self.file_handles[bx].flush()
                    self.write_reg('AX', cx)
                    self.FR.carry = 0
                except Exception:
                    self.write_reg('AX', 5)
                    self.FR.carry = 1
            else:
                self.write_reg('AX', 6)
                self.FR.carry = 1

        elif ah == 0x41: # Delete file (DS:DX=ASCIIZ filename)
            filename = self.read_asciiz_from_mem(self.read_reg('DS'), self.read_reg('DX'))
            try:
                if os.path.exists(filename):
                    os.remove(filename)
                self.FR.carry = 0
            except Exception:
                self.write_reg('AX', 2) # File not found
                self.FR.carry = 1

        elif ah == 0x42: # LSEEK (BX=handle, AL=whence, CX:DX=offset)
            bx = self.read_reg('BX')
            whence = al & 0x03 # 0=start, 1=current, 2=end
            cx_val = self.read_reg('CX')
            dx_val = self.read_reg('DX')
            offset = (cx_val << 16) | dx_val
            if bx in self.file_handles:
                try:
                    new_pos = self.file_handles[bx].seek(offset, whence)
                    self.write_reg('DX', (new_pos >> 16) & 0xFFFF)
                    self.write_reg('AX', new_pos & 0xFFFF)
                    self.FR.carry = 0
                except Exception:
                    self.write_reg('AX', 1) # Invalid function
                    self.FR.carry = 1
            else:
                self.write_reg('AX', 6)
                self.FR.carry = 1

        elif ah == 0x4c: # Exit with return code
            if self.int_msg:
                self.print("Interrupt Routine: Terminate with Return Code\n")
            self.print(f"\nExit with return code {al}\n")
            self.shutdown = True

        else:
            sys.exit("Interrupt Error")

    def bios_isr_10h(self):
        ah = self.read_reg('AH')
        al = self.read_reg('AL')
        bh = self.read_reg('BH')
        bl = self.read_reg('BL')
        cx = self.read_reg('CX')
        dh = self.read_reg('DH')
        dl = self.read_reg('DL')

        if self.int_msg:
            self.print(f"\nInvoking BIOS Video Interrupt 10H, AH={hex(ah)}\n")

        if ah == 0x00: # Set video mode (AL = mode, e.g. 03h 80x25 text)
            self.video.video_mode = al
            self.video.clear_screen(attr=0x07)

        elif ah == 0x01: # Set cursor shape (CH/CL)
            pass

        elif ah == 0x02: # Set cursor position (DH=row, DL=col)
            self.video.set_cursor(dh, dl)

        elif ah == 0x03: # Read cursor position (DH=row, DL=col, CH/CL=shape)
            r, c = self.video.get_cursor()
            self.write_reg('DH', r)
            self.write_reg('DL', c)
            self.write_reg('CX', 0x0607) # Standard cursor scan lines

        elif ah == 0x06: # Scroll up / clear window (AL=lines, BH=attr, CH/CL=ul, DH/DL=lr)
            if al == 0:
                self.video.clear_screen(attr=bh)
            else:
                self.video.scroll_up(lines=al, attr=bh)

        elif ah == 0x07: # Scroll down window
            pass

        elif ah == 0x08: # Read char and attribute at cursor
            r, c = self.video.get_cursor()
            char_code, attr = self.video.read_char_at(r, c)
            self.write_reg('AL', char_code)
            self.write_reg('AH', attr)

        elif ah == 0x09: # Write char and attribute at cursor (AL=char, BL=attr, CX=count)
            r, c = self.video.get_cursor()
            count = max(1, cx)
            for i in range(count):
                curr_col = (c + i) % 80
                curr_row = r + (c + i) // 80
                if curr_row < 25:
                    self.video.write_char_at(curr_row, curr_col, al, bl)
            self.video.sync_display()

        elif ah == 0x0A: # Write char only at cursor (AL=char, CX=count)
            r, c = self.video.get_cursor()
            count = max(1, cx)
            for i in range(count):
                curr_col = (c + i) % 80
                curr_row = r + (c + i) // 80
                if curr_row < 25:
                    _, cur_attr = self.video.read_char_at(curr_row, curr_col)
                    self.video.write_char_at(curr_row, curr_col, al, cur_attr)
            self.video.sync_display()

        elif ah == 0x0E: # Teletype output (AL=char, BL=foreground color)
            attr = bl if bl != 0 else 0x07
            self.video.teletype_output(al, attr)

        elif ah == 0x13: # Write string (ES:BP=string, CX=length, DH=row, DL=col, BL=attr)
            es = self.read_reg('ES')
            bp = self.read_reg('BP')
            addr = (es << 4) + bp
            cur_r = dh
            cur_c = dl
            for i in range(cx):
                b = self.bus.read_byte(addr + i)
                char_val = to_decimal(b[0]) if isinstance(b, list) else to_decimal(b)
                self.video.write_char_at(cur_r, cur_c, char_val, bl)
                cur_c += 1
                if cur_c >= 80:
                    cur_c = 0
                    cur_r += 1
            self.video.set_cursor(cur_r, cur_c)
            self.video.sync_display(force=True)

    def interrupt_handler(self, int_type):
        self.opbyte = 2  # Interrupt stack entries and vector fields are words.
        self.inc_reg('SP', -2) # Save context
        self.write_mem(self.ss_sp, self.FR.get_int())
        self.FR.trap = 0
        self.FR.interrupt = 0
        self.inc_reg('SP', -2)
        self.write_mem(self.ss_sp, self.get_int('CS'))
        self.inc_reg('SP', -2)
        self.write_mem(self.ss_sp, self.get_int('IP'))
        ip_val = self.get_int_from_adr(int_type * 4)
        cs_val = self.get_int_from_adr(int_type * 4 + 2)
        self.write_reg('IP', ip_val)
        self.write_reg('CS', cs_val)
        if self.int_msg:
            self.print(f"Executing Interrupt {hex(int_type)}...\n")
            self.print("Context saved successfully\n")
            self.print(f"Read IVT at {hex(int_type * 4)}: Offset {hex(ip_val)} => IP\n")
            self.print(f"Read IVT at {hex(int_type * 4 + 2)}: Segment {hex(cs_val)} => CS\n")
            self.print("Entering Interrupt Service Routine...\n")

    def miscellaneous_ins(self): 
        if self.opcode == 'NOP':
            pass
        elif self.opcode == 'INT':
            # Interrupt start
            if not self.opd:
                self.print("\nBreakpoint Interrupt (INT 3)\n")
                self.interrupt = True
            else:
                int_type = to_decimal(self.opd[0])
                if int_type == 3: # Breakpoint
                    self.print("\nBreakpoint Interrupt (INT 3)\n")
                    self.interrupt = True
                elif int_type == to_decimal('10H'):
                    self.bios_isr_10h()
                elif int_type == to_decimal('21H'):
                    self.dos_isr_21h()
                elif int_type in [to_decimal(i) for i in ['7ch']]:
                    self.interrupt_handler(int_type)
                else:
                    sys.exit("Interrupt Type Error")

        elif self.opcode == 'IRET':
            if self.int_msg:
                self.print("Interrupt Routine finished, restoring context...\n")
            self.opcode = 'POP'
            self.opd = ['IP']
            self.control_circuit()

            self.opcode = 'POP'
            self.opd = ['CS']
            self.control_circuit()

            self.opcode = 'POPF'
            self.control_circuit()
            if self.int_msg:
                self.print("Context restored successfully\n")

        elif self.opcode == 'XLAT':
            pass
        elif self.opcode == 'HLT':
            self.shutdown = True
        elif self.opcode == 'ESC':
            pass
        elif self.opcode == 'INTO':
            if self.FR.overflow:
                self.interrupt_handler(4) # Overflow Interrupt
        elif self.opcode == 'LOCK':
            pass
        elif self.opcode == 'WAIT':
            pass
        else:
            sys.exit("Operation code not supported")
