import re
import sys
import ast
from pprint import pprint
from emulator.instructions import all_ins,transfer_control_ins

class AssemblyError(Exception):
    """Raised when the assembler encounters a syntax or semantic error.
    
    Attributes:
        message  -- human-readable description
        line     -- 1-based source line number (None if unknown)
        source   -- the original source text of the offending line
    """
    def __init__(self, message, line=None, source=None):
        self.message = message
        self.line = line
        self.source = source
        loc = f" at line {line}" if line is not None else ""
        src = f"\n  Source: {source}" if source else ""
        super().__init__(f"AssemblyError{loc}: {message}{src}")


data_def_ins = ['DB', 'DW', 'DD', 'DQ', 'DT', 'DUP']

_QUOTED = r"""(?:'(?:\\.|''|[^'\\])*'|"(?:\\.|""|[^"\\])*")"""
_TOKEN = re.compile(_QUOTED + r"""|;.*|[^'";,\s]+|['"]""")
_DATA_VALUE = re.compile(_QUOTED + r"|(?<!\w)[0-9A-Fa-f]+[HhBbOoDd][,\s\]]+|\?")


def _tokenize(line, line_number=None):
    tokens = []
    for match in _TOKEN.finditer(line):
        token = match.group()
        if token.startswith(';'):
            line = line[:match.start()]
            break
        if token.startswith(("'", '"')):
            if len(token) == 1:
                raise AssemblyError("Unterminated quoted literal", line_number, line)
            tokens.append(token)
        else:
            tokens.append(token.upper())
    return tokens, line.strip()


def _parse_data_values(string):
    def normalize(match):
        token = match.group()
        if token == '?':
            return '0'
        if token.startswith(("'", '"')):
            quote = token[0]
            # MASM doubles the delimiter to include it inside a string.
            return quote + token[1:-1].replace(quote * 2, '\\' + quote) + quote
        return to_int_str(match)

    return ast.literal_eval(_DATA_VALUE.sub(normalize, '[' + string + ']'))


def to_int_str(matched):
    string = matched.group()
    idx = re.search(r'[,\s\]]', string).span()[0]
    suffix = string[idx:]
    string = string[:idx]
    int_str = str(to_decimal(string))
    # print("int_st:", int_str)
    return int_str + suffix

def to_decimal(num):
    # all kinds of string of num to decimal
    # print(f"converting {num} to decimal")
    if isinstance(num, int):
        return int(num)
    if (num.startswith("'") and num.endswith("'")) or (num.startswith('"') and num.endswith('"')):
        inner = num[1:-1].replace(num[0] * 2, num[0])
        if len(inner) == 1:
            return ord(inner)
    if num.startswith('0x'):
        return int(num, 16)
    if num.startswith('0X'):
        return int(num[2:], 16)
    num = num.upper()
    if num[-1] == 'B':
        res = int(num.rstrip('B'), 2)
    elif num[-1] == 'O':
        res = int(num.rstrip('O'), 8)
    elif num[-1] == 'D':
        res = int(num.rstrip('D'), 10)
    elif num[-1] == 'H':
        res = int(num.rstrip('H'), 16)
    else:
        res = int(num)
    return res

class Assembler(object):
    # Assembler (Actually an Interpreter)
    def __init__(self, seg):
        self.seg_adr = {reg: hex(seg[reg]) for reg in ('DS', 'CS', 'SS', 'ES')}
        self._reset()

    def _reset(self):
        self.name = ''
        self.title = ''
        self.space = {} # Segment space
        self.seg_id = {} # Segment name
        self.seg_len = {} # Segment actual length
        self.tags = {} # Labels
        self.vars = {} # Variables
        self.constants = {}  # EQU symbol table: name -> value string
        self.ip = '0'    # Program entry offset
        self.ins_origin = [] # Raw unparsed instructions
        self._source_rows = []
        self.ip_to_source_line = {}  # CS instruction offset -> original zero-based row

    def compile(self, code):
        self._reset()
        instructions = self.__preprocessing(code)
        # Pre-scan ASSUME directives so segments defined before ASSUME are recognized
        for ins in instructions:
            if ins and ins[0] == 'ASSUME':
                self.__assume(ins[1:])
        # Provide fallback mappings for standard segment names
        default_mappings = {'CODE': 'CS', 'DATA': 'DS', 'STACK': 'SS', 'EXTRA': 'ES'}
        for name, reg in default_mappings.items():
            if name not in self.seg_id:
                self.seg_id[name] = reg

        for ip in range(len(instructions)):
            ins = instructions[ip]
            if ins[0] == 'NAME': # Module name
                self.name = ins[1] 
            elif ins[0] == 'TITLE': # File name
                self.title = ins[1]
            elif ins[0] == 'ASSUME': # Already handled in pre-scan
                self.__assume(ins[1:])
            elif len(ins) > 1 and ins[1] == 'SEGMENT':
                ip = self.__segment(instructions, ip)
            elif ins[0] == 'END':
                self.ip = self.tags[ins[1]]['offset']

        self.__eval_id()
        for offset, row in self.ip_to_source_line.items():
            opcode = self.space['CS'][offset][0]
            if opcode not in all_ins:
                raise AssemblyError(f"Unknown instruction '{opcode}'", row + 1, self.ins_origin[self._source_rows.index(row)])

        # print()
        # for key, val in self.space.items():
        #     print(key,':')
        #     pprint(val[:100], compact=True)
        #     print()
        # print("seg_id:",self.seg_id)
        # print("\ntags:")
        # pprint(self.tags)
        # print("\nvars:")
        # pprint(self.vars)
        # print("\ninitital ip:", self.ip)
        return self

    def __eval_id(self):  #TODO(Zubin) make it simple
        # Resolve labels (for jmp/loop) and variables
        var_dict = {}
        for key, val in self.seg_id.items():
            var_dict[key] = str(self.seg_adr[val]) # Resolve segment name to segment address
        for key, val in self.vars.items():
            # var_dict[key] = hex(int(val['seg'], 16) * 16 + int(val['offset'], 16)) # Physical address
            for k, v in self.seg_adr.items():
                if v == val['seg']:
                    seg_name = k
            var_dict[key] = seg_name + ':[' + str(hex(int(val['offset'], 16))) + ']' # "segment:offset"
        # print("var_dict:", var_dict)
        for key, cells in self.space.items():
            for i in range(self.seg_len[key]):
                ins = cells[i]
                if ins:
                    if ins[0] in transfer_control_ins and ins[-1] in self.tags.keys():
                        # jmp/call short/empty tag -> jmp/call tag.offset
                        # loop/jcxz tag -> loop/jcxz tag.offset
                        # jmp/call near ptr tag -> jmp/call tag.offset
                        # jmp/call far ptr tag -> jmp/call tag.seg:tag.offset
                        for s in ['SHORT', 'NEAR', 'PTR']:
                            if s in ins:
                                self.space[key][i].remove(s)
                        if ins[1] == 'FAR':
                            self.space[key][i].remove('FAR')
                            dst = self.tags[ins[1]]['seg'] + ':' + self.tags[ins[1]]['offset']
                            self.space[key][i][1] = dst
                        else:
                            self.space[key][i][1] = self.tags[ins[1]]['offset']
                    j = 0
                    while j < len(ins):
                        if ins[j] in ('SEG', 'OFFSET', 'TYPE'):
                            operator = ins[j]
                            name = ins[j + 1] if j + 1 < len(ins) else None
                            symbol = self.vars.get(name) or self.tags.get(name)
                            if symbol is None:
                                row = self.ip_to_source_line.get(i) if key == 'CS' else None
                                source = self.ins_origin[self._source_rows.index(row)] if row is not None else None
                                raise AssemblyError(f"{operator} requires a defined label or variable",
                                                    row + 1 if row is not None else None, source)
                            ins[j:j + 2] = [str(symbol[operator.lower()])]
                        # Replace variables and labels
                        for k, v in var_dict.items():
                            if ins[j] == k:
                                self.space[key][i][j] = v
                            elif ins[j][:len(k)] == k and ins[j][len(k)] == '[':
                                self.space[key][i][j] = v + ins[j][len(k):]
                        # Replace EQU constants
                        for k, v in self.constants.items():
                            if ins[j] == k:
                                self.space[key][i][j] = v
                        j += 1
                        # Variable: MOV BX,A[SI]  A = a.seg*16 + a.offset
                        # Variable: add ax, Item  Item = [a.seg*16 + a.offset]
                        # Segment name: MOV AX,DRG    ORG = org.seg

    def __segment(self, instructions, ip):
        seg_ip = 0  # Current segment offset, i.e., '$'
        extent = 0  # A later ORG may move the location counter backwards.
        seg_ins = instructions[ip]
        seg_tmp = seg_ins[0]
        seg_name = self.seg_id[seg_tmp] # CS DS SS ES
        self.space[seg_name] = [['0']] * int('10000', 16)
        if seg_name == 'CS':
            self.ip_to_source_line.clear()
        for i in range(ip+1, len(instructions)):
            ins = instructions[i]
            for j in range(len(ins)):
                if ins[j] == '$':
                    ins[j] = str(hex(seg_ip))
            ins_ori = self.ins_origin[i]
            if ':' in ins[0]:
                tag, following = ins[0].split(':', 1)
                self.tags[tag] = {'seg': self.seg_adr[seg_name],
                                  'offset': hex(seg_ip),
                                  'type': 0}
                ins = ([following] if following else []) + ins[1:]
                ins_ori = ins_ori.split(':', 1)[1].lstrip()
                if not ins:
                    continue
            if ins[0] == 'ORG':
                extent = max(extent, seg_ip)
                try:
                    seg_ip = to_decimal(ins[1])
                except (ValueError, IndexError):
                    seg_ip = -1
                if len(ins) != 2 or not 0 <= seg_ip < 0x10000:
                    raise AssemblyError("ORG requires a 16-bit offset", self._source_rows[i] + 1, self.ins_origin[i])
            elif ins[0] == 'EVEN': # Align next memory variable to even address
                seg_ip += seg_ip % 2
            elif ins[0] == 'ALIGN':
                try:
                    num = to_decimal(ins[1])
                except (ValueError, IndexError):
                    num = 0
                if len(ins) != 2 or num <= 0 or num & (num - 1):
                    raise AssemblyError("ALIGN requires a positive power of two",
                                        self._source_rows[i] + 1, self.ins_origin[i])
                seg_ip += (-seg_ip) % num
                if seg_ip > 0x10000:
                    raise AssemblyError("Alignment exceeds segment size", self._source_rows[i] + 1, self.ins_origin[i])
            elif ins[0] == seg_tmp or ins == ['ENDS']:
                if ins[0] == seg_tmp and ins[1:] != ['ENDS']:
                    raise AssemblyError(f"Expected 'ENDS' to close segment '{seg_tmp}'",
                                        line=self._source_rows[i] + 1, source=ins_ori)
                self.seg_len[seg_name] = max(extent, seg_ip)
                return i + 1

            elif ins[0] == 'END' or ins[1:2] in (['SEGMENT'], ['ENDS']):
                raise AssemblyError(f"Expected '{seg_tmp} ENDS' before '{ins_ori}'",
                                    line=self._source_rows[i] + 1, source=ins_ori)
            
            elif ins[0] == 'ASSUME':
                self.__assume(ins[1:])
                # Directive only, generate no instruction in space

            elif len(ins) >= 3 and ins[1] == 'EQU':  # EQU constant definition
                # EQU NAME VALUE — register a symbolic constant
                equ_name = ins[0]
                equ_val_str = ins_ori.split(None, 2)[2].strip() if len(ins_ori.split(None, 2)) > 2 else ins[2]
                self.constants[equ_name] = equ_val_str
                # Don't consume segment IP — EQU generates no code

            elif len(ins) >= 2 and ins[1] == 'PROC':
                # PROC definition — treat as a label entry point; NEAR/FAR are only advisory
                proc_name = ins[0]
                self.tags[proc_name] = {
                    'seg': self.seg_adr[seg_name],
                    'offset': hex(seg_ip),
                    'type': 0
                }

            elif len(ins) >= 2 and ins[1] == 'ENDP':
                # ENDP — marks end of procedure definition, no code generated
                pass

            elif ins[0] in data_def_ins or (len(ins) > 2 and ins[1] in data_def_ins):
                if ins[0] not in data_def_ins:
                    self.vars[ins[0]] = {'seg': self.seg_adr[seg_name],
                                         'offset': hex(seg_ip), 'type': 0}
                    ins = ins[1:]
                    ins_ori = ins_ori.split(None, 1)[1]
                try:
                    byte_list = self.__data_define(ins, ins_ori)
                except (ValueError, SyntaxError, AssemblyError) as err:
                    message = err.message if isinstance(err, AssemblyError) else f"Invalid {ins[0]} initializer"
                    raise AssemblyError(message, self._source_rows[i] + 1, self.ins_origin[i]) from err
                if seg_ip + len(byte_list) > 0x10000:
                    raise AssemblyError("Data exceeds segment size", self._source_rows[i] + 1, self.ins_origin[i])
                self.space[seg_name][seg_ip:seg_ip+len(byte_list)] = byte_list
                if seg_name == 'CS':
                    # ORG can place data over an earlier instruction.
                    for offset in range(seg_ip, seg_ip + len(byte_list)):
                        self.ip_to_source_line.pop(offset, None)
                seg_ip += len(byte_list)
            else: # Emit an instruction at the current segment offset
                if seg_ip >= 0x10000:
                    raise AssemblyError("Instruction exceeds segment size", self._source_rows[i] + 1, self.ins_origin[i])
                self.space[seg_name][seg_ip] = ins
                if seg_name == 'CS':
                    self.ip_to_source_line[seg_ip] = self._source_rows[i]
                seg_ip += 1

        raise AssemblyError(f"Missing '{seg_tmp} ENDS' for segment opened here",
                            line=self._source_rows[ip] + 1, source=self.ins_origin[ip])

    def __data_define(self, ins, ins_ori):
        var = ins[0]
        var_ori = ins_ori.split()[0]
        byte_list = []

        if len(ins) > 2 and ins[2][:3] == 'DUP': # db Imm dup ()
            times = to_decimal(ins[1])
            idx = ins_ori.find('(')
            dup_str = var + ' ' + ins_ori[idx + 1:-1]
            dup_list, _ = _tokenize(dup_str)
            byte_list = self.__data_define(dup_list, dup_str) * times

        elif var == 'DB': # DB　’A’, ‘D’, 0Dh, ‘$’   DB　1, 3, 5, 7, 9, 11
            db_str = ins_ori.replace(var_ori, '', 1).strip()
            byte_list = self.__str_to_bytes(db_str)

        elif var == 'DW':
            dw_str = ins_ori.replace(var_ori, '', 1).strip()
            byte_list = self.__str_to_words(dw_str)

        elif var == 'DD':
            dd_str = ins_ori.replace(var_ori, '', 1).strip()
            byte_list = self.__str_to_dwords(dd_str)
            
        else:
            raise AssemblyError(f"Unknown data definition directive '{var}'", source=ins_ori)
        
        # print("bytes_list: ", byte_list)
        return byte_list

    @classmethod
    def __str_to_bytes(cls, string):
        str_list = _parse_data_values(string)
        byte_list = []
        for item in str_list:
            if isinstance(item, int):
                byte_list.append([hex(item)])
            elif isinstance(item, str):
                for s in item:
                    byte_list.append([hex(ord(s))])
            else:
                raise AssemblyError(f"DB directive: cannot convert item '{item}' to byte")
        return byte_list

    @classmethod
    def __str_to_words(cls, string):
        str_list = _parse_data_values(string)
        byte_list = []
        for item in str_list:
            if not isinstance(item, int):
                raise AssemblyError(f"DW directive: expected integer value, got '{item}'")
            high, low = item >> 8, item & 0x0ff
            byte_list.append([hex(low)])  # little endian
            byte_list.append([hex(high)]) 
        return byte_list

    @classmethod
    def __str_to_dwords(cls, string):
        str_list = _parse_data_values(string)
        byte_list = []
        for item in str_list:
            if not isinstance(item, int):
                raise AssemblyError(f"DD directive: expected integer value, got '{item}'")
            byte_list.append([hex(item & 0x0ff)]) # little endian
            byte_list.append([hex(item >> 8 & 0x0ff)])
            byte_list.append([hex(item >> 16 & 0x0ff)])
            byte_list.append([hex(item >> 24)])
        return byte_list

    def __assume(self, ins):
        for i in ins:
            i = i.split(':')
            self.seg_id[i[1]] = i[0]

    def __preprocessing(self, code):
        instructions = []
        for row, line in enumerate(code.splitlines()):
            tokens, source = _tokenize(line, row + 1)
            if tokens:
                instructions.append(tokens)
                self.ins_origin.append(source)
                self._source_rows.append(row)
        # for i in range(len(instructions)):
        #     print(instructions[i])
        # print()
        return instructions
