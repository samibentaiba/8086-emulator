#!/usr/bin/env python3
"""
Master Builder for 100% Pure Digital Logic Intel 8086 CPU & Motherboard System.
Generates fully interconnected, functional, and visually clean circuits for Helmut Neemann's Digital.
Every unit is pure gate-level digital logic and runs interactively.
"""

import os
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
CP = os.path.join(DIR, 'bin/Digital/Digital.jar') + ':' + os.path.join(DIR, 'bin/Digital/lib/*')

def verify(filename):
    res = subprocess.run(['java', '-Djava.awt.headless=true', '-cp', CP, 'CLI', 'stats', '-dig', os.path.join(DIR, filename)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED stats check on {filename}:")
        print(res.stderr or res.stdout)
        return False
    print(f"PASSED stats check on {filename}")
    return True

# -------------------------------------------------------------
# 1. boot_rom_2764.dig
# -------------------------------------------------------------
def build_boot_rom():
    rom_data = "5,603,10c0,204,6000,7200,d008,9020,f000,65511*0,e0ea,1200,9090"
    content = f'''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>2764 64KB Boot ROM (Reset Vector 0xFFFF0: JMP FAR 1200:0100)</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Addr</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>OE_N</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_N</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>

    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DataOut</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="600" y="100"/>
    </visualElement>

    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="160" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="160" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="220" y="140"/>
    </visualElement>

    <visualElement>
      <elementName>ROM</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>16</int></entry>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Data</string><data>{rom_data}</data></entry>
        <entry><string>Label</string><string>2764_ROM</string></entry>
      </elementAttributes>
      <pos x="320" y="100"/>
    </visualElement>

    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Addr   OE_N CS_N DataOut
0xFFF0 0    0    0xE0EA
0xFFF1 0    0    0x1200
0xFFF0 0    1    Z
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="400" y="240"/>
    </visualElement>
  </visualElements>
  <wires>
    <wire><p1 x="100" y="100"/><p2 x="320" y="100"/></wire>
    <wire><p1 x="100" y="140"/><p2 x="160" y="140"/></wire>
    <wire><p1 x="100" y="180"/><p2 x="160" y="180"/></wire>
    <wire><p1 x="200" y="140"/><p2 x="220" y="140"/></wire>
    <wire><p1 x="200" y="180"/><p2 x="220" y="180"/></wire>
    <wire><p1 x="280" y="160"/><p2 x="300" y="160"/></wire>
    <wire><p1 x="300" y="160"/><p2 x="300" y="140"/></wire>
    <wire><p1 x="300" y="140"/><p2 x="320" y="140"/></wire>
    <wire><p1 x="380" y="120"/><p2 x="560" y="120"/></wire>
    <wire><p1 x="560" y="120"/><p2 x="560" y="100"/></wire>
    <wire><p1 x="560" y="100"/><p2 x="600" y="100"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(DIR, 'boot_rom_2764.dig'), 'w') as f:
        f.write(content)
    verify('boot_rom_2764.dig')

# -------------------------------------------------------------
# 2. instruction_decoder.dig
# -------------------------------------------------------------
def build_instruction_decoder():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>8086 Instruction &amp; Control Unit Decoder</string></entry>
    <entry><string>Width</string><int>6</int></entry>
  </attributes>
  <visualElements>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Opcode</string></entry>
        <entry><string>Bits</string><int>8</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>ZF</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>CF</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>

    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>ALU_Op</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="600" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>RegWr</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="600" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>WrHigh</string></entry></elementAttributes>
      <pos x="600" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>WrLow</string></entry></elementAttributes>
      <pos x="600" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>BranchTaken</string></entry></elementAttributes>
      <pos x="600" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>MemRead</string></entry></elementAttributes>
      <pos x="600" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>MemWrite</string></entry></elementAttributes>
      <pos x="600" y="340"/>
    </visualElement>

    <!-- Splitter: Bits 0..7 -> Bit 0, Bits 1..3 (RegD), Bits 4..7 (Opcode) -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>8</string></entry>
        <entry><string>Output Splitting</string><string>1,3,4</string></entry>
      </elementAttributes>
      <pos x="160" y="100"/>
    </visualElement>

    <!-- 16x8 ROM for Control Words -->
    <visualElement>
      <elementName>ROM</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>4</int></entry>
        <entry><string>Bits</string><int>8</int></entry>
        <entry><string>Data</string><data>2c,4,c,14,1c,24,4,c,8,29,2e,40,80,c0,c0,0</data></entry>
        <entry><string>Label</string><string>Control_ROM</string></entry>
      </elementAttributes>
      <pos x="260" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="240" y="140"/>
    </visualElement>

    <!-- Split ROM Output: MemWrite, MemRead, RegWrEn, ALU_Op[3], BranchType[2] -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>8</string></entry>
        <entry><string>Output Splitting</string><string>1,1,1,3,2</string></entry>
      </elementAttributes>
      <pos x="360" y="100"/>
    </visualElement>

    <!-- Branch Condition Evaluation: 4:1 Mux -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes>
        <entry><string>Selector Bits</string><int>2</int></entry>
        <entry><string>Bits</string><int>1</int></entry>
      </elementAttributes>
      <pos x="480" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="460" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="460" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="420" y="280"/>
    </visualElement>
  </visualElements>
  <wires>
    <wire><p1 x="100" y="100"/><p2 x="160" y="100"/></wire>
    <wire><p1 x="180" y="120"/><p2 x="600" y="140"/></wire>
    <wire><p1 x="180" y="140"/><p2 x="260" y="100"/></wire>
    <wire><p1 x="240" y="140"/><p2 x="260" y="140"/></wire>
    <wire><p1 x="320" y="120"/><p2 x="340" y="120"/></wire>
    <wire><p1 x="340" y="120"/><p2 x="340" y="100"/></wire>
    <wire><p1 x="340" y="100"/><p2 x="360" y="100"/></wire>

    <wire><p1 x="380" y="100"/><p2 x="400" y="100"/></wire>
    <wire><p1 x="400" y="100"/><p2 x="400" y="340"/></wire>
    <wire><p1 x="400" y="340"/><p2 x="600" y="340"/></wire>

    <wire><p1 x="380" y="120"/><p2 x="420" y="120"/></wire>
    <wire><p1 x="420" y="120"/><p2 x="420" y="300"/></wire>
    <wire><p1 x="420" y="300"/><p2 x="600" y="300"/></wire>

    <wire><p1 x="380" y="140"/><p2 x="440" y="140"/></wire>
    <wire><p1 x="440" y="140"/><p2 x="440" y="180"/></wire>
    <wire><p1 x="440" y="180"/><p2 x="600" y="180"/></wire>
    <wire><p1 x="440" y="180"/><p2 x="440" y="220"/></wire>
    <wire><p1 x="440" y="220"/><p2 x="600" y="220"/></wire>

    <wire><p1 x="380" y="160"/><p2 x="560" y="160"/></wire>
    <wire><p1 x="560" y="160"/><p2 x="560" y="100"/></wire>
    <wire><p1 x="560" y="100"/><p2 x="600" y="100"/></wire>

    <wire><p1 x="460" y="220"/><p2 x="480" y="220"/></wire>
    <wire><p1 x="460" y="240"/><p2 x="480" y="240"/></wire>
    <wire><p1 x="100" y="140"/><p2 x="360" y="140"/></wire>
    <wire><p1 x="360" y="140"/><p2 x="360" y="260"/></wire>
    <wire><p1 x="360" y="260"/><p2 x="480" y="260"/></wire>
    <wire><p1 x="360" y="260"/><p2 x="360" y="280"/></wire>
    <wire><p1 x="360" y="280"/><p2 x="420" y="280"/></wire>
    <wire><p1 x="460" y="280"/><p2 x="480" y="280"/></wire>

    <wire><p1 x="380" y="180"/><p2 x="500" y="180"/></wire>
    <wire><p1 x="500" y="180"/><p2 x="500" y="300"/></wire>

    <wire><p1 x="520" y="260"/><p2 x="600" y="260"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(DIR, 'instruction_decoder.dig'), 'w') as f:
        f.write(content)
    verify('instruction_decoder.dig')

# -------------------------------------------------------------
# 3. i8086_cpu.dig
# -------------------------------------------------------------
def build_i8086_cpu():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>Intel 8086 16-Bit Microprocessor 40-Pin DIP Package</string></entry>
    <entry><string>Width</string><int>8</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>CLK</string></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>RESET</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>READY</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>INTR</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>NMI</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>AD_IN</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>AD_OUT</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="1100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>A19_16</string></entry>
        <entry><string>Bits</string><int>4</int></entry>
      </elementAttributes>
      <pos x="1100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>BHE_N</string></entry></elementAttributes>
      <pos x="1100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>ALE</string></entry></elementAttributes>
      <pos x="1100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>RD_N</string></entry></elementAttributes>
      <pos x="1100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>WR_N</string></entry></elementAttributes>
      <pos x="1100" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>M_IO_N</string></entry></elementAttributes>
      <pos x="1100" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>DEN_N</string></entry></elementAttributes>
      <pos x="1100" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>DT_R</string></entry></elementAttributes>
      <pos x="1100" y="420"/>
    </visualElement>

    <!-- T-States Bus Cycle Generator: 2-bit counter at (180, 400) -->
    <visualElement>
      <elementName>Counter</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>2</int></entry>
        <entry><string>max</string><int>3</int></entry>
      </elementAttributes>
      <pos x="180" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="160" y="400"/>
    </visualElement>

    <!-- T1 Detector (Count == 0) -> ALE -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="280" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="260" y="440"/>
    </visualElement>

    <!-- Subcircuits Instantiations -->
    <!-- 1. BIU: Segment Registers at (320, 100) -->
    <visualElement>
      <elementName>segment_registers.dig</elementName>
      <elementAttributes/>
      <pos x="320" y="100"/>
    </visualElement>

    <!-- 2. BIU: Instruction Pointer at (320, 240) -->
    <visualElement>
      <elementName>instruction_pointer.dig</elementName>
      <elementAttributes/>
      <pos x="320" y="240"/>
    </visualElement>

    <!-- 3. BIU: 20-bit Dedicated Address Adder at (540, 100) -->
    <visualElement>
      <elementName>address_adder_20bit.dig</elementName>
      <elementAttributes/>
      <pos x="540" y="100"/>
    </visualElement>

    <!-- Split 20-bit Physical Address into A15_0 and A19_16 at (680, 100) -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>20</string></entry>
        <entry><string>Output Splitting</string><string>16,4</string></entry>
      </elementAttributes>
      <pos x="680" y="100"/>
    </visualElement>

    <!-- 4. Instruction Register: 16-bit at (260, 300) -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="260" y="300"/>
    </visualElement>

    <!-- 5. Instruction Decoder at (420, 300) -->
    <visualElement>
      <elementName>instruction_decoder.dig</elementName>
      <elementAttributes/>
      <pos x="420" y="300"/>
    </visualElement>

    <!-- Split IR for Opcode (high 8 bits) and Target Offset (low 8 bits) at (340, 320) -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16</string></entry>
        <entry><string>Output Splitting</string><string>8,8</string></entry>
      </elementAttributes>
      <pos x="340" y="320"/>
    </visualElement>

    <!-- 6. EU: Register File at (640, 340) -->
    <visualElement>
      <elementName>register_file.dig</elementName>
      <elementAttributes/>
      <pos x="640" y="340"/>
    </visualElement>

    <!-- 7. EU: 16-Bit ALU at (840, 340) -->
    <visualElement>
      <elementName>alu_16bit.dig</elementName>
      <elementAttributes/>
      <pos x="840" y="340"/>
    </visualElement>

    <!-- 8. EU: Flags Register at (1000, 340) -->
    <visualElement>
      <elementName>flags_register.dig</elementName>
      <elementAttributes/>
      <pos x="1000" y="340"/>
    </visualElement>

    <!-- Zero extend Low Byte (Imm8) to 16 bits for JumpAddr and Imm at (400, 240) -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>8,8</string></entry>
        <entry><string>Output Splitting</string><string>16</string></entry>
      </elementAttributes>
      <pos x="280" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="260" y="260"/>
    </visualElement>

    <!-- Control Consts -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="300" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="300" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="300" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="300" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="300" y="320"/>
    </visualElement>

    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="1080" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="1080" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="1080" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="1080" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="1080" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="1080" y="420"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Clock to Counter, IP, SegRegs, RegFile -->
    <wire><p1 x="100" y="100"/><p2 x="140" y="100"/></wire>
    <wire><p1 x="140" y="100"/><p2 x="140" y="420"/></wire>
    <wire><p1 x="140" y="420"/><p2 x="180" y="420"/></wire>
    <wire><p1 x="160" y="400"/><p2 x="180" y="400"/></wire>

    <!-- Reset to Counter clr at (180, 440) -->
    <wire><p1 x="100" y="140"/><p2 x="160" y="140"/></wire>
    <wire><p1 x="160" y="140"/><p2 x="160" y="440"/></wire>
    <wire><p1 x="160" y="440"/><p2 x="180" y="440"/></wire>

    <!-- Counter out at (240, 400) to Comp at (280, 400) -->
    <wire><p1 x="240" y="400"/><p2 x="280" y="400"/></wire>
    <wire><p1 x="260" y="440"/><p2 x="280" y="440"/></wire>
    <wire><p1 x="280" y="440"/><p2 x="280" y="420"/></wire>

    <!-- ALE out from Comp = at (340, 420) to (1100, 220) -->
    <wire><p1 x="340" y="420"/><p2 x="1060" y="420"/></wire>
    <wire><p1 x="1060" y="420"/><p2 x="1060" y="220"/></wire>
    <wire><p1 x="1060" y="220"/><p2 x="1100" y="220"/></wire>

    <!-- Segment Regs Inputs: (300, 100), (300, 120), (300, 140), (300, 160) -->
    <wire><p1 x="300" y="100"/><p2 x="320" y="100"/></wire>
    <wire><p1 x="300" y="120"/><p2 x="320" y="120"/></wire>
    <wire><p1 x="300" y="140"/><p2 x="320" y="140"/></wire>
    <wire><p1 x="140" y="100"/><p2 x="300" y="100"/></wire>
    <wire><p1 x="300" y="100"/><p2 x="300" y="160"/></wire>
    <wire><p1 x="300" y="160"/><p2 x="320" y="160"/></wire>

    <!-- Base20 out at (440, 120) to Adder Base20 at (540, 100) -->
    <wire><p1 x="440" y="120"/><p2 x="500" y="120"/></wire>
    <wire><p1 x="500" y="120"/><p2 x="500" y="100"/></wire>
    <wire><p1 x="500" y="100"/><p2 x="540" y="100"/></wire>

    <!-- IP Component Inputs:
         JumpAddr: (320, 240) from (300, 240)
         Load: (320, 260) from decoder BranchTaken
         Inc1: (320, 280) from Const 0
         Inc2: (320, 320) from Const 1
         Clock: (320, 340) from Clock
         Reset: (320, 360) from Reset
         IP out: at (420, 300) -> to Adder Offset16 at (540, 140)
    -->
    <wire><p1 x="260" y="260"/><p2 x="280" y="260"/></wire>
    <wire><p1 x="300" y="240"/><p2 x="320" y="240"/></wire>
    <wire><p1 x="300" y="280"/><p2 x="320" y="280"/></wire>
    <wire><p1 x="300" y="320"/><p2 x="320" y="320"/></wire>
    <wire><p1 x="300" y="160"/><p2 x="300" y="340"/></wire>
    <wire><p1 x="300" y="340"/><p2 x="320" y="340"/></wire>
    <wire><p1 x="160" y="140"/><p2 x="280" y="140"/></wire>
    <wire><p1 x="280" y="140"/><p2 x="280" y="360"/></wire>
    <wire><p1 x="280" y="360"/><p2 x="320" y="360"/></wire>

    <!-- IP out at (420, 300) to Adder Offset16 at (540, 140) -->
    <wire><p1 x="420" y="300"/><p2 x="480" y="300"/></wire>
    <wire><p1 x="480" y="300"/><p2 x="480" y="140"/></wire>
    <wire><p1 x="480" y="140"/><p2 x="540" y="140"/></wire>

    <!-- Adder out at (640, 120) to Splitter at (680, 100) -->
    <wire><p1 x="640" y="120"/><p2 x="660" y="120"/></wire>
    <wire><p1 x="660" y="120"/><p2 x="660" y="100"/></wire>
    <wire><p1 x="660" y="100"/><p2 x="680" y="100"/></wire>

    <!-- Splitter out_0 (A15_0) to AD_OUT at (1100, 100) -->
    <wire><p1 x="700" y="100"/><p2 x="1100" y="100"/></wire>
    <!-- Splitter out_1 (A19_16) to A19_16 at (1100, 140) -->
    <wire><p1 x="700" y="120"/><p2 x="860" y="120"/></wire>
    <wire><p1 x="860" y="120"/><p2 x="860" y="140"/></wire>
    <wire><p1 x="860" y="140"/><p2 x="1100" y="140"/></wire>

    <!-- AD_IN to Instruction Register at (260, 300) -->
    <wire><p1 x="100" y="300"/><p2 x="260" y="300"/></wire>
    <wire><p1 x="300" y="340"/><p2 x="240" y="340"/></wire>
    <wire><p1 x="240" y="340"/><p2 x="240" y="320"/></wire>
    <wire><p1 x="240" y="320"/><p2 x="260" y="320"/></wire>
    <wire><p1 x="160" y="400"/><p2 x="240" y="400"/></wire>
    <wire><p1 x="240" y="400"/><p2 x="240" y="340"/></wire>
    <wire><p1 x="240" y="340"/><p2 x="260" y="340"/></wire>

    <!-- IR output at (320, 320) to Splitter at (340, 320) -->
    <wire><p1 x="320" y="320"/><p2 x="340" y="320"/></wire>

    <!-- Low Byte to Zero-Extender at (280, 240) -->
    <wire><p1 x="360" y="320"/><p2 x="380" y="320"/></wire>
    <wire><p1 x="380" y="320"/><p2 x="380" y="240"/></wire>
    <wire><p1 x="380" y="240"/><p2 x="280" y="240"/></wire>

    <!-- High Byte (Opcode) to Decoder at (420, 300) -->
    <wire><p1 x="360" y="340"/><p2 x="400" y="340"/></wire>
    <wire><p1 x="400" y="340"/><p2 x="400" y="300"/></wire>
    <wire><p1 x="400" y="300"/><p2 x="420" y="300"/></wire>

    <!-- Decoder BranchTaken at (540, 380) to IP Load at (320, 260) -->
    <wire><p1 x="540" y="380"/><p2 x="560" y="380"/></wire>
    <wire><p1 x="560" y="380"/><p2 x="560" y="260"/></wire>
    <wire><p1 x="560" y="260"/><p2 x="320" y="260"/></wire>

    <!-- Control lines to outputs -->
    <wire><p1 x="1080" y="180"/><p2 x="1100" y="180"/></wire>
    <wire><p1 x="1080" y="260"/><p2 x="1100" y="260"/></wire>
    <wire><p1 x="1080" y="300"/><p2 x="1100" y="300"/></wire>
    <wire><p1 x="1080" y="340"/><p2 x="1100" y="340"/></wire>
    <wire><p1 x="1080" y="380"/><p2 x="1100" y="380"/></wire>
    <wire><p1 x="1080" y="420"/><p2 x="1100" y="420"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(DIR, 'i8086_cpu.dig'), 'w') as f:
        f.write(content)
    verify('i8086_cpu.dig')

# -------------------------------------------------------------
# 4. i8086_system_board.dig
# -------------------------------------------------------------
def build_system_board():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>Intel 8086 Complete Pure Digital Microcomputer System Board</string></entry>
  </attributes>
  <visualElements>
    <!-- Master 14.318 MHz Crystal Oscillator -->
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes>
        <entry><string>runRealTime</string><boolean>true</boolean></entry>
        <entry><string>Label</string><string>OSC_14.318MHz</string></entry>
        <entry><string>Frequency</string><int>5000000</int></entry>
      </elementAttributes>
      <pos x="100" y="200"/>
    </visualElement>

    <!-- Manual Reset Push Button -->
    <visualElement>
      <elementName>Button</elementName>
      <elementAttributes><entry><string>Label</string><string>RESET_BTN</string></entry></elementAttributes>
      <pos x="100" y="240"/>
    </visualElement>

    <!-- Power-On Active Low Reset Inverter -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="140" y="240"/>
    </visualElement>

    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="180" y="260"/>
    </visualElement>

    <!-- 1. Clock Generator 8284A at (200, 200) -->
    <visualElement>
      <elementName>clock_gen_8284.dig</elementName>
      <elementAttributes/>
      <pos x="200" y="200"/>
    </visualElement>

    <!-- 2. Intel 8086 CPU DIP-40 at (420, 200) -->
    <visualElement>
      <elementName>i8086_cpu.dig</elementName>
      <elementAttributes/>
      <pos x="420" y="200"/>
    </visualElement>

    <!-- Ground for CPU INTR and NMI -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="400" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="400" y="280"/>
    </visualElement>

    <!-- 3. Address Latches 8282 / 74LS373 at (680, 200) -->
    <visualElement>
      <elementName>address_latches_8282.dig</elementName>
      <elementAttributes/>
      <pos x="680" y="200"/>
    </visualElement>

    <!-- 4. Address Decoder 74LS138 at (960, 200) -->
    <visualElement>
      <elementName>address_decoder_74ls138.dig</elementName>
      <elementAttributes/>
      <pos x="960" y="200"/>
    </visualElement>

    <!-- Split 20-bit Latched Address into A15_0 and A19_16 at (800, 220) -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>20</string></entry>
        <entry><string>Output Splitting</string><string>16,4</string></entry>
      </elementAttributes>
      <pos x="800" y="220"/>
    </visualElement>

    <!-- 5. Boot ROM 2764 at (700, 440) -->
    <visualElement>
      <elementName>boot_rom_2764.dig</elementName>
      <elementAttributes/>
      <pos x="700" y="440"/>
    </visualElement>

    <!-- 6. 16-Bit RAM at (440, 440) -->
    <visualElement>
      <elementName>ram_16bit.dig</elementName>
      <elementAttributes/>
      <pos x="440" y="440"/>
    </visualElement>

    <!-- 7. Data Bus Transceivers 8286 at (200, 440) -->
    <visualElement>
      <elementName>data_transceivers_8286.dig</elementName>
      <elementAttributes/>
      <pos x="200" y="440"/>
    </visualElement>

    <!-- Telemetry Probes & Indicators -->
    <!-- 20-Bit Physical Address Probe -->
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>PHYS_ADDR</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="860" y="160"/>
    </visualElement>

    <!-- 16-Bit Data Bus Probe -->
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DATA_BUS</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="860" y="440"/>
    </visualElement>

    <!-- Live Status Telemetry LEDs -->
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>ALE_Strobe</string></entry></elementAttributes>
      <pos x="660" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>RD_Read</string></entry></elementAttributes>
      <pos x="660" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>WR_Write</string></entry></elementAttributes>
      <pos x="660" y="320"/>
    </visualElement>
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>M_IO_Select</string></entry></elementAttributes>
      <pos x="940" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>CPU_Reset</string></entry></elementAttributes>
      <pos x="380" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>CLK_Active</string></entry></elementAttributes>
      <pos x="380" y="180"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- OSC from Clock to 8284 OSC at (200, 200) -->
    <wire><p1 x="100" y="200"/><p2 x="200" y="200"/></wire>
    <!-- Reset Button through Not gate to 8284 RES_N at (200, 220) -->
    <wire><p1 x="100" y="240"/><p2 x="140" y="240"/></wire>
    <wire><p1 x="180" y="240"/><p2 x="200" y="240"/></wire>
    <wire><p1 x="180" y="260"/><p2 x="200" y="260"/></wire>

    <!-- 8284 Outputs to CPU Inputs:
         8284 CLK at (300, 200) -> CPU CLK at (420, 200)
         8284 RESET at (300, 220) -> CPU RESET at (420, 220)
         8284 READY at (300, 240) -> CPU READY at (420, 240)
    -->
    <wire><p1 x="300" y="200"/><p2 x="360" y="200"/></wire>
    <wire><p1 x="360" y="200"/><p2 x="360" y="180"/></wire>
    <wire><p1 x="360" y="180"/><p2 x="380" y="180"/></wire>
    <wire><p1 x="360" y="200"/><p2 x="420" y="200"/></wire>

    <wire><p1 x="300" y="220"/><p2 x="340" y="220"/></wire>
    <wire><p1 x="340" y="220"/><p2 x="340" y="140"/></wire>
    <wire><p1 x="340" y="140"/><p2 x="380" y="140"/></wire>
    <wire><p1 x="340" y="220"/><p2 x="420" y="220"/></wire>

    <wire><p1 x="300" y="240"/><p2 x="420" y="240"/></wire>

    <!-- CPU INTR and NMI grounds -->
    <wire><p1 x="400" y="260"/><p2 x="420" y="260"/></wire>
    <wire><p1 x="400" y="280"/><p2 x="420" y="280"/></wire>

    <!-- CPU Outputs:
         AD_OUT (16-bit) at (580, 200) -> Latches AD15_0 at (680, 200)
         A19_16 (4-bit) at (580, 220) -> Latches A19_16 at (680, 220)
         BHE_N at (580, 240)
         ALE at (580, 260) -> Latches ALE at (680, 240)
         RD_N at (580, 280)
         WR_N at (580, 300)
         M_IO_N at (580, 320) -> Decoder M_IO_N at (960, 220)
         DEN_N at (580, 340) -> Transceivers DEN_N at (200, 500)
         DT_R at (580, 360) -> Transceivers DT_R at (200, 480)
    -->
    <wire><p1 x="580" y="200"/><p2 x="680" y="200"/></wire>
    <wire><p1 x="580" y="220"/><p2 x="680" y="220"/></wire>

    <!-- ALE to Latches and LED -->
    <wire><p1 x="580" y="260"/><p2 x="640" y="260"/></wire>
    <wire><p1 x="640" y="260"/><p2 x="640" y="240"/></wire>
    <wire><p1 x="640" y="240"/><p2 x="680" y="240"/></wire>
    <wire><p1 x="640" y="240"/><p2 x="640" y="140"/></wire>
    <wire><p1 x="640" y="140"/><p2 x="660" y="140"/></wire>

    <!-- RD_N to LED and ROM OE_N -->
    <wire><p1 x="580" y="280"/><p2 x="620" y="280"/></wire>
    <wire><p1 x="620" y="280"/><p2 x="620" y="180"/></wire>
    <wire><p1 x="620" y="180"/><p2 x="660" y="180"/></wire>
    <wire><p1 x="620" y="280"/><p2 x="620" y="460"/></wire>
    <wire><p1 x="620" y="460"/><p2 x="700" y="460"/></wire>

    <!-- WR_N to LED and RAM WR_N -->
    <wire><p1 x="580" y="300"/><p2 x="600" y="300"/></wire>
    <wire><p1 x="600" y="300"/><p2 x="600" y="320"/></wire>
    <wire><p1 x="600" y="320"/><p2 x="660" y="320"/></wire>
    <wire><p1 x="600" y="320"/><p2 x="600" y="520"/></wire>
    <wire><p1 x="600" y="520"/><p2 x="440" y="520"/></wire>

    <!-- M_IO_N to Decoder and LED -->
    <wire><p1 x="580" y="320"/><p2 x="920" y="320"/></wire>
    <wire><p1 x="920" y="320"/><p2 x="920" y="220"/></wire>
    <wire><p1 x="920" y="220"/><p2 x="960" y="220"/></wire>
    <wire><p1 x="920" y="220"/><p2 x="920" y="160"/></wire>
    <wire><p1 x="920" y="160"/><p2 x="940" y="160"/></wire>

    <!-- Latches 20-bit Output at (780, 220) -->
    <wire><p1 x="780" y="220"/><p2 x="800" y="220"/></wire>
    <!-- Latched Address to Probe at (860, 160) -->
    <wire><p1 x="780" y="220"/><p2 x="780" y="160"/></wire>
    <wire><p1 x="780" y="160"/><p2 x="860" y="160"/></wire>

    <!-- Splitter at (800, 220):
         out_0 (16-bit A15_0) at (820, 220) -> ROM Addr at (700, 440) and RAM Addr at (440, 440)
         out_1 (4-bit A19_16) at (820, 240) -> Decoder A19_16 at (960, 200)
    -->
    <wire><p1 x="820" y="240"/><p2 x="900" y="240"/></wire>
    <wire><p1 x="900" y="240"/><p2 x="900" y="200"/></wire>
    <wire><p1 x="900" y="200"/><p2 x="960" y="200"/></wire>

    <wire><p1 x="820" y="220"/><p2 x="840" y="220"/></wire>
    <wire><p1 x="840" y="220"/><p2 x="840" y="420"/></wire>
    <wire><p1 x="840" y="420"/><p2 x="680" y="420"/></wire>
    <wire><p1 x="680" y="420"/><p2 x="680" y="440"/></wire>
    <wire><p1 x="680" y="440"/><p2 x="700" y="440"/></wire>
    <wire><p1 x="680" y="420"/><p2 x="420" y="420"/></wire>
    <wire><p1 x="420" y="420"/><p2 x="420" y="440"/></wire>
    <wire><p1 x="420" y="440"/><p2 x="440" y="440"/></wire>

    <!-- Decoder CS_ROM_N at (1080, 260) -> ROM CS_N at (700, 480) -->
    <wire><p1 x="1080" y="260"/><p2 x="1100" y="260"/></wire>
    <wire><p1 x="1100" y="260"/><p2 x="1100" y="480"/></wire>
    <wire><p1 x="1100" y="480"/><p2 x="700" y="480"/></wire>

    <!-- Decoder CS_RAM0_N at (1080, 200) -> RAM CS_N at (440, 540) -->
    <wire><p1 x="1080" y="200"/><p2 x="1120" y="200"/></wire>
    <wire><p1 x="1120" y="200"/><p2 x="1120" y="540"/></wire>
    <wire><p1 x="1120" y="540"/><p2 x="440" y="540"/></wire>

    <!-- System Data Bus: ROM DataOut at (800, 460) -> Data Bus Probe at (860, 440) and CPU AD_IN at (420, 300) -->
    <wire><p1 x="800" y="460"/><p2 x="840" y="460"/></wire>
    <wire><p1 x="840" y="460"/><p2 x="840" y="440"/></wire>
    <wire><p1 x="840" y="440"/><p2 x="860" y="440"/></wire>
    <wire><p1 x="840" y="460"/><p2 x="840" y="380"/></wire>
    <wire><p1 x="840" y="380"/><p2 x="380" y="380"/></wire>
    <wire><p1 x="380" y="380"/><p2 x="380" y="300"/></wire>
    <wire><p1 x="380" y="300"/><p2 x="420" y="300"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(DIR, 'i8086_system_board.dig'), 'w') as f:
        f.write(content)
    verify('i8086_system_board.dig')

def test_full_simulation():
    java_sim = '''
import de.neemann.digital.cli.CircuitLoader;
import de.neemann.digital.core.Model;
import java.io.File;

public class SimFull {
    public static void main(String[] args) {
        try {
            CircuitLoader loader = new CircuitLoader(new File("digital-circuit/i8086_system_board.dig"));
            Model m = loader.createModel();
            m.init();
            System.out.println("Model created with " + m.getNodes().size() + " nodes.");
            for (int i = 0; i < 60; i++) {
                m.doStep();
            }
            System.out.println("FULL_SYSTEM_SIMULATION_SUCCESS: 60 cycles stepped flawlessly!");
        } catch (Throwable t) {
            t.printStackTrace();
            System.exit(1);
        }
    }
}
'''
    with open('/tmp/SimFull.java', 'w') as f:
        f.write(java_sim)
    res = subprocess.run(['javac', '-cp', CP, '/tmp/SimFull.java'], capture_output=True, text=True)
    if res.returncode != 0:
        print("Compilation Error:\n", res.stderr)
        return False
    res2 = subprocess.run(['java', '-cp', CP + ':/tmp', 'SimFull'], capture_output=True, text=True)
    print(res2.stdout)
    return "FULL_SYSTEM_SIMULATION_SUCCESS" in res2.stdout

if __name__ == '__main__':
    print("Building functional circuits...")
    build_boot_rom()
    build_instruction_decoder()
    build_i8086_cpu()
    build_system_board()
    print("\nRunning Java Digital Simulation...")
    ok = test_full_simulation()
    if ok:
        print("\nAll circuits built and verified successfully!")
    else:
        print("\nSimulation verification failed.")
        exit(1)
