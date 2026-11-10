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

    def print(self, string):
        # emulator print
        print(string, end='')

        self.output += string

    def run(self):
        self.IR = self.bus.instruction_queue.get()
        self.opcode = self.IR[0]
        self.bus.reg['IP'] += 1
        self.opd = []
        if len(self.IR) > 1:
            self.opd = self.IR[1:]
        self.get_opbyte()
        self.control_circuit()

    def get_opbyte(self):
        self.opbyte = 2
        for pr in self.opd:
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

        num = self.to_unsigned(num) & 0xffff
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
        # Resolve all memory addressing: direct, register indirect, base, index, base-index, relative base-index
        adr_reg = ['BX', 'SI', 'DI', 'BP']
        seg_reg = ['DS', 'CS', 'SS', 'ES']
        par_list = [s for s in re.split(r'\W', opd) if s]
        address = 0
        has_seg = False
        for par in par_list:
            if par in adr_reg:
                address += self.read_reg(par)
            elif par in seg_reg:
                address += self.read_reg(par) << 4
                has_seg = True
            else:
                address += to_decimal(par)
        if not has_seg:
            if 'BP' in par_list: # Default segment register is SS when BP is present
                address += self.read_reg('SS') << 4
            else:
                address += self.read_reg('DS') << 4
        # self.print("Get Address " + hex(address) + " from operand: " + opd)
        return address

    def get_offset(self, opd):
        # Resolve memory addressing offset: direct, register indirect, base, index, base-index
        # lea 0x3412:0x34; lea [si+bx]; lea 0x12; lea ss:offset; lea [bx][di]
        adr_reg = ['BX', 'SI', 'DI', 'BP']
        seg_reg = ['DS', 'CS', 'SS', 'ES']
        opd = opd.split(':')[-1] # Remove segment prefix
        par_list = [s for s in re.split(r'\W', opd) if s]
        offset = 0
        for par in par_list:
            if par in adr_reg:
                offset += self.read_reg(par)
            elif par in seg_reg:
                pass
            else:
                offset += to_decimal(par)
        return offset

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
            opd = '[' + str(opd) + ']'
        # Register
        if self.is_reg(opd):
            res = self.read_reg(opd)
        # Memory
        elif '[' in opd:
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
        return '[' in opd

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

        elif self.opcode == 'LDS':
            adr = self.get_address(self.opd[1])
            self.write_reg(self.opd[0], self.get_int(adr))
            self.write_reg('DS', self.get_int(adr + 2))

        elif self.opcode == 'LES':
            adr = self.get_address(self.opd[1])
            self.write_reg(self.opd[0], self.get_int(adr))
            self.write_reg('ES', self.get_int(adr + 2))
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
        result = 0
        for i in range(self.opbyte * 8):
            if i == self.opbyte * 8 - 1:
                result -= (num >> i & 1) << i
            else:
                result += (num >> i & 1) << i
        return result

    # Convert num to unsigned decimal based on opbyte
    def to_unsigned(self, num):
        result = 0
        for i in range(self.opbyte * 8):
            result += (num >> i & 1) << i
        return result

    # Check for signed overflow based on opbyte range
    def is_overflow(self, num):
        low = self.to_signed(int('1' + (self.opbyte * 8 - 1) * '0', 2))
        high = self.to_signed(int('0' + (self.opbyte * 8 - 1) * '1', 2))
        return num > high or num < low

    def set_pf(self, result):
        if self.popcount(result) % 2 == 0:
            self.FR.parity = 1
        else:
            self.FR.parity = 0

    def set_of(self, result):
        if self.is_overflow(result):
            self.FR.overflow = 1
        else:
            self.FR.overflow = 0

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

    def arithmetic_ins(self):
        if self.opcode == 'ADD':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = (res1 + res2) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 + res2)
            self.set_cf(((self.to_unsigned(res1) + self.to_unsigned(res2)) >> (self.opbyte * 8)) > 0)
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'ADC':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = (res1 + res2 + self.FR.carry) & int(
                "0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 + res2 + self.FR.carry)
            self.set_cf(((self.to_unsigned(res1) + self.to_unsigned(res2) + self.FR.carry) >> (self.opbyte * 8)) > 0)
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'SUB':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = (res1 - res2) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - res2)
            self.set_cf(self.to_unsigned(res1) < self.to_unsigned(res2))
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'SBB':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = (res1 - res2 - self.FR.carry) & int(
                "0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - res2 - self.FR.carry)
            if self.FR.carry == 1:
                self.set_cf(self.to_unsigned(res1) <= self.to_unsigned(res2))
            else:
                self.set_cf(self.to_unsigned(res1) < self.to_unsigned(res2))
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'MUL':
            assert self.opbyte in [1, 2]
            res2 = self.get_int(self.opd[0])
            if self.opbyte == 1:
                res1 = self.read_reg('AL')
                self.write_reg('AX', res1 * res2)
                if self.read_reg('AH') > 0:
                    self.FR.carry = self.FR.overflow = 1
                else:
                    self.FR.carry = self.FR.overflow = 0
            elif self.opbyte == 2:
                res1 = self.read_reg('AX')
                result = res1 * res2
                self.write_reg('AX', result & 0xff)
                self.write_reg('DX', (result >> 8) & 0xff)
                if self.read_reg('DX') > 0:
                    self.FR.carry = self.FR.overflow = 1
                else:
                    self.FR.carry = self.FR.overflow = 0

        elif self.opcode == 'DIV':
            assert self.opbyte in [1, 2]
            res2 = self.get_int(self.opd[0])
            if res2 == 0:
                self.interrupt_handler(0) # int 0：division by zero
            elif self.opbyte == 1:
                res1 = self.read_reg('AX')
                self.write_reg('AL', res1 // res2)
                self.write_reg('AH', res1 % res2)
            elif self.opbyte == 2:
                res1 = (self.read_reg('DX') << 8) + self.read_reg('AX')
                self.write_reg('AX', res1 // res2)
                self.write_reg('DX', res1 % res2)

        elif self.opcode == 'INC':
            res1 = self.get_int(self.opd[0])
            result = (res1 + 1) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 + 1)
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'DEC':
            res1 = self.get_int(self.opd[0])
            result = (res1 - 1) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - 1)
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

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
            res1 = self.get_int(self.opd[0])
            result = ((~res1) + 1) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of((~res1) + 1)

            self.set_cf((self.to_unsigned(~res1) + 1) >> (self.opbyte * 8) > 0)

            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

            self.put_int(self.opd[0], result)

        elif self.opcode == 'CMP':
            res1 = self.get_int(self.opd[0])
            res2 = self.get_int(self.opd[1])
            result = (res1 - res2) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - res2)
            self.set_cf(self.to_unsigned(res1) < self.to_unsigned(res2))
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

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

        elif self.opcode == 'SAL':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                temp = res << 1
                self.FR.carry = temp >> (self.opbyte * 8) & 1
                if (temp >> (self.opbyte * 8 - 1) & 1) == \
                    (res >> (self.opbyte * 8 - 1) & 1):
                    self.FR.overflow = 0
                else:
                    self.FR.overflow = 1
                res = temp & int('1' * self.opbyte * 8, 2)
            self.put_int(self.opd[0], res)

        elif self.opcode == 'SHL':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                temp = res << 1
                self.FR.carry = temp >> (self.opbyte * 8) & 1
                if (temp >> (self.opbyte * 8 - 1) & 1) == \
                    (res >> (self.opbyte * 8 - 1) & 1):
                    self.FR.overflow = 0
                else:
                    self.FR.overflow = 1
                res = temp & int('1' * self.opbyte * 8, 2)
            self.put_int(self.opd[0], res)

        elif self.opcode == 'SAR':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                self.FR.carry = res & 1
                self.FR.overflow = 0
                op = res >> (self.opbyte * 8 - 1) & 1
                res = (res >> 1) + (op << (self.opbyte * 8 - 1))
            self.put_int(self.opd[0], res)

        elif self.opcode == 'SHR':
            res = self.get_int(self.opd[0])
            cnt = self.get_int(self.opd[1])
            while cnt:
                cnt -= 1
                self.FR.carry = res & 1
                if res >> (self.opbyte * 8 - 1) & 1:
                    self.FR.overflow = 1
                else:
                    self.FR.overflow = 0
                res >>= 1
            self.put_int(self.opd[0], res)

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
        
        if self.opcode == 'JMP':
            # self.opbyte = 2
            if self.is_mem(self.opd[0]): # Target address in memory: jmp word/dword ptr [adr]
                adr = self.get_address(self.opd[0])
                if self.opbyte == 4:
                    self.opbyte = 2
                    self.write_reg('CS', self.get_int(adr + 2))
                self.write_reg('IP', self.get_int(adr))
            elif ':' in self.opd[0]:    # Far jump: jmp cs:ip
                self.opd = [s for s in re.split(' |:', self.opd[0]) if s]
                self.write_reg('CS', self.get_int(self.opd[0]))
                self.write_reg('IP', self.get_int(self.opd[1]))
            else:                     # Short jump, near jump, register jump: jmp ip/reg
                self.write_reg('IP', self.get_int(self.opd[0]))

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

        elif self.opcode == 'CALL':
            if self.opbyte == 4 or ':' in self.opcode[0]:
                self.inc_reg('SP', -2)
                self.write_mem(self.ss_sp, self.bus.reg['CS'])
            self.inc_reg('SP', -2)
            self.write_mem(self.ss_sp, self.bus.reg['IP'])
            self.opcode = 'JMP'
            self.control_circuit()

        elif self.opcode == 'RET':
            self.write_reg('IP', self.get_int_from_adr(self.ss_sp))
            self.inc_reg('SP', 2)

        elif self.opcode == 'RETF':
            self.write_reg('IP', self.get_int_from_adr(self.ss_sp))
            self.inc_reg('SP', 2)
            self.write_reg('CS', self.get_int_from_adr(self.ss_sp))
            self.inc_reg('SP', 2)

        elif self.opcode in conditional_jump_ins:
            # All conditional jumps are short jumps
            jmp_map = {
                'JA':  self.FR.carry == 0 and self.FR.zero == 0,
                'JAE': self.FR.carry == 0,
                'JB': self.FR.carry == 1,
                'JBE': self.FR.carry == 0 and self.FR.zero == 1,
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
                'JNG': self.FR.zero == 1 and self.FR.sign != self.FR.overflow,
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
            res_list = self.bus.read_word(src_adr)
            self.write_mem(dst_adr, res_list)
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

            result = (res1 - res2) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - res2)
            self.set_cf(self.to_unsigned(res1) < self.to_unsigned(res2))
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

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

            result = (res1 - res2) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - res2)
            self.set_cf(self.to_unsigned(res1) < self.to_unsigned(res2))
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

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

            result = (res1 - res2) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - res2)
            self.set_cf(self.to_unsigned(res1) < self.to_unsigned(res2))
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

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

            result = (res1 - res2) & int("0x" + "f" * self.opbyte * 2, 16)

            self.set_of(res1 - res2)
            self.set_cf(self.to_unsigned(res1) < self.to_unsigned(res2))
            self.set_pf(result)
            self.set_zf(result)
            self.set_sf(result)

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
            val = to_decimal(input(f"Input to Port {port}: "))
            self.write_reg(self.opd[0], val)
        elif self.opcode == 'OUT':
            # Output from AL or AX to port. OUT 4, AX; OUT DX, AX
            # If port > 255, DX is used.
            port = self.get_int(self.opd[0])
            val = self.read_reg(self.opd[1])
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
            char = input()[0]
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
            self.write_reg('DL', int(now.microsecond * 1e4))
        
        elif ah == 0x35:
            if self.int_msg:
                self.print("Interrupt Routine: Get Interrupt Vector\n")
            int_type = self.read_reg('AL')
            self.write_reg('BX', self.get_int_from_adr(int_type * 4))
            self.write_reg('ES', self.get_int_from_adr(int_type * 4 + 2))
        
        elif ah == 0x4c: # Exit with return code
            if self.int_msg:
                self.print("Interrupt Routine: Terminate with Return Code\n")
            self.print(f"\nExit with return code {al}\n")
            self.shutdown = True

        else:
            sys.exit("Interrupt Error")

    def bios_isr_10h(self):
        pass

    def interrupt_handler(self, int_type):
        self.inc_reg('SP', -2) # Save context
        self.write_mem(self.ss_sp, self.FR.get_int())
        self.FR.trap = 0
        self.FR.interrupt = 0
        self.inc_reg('SP', -2)
        self.write_mem(self.ss_sp, self.get_int('CS'))
        self.inc_reg('SP', -2)
        self.write_mem(self.ss_sp, self.get_int('IP'))
        self.opbyte = 2
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