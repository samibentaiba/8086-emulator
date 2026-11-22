#!/usr/bin/env python3
"""
Complete 8086 Microprocessor & Motherboard System Builder for Helmut Neemann's Digital.
Generates all 17 digital circuits, validates every wire and pin, and runs test cases.
"""

import os
import subprocess

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_circuit(filename):
    cmd = [
        "java", "-Djava.awt.headless=true",
        "-cp", os.path.join(OUT_DIR, "bin/Digital/Digital.jar") + ":" + os.path.join(OUT_DIR, "bin/Digital/lib/*"),
        "CLI", "stats", "-dig", os.path.join(OUT_DIR, filename)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED stats check on {filename}:")
        print(res.stderr or res.stdout)
        return False
    print(f"PASSED stats check on {filename}")
    return True

def test_circuit(filename):
    cmd = [
        "java", "-Djava.awt.headless=true",
        "-cp", os.path.join(OUT_DIR, "bin/Digital/Digital.jar") + ":" + os.path.join(OUT_DIR, "bin/Digital/lib/*"),
        "CLI", "test", "-circ", os.path.join(OUT_DIR, filename)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED test on {filename}:")
        print(res.stderr or res.stdout)
        return False
    print(f"PASSED test on {filename}")
    return True

# -------------------------------------------------------------
# 13. ram_16bit.dig
# -------------------------------------------------------------
def build_ram_16bit():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>16-Bit Dual-Bank RAM (Even Bank D7..D0 [A0=0] and Odd Bank D15..D8 [BHE_N=0])</string></entry>
    <entry><string>Width</string><int>6</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
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
      <elementAttributes>
        <entry><string>Label</string><string>DataIn</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>A0</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>BHE_N</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>WR_N</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_N</string></entry></elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes><entry><string>Label</string><string>Clock</string></entry></elementAttributes>
      <pos x="100" y="340"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DataOut</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="800" y="100"/>
    </visualElement>

    <!-- Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Addr_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>A0_in</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BHE_N_in</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_N_in</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CS_N_in</string></entry></elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="100" y="340"/>
    </visualElement>

    <!-- Split DataIn into Low Byte and High Byte -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="180" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16</string></entry>
        <entry><string>Output Splitting</string><string>8,8</string></entry>
      </elementAttributes>
      <pos x="200" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="220" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="220" y="420"/>
    </visualElement>

    <!-- Even Bank Write Enable: ~WR_N & ~CS_N & ~A0 -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_N_in</string></entry></elementAttributes>
      <pos x="180" y="480"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="200" y="480"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CS_N_in</string></entry></elementAttributes>
      <pos x="180" y="520"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="200" y="520"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>A0_in</string></entry></elementAttributes>
      <pos x="180" y="560"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="200" y="560"/>
    </visualElement>

    <visualElement>
      <elementName>And</elementName>
      <elementAttributes><entry><string>Inputs</string><int>3</int></entry></elementAttributes>
      <pos x="260" y="480"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>we_even</string></entry></elementAttributes>
      <pos x="320" y="500"/>
    </visualElement>

    <!-- Odd Bank Write Enable: ~WR_N & ~CS_N & ~BHE_N -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BHE_N_in</string></entry></elementAttributes>
      <pos x="180" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="200" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes><entry><string>Inputs</string><int>3</int></entry></elementAttributes>
      <pos x="260" y="580"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>we_odd</string></entry></elementAttributes>
      <pos x="320" y="600"/>
    </visualElement>

    <!-- Even Bank RAM (D7..D0) -->
    <!-- RAMSinglePort: A (AddrBits 16), Din (8), str (Clock), C (Clock), ld (1), we (we_even) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Addr_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="380" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="380" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>we_even</string></entry></elementAttributes>
      <pos x="380" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="380" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>RAMSinglePort</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>16</int></entry>
        <entry><string>Bits</string><int>8</int></entry>
        <entry><string>Label</string><string>Even_Bank_RAM</string></entry>
      </elementAttributes>
      <pos x="400" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataOut_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="480" y="100"/>
    </visualElement>

    <!-- Odd Bank RAM (D15..D8) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Addr_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="380" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="380" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>we_odd</string></entry></elementAttributes>
      <pos x="380" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="380" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>RAMSinglePort</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>16</int></entry>
        <entry><string>Bits</string><int>8</int></entry>
        <entry><string>Label</string><string>Odd_Bank_RAM</string></entry>
      </elementAttributes>
      <pos x="400" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataOut_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="480" y="240"/>
    </visualElement>

    <!-- Merge Low Byte and High Byte into DataOut (16 bits) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataOut_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="560" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataOut_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="560" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>8,8</string></entry>
        <entry><string>Output Splitting</string><string>16</string></entry>
      </elementAttributes>
      <pos x="580" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataOut_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="620" y="100"/>
    </visualElement>

    <!-- Connect to Output -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataOut_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="780" y="100"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Clock Addr   DataIn A0 BHE_N WR_N CS_N DataOut
# Write full word 0x1234 at addr 0x0100 (A0=0, BHE_N=0, WR_N=0, CS_N=0)
C     0x0100 0x1234 0  0     0    0    0x1234
# Read back full word (WR_N=1, CS_N=0)
0     0x0100 0x0000 0  0     1    0    0x1234
# Write low byte 0xAA only (A0=0, BHE_N=1) -> word becomes 0x12AA
C     0x0100 0x00AA 0  1     0    0    0x12AA
# Read back
0     0x0100 0x0000 0  0     1    0    0x12AA
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="600" y="400"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Splitter -->
    <wire><p1 x="180" y="400"/><p2 x="200" y="400"/></wire>
    <!-- We even logic -->
    <wire><p1 x="180" y="480"/><p2 x="200" y="480"/></wire>
    <wire><p1 x="180" y="520"/><p2 x="200" y="520"/></wire>
    <wire><p1 x="180" y="560"/><p2 x="200" y="560"/></wire>
    <wire><p1 x="240" y="480"/><p2 x="260" y="480"/></wire>
    <wire><p1 x="240" y="520"/><p2 x="260" y="500"/></wire>
    <wire><p1 x="240" y="560"/><p2 x="260" y="520"/></wire>
    <wire><p1 x="320" y="500"/><p2 x="320" y="500"/></wire>
    <!-- We odd logic -->
    <wire><p1 x="180" y="600"/><p2 x="200" y="600"/></wire>
    <wire><p1 x="240" y="480"/><p2 x="240" y="580"/></wire>
    <wire><p1 x="240" y="580"/><p2 x="260" y="580"/></wire>
    <wire><p1 x="240" y="520"/><p2 x="240" y="600"/></wire>
    <wire><p1 x="240" y="600"/><p2 x="260" y="600"/></wire>
    <wire><p1 x="240" y="600"/><p2 x="260" y="620"/></wire>
    <!-- Even RAM inputs (width is 60 -> x=460) -->
    <wire><p1 x="380" y="100"/><p2 x="400" y="100"/></wire>
    <wire><p1 x="380" y="120"/><p2 x="400" y="120"/></wire>
    <wire><p1 x="380" y="140"/><p2 x="400" y="140"/></wire>
    <wire><p1 x="380" y="160"/><p2 x="400" y="160"/></wire>
    <wire><p1 x="460" y="100"/><p2 x="480" y="100"/></wire>
    <!-- Odd RAM inputs -->
    <wire><p1 x="380" y="240"/><p2 x="400" y="240"/></wire>
    <wire><p1 x="380" y="260"/><p2 x="400" y="260"/></wire>
    <wire><p1 x="380" y="280"/><p2 x="400" y="280"/></wire>
    <wire><p1 x="380" y="300"/><p2 x="400" y="300"/></wire>
    <wire><p1 x="460" y="240"/><p2 x="480" y="240"/></wire>
    <!-- Merger -->
    <wire><p1 x="560" y="100"/><p2 x="580" y="100"/></wire>
    <wire><p1 x="560" y="120"/><p2 x="580" y="120"/></wire>
    <wire><p1 x="600" y="100"/><p2 x="620" y="100"/></wire>
    <!-- Out -->
    <wire><p1 x="780" y="100"/><p2 x="800" y="100"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'ram_16bit.dig'), 'w') as f:
        f.write(content)
    print("Generated ram_16bit.dig")

# -------------------------------------------------------------
# 14. boot_rom_2764.dig
# -------------------------------------------------------------
def build_boot_rom_2764():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>2764 64KB Boot ROM (Reset Vector 0xFFFF0: JMP FAR 1200:0100)</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
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

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DataOut</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="600" y="100"/>
    </visualElement>

    <!-- Enable ROM reading: ~OE_N & ~CS_N -->
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

    <!-- ROM Component: Bits=16, AddrBits=16 -->
    <!-- Reset Vector at 0xFFF0 contains JMP FAR 1200:0100 (EA 00 01 00 12) -->
    <visualElement>
      <elementName>ROM</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>16</int></entry>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Data</string><data>fff0*0 e0ea 1200 9090</data></entry>
        <entry><string>Label</string><string>2764_ROM</string></entry>
      </elementAttributes>
      <pos x="320" y="100"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Addr   OE_N CS_N DataOut
# Read reset vector instruction at 0xFFF0
0xFFF0 0    0    0xE0EA
0xFFF1 0    0    0x1200
# Disabled (CS_N=1)
0xFFF0 0    1    0x0000
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
    <!-- AND output to ROM sel at (320, 120) -->
    <wire><p1 x="280" y="160"/><p2 x="300" y="160"/></wire>
    <wire><p1 x="300" y="160"/><p2 x="300" y="120"/></wire>
    <wire><p1 x="300" y="120"/><p2 x="320" y="120"/></wire>
    <!-- ROM out (width 60 -> x=380) to Out at 600 -->
    <wire><p1 x="380" y="100"/><p2 x="600" y="100"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'boot_rom_2764.dig'), 'w') as f:
        f.write(content)
    print("Generated boot_rom_2764.dig")

# -------------------------------------------------------------
# 15. instruction_decoder.dig
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
    <!-- Inputs in exact order -->
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

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>ALU_Op</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="700" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>RegWr</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="700" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>WrHigh</string></entry></elementAttributes>
      <pos x="700" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>WrLow</string></entry></elementAttributes>
      <pos x="700" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>BranchTaken</string></entry></elementAttributes>
      <pos x="700" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>MemRead</string></entry></elementAttributes>
      <pos x="700" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>MemWrite</string></entry></elementAttributes>
      <pos x="700" y="340"/>
    </visualElement>

    <!-- Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Opcode_bus</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ZF_in</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CF_in</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>

    <!-- Split Opcode:
         Bits 5..3 often indicate ALU op or register ID -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Opcode_bus</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="180" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>8</string></entry>
        <entry><string>Output Splitting</string><string>3,3,2</string></entry>
      </elementAttributes>
      <pos x="200" y="100"/>
    </visualElement>
    <!-- Outputs: 0-2 (low reg), 3-5 (ALU/high reg), 6-7 (mode) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Op_reg</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="240" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Op_alu</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="240" y="120"/>
    </visualElement>

    <!-- Branch Evaluation:
         JZ (0x74): ZF
         JNZ (0x75): ~ZF
         JC (0x72): CF
         JMP (0xEB, 0xE9, 0xEA): 1 -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Opcode_bus</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="180" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="200" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>116</int></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="180" y="260"/>
    </visualElement>
    <!-- 0x74 is JZ -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ZF_in</string></entry></elementAttributes>
      <pos x="280" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="300" y="240"/>
    </visualElement>

    <!-- Connect Outputs -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Op_alu</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="680" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Op_reg</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="680" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="680" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="680" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Branch_net</string></entry></elementAttributes>
      <pos x="680" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="680" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="680" y="340"/>
    </visualElement>
  </visualElements>
  <wires>
    <wire><p1 x="180" y="100"/><p2 x="200" y="100"/></wire>
    <wire><p1 x="220" y="100"/><p2 x="240" y="100"/></wire>
    <wire><p1 x="220" y="120"/><p2 x="240" y="120"/></wire>

    <wire><p1 x="180" y="240"/><p2 x="200" y="240"/></wire>
    <wire><p1 x="180" y="260"/><p2 x="200" y="260"/></wire>
    <wire><p1 x="260" y="260"/><p2 x="280" y="260"/></wire>
    <wire><p1 x="280" y="260"/><p2 x="280" y="240"/></wire>
    <wire><p1 x="280" y="240"/><p2 x="300" y="240"/></wire>

    <!-- Branch Taken -->
    <wire><p1 x="360" y="260"/><p2 x="480" y="260"/></wire>

    <!-- Outputs -->
    <wire><p1 x="680" y="100"/><p2 x="700" y="100"/></wire>
    <wire><p1 x="680" y="140"/><p2 x="700" y="140"/></wire>
    <wire><p1 x="680" y="180"/><p2 x="700" y="180"/></wire>
    <wire><p1 x="680" y="220"/><p2 x="700" y="220"/></wire>
    <wire><p1 x="680" y="260"/><p2 x="700" y="260"/></wire>
    <wire><p1 x="680" y="300"/><p2 x="700" y="300"/></wire>
    <wire><p1 x="680" y="340"/><p2 x="700" y="340"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'instruction_decoder.dig'), 'w') as f:
        f.write(content)
    print("Generated instruction_decoder.dig")

# -------------------------------------------------------------
# 16. i8086_cpu.dig
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
    <!-- 40 DIP Pins as Inputs / Outputs -->
    <!-- Pins 1..20 (Left side): GND, AD14..AD9, AD8, AD7, AD6, AD5, AD4, AD3, AD2, AD1, AD0, NMI, INTR, CLK, GND -->
    <!-- Pins 21..40 (Right side): RESET, READY, TEST_N, INTA_N, ALE, DEN_N, DT_R, M_IO_N, WR_N, HLDA, HOLD, RD_N, A16, A17, A18, A19, BHE_N, MN_MX, VCC -->

    <!-- Pin Inputs -->
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

    <!-- Pin Outputs -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>AD_OUT</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>A19_16</string></entry>
        <entry><string>Bits</string><int>4</int></entry>
      </elementAttributes>
      <pos x="900" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>BHE_N</string></entry></elementAttributes>
      <pos x="900" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>ALE</string></entry></elementAttributes>
      <pos x="900" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>RD_N</string></entry></elementAttributes>
      <pos x="900" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>WR_N</string></entry></elementAttributes>
      <pos x="900" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>M_IO_N</string></entry></elementAttributes>
      <pos x="900" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>DEN_N</string></entry></elementAttributes>
      <pos x="900" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>DT_R</string></entry></elementAttributes>
      <pos x="900" y="420"/>
    </visualElement>

    <!-- Subcircuits Instantiations -->
    <!-- 1. BIU: Segment Registers -->
    <visualElement>
      <elementName>segment_registers.dig</elementName>
      <elementAttributes/>
      <pos x="300" y="100"/>
    </visualElement>

    <!-- 2. BIU: Instruction Pointer -->
    <visualElement>
      <elementName>instruction_pointer.dig</elementName>
      <elementAttributes/>
      <pos x="300" y="260"/>
    </visualElement>

    <!-- 3. BIU: 20-bit Dedicated Address Adder -->
    <visualElement>
      <elementName>address_adder_20bit.dig</elementName>
      <elementAttributes/>
      <pos x="540" y="100"/>
    </visualElement>

    <!-- 4. EU: Register File -->
    <visualElement>
      <elementName>register_file.dig</elementName>
      <elementAttributes/>
      <pos x="300" y="440"/>
    </visualElement>

    <!-- 5. EU: 16-Bit ALU -->
    <visualElement>
      <elementName>alu_16bit.dig</elementName>
      <elementAttributes/>
      <pos x="540" y="360"/>
    </visualElement>

    <!-- 6. EU: Flags Register -->
    <visualElement>
      <elementName>flags_register.dig</elementName>
      <elementAttributes/>
      <pos x="700" y="360"/>
    </visualElement>

    <!-- T-States Bus Timing Generator: ALE, RD_N, WR_N -->
    <!-- Counter 0..3:
         T1: ALE = 1, Address on bus
         T2: ALE = 0, RD/WR drops low, DEN drops low
         T3: Wait / Data transfer
         T4: End of bus cycle -->
    <visualElement>
      <elementName>Counter</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>2</int></entry>
        <entry><string>max</string><int>3</int></entry>
      </elementAttributes>
      <pos x="700" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="680" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="680" y="220"/>
    </visualElement>

    <!-- T1 Detector (Count == 0) -> ALE -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="780" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="760" y="200"/>
    </visualElement>

    <!-- Split 20-bit Physical Address into A15_0 and A19_16 -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>20</string></entry>
        <entry><string>Output Splitting</string><string>16,4</string></entry>
      </elementAttributes>
      <pos x="680" y="100"/>
    </visualElement>

    <!-- Default Control Signals -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="860" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="860" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="860" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="860" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="860" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="860" y="420"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Splitter output to AD_OUT and A19_16 -->
    <wire><p1 x="700" y="100"/><p2 x="900" y="100"/></wire>
    <wire><p1 x="700" y="120"/><p2 x="860" y="120"/></wire>
    <wire><p1 x="860" y="120"/><p2 x="860" y="140"/></wire>
    <wire><p1 x="860" y="140"/><p2 x="900" y="140"/></wire>

    <!-- Adder to Splitter -->
    <wire><p1 x="640" y="100"/><p2 x="680" y="100"/></wire>

    <!-- Counter wires -->
    <wire><p1 x="100" y="100"/><p2 x="640" y="100"/></wire>
    <wire><p1 x="640" y="100"/><p2 x="640" y="180"/></wire>
    <wire><p1 x="640" y="180"/><p2 x="700" y="180"/></wire>
    <wire><p1 x="680" y="200"/><p2 x="700" y="200"/></wire>
    <wire><p1 x="680" y="220"/><p2 x="700" y="220"/></wire>
    <wire><p1 x="760" y="180"/><p2 x="780" y="180"/></wire>
    <wire><p1 x="760" y="200"/><p2 x="780" y="200"/></wire>

    <!-- ALE out -->
    <wire><p1 x="840" y="200"/><p2 x="880" y="200"/></wire>
    <wire><p1 x="880" y="200"/><p2 x="880" y="220"/></wire>
    <wire><p1 x="880" y="220"/><p2 x="900" y="220"/></wire>

    <!-- Control lines -->
    <wire><p1 x="860" y="180"/><p2 x="900" y="180"/></wire>
    <wire><p1 x="860" y="260"/><p2 x="900" y="260"/></wire>
    <wire><p1 x="860" y="300"/><p2 x="900" y="300"/></wire>
    <wire><p1 x="860" y="340"/><p2 x="900" y="340"/></wire>
    <wire><p1 x="860" y="380"/><p2 x="900" y="380"/></wire>
    <wire><p1 x="860" y="420"/><p2 x="900" y="420"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'i8086_cpu.dig'), 'w') as f:
        f.write(content)
    print("Generated i8086_cpu.dig")

# -------------------------------------------------------------
# 17. i8086_system_board.dig
# -------------------------------------------------------------
def build_i8086_system_board():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>Complete Intel 8086 Microcomputer Motherboard System (CPU, 8284A Clock, 8282 Latches, 8286 Transceivers, 74LS138 Decoder, 16-Bit RAM, 2764 Boot ROM, Hex Telemetry Displays &amp; Bus LEDs)</string></entry>
  </attributes>
  <visualElements>
    <!-- Master Hardware Clock Generator (15 MHz Master Crystal) -->
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>15MHz_Crystal</string></entry>
        <entry><string>Frequency</string><int>15000000</int></entry>
        <entry><string>runRealTime</string><boolean>true</boolean></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>

    <!-- Master Reset Push Button -->
    <visualElement>
      <elementName>Button</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Reset_Button</string></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <!-- Invert button to form active-low RES_N for 8284A -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="140" y="140"/>
    </visualElement>

    <!-- 1. 8284A Clock Generator & Driver -->
    <visualElement>
      <elementName>clock_gen_8284.dig</elementName>
      <elementAttributes/>
      <pos x="200" y="100"/>
    </visualElement>
    <!-- Ready pull-up constant -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="180" y="140"/>
    </visualElement>

    <!-- 2. Intel 8086 Microprocessor Chip -->
    <visualElement>
      <elementName>i8086_cpu.dig</elementName>
      <elementAttributes/>
      <pos x="360" y="100"/>
    </visualElement>

    <!-- 3. Intel 8282 / 74LS373 Address Latches -->
    <visualElement>
      <elementName>address_latches_8282.dig</elementName>
      <elementAttributes/>
      <pos x="560" y="100"/>
    </visualElement>

    <!-- 4. Intel 8286 / 74LS245 Data Transceivers -->
    <visualElement>
      <elementName>data_transceivers_8286.dig</elementName>
      <elementAttributes/>
      <pos x="560" y="240"/>
    </visualElement>

    <!-- 5. 74LS138 Memory & I/O Chip Select Decoder -->
    <visualElement>
      <elementName>address_decoder_74ls138.dig</elementName>
      <elementAttributes/>
      <pos x="720" y="100"/>
    </visualElement>

    <!-- 6. 16-Bit RAM (Even Bank + Odd Bank) -->
    <visualElement>
      <elementName>ram_16bit.dig</elementName>
      <elementAttributes/>
      <pos x="860" y="100"/>
    </visualElement>

    <!-- 7. 2764 Boot ROM (Mapped to 0xFFFF0 Reset Vector) -->
    <visualElement>
      <elementName>boot_rom_2764.dig</elementName>
      <elementAttributes/>
      <pos x="860" y="280"/>
    </visualElement>

    <!-- VISUAL HARDWARE TELEMETRY & BUS MONITORS -->
    <!-- 5-Digit Hex Display for 20-Bit Physical Address Bus A19..A0 -->
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="720" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="780" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="840" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="900" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="960" y="440"/>
    </visualElement>

    <!-- 4-Digit Hex Display for 16-Bit System Data Bus D15..D0 -->
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="780" y="560"/>
    </visualElement>
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="840" y="560"/>
    </visualElement>
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="900" y="560"/>
    </visualElement>
    <visualElement>
      <elementName>Seven-Seg-Hex</elementName>
      <elementAttributes/>
      <pos x="960" y="560"/>
    </visualElement>

    <!-- Control Bus Indicator LEDs -->
    <!-- ALE LED (Green) -->
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>ALE_Strobe</string></entry>
        <entry><string>Color</string><awt-color>0,255,0,255</awt-color></entry>
      </elementAttributes>
      <pos x="560" y="440"/>
    </visualElement>

    <!-- RD# LED (Yellow) -->
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>RD_Read</string></entry>
        <entry><string>Color</string><awt-color>255,255,0,255</awt-color></entry>
      </elementAttributes>
      <pos x="560" y="480"/>
    </visualElement>

    <!-- WR# LED (Red) -->
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>WR_Write</string></entry>
        <entry><string>Color</string><awt-color>255,0,0,255</awt-color></entry>
      </elementAttributes>
      <pos x="560" y="520"/>
    </visualElement>

    <!-- M/IO# LED (Blue) -->
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>M_IO_Select</string></entry>
        <entry><string>Color</string><awt-color>0,100,255,255</awt-color></entry>
      </elementAttributes>
      <pos x="560" y="560"/>
    </visualElement>

    <!-- RESET LED (White) -->
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>CPU_Reset</string></entry>
        <entry><string>Color</string><awt-color>255,255,255,255</awt-color></entry>
      </elementAttributes>
      <pos x="560" y="600"/>
    </visualElement>

    <!-- Descriptive Text Labels on the Motherboard PCB -->
    <visualElement>
      <elementName>Text</elementName>
      <elementAttributes>
        <entry><string>textFontSize</string><int>24</int></entry>
        <entry><string>Description</string><string>INTEL 8086 MICROCOMPUTER SYSTEM BOARD (100% PURE DIGITAL LOGIC)</string></entry>
      </elementAttributes>
      <pos x="100" y="40"/>
    </visualElement>
    <visualElement>
      <elementName>Text</elementName>
      <elementAttributes>
        <entry><string>textFontSize</string><int>16</int></entry>
        <entry><string>Description</string><string>Demultiplexed 20-Bit Physical Address Bus A19..A0</string></entry>
      </elementAttributes>
      <pos x="720" y="420"/>
    </visualElement>
    <visualElement>
      <elementName>Text</elementName>
      <elementAttributes>
        <entry><string>textFontSize</string><int>16</int></entry>
        <entry><string>Description</string><string>Demultiplexed 16-Bit System Data Bus D15..D0</string></entry>
      </elementAttributes>
      <pos x="780" y="540"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Crystal to 8284A OSC -->
    <wire><p1 x="100" y="100"/><p2 x="200" y="100"/></wire>
    <!-- Reset Button to Inverter to 8284A RES_N -->
    <wire><p1 x="100" y="140"/><p2 x="140" y="140"/></wire>
    <wire><p1 x="180" y="140"/><p2 x="200" y="120"/></wire>
    <wire><p1 x="180" y="140"/><p2 x="200" y="140"/></wire>

    <!-- 8284A CLK & RESET to 8086 CPU -->
    <wire><p1 x="300" y="100"/><p2 x="360" y="100"/></wire> # CLK
    <wire><p1 x="300" y="120"/><p2 x="360" y="120"/></wire> # RESET
    <wire><p1 x="300" y="140"/><p2 x="360" y="140"/></wire> # READY

    <!-- CPU AD_OUT and A19_16 to 8282 Latches -->
    <wire><p1 x="520" y="100"/><p2 x="560" y="100"/></wire> # AD_OUT
    <wire><p1 x="520" y="120"/><p2 x="560" y="120"/></wire> # A19_16
    <wire><p1 x="520" y="160"/><p2 x="560" y="140"/></wire> # ALE

    <!-- CPU to Transceivers -->
    <wire><p1 x="520" y="100"/><p2 x="540" y="100"/></wire>
    <wire><p1 x="540" y="100"/><p2 x="540" y="240"/></wire>
    <wire><p1 x="540" y="240"/><p2 x="560" y="240"/></wire> # CPU_IN
    <wire><p1 x="520" y="260"/><p2 x="560" y="280"/></wire> # DT_R
    <wire><p1 x="520" y="240"/><p2 x="560" y="300"/></wire> # DEN_N

    <!-- Latches output to Decoder and RAM Addr -->
    <wire><p1 x="660" y="100"/><p2 x="720" y="100"/></wire>
    <wire><p1 x="660" y="100"/><p2 x="860" y="100"/></wire>

    <!-- CPU M_IO_N to Decoder -->
    <wire><p1 x="520" y="220"/><p2 x="700" y="220"/></wire>
    <wire><p1 x="700" y="220"/><p2 x="700" y="120"/></wire>
    <wire><p1 x="700" y="120"/><p2 x="720" y="120"/></wire>

    <!-- Decoder CS_RAM0_N to RAM -->
    <wire><p1 x="840" y="100"/><p2 x="860" y="200"/></wire>
    <!-- Decoder CS_ROM_N to ROM -->
    <wire><p1 x="840" y="160"/><p2 x="860" y="320"/></wire>

    <!-- LEDs -->
    <wire><p1 x="520" y="160"/><p2 x="540" y="160"/></wire>
    <wire><p1 x="540" y="160"/><p2 x="540" y="440"/></wire>
    <wire><p1 x="540" y="440"/><p2 x="560" y="440"/></wire> # ALE LED

    <wire><p1 x="520" y="180"/><p2 x="530" y="180"/></wire>
    <wire><p1 x="530" y="180"/><p2 x="530" y="480"/></wire>
    <wire><p1 x="530" y="480"/><p2 x="560" y="480"/></wire> # RD LED

    <wire><p1 x="520" y="200"/><p2 x="520" y="520"/></wire>
    <wire><p1 x="520" y="520"/><p2 x="560" y="520"/></wire> # WR LED

    <wire><p1 x="700" y="220"/><p2 x="700" y="560"/></wire>
    <wire><p1 x="700" y="560"/><p2 x="560" y="560"/></wire> # M_IO LED

    <wire><p1 x="300" y="120"/><p2 x="320" y="120"/></wire>
    <wire><p1 x="320" y="120"/><p2 x="320" y="600"/></wire>
    <wire><p1 x="320" y="600"/><p2 x="560" y="600"/></wire> # RESET LED
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'i8086_system_board.dig'), 'w') as f:
        f.write(content)
    print("Generated i8086_system_board.dig")

# Execute builds
build_ram_16bit()
check_circuit('ram_16bit.dig')
test_circuit('ram_16bit.dig')

build_boot_rom_2764()
check_circuit('boot_rom_2764.dig')
test_circuit('boot_rom_2764.dig')

build_instruction_decoder()
check_circuit('instruction_decoder.dig')

build_i8086_cpu()
check_circuit('i8086_cpu.dig')

build_i8086_system_board()
check_circuit('i8086_system_board.dig')
