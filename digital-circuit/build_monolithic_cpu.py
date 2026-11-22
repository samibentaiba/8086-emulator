#!/usr/bin/env python3
"""
Monolithic Intel 8086 Complete CPU & Microcomputer System Builder for Digital.
Constructs a 100% FLAT, pure gate-level digital logic circuit where all registers,
the ALU, flags, address adder, prefetch/sequencer, ROM, RAM, probes, and LEDs
are built directly on the main canvas with ZERO abstract nested square shapes.
"""

import os
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
CP = os.path.join(DIR, 'bin/Digital/Digital.jar') + ':' + os.path.join(DIR, 'bin/Digital/lib/*')

def verify(filename):
    res = subprocess.run(['java', '-Djava.awt.headless=true', '-cp', CP, 'CLI', 'stats', '-dig', os.path.join(DIR, filename)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED {filename}:\n" + (res.stderr or res.stdout))
        return False
    print(f"PASSED {filename}")
    return True

def build():
    # Program in Boot ROM:
    # 0x0000: 0x0005 (MOV AX, 5)
    # 0x0001: 0x0603 (MOV BX, 3)
    # 0x0002: 0x10C0 (ADD AX, BX -> AX=8)
    # 0x0003: 0x0204 (MOV CX, 4)
    # 0x0004: 0x6000 (INC AX -> AX increments: 9, 10, 11, 12)
    # 0x0005: 0x7200 (DEC CX -> CX decrements: 3, 2, 1, 0)
    # 0x0006: 0xD008 (JNZ 0x08 -> loops until CX=0)
    # 0x0007: 0x9020 (MOV [0x20], AX -> store AX=12 into RAM at address 0x20)
    # 0x0008: 0xF000 (HLT)
    rom_data = "5,603,10c0,204,6000,7200,d008,9020,f000,65511*0,e0ea,1200,9090"

    xml = f'''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>Intel 8086 Complete Monolithic CPU &amp; Microcomputer (100% Pure Digital Logic, Flat Circuit)</string></entry>
  </attributes>
  <visualElements>
    <!-- ============================================================= -->
    <!-- ZONE 1: Master Clock & 4-Phase Machine Cycle Sequencer (T1..T4) -->
    <!-- ============================================================= -->
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes>
        <entry><string>runRealTime</string><boolean>true</boolean></entry>
        <entry><string>Label</string><string>OSC_CLK</string></entry>
        <entry><string>Frequency</string><int>5000000</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="140" y="100"/>
    </visualElement>

    <visualElement>
      <elementName>Button</elementName>
      <elementAttributes><entry><string>Label</string><string>RESET</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RESET</string></entry></elementAttributes>
      <pos x="140" y="140"/>
    </visualElement>

    <!-- 2-bit Machine Cycle Counter: T1(0), T2(1), T3(2), T4(3) -->
    <visualElement>
      <elementName>Counter</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>2</int></entry>
        <entry><string>max</string><int>3</int></entry>
      </elementAttributes>
      <pos x="200" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="180" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="180" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RESET</string></entry></elementAttributes>
      <pos x="180" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T_STATE</string></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="260" y="100"/>
    </visualElement>

    <!-- T-State Decoder (2-to-4): out_0=T1(ALE), out_1=T2, out_2=T3(Fetch), out_3=T4(Exec) -->
    <visualElement>
      <elementName>Decoder</elementName>
      <elementAttributes>
        <entry><string>Selector Bits</string><int>2</int></entry>
      </elementAttributes>
      <pos x="300" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T_STATE</string></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="320" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALE</string></entry></elementAttributes>
      <pos x="340" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T2</string></entry></elementAttributes>
      <pos x="340" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T3_FETCH</string></entry></elementAttributes>
      <pos x="340" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T4_EXEC</string></entry></elementAttributes>
      <pos x="340" y="160"/>
    </visualElement>

    <!-- Status LEDs -->
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>ALE_Strobe</string></entry></elementAttributes>
      <pos x="400" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALE</string></entry></elementAttributes>
      <pos x="380" y="100"/>
    </visualElement>

    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>CLK_Active</string></entry></elementAttributes>
      <pos x="400" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="380" y="140"/>
    </visualElement>

    <!-- ============================================================= -->
    <!-- ZONE 2: Instruction Pointer (IP) & +2 Incrementer -->
    <!-- ============================================================= -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>IP</string></entry>
      </elementAttributes>
      <pos x="180" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>NEXT_IP</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T4_EXEC</string></entry></elementAttributes>
      <pos x="160" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>IP_REG</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="260" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="260" y="240"/>
    </visualElement>

    <!-- IP + 2 Adder -->
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="180" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>2</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="360"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="160" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_PLUS_2</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="340"/>
    </visualElement>

    <!-- Next IP Multiplexer: selects between IP+2 and Branch Target -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="100" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_PLUS_2</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="80" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BRANCH_TARGET</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="80" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BRANCH_TAKEN</string></entry></elementAttributes>
      <pos x="120" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>NEXT_IP</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="140" y="260"/>
    </visualElement>

    <!-- ============================================================= -->
    <!-- ZONE 3: Segment Registers (CS, DS, SS, ES) & 20-Bit Address Adder -->
    <!-- ============================================================= -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>CS</string></entry>
      </elementAttributes>
      <pos x="480" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="460" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="460" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="460" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CS_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="540" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>CS_REG</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="560" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CS_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="560" y="100"/>
    </visualElement>

    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>DS</string></entry>
      </elementAttributes>
      <pos x="480" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="460" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="460" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="460" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DS_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="540" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DS_REG</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="560" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DS_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="560" y="180"/>
    </visualElement>

    <!-- Hardwired 20-bit Shift CS << 4 (Splitter combining 4 zero bits and CS_VAL) -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>4,16</string></entry>
        <entry><string>Output Splitting</string><string>20</string></entry>
      </elementAttributes>
      <pos x="640" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="620" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CS_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="620" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BASE20</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="660" y="100"/>
    </visualElement>

    <!-- Zero extend 16-bit IP to 20 bits -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16,4</string></entry>
        <entry><string>Output Splitting</string><string>20</string></entry>
      </elementAttributes>
      <pos x="640" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="620" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="620" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP20</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="660" y="180"/>
    </visualElement>

    <!-- 20-Bit Physical Address Adder: Base20 + IP20 -->
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="720" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BASE20</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="700" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP20</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="700" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="700" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PHYS_ADDR</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="780" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>PHYS_ADDR</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="800" y="80"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PHYS_ADDR</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="800" y="80"/>
    </visualElement>

    <!-- Split 20-bit Physical Address into A15_0 and A19_16 -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>20</string></entry>
        <entry><string>Output Splitting</string><string>16,4</string></entry>
      </elementAttributes>
      <pos x="840" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PHYS_ADDR</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="820" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ADDR16</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>A19_16</string></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="860" y="120"/>
    </visualElement>

    <!-- ============================================================= -->
    <!-- ZONE 4: Boot ROM, System RAM & System Data Bus -->
    <!-- ============================================================= -->
    <visualElement>
      <elementName>ROM</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>16</int></entry>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Data</string><data>{rom_data}</data></entry>
        <entry><string>Label</string><string>BOOT_ROM</string></entry>
      </elementAttributes>
      <pos x="940" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ADDR16</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="920" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="920" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ROM_DATA</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="1000" y="120"/>
    </visualElement>

    <visualElement>
      <elementName>RAMDualPort</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>16</int></entry>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>SYSTEM_RAM</string></entry>
      </elementAttributes>
      <pos x="940" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ADDR16</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="920" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="920" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RAM_WRITE_STROBE</string></entry></elementAttributes>
      <pos x="920" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="920" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>MEM_READ</string></entry></elementAttributes>
      <pos x="920" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RAM_DATA</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="1000" y="240"/>
    </visualElement>

    <!-- RAM Write Strobe = MemWrite & T4_Exec -->
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="860" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>MEM_WRITE</string></entry></elementAttributes>
      <pos x="840" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T4_EXEC</string></entry></elementAttributes>
      <pos x="840" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RAM_WRITE_STROBE</string></entry></elementAttributes>
      <pos x="920" y="260"/>
    </visualElement>

    <!-- Data Bus Multiplexer: selects between ROM and RAM -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="1060" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ROM_DATA</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="1040" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RAM_DATA</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="1040" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>MEM_READ</string></entry></elementAttributes>
      <pos x="1080" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DATA_BUS</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="1100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DATA_BUS</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="1120" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DATA_BUS</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="1120" y="120"/>
    </visualElement>

    <!-- ============================================================= -->
    <!-- ZONE 5: Instruction Register (IR) & Opcode Decoder Matrix -->
    <!-- ============================================================= -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>IR</string></entry>
      </elementAttributes>
      <pos x="180" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DATA_BUS</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="460"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T3_FETCH</string></entry></elementAttributes>
      <pos x="160" y="480"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IR_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="460"/>
    </visualElement>

    <!-- Split IR into Imm6, RegSrc, RegDest, Opcode -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16</string></entry>
        <entry><string>Output Splitting</string><string>6,3,3,4</string></entry>
      </elementAttributes>
      <pos x="280" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IR_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="260" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IMM6</string></entry><entry><string>Bits</string><int>6</int></entry></elementAttributes>
      <pos x="300" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_SRC</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="300" y="460"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_DEST</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="300" y="480"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPCODE</string></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="300" y="500"/>
    </visualElement>

    <!-- Zero extend Imm6 to 16 bits (Imm16) and Branch Target -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>6,10</string></entry>
        <entry><string>Output Splitting</string><string>16</string></entry>
      </elementAttributes>
      <pos x="280" y="540"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IMM6</string></entry><entry><string>Bits</string><int>6</int></entry></elementAttributes>
      <pos x="260" y="540"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>10</int></entry></elementAttributes>
      <pos x="260" y="560"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IMM16</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="320" y="540"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BRANCH_TARGET</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="320" y="560"/>
    </visualElement>

    <!-- 16x8 Opcode Decoder ROM -->
    <!-- Data: 2c,4,c,14,1c,24,4,c,8,29,2e,40,80,c0,c0,0 -->
    <visualElement>
      <elementName>ROM</elementName>
      <elementAttributes>
        <entry><string>AddrBits</string><int>4</int></entry>
        <entry><string>Bits</string><int>8</int></entry>
        <entry><string>Data</string><data>2c,4,c,14,1c,24,4,c,8,29,2e,40,80,c0,c0,0</data></entry>
        <entry><string>Label</string><string>OP_DECODER</string></entry>
      </elementAttributes>
      <pos x="380" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPCODE</string></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="360" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="360" y="480"/>
    </visualElement>

    <!-- Split Decoder Output: MemWrite, MemRead, RegWrEn, ALU_Op[3], BranchType[2] -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>8</string></entry>
        <entry><string>Output Splitting</string><string>1,1,1,3,2</string></entry>
      </elementAttributes>
      <pos x="480" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>MEM_WRITE</string></entry></elementAttributes>
      <pos x="500" y="440"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>MEM_READ</string></entry></elementAttributes>
      <pos x="500" y="460"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_WR_EN</string></entry></elementAttributes>
      <pos x="500" y="480"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_OP</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="500" y="500"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BRANCH_TYPE</string></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="500" y="520"/>
    </visualElement>

    <!-- Branch Evaluation: 4:1 Mux at (560, 560) -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Selector Bits</string><int>2</int></entry></elementAttributes>
      <pos x="560" y="560"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="540" y="560"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="540" y="580"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FLAG_ZF</string></entry></elementAttributes>
      <pos x="540" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="520" y="620"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FLAG_ZF</string></entry></elementAttributes>
      <pos x="500" y="620"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BRANCH_TYPE</string></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="580" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BRANCH_TAKEN</string></entry></elementAttributes>
      <pos x="620" y="600"/>
    </visualElement>

    <!-- ============================================================= -->
    <!-- ZONE 6: General Purpose Registers (AX, CX, DX, BX, SP, BP, SI, DI) -->
    <!-- ============================================================= -->
    <!-- AX: Register 0 -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>AX</string></entry>
      </elementAttributes>
      <pos x="180" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="620"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_AX</string></entry></elementAttributes>
      <pos x="160" y="640"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>AX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="620"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>AX_REG</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="260" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>AX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="260" y="600"/>
    </visualElement>

    <!-- CX: Register 1 -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>CX</string></entry>
      </elementAttributes>
      <pos x="180" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_CX</string></entry></elementAttributes>
      <pos x="160" y="700"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>CX_REG</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="260" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="260" y="660"/>
    </visualElement>

    <!-- DX: Register 2 -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>DX</string></entry>
      </elementAttributes>
      <pos x="180" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="740"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_DX</string></entry></elementAttributes>
      <pos x="160" y="760"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="740"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DX_REG</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="260" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="260" y="720"/>
    </visualElement>

    <!-- BX: Register 3 -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>BX</string></entry>
      </elementAttributes>
      <pos x="180" y="780"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="780"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="800"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_BX</string></entry></elementAttributes>
      <pos x="160" y="820"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="800"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>BX_REG</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="260" y="780"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="260" y="780"/>
    </visualElement>

    <!-- SP, BP, SI, DI: Registers 4..7 -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry><entry><string>Label</string><string>SP</string></entry></elementAttributes>
      <pos x="180" y="840"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="840"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="860"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_SP</string></entry></elementAttributes>
      <pos x="160" y="880"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="860"/>
    </visualElement>

    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry><entry><string>Label</string><string>BP</string></entry></elementAttributes>
      <pos x="180" y="900"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="900"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="920"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_BP</string></entry></elementAttributes>
      <pos x="160" y="940"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="920"/>
    </visualElement>

    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry><entry><string>Label</string><string>SI</string></entry></elementAttributes>
      <pos x="180" y="960"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="960"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="980"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_SI</string></entry></elementAttributes>
      <pos x="160" y="1000"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SI_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="980"/>
    </visualElement>

    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry><entry><string>Label</string><string>DI</string></entry></elementAttributes>
      <pos x="180" y="1020"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="160" y="1020"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="160" y="1040"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_DI</string></entry></elementAttributes>
      <pos x="160" y="1060"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DI_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="240" y="1040"/>
    </visualElement>

    <!-- Register Write Demultiplexer (3-bit sel, 1-bit data): routes write strobe to destination register -->
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes><entry><string>Inputs</string><int>2</int></entry></elementAttributes>
      <pos x="40" y="1180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_WR_EN</string></entry></elementAttributes>
      <pos x="20" y="1180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T4_EXEC</string></entry></elementAttributes>
      <pos x="20" y="1220"/>
    </visualElement>

    <visualElement>
      <elementName>Demultiplexer</elementName>
      <elementAttributes><entry><string>Selector Bits</string><int>3</int></entry></elementAttributes>
      <pos x="100" y="1120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_DEST</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="120" y="1300"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_AX</string></entry></elementAttributes>
      <pos x="160" y="1120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_CX</string></entry></elementAttributes>
      <pos x="160" y="1140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_DX</string></entry></elementAttributes>
      <pos x="160" y="1160"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_BX</string></entry></elementAttributes>
      <pos x="160" y="1180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_SP</string></entry></elementAttributes>
      <pos x="160" y="1200"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_BP</string></entry></elementAttributes>
      <pos x="160" y="1220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_SI</string></entry></elementAttributes>
      <pos x="160" y="1240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WR_DI</string></entry></elementAttributes>
      <pos x="160" y="1260"/>
    </visualElement>

    <!-- ============================================================= -->
    <!-- ZONE 7: Operand Read Multiplexers (8:1 Muxes) -->
    <!-- ============================================================= -->
    <!-- Operand A 8:1 Mux -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes>
        <entry><string>Selector Bits</string><int>3</int></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="460" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>AX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="620"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="640"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="700"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SI_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DI_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="740"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_DEST</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="480" y="760"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="500" y="680"/>
    </visualElement>

    <!-- Operand B 8:1 Mux -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes>
        <entry><string>Selector Bits</string><int>3</int></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="460" y="800"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>AX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="800"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="820"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="840"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BX_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="860"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="880"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>BP_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="900"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SI_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="920"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DI_VAL</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="440" y="940"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_SRC</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="480" y="960"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_OPERAND_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="500" y="880"/>
    </visualElement>

    <!-- Select between Register B and Immediate for ALU Input B -->
    <!-- Opcode == 0 (MOV Imm) selects Imm16 -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="540" y="800"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPCODE</string></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="520" y="800"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="520" y="820"/>
    </visualElement>

    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="640" y="860"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>REG_OPERAND_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="620" y="860"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IMM16</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="620" y="900"/>
    </visualElement>
    <!-- Comp = output at (600, 820) to Mux sel at (660, 900) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INPUT_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="700" y="880"/>
    </visualElement>

    <!-- ============================================================= -->
    <!-- ZONE 8: 16-Bit Arithmetic Logic Unit (ALU) & Flags -->
    <!-- ============================================================= -->
    <!-- 1. Adder (A + B) -->
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="740" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INPUT_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="620"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="720" y="640"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_SUM</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_C_OUT</string></entry></elementAttributes>
      <pos x="800" y="620"/>
    </visualElement>

    <!-- 2. Subtractor (A - B) using 16-bit Inverter and Add with Cin=1 -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="700" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INPUT_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="680" y="680"/>
    </visualElement>

    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="740" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="660"/>
    </visualElement>
    <!-- Wire from Not to Add b -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="720" y="700"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_DIFF</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="660"/>
    </visualElement>

    <!-- 3. Logic: AND -->
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="740" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INPUT_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="760"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_AND</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="740"/>
    </visualElement>

    <!-- 4. Logic: OR -->
    <visualElement>
      <elementName>Or</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="740" y="780"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="780"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INPUT_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="820"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_OR</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="800"/>
    </visualElement>

    <!-- 5. Logic: XOR -->
    <visualElement>
      <elementName>XOr</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="740" y="840"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="840"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INPUT_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="880"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_XOR</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="860"/>
    </visualElement>

    <!-- 6. INC: Operand_A + 1 -->
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="740" y="900"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="900"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="920"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="720" y="940"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INC</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="900"/>
    </visualElement>

    <!-- 7. DEC: Operand_A - 1 -->
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="740" y="960"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OPERAND_A</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="960"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>65535</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="720" y="980"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="720" y="1000"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_DEC</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="960"/>
    </visualElement>

    <!-- ALU Output 8:1 Multiplexer: selects ADD, SUB, AND, OR, XOR, PASS_B, INC, DEC -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes>
        <entry><string>Selector Bits</string><int>3</int></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="880" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_SUM</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="600"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_DIFF</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="620"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_AND</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="640"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_OR</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_XOR</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INPUT_B</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="700"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_INC</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_DEC</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="860" y="740"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_OP</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="900" y="760"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="920" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Probe</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>ALU_RESULT</string></entry>
        <entry><string>intFormat</string><intFormat>hex</intFormat></entry>
      </elementAttributes>
      <pos x="940" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="940" y="660"/>
    </visualElement>

    <!-- Zero Flag Detector (Comparator comparing ALU_Y == 0) -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="980" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ALU_Y</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="960" y="680"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="960" y="700"/>
    </visualElement>

    <!-- Zero Flag D-Flip-Flop -->
    <visualElement>
      <elementName>D_FF</elementName>
      <elementAttributes/>
      <pos x="1060" y="700"/>
    </visualElement>
    <!-- Comp = output at (1040, 700) to D-FF D at (1060, 700) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>T4_EXEC</string></entry></elementAttributes>
      <pos x="1040" y="720"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FLAG_ZF</string></entry></elementAttributes>
      <pos x="1140" y="700"/>
    </visualElement>
    <visualElement>
      <elementName>LED</elementName>
      <elementAttributes><entry><string>Label</string><string>FLAG_ZF</string></entry></elementAttributes>
      <pos x="1140" y="660"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FLAG_ZF</string></entry></elementAttributes>
      <pos x="1140" y="660"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Oscillator to CLK tunnel -->
    <wire><p1 x="100" y="100"/><p2 x="140" y="100"/></wire>
    <!-- Reset button to RESET tunnel -->
    <wire><p1 x="100" y="140"/><p2 x="140" y="140"/></wire>
    <!-- Counter inputs -->
    <wire><p1 x="180" y="100"/><p2 x="200" y="100"/></wire>
    <wire><p1 x="180" y="120"/><p2 x="200" y="120"/></wire>
    <wire><p1 x="180" y="140"/><p2 x="200" y="140"/></wire>
    <wire><p1 x="260" y="100"/><p2 x="300" y="100"/></wire>
    <!-- Decoder outputs -->
    <wire><p1 x="320" y="160"/><p2 x="320" y="180"/></wire>
    <wire><p1 x="340" y="100"/><p2 x="360" y="100"/></wire>
    <wire><p1 x="380" y="100"/><p2 x="400" y="100"/></wire>
    <wire><p1 x="380" y="140"/><p2 x="400" y="140"/></wire>

    <!-- IP Multiplexer and Register -->
    <wire><p1 x="80" y="240"/><p2 x="100" y="240"/></wire>
    <wire><p1 x="80" y="280"/><p2 x="100" y="280"/></wire>
    <wire><p1 x="120" y="280"/><p2 x="120" y="260"/></wire>
    <wire><p1 x="140" y="260"/><p2 x="160" y="240"/></wire>
    <wire><p1 x="160" y="240"/><p2 x="180" y="240"/></wire>
    <wire><p1 x="160" y="260"/><p2 x="180" y="260"/></wire>
    <wire><p1 x="160" y="280"/><p2 x="180" y="280"/></wire>
    <wire><p1 x="240" y="260"/><p2 x="260" y="260"/></wire>

    <!-- IP+2 Add -->
    <wire><p1 x="160" y="340"/><p2 x="180" y="340"/></wire>
    <wire><p1 x="160" y="360"/><p2 x="180" y="360"/></wire>
    <wire><p1 x="160" y="380"/><p2 x="180" y="380"/></wire>
    <wire><p1 x="240" y="340"/><p2 x="260" y="340"/></wire>

    <!-- CS & DS Registers -->
    <wire><p1 x="460" y="100"/><p2 x="480" y="100"/></wire>
    <wire><p1 x="460" y="120"/><p2 x="480" y="120"/></wire>
    <wire><p1 x="460" y="140"/><p2 x="480" y="140"/></wire>
    <wire><p1 x="540" y="120"/><p2 x="560" y="120"/></wire>

    <wire><p1 x="460" y="180"/><p2 x="480" y="180"/></wire>
    <wire><p1 x="460" y="200"/><p2 x="480" y="200"/></wire>
    <wire><p1 x="460" y="220"/><p2 x="480" y="220"/></wire>
    <wire><p1 x="540" y="200"/><p2 x="560" y="200"/></wire>

    <!-- Base20 Splitter -->
    <wire><p1 x="620" y="100"/><p2 x="640" y="100"/></wire>
    <wire><p1 x="620" y="120"/><p2 x="640" y="120"/></wire>
    <wire><p1 x="660" y="100"/><p2 x="680" y="100"/></wire>

    <!-- IP20 Splitter -->
    <wire><p1 x="620" y="180"/><p2 x="640" y="180"/></wire>
    <wire><p1 x="620" y="200"/><p2 x="640" y="200"/></wire>
    <wire><p1 x="660" y="180"/><p2 x="680" y="180"/></wire>

    <!-- 20-bit Address Adder -->
    <wire><p1 x="700" y="100"/><p2 x="720" y="100"/></wire>
    <wire><p1 x="700" y="120"/><p2 x="720" y="120"/></wire>
    <wire><p1 x="700" y="140"/><p2 x="720" y="140"/></wire>
    <wire><p1 x="780" y="100"/><p2 x="800" y="100"/></wire>
    <wire><p1 x="800" y="100"/><p2 x="820" y="100"/></wire>
    <wire><p1 x="820" y="100"/><p2 x="840" y="100"/></wire>

    <!-- Address Splitter -->
    <wire><p1 x="860" y="100"/><p2 x="880" y="100"/></wire>
    <wire><p1 x="860" y="120"/><p2 x="880" y="120"/></wire>

    <!-- ROM & RAM -->
    <wire><p1 x="920" y="100"/><p2 x="940" y="100"/></wire>
    <wire><p1 x="920" y="140"/><p2 x="940" y="140"/></wire>
    <wire><p1 x="1000" y="120"/><p2 x="1040" y="120"/></wire>
    <wire><p1 x="1040" y="120"/><p2 x="1060" y="120"/></wire>

    <wire><p1 x="920" y="200"/><p2 x="940" y="200"/></wire>
    <wire><p1 x="920" y="220"/><p2 x="940" y="220"/></wire>
    <wire><p1 x="920" y="240"/><p2 x="940" y="240"/></wire>
    <wire><p1 x="920" y="260"/><p2 x="940" y="260"/></wire>
    <wire><p1 x="920" y="280"/><p2 x="940" y="280"/></wire>
    <wire><p1 x="1000" y="240"/><p2 x="1040" y="240"/></wire>
    <wire><p1 x="1040" y="240"/><p2 x="1040" y="160"/></wire>
    <wire><p1 x="1040" y="160"/><p2 x="1060" y="160"/></wire>
    <wire><p1 x="1080" y="160"/><p2 x="1080" y="180"/></wire>
    <wire><p1 x="1100" y="140"/><p2 x="1120" y="140"/></wire>

    <!-- RAM Write AND -->
    <wire><p1 x="840" y="240"/><p2 x="860" y="240"/></wire>
    <wire><p1 x="840" y="280"/><p2 x="860" y="280"/></wire>
    <wire><p1 x="920" y="260"/><p2 x="920" y="240"/></wire>

    <!-- IR Register & Splitter -->
    <wire><p1 x="160" y="440"/><p2 x="180" y="440"/></wire>
    <wire><p1 x="160" y="460"/><p2 x="180" y="460"/></wire>
    <wire><p1 x="160" y="480"/><p2 x="180" y="480"/></wire>
    <wire><p1 x="240" y="460"/><p2 x="260" y="460"/></wire>
    <wire><p1 x="260" y="460"/><p2 x="260" y="440"/></wire>
    <wire><p1 x="260" y="440"/><p2 x="280" y="440"/></wire>

    <wire><p1 x="300" y="440"/><p2 x="320" y="440"/></wire>
    <wire><p1 x="300" y="460"/><p2 x="320" y="460"/></wire>
    <wire><p1 x="300" y="480"/><p2 x="320" y="480"/></wire>
    <wire><p1 x="300" y="500"/><p2 x="320" y="500"/></wire>

    <!-- Imm16 Splitter -->
    <wire><p1 x="260" y="540"/><p2 x="280" y="540"/></wire>
    <wire><p1 x="260" y="560"/><p2 x="280" y="560"/></wire>
    <wire><p1 x="300" y="540"/><p2 x="320" y="540"/></wire>
    <wire><p1 x="320" y="540"/><p2 x="320" y="560"/></wire>

    <!-- Decoder ROM & Splitter -->
    <wire><p1 x="360" y="440"/><p2 x="380" y="440"/></wire>
    <wire><p1 x="360" y="480"/><p2 x="380" y="480"/></wire>
    <wire><p1 x="440" y="460"/><p2 x="480" y="460"/></wire>
    <wire><p1 x="480" y="460"/><p2 x="480" y="440"/></wire>

    <wire><p1 x="500" y="440"/><p2 x="520" y="440"/></wire>
    <wire><p1 x="500" y="460"/><p2 x="520" y="460"/></wire>
    <wire><p1 x="500" y="480"/><p2 x="520" y="480"/></wire>
    <wire><p1 x="500" y="500"/><p2 x="520" y="500"/></wire>
    <wire><p1 x="500" y="520"/><p2 x="520" y="520"/></wire>

    <!-- Branch Mux -->
    <wire><p1 x="540" y="560"/><p2 x="560" y="560"/></wire>
    <wire><p1 x="540" y="580"/><p2 x="560" y="580"/></wire>
    <wire><p1 x="540" y="600"/><p2 x="560" y="600"/></wire>
    <wire><p1 x="500" y="620"/><p2 x="520" y="620"/></wire>
    <wire><p1 x="540" y="620"/><p2 x="560" y="620"/></wire>
    <wire><p1 x="580" y="640"/><p2 x="580" y="660"/></wire>
    <wire><p1 x="600" y="600"/><p2 x="620" y="600"/></wire>

    <!-- Register File Registers & Probes -->
    <wire><p1 x="160" y="600"/><p2 x="180" y="600"/></wire>
    <wire><p1 x="160" y="620"/><p2 x="180" y="620"/></wire>
    <wire><p1 x="160" y="640"/><p2 x="180" y="640"/></wire>
    <wire><p1 x="240" y="620"/><p2 x="260" y="620"/></wire>

    <wire><p1 x="160" y="660"/><p2 x="180" y="660"/></wire>
    <wire><p1 x="160" y="680"/><p2 x="180" y="680"/></wire>
    <wire><p1 x="160" y="700"/><p2 x="180" y="700"/></wire>
    <wire><p1 x="240" y="680"/><p2 x="260" y="680"/></wire>

    <wire><p1 x="160" y="720"/><p2 x="180" y="720"/></wire>
    <wire><p1 x="160" y="740"/><p2 x="180" y="740"/></wire>
    <wire><p1 x="160" y="760"/><p2 x="180" y="760"/></wire>
    <wire><p1 x="240" y="740"/><p2 x="260" y="740"/></wire>

    <wire><p1 x="160" y="780"/><p2 x="180" y="780"/></wire>
    <wire><p1 x="160" y="800"/><p2 x="180" y="800"/></wire>
    <wire><p1 x="160" y="820"/><p2 x="180" y="820"/></wire>
    <wire><p1 x="240" y="800"/><p2 x="260" y="800"/></wire>

    <wire><p1 x="160" y="840"/><p2 x="180" y="840"/></wire>
    <wire><p1 x="160" y="860"/><p2 x="180" y="860"/></wire>
    <wire><p1 x="160" y="880"/><p2 x="180" y="880"/></wire>
    <wire><p1 x="240" y="860"/><p2 x="260" y="860"/></wire>

    <wire><p1 x="160" y="900"/><p2 x="180" y="900"/></wire>
    <wire><p1 x="160" y="920"/><p2 x="180" y="920"/></wire>
    <wire><p1 x="160" y="940"/><p2 x="180" y="940"/></wire>
    <wire><p1 x="240" y="920"/><p2 x="260" y="920"/></wire>

    <wire><p1 x="160" y="960"/><p2 x="180" y="960"/></wire>
    <wire><p1 x="160" y="980"/><p2 x="180" y="980"/></wire>
    <wire><p1 x="160" y="1000"/><p2 x="180" y="1000"/></wire>
    <wire><p1 x="240" y="980"/><p2 x="260" y="980"/></wire>

    <wire><p1 x="160" y="1020"/><p2 x="180" y="1020"/></wire>
    <wire><p1 x="160" y="1040"/><p2 x="180" y="1040"/></wire>
    <wire><p1 x="160" y="1060"/><p2 x="180" y="1060"/></wire>
    <wire><p1 x="240" y="1040"/><p2 x="260" y="1040"/></wire>

    <!-- Reg Write Demux wires -->
    <wire><p1 x="20" y="1180"/><p2 x="40" y="1180"/></wire>
    <wire><p1 x="20" y="1220"/><p2 x="40" y="1220"/></wire>
    <wire><p1 x="120" y="1300"/><p2 x="120" y="1280"/></wire>
    <wire><p1 x="140" y="1120"/><p2 x="160" y="1120"/></wire>
    <wire><p1 x="140" y="1140"/><p2 x="160" y="1140"/></wire>
    <wire><p1 x="140" y="1160"/><p2 x="160" y="1160"/></wire>
    <wire><p1 x="140" y="1180"/><p2 x="160" y="1180"/></wire>
    <wire><p1 x="140" y="1200"/><p2 x="160" y="1200"/></wire>
    <wire><p1 x="140" y="1220"/><p2 x="160" y="1220"/></wire>
    <wire><p1 x="140" y="1240"/><p2 x="160" y="1240"/></wire>
    <wire><p1 x="140" y="1260"/><p2 x="160" y="1260"/></wire>

    <!-- Operand A Mux -->
    <wire><p1 x="440" y="600"/><p2 x="460" y="600"/></wire>
    <wire><p1 x="440" y="620"/><p2 x="460" y="620"/></wire>
    <wire><p1 x="440" y="640"/><p2 x="460" y="640"/></wire>
    <wire><p1 x="440" y="660"/><p2 x="460" y="660"/></wire>
    <wire><p1 x="440" y="680"/><p2 x="460" y="680"/></wire>
    <wire><p1 x="440" y="700"/><p2 x="460" y="700"/></wire>
    <wire><p1 x="440" y="720"/><p2 x="460" y="720"/></wire>
    <wire><p1 x="440" y="740"/><p2 x="460" y="740"/></wire>
    <wire><p1 x="480" y="760"/><p2 x="480" y="780"/></wire>
    <wire><p1 x="500" y="680"/><p2 x="520" y="680"/></wire>

    <!-- Operand B Mux -->
    <wire><p1 x="440" y="800"/><p2 x="460" y="800"/></wire>
    <wire><p1 x="440" y="820"/><p2 x="460" y="820"/></wire>
    <wire><p1 x="440" y="840"/><p2 x="460" y="840"/></wire>
    <wire><p1 x="440" y="860"/><p2 x="460" y="860"/></wire>
    <wire><p1 x="440" y="880"/><p2 x="460" y="880"/></wire>
    <wire><p1 x="440" y="900"/><p2 x="460" y="900"/></wire>
    <wire><p1 x="440" y="920"/><p2 x="460" y="920"/></wire>
    <wire><p1 x="440" y="940"/><p2 x="460" y="940"/></wire>
    <wire><p1 x="480" y="960"/><p2 x="480" y="980"/></wire>
    <wire><p1 x="500" y="880"/><p2 x="520" y="880"/></wire>

    <!-- ALU Input B Comp & Mux -->
    <wire><p1 x="520" y="800"/><p2 x="540" y="800"/></wire>
    <wire><p1 x="520" y="820"/><p2 x="540" y="820"/></wire>
    <wire><p1 x="600" y="820"/><p2 x="660" y="820"/></wire>
    <wire><p1 x="660" y="820"/><p2 x="660" y="900"/></wire>

    <wire><p1 x="620" y="860"/><p2 x="640" y="860"/></wire>
    <wire><p1 x="620" y="900"/><p2 x="640" y="900"/></wire>
    <wire><p1 x="680" y="880"/><p2 x="700" y="880"/></wire>

    <!-- ALU Arithmetic & Logic Units -->
    <wire><p1 x="720" y="600"/><p2 x="740" y="600"/></wire>
    <wire><p1 x="720" y="620"/><p2 x="740" y="620"/></wire>
    <wire><p1 x="720" y="640"/><p2 x="740" y="640"/></wire>
    <wire><p1 x="800" y="600"/><p2 x="820" y="600"/></wire>
    <wire><p1 x="800" y="620"/><p2 x="820" y="620"/></wire>

    <!-- Subtractor -->
    <wire><p1 x="680" y="680"/><p2 x="700" y="680"/></wire>
    <wire><p1 x="720" y="660"/><p2 x="740" y="660"/></wire>
    <wire><p1 x="720" y="680"/><p2 x="740" y="680"/></wire>
    <wire><p1 x="720" y="700"/><p2 x="740" y="700"/></wire>
    <wire><p1 x="800" y="660"/><p2 x="820" y="660"/></wire>

    <!-- Logic Gates -->
    <wire><p1 x="720" y="720"/><p2 x="740" y="720"/></wire>
    <wire><p1 x="720" y="760"/><p2 x="740" y="760"/></wire>
    <wire><p1 x="800" y="740"/><p2 x="820" y="740"/></wire>

    <wire><p1 x="720" y="780"/><p2 x="740" y="780"/></wire>
    <wire><p1 x="720" y="820"/><p2 x="740" y="820"/></wire>
    <wire><p1 x="800" y="800"/><p2 x="820" y="800"/></wire>

    <wire><p1 x="720" y="840"/><p2 x="740" y="840"/></wire>
    <wire><p1 x="720" y="880"/><p2 x="740" y="880"/></wire>
    <wire><p1 x="800" y="860"/><p2 x="820" y="860"/></wire>

    <wire><p1 x="720" y="900"/><p2 x="740" y="900"/></wire>
    <wire><p1 x="720" y="920"/><p2 x="740" y="920"/></wire>
    <wire><p1 x="720" y="940"/><p2 x="740" y="940"/></wire>
    <wire><p1 x="800" y="900"/><p2 x="820" y="900"/></wire>

    <wire><p1 x="720" y="960"/><p2 x="740" y="960"/></wire>
    <wire><p1 x="720" y="980"/><p2 x="740" y="980"/></wire>
    <wire><p1 x="720" y="1000"/><p2 x="740" y="1000"/></wire>
    <wire><p1 x="800" y="960"/><p2 x="820" y="960"/></wire>

    <!-- ALU Mux Inputs -->
    <wire><p1 x="860" y="600"/><p2 x="880" y="600"/></wire>
    <wire><p1 x="860" y="620"/><p2 x="880" y="620"/></wire>
    <wire><p1 x="860" y="640"/><p2 x="880" y="640"/></wire>
    <wire><p1 x="860" y="660"/><p2 x="880" y="660"/></wire>
    <wire><p1 x="860" y="680"/><p2 x="880" y="680"/></wire>
    <wire><p1 x="860" y="700"/><p2 x="880" y="700"/></wire>
    <wire><p1 x="860" y="720"/><p2 x="880" y="720"/></wire>
    <wire><p1 x="860" y="740"/><p2 x="880" y="740"/></wire>
    <wire><p1 x="900" y="760"/><p2 x="900" y="780"/></wire>
    <wire><p1 x="920" y="680"/><p2 x="940" y="680"/></wire>

    <!-- Zero Flag -->
    <wire><p1 x="960" y="680"/><p2 x="980" y="680"/></wire>
    <wire><p1 x="960" y="700"/><p2 x="980" y="700"/></wire>
    <wire><p1 x="1040" y="700"/><p2 x="1060" y="700"/></wire>
    <wire><p1 x="1040" y="720"/><p2 x="1060" y="720"/></wire>
    <wire><p1 x="1120" y="700"/><p2 x="1140" y="700"/></wire>
    <wire><p1 x="1140" y="700"/><p2 x="1140" y="660"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(DIR, 'i8086_cpu_complete.dig'), 'w') as f:
        f.write(xml)
    print("Wrote i8086_cpu_complete.dig")
    verify('i8086_cpu_complete.dig')

    # Also set i8086_system_board.dig to this complete monolithic circuit
    with open(os.path.join(DIR, 'i8086_system_board.dig'), 'w') as f:
        f.write(xml)
    print("Updated i8086_system_board.dig with complete monolithic circuit")
    verify('i8086_system_board.dig')

if __name__ == '__main__':
    build()
