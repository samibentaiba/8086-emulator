#!/usr/bin/env python3
"""
8086 Digital Circuit Suite Builder - Phase 2
Generates circuits 7 to 17 for HNeemann's Digital simulator.
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
# 7. flags_register.dig
# -------------------------------------------------------------
def build_flags_register():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>8086 16-Bit Status and Control Flags Register (CF, PF, AF, ZF, SF, TF, IF, DF, OF)</string></entry>
    <entry><string>Width</string><int>6</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>CF_in</string></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>PF_in</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>AF_in</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>ZF_in</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>SF_in</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>OF_in</string></entry></elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>FlagWr</string></entry></elementAttributes>
      <pos x="100" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes><entry><string>Label</string><string>Clock</string></entry></elementAttributes>
      <pos x="100" y="380"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>FlagsWord</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="800" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CF</string></entry></elementAttributes>
      <pos x="800" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>PF</string></entry></elementAttributes>
      <pos x="800" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>AF</string></entry></elementAttributes>
      <pos x="800" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>ZF</string></entry></elementAttributes>
      <pos x="800" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>SF</string></entry></elementAttributes>
      <pos x="800" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>OF</string></entry></elementAttributes>
      <pos x="800" y="340"/>
    </visualElement>

    <!-- Input Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CF_in_net</string></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PF_in_net</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>AF_in_net</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ZF_in_net</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SF_in_net</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OF_in_net</string></entry></elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FlagWr_net</string></entry></elementAttributes>
      <pos x="100" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="100" y="380"/>
    </visualElement>
'''
    flags = [("CF", 100), ("PF", 180), ("AF", 260), ("ZF", 340), ("SF", 420), ("OF", 500)]
    wires = []

    for name, fy in flags:
        content += f'''
    <!-- Flag {name} Register -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_in_net</string></entry></elementAttributes>
      <pos x="200" y="{fy}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="200" y="{fy + 20}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FlagWr_net</string></entry></elementAttributes>
      <pos x="200" y="{fy + 40}"/>
    </visualElement>
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>1</int></entry>
        <entry><string>Label</string><string>{name}</string></entry>
      </elementAttributes>
      <pos x="220" y="{fy}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_out</string></entry></elementAttributes>
      <pos x="300" y="{fy + 20}"/>
    </visualElement>
'''
        wires.append(f'<wire><p1 x="200" y="{fy}"/><p2 x="220" y="{fy}"/></wire>')
        wires.append(f'<wire><p1 x="200" y="{fy + 20}"/><p2 x="220" y="{fy + 20}"/></wire>')
        wires.append(f'<wire><p1 x="200" y="{fy + 40}"/><p2 x="220" y="{fy + 40}"/></wire>')
        wires.append(f'<wire><p1 x="280" y="{fy + 20}"/><p2 x="300" y="{fy + 20}"/></wire>')

    # Standard 8086 16-bit Flags Word Combiner:
    # bit 0: CF, bit 1: 1, bit 2: PF, bit 3: 0, bit 4: AF, bit 5: 0, bit 6: ZF, bit 7: SF
    # bit 8: 0 (TF), bit 9: 1 (IF), bit 10: 0 (DF), bit 11: OF, bits 12..15: 1111 (0xF)
    content += '''
    <!-- Assemble 8086 FlagsWord -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CF_out</string></entry></elementAttributes>
      <pos x="440" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="440" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PF_out</string></entry></elementAttributes>
      <pos x="440" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="440" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>AF_out</string></entry></elementAttributes>
      <pos x="440" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="440" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ZF_out</string></entry></elementAttributes>
      <pos x="440" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SF_out</string></entry></elementAttributes>
      <pos x="440" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="440" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="440" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="440" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OF_out</string></entry></elementAttributes>
      <pos x="440" y="320"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>15</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="440" y="340"/>
    </visualElement>

    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>1,1,1,1,1,1,1,1,1,1,1,1,4</string></entry>
        <entry><string>Output Splitting</string><string>16</string></entry>
      </elementAttributes>
      <pos x="460" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FlagsWord_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="500" y="100"/>
    </visualElement>
'''
    for i in range(13):
        wires.append(f'<wire><p1 x="440" y="{100 + i*20}"/><p2 x="460" y="{100 + i*20}"/></wire>')
    wires.append('<wire><p1 x="480" y="100"/><p2 x="500" y="100"/></wire>')

    # Connect to outputs
    content += '''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>FlagsWord_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="780" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CF_out</string></entry></elementAttributes>
      <pos x="780" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PF_out</string></entry></elementAttributes>
      <pos x="780" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>AF_out</string></entry></elementAttributes>
      <pos x="780" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ZF_out</string></entry></elementAttributes>
      <pos x="780" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SF_out</string></entry></elementAttributes>
      <pos x="780" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OF_out</string></entry></elementAttributes>
      <pos x="780" y="340"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Clock CF_in PF_in AF_in ZF_in SF_in OF_in FlagWr CF PF AF ZF SF OF FlagsWord
# Initial write: Set ZF=1, PF=1
C     0     1     0     1     0     0     1      0  1  0  1  0  0  0xF246
# Next write: Set CF=1, SF=1, OF=1, clear ZF
C     1     0     0     0     1     1     1      1  0  0  0  1  1  0xFA83
# FlagWr=0: hold values
C     0     0     0     0     0     0     0      1  0  0  0  1  1  0xFA83
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="600" y="440"/>
    </visualElement>
  </visualElements>
'''
    wires.append('<wire><p1 x="780" y="100"/><p2 x="800" y="100"/></wire>')
    wires.append('<wire><p1 x="780" y="140"/><p2 x="800" y="140"/></wire>')
    wires.append('<wire><p1 x="780" y="180"/><p2 x="800" y="180"/></wire>')
    wires.append('<wire><p1 x="780" y="220"/><p2 x="800" y="220"/></wire>')
    wires.append('<wire><p1 x="780" y="260"/><p2 x="800" y="260"/></wire>')
    wires.append('<wire><p1 x="780" y="300"/><p2 x="800" y="300"/></wire>')
    wires.append('<wire><p1 x="780" y="340"/><p2 x="800" y="340"/></wire>')

    content += '  <wires>\n'
    for w in wires:
        content += f'    {w}\n'
    content += '  </wires>\n</circuit>\n'

    with open(os.path.join(OUT_DIR, 'flags_register.dig'), 'w') as f:
        f.write(content)
    print("Generated flags_register.dig")

# -------------------------------------------------------------
# 8. queue_6byte.dig
# -------------------------------------------------------------
def build_queue_6byte():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>8086 6-Byte Instruction Prefetch FIFO Queue</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>ByteIn</string></entry>
        <entry><string>Bits</string><int>8</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>Push</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>Pop</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>Flush</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes><entry><string>Label</string><string>Clock</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Opcode</string></entry>
        <entry><string>Bits</string><int>8</int></entry>
      </elementAttributes>
      <pos x="800" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>Empty</string></entry></elementAttributes>
      <pos x="800" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>Full</string></entry></elementAttributes>
      <pos x="800" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Count</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="800" y="220"/>
    </visualElement>

    <!-- Input Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ByteIn_bus</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Push_in</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Pop_in</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Flush_in</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>

    <!-- Up/Down Counter for Count (3 bits: 0 to 6) -->
    <!-- Add Count + 1 on Push, Count - 1 on Pop -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Count_val</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="200" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="200" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="220" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="200" y="140"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Count_val</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="200" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="200" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Sub</elementName>
      <elementAttributes><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="220" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="200" y="220"/>
    </visualElement>

    <!-- Next Count MUX:
         if Flush then 0
         else if Push & !Pop then Count + 1
         else if Pop & !Push then Count - 1
         else Count -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Count_val</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="320" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="340" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Push_in</string></entry></elementAttributes>
      <pos x="360" y="140"/>
    </visualElement>

    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="420" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Pop_in</string></entry></elementAttributes>
      <pos x="440" y="160"/>
    </visualElement>

    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="480" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="500" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Flush_in</string></entry></elementAttributes>
      <pos x="520" y="180"/>
    </visualElement>

    <!-- Count enable: Push | Pop | Flush -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Push_in</string></entry></elementAttributes>
      <pos x="420" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Pop_in</string></entry></elementAttributes>
      <pos x="420" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Flush_in</string></entry></elementAttributes>
      <pos x="420" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Or</elementName>
      <elementAttributes><entry><string>Inputs</string><int>3</int></entry></elementAttributes>
      <pos x="440" y="240"/>
    </visualElement>

    <!-- Count Register -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>3</int></entry>
        <entry><string>Label</string><string>QueueCount</string></entry>
      </elementAttributes>
      <pos x="580" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="560" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Count_val</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="660" y="180"/>
    </visualElement>

    <!-- Empty flag: Count == 0 -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Count_val</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="660" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="680" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="660" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Empty_net</string></entry></elementAttributes>
      <pos x="760" y="260"/>
    </visualElement>

    <!-- Full flag: Count == 6 -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Count_val</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="660" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="680" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>6</int></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="660" y="320"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Full_net</string></entry></elementAttributes>
      <pos x="760" y="320"/>
    </visualElement>

    <!-- Q0 Register (Head / Opcode) -->
    <!-- When Push: if Count==0 then Q0 loads ByteIn -->
    <!-- When Pop: Q0 loads Q1 -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ByteIn_bus</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="200" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Q1_val</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="200" y="420"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="220" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Pop_in</string></entry></elementAttributes>
      <pos x="240" y="420"/>
    </visualElement>

    <!-- Q0 Enable: (Push & Empty) | Pop | Flush -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Push_in</string></entry></elementAttributes>
      <pos x="200" y="480"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Empty_net</string></entry></elementAttributes>
      <pos x="200" y="520"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="220" y="480"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Pop_in</string></entry></elementAttributes>
      <pos x="300" y="520"/>
    </visualElement>
    <visualElement>
      <elementName>Or</elementName>
      <elementAttributes/>
      <pos x="320" y="500"/>
    </visualElement>

    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>8</int></entry>
        <entry><string>Label</string><string>Q0</string></entry>
      </elementAttributes>
      <pos x="420" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="400" y="420"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Q0_val</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="500" y="420"/>
    </visualElement>

    <!-- Q1 Register -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>ByteIn_bus</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="400" y="500"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="400" y="520"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Push_in</string></entry></elementAttributes>
      <pos x="400" y="540"/>
    </visualElement>
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>8</int></entry>
        <entry><string>Label</string><string>Q1</string></entry>
      </elementAttributes>
      <pos x="420" y="500"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Q1_val</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="500" y="520"/>
    </visualElement>

    <!-- Connect to Outputs -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Q0_val</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="780" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Empty_net</string></entry></elementAttributes>
      <pos x="780" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Full_net</string></entry></elementAttributes>
      <pos x="780" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Count_val</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="780" y="220"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Clock Flush Push Pop ByteIn Opcode Empty Full Count
# Step 1: Initial flush -> Empty=1, Count=0
C     1     0    0   0x00   0x00   1     0    0
# Step 2: Push opcode 0x90 (NOP) -> Count=1, Empty=0, Opcode=0x90
C     0     1    0   0x90   0x90   0     0    1
# Step 3: Push opcode 0xB8 (MOV AX) -> Count=2
C     0     1    0   0xB8   0x90   0     0    2
# Step 4: Pop first instruction (0x90) -> Opcode becomes 0xB8, Count=1
C     0     0    1   0x00   0xB8   0     0    1
# Step 5: Flush
C     1     0    0   0x00   0x00   1     0    0
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="600" y="600"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Adder / Subtractor wires -->
    <wire><p1 x="200" y="100"/><p2 x="220" y="100"/></wire>
    <wire><p1 x="200" y="120"/><p2 x="220" y="120"/></wire>
    <wire><p1 x="200" y="140"/><p2 x="220" y="140"/></wire>
    <wire><p1 x="200" y="180"/><p2 x="220" y="180"/></wire>
    <wire><p1 x="200" y="200"/><p2 x="220" y="200"/></wire>
    <wire><p1 x="200" y="220"/><p2 x="220" y="220"/></wire>
    <!-- Next Count Muxes -->
    <wire><p1 x="280" y="100"/><p2 x="300" y="100"/></wire>
    <wire><p1 x="300" y="100"/><p2 x="300" y="140"/></wire>
    <wire><p1 x="300" y="140"/><p2 x="340" y="140"/></wire>
    <wire><p1 x="320" y="100"/><p2 x="340" y="100"/></wire>
    <wire><p1 x="380" y="120"/><p2 x="420" y="120"/></wire>
    <wire><p1 x="280" y="180"/><p2 x="400" y="180"/></wire>
    <wire><p1 x="400" y="180"/><p2 x="400" y="160"/></wire>
    <wire><p1 x="400" y="160"/><p2 x="420" y="160"/></wire>
    <wire><p1 x="460" y="140"/><p2 x="500" y="140"/></wire>
    <wire><p1 x="480" y="160"/><p2 x="500" y="160"/></wire>
    <wire><p1 x="540" y="160"/><p2 x="580" y="160"/></wire>
    <!-- OR gate inputs -->
    <wire><p1 x="420" y="240"/><p2 x="440" y="240"/></wire>
    <wire><p1 x="420" y="260"/><p2 x="440" y="260"/></wire>
    <wire><p1 x="420" y="280"/><p2 x="440" y="280"/></wire>
    <!-- OR to Reg en at (580, 200) -->
    <wire><p1 x="500" y="260"/><p2 x="560" y="260"/></wire>
    <wire><p1 x="560" y="260"/><p2 x="560" y="200"/></wire>
    <wire><p1 x="560" y="200"/><p2 x="580" y="200"/></wire>
    <!-- Reg Clock -->
    <wire><p1 x="560" y="180"/><p2 x="580" y="180"/></wire>
    <wire><p1 x="640" y="180"/><p2 x="660" y="180"/></wire>
    <!-- Comparators -->
    <wire><p1 x="660" y="240"/><p2 x="680" y="240"/></wire>
    <wire><p1 x="660" y="260"/><p2 x="680" y="260"/></wire>
    <wire><p1 x="740" y="260"/><p2 x="760" y="260"/></wire>
    <wire><p1 x="660" y="300"/><p2 x="680" y="300"/></wire>
    <wire><p1 x="660" y="320"/><p2 x="680" y="320"/></wire>
    <wire><p1 x="740" y="320"/><p2 x="760" y="320"/></wire>
    <!-- Q0 logic -->
    <wire><p1 x="200" y="380"/><p2 x="220" y="380"/></wire>
    <wire><p1 x="200" y="420"/><p2 x="220" y="420"/></wire>
    <wire><p1 x="260" y="400"/><p2 x="420" y="400"/></wire>
    <wire><p1 x="200" y="480"/><p2 x="220" y="480"/></wire>
    <wire><p1 x="200" y="520"/><p2 x="220" y="520"/></wire>
    <wire><p1 x="280" y="500"/><p2 x="320" y="500"/></wire>
    <wire><p1 x="300" y="520"/><p2 x="300" y="540"/></wire>
    <wire><p1 x="300" y="540"/><p2 x="320" y="540"/></wire>
    <wire><p1 x="380" y="520"/><p2 x="400" y="520"/></wire>
    <wire><p1 x="400" y="520"/><p2 x="400" y="440"/></wire>
    <wire><p1 x="400" y="440"/><p2 x="420" y="440"/></wire>
    <wire><p1 x="400" y="420"/><p2 x="420" y="420"/></wire>
    <wire><p1 x="480" y="420"/><p2 x="500" y="420"/></wire>
    <!-- Q1 logic -->
    <wire><p1 x="400" y="500"/><p2 x="420" y="500"/></wire>
    <wire><p1 x="400" y="520"/><p2 x="420" y="520"/></wire>
    <wire><p1 x="400" y="540"/><p2 x="420" y="540"/></wire>
    <wire><p1 x="480" y="520"/><p2 x="500" y="520"/></wire>
    <!-- Outputs -->
    <wire><p1 x="780" y="100"/><p2 x="800" y="100"/></wire>
    <wire><p1 x="780" y="140"/><p2 x="800" y="140"/></wire>
    <wire><p1 x="780" y="180"/><p2 x="800" y="180"/></wire>
    <wire><p1 x="780" y="220"/><p2 x="800" y="220"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'queue_6byte.dig'), 'w') as f:
        f.write(content)
    print("Generated queue_6byte.dig")

# -------------------------------------------------------------
# 9. clock_gen_8284.dig
# -------------------------------------------------------------
def build_clock_gen_8284():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>Intel 8284A Clock Generator &amp; Driver (Divide-by-3 33% Duty Cycle CLK, RESET &amp; READY Synchronizers)</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>OSC</string></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>RES_N</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>RDY_IN</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CLK</string></entry></elementAttributes>
      <pos x="700" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>RESET</string></entry></elementAttributes>
      <pos x="700" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>READY</string></entry></elementAttributes>
      <pos x="700" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>PCLK</string></entry></elementAttributes>
      <pos x="700" y="220"/>
    </visualElement>

    <!-- Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OSC_in</string></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RES_N_in</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RDY_in_net</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>

    <!-- Divide-by-3 Counter: states 0, 1, 2
         CLK is HIGH during state 0, LOW during states 1 and 2 (33.3% duty cycle) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OSC_in</string></entry></elementAttributes>
      <pos x="180" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Counter</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>2</int></entry>
        <entry><string>max</string><int>2</int></entry>
      </elementAttributes>
      <pos x="200" y="100"/>
    </visualElement>
    <!-- Counter en (x+200, y+120) tied to 1 -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="180" y="120"/>
    </visualElement>
    <!-- Counter clr (x+200, y+140) tied to 0 -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="180" y="140"/>
    </visualElement>

    <!-- State comparator: CLK = (Count == 0) -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="300" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="280" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK_net</string></entry></elementAttributes>
      <pos x="380" y="120"/>
    </visualElement>

    <!-- RESET Synchronizer: Inverts RES_N and synchronizes with CLK falling edge -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RES_N_in</string></entry></elementAttributes>
      <pos x="180" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="200" y="240"/>
    </visualElement>
    <!-- D-FF for RESET sync -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OSC_in</string></entry></elementAttributes>
      <pos x="240" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>D_FF</elementName>
      <elementAttributes/>
      <pos x="260" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RESET_net</string></entry></elementAttributes>
      <pos x="340" y="240"/>
    </visualElement>

    <!-- READY Synchronizer: D-FF on CLK -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RDY_in_net</string></entry></elementAttributes>
      <pos x="180" y="320"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK_net</string></entry></elementAttributes>
      <pos x="180" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>D_FF</elementName>
      <elementAttributes/>
      <pos x="200" y="320"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>READY_net</string></entry></elementAttributes>
      <pos x="280" y="320"/>
    </visualElement>

    <!-- PCLK Divider: /2 on CLK -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK_net</string></entry></elementAttributes>
      <pos x="180" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>T_FF</elementName>
      <elementAttributes/>
      <pos x="200" y="400"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry></elementAttributes>
      <pos x="180" y="420"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PCLK_net</string></entry></elementAttributes>
      <pos x="280" y="400"/>
    </visualElement>

    <!-- Connect Outputs -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK_net</string></entry></elementAttributes>
      <pos x="680" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RESET_net</string></entry></elementAttributes>
      <pos x="680" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>READY_net</string></entry></elementAttributes>
      <pos x="680" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>PCLK_net</string></entry></elementAttributes>
      <pos x="680" y="220"/>
    </visualElement>

    <!-- Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
OSC RES_N RDY_IN CLK RESET READY
# Power on: RES_N = 0 (reset active)
C   0     1      1   1     1
C   0     1      0   1     1
C   0     1      0   1     1
# Normal running: RES_N = 1 (reset cleared)
C   1     1      1   0     1
C   1     1      0   0     1
C   1     1      0   0     1
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="500" y="340"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Counter wires -->
    <wire><p1 x="180" y="100"/><p2 x="200" y="100"/></wire>
    <wire><p1 x="180" y="120"/><p2 x="200" y="120"/></wire>
    <wire><p1 x="180" y="140"/><p2 x="200" y="140"/></wire>
    <wire><p1 x="260" y="100"/><p2 x="300" y="100"/></wire>
    <wire><p1 x="280" y="120"/><p2 x="300" y="120"/></wire>
    <wire><p1 x="360" y="120"/><p2 x="380" y="120"/></wire>
    <!-- RESET sync -->
    <wire><p1 x="180" y="240"/><p2 x="200" y="240"/></wire>
    <wire><p1 x="240" y="240"/><p2 x="260" y="240"/></wire>
    <wire><p1 x="240" y="260"/><p2 x="260" y="260"/></wire>
    <wire><p1 x="320" y="240"/><p2 x="340" y="240"/></wire>
    <!-- READY sync -->
    <wire><p1 x="180" y="320"/><p2 x="200" y="320"/></wire>
    <wire><p1 x="180" y="340"/><p2 x="200" y="340"/></wire>
    <wire><p1 x="260" y="320"/><p2 x="280" y="320"/></wire>
    <!-- PCLK divider -->
    <wire><p1 x="180" y="400"/><p2 x="200" y="400"/></wire>
    <wire><p1 x="180" y="420"/><p2 x="200" y="420"/></wire>
    <wire><p1 x="260" y="400"/><p2 x="280" y="400"/></wire>
    <!-- Outputs -->
    <wire><p1 x="680" y="100"/><p2 x="700" y="100"/></wire>
    <wire><p1 x="680" y="140"/><p2 x="700" y="140"/></wire>
    <wire><p1 x="680" y="180"/><p2 x="700" y="180"/></wire>
    <wire><p1 x="680" y="220"/><p2 x="700" y="220"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'clock_gen_8284.dig'), 'w') as f:
        f.write(content)
    print("Generated clock_gen_8284.dig")

# -------------------------------------------------------------
# 10. address_latches_8282.dig
# -------------------------------------------------------------
def build_address_latches_8282():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>3x Intel 8282 / 74LS373 Octal Transparent Latches Demultiplexing A19..A0 on ALE Strobe</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>AD15_0</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>A19_16</string></entry>
        <entry><string>Bits</string><int>4</int></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>ALE</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>A19_0</string></entry>
        <entry><string>Bits</string><int>20</int></entry>
      </elementAttributes>
      <pos x="600" y="100"/>
    </visualElement>

    <!-- Merge AD15_0 and A19_16 into 20-bit raw address -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16,4</string></entry>
        <entry><string>Output Splitting</string><string>20</string></entry>
      </elementAttributes>
      <pos x="200" y="100"/>
    </visualElement>

    <!-- 20-Bit D-Latch Register enabled by ALE -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>20</int></entry>
        <entry><string>Label</string><string>8282_Latches</string></entry>
      </elementAttributes>
      <pos x="300" y="100"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
ALE AD15_0 A19_16 A19_0
# Pulse ALE high: latch address 0x12340
1   0x2340 1      0x12340
# ALE drops low: address 0x12340 remains latched even when AD bus changes to data!
0   0xFFFF 0      0x12340
0   0x0000 0      0x12340
# New bus cycle: ALE pulses high, latches 0xF0100
1   0x0100 0xF    0xF0100
0   0xAAAA 0      0xF0100
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="300" y="240"/>
    </visualElement>
  </visualElements>
  <wires>
    <wire><p1 x="100" y="100"/><p2 x="200" y="100"/></wire>
    <wire><p1 x="100" y="140"/><p2 x="160" y="140"/></wire>
    <wire><p1 x="160" y="140"/><p2 x="160" y="120"/></wire>
    <wire><p1 x="160" y="120"/><p2 x="200" y="120"/></wire>
    <!-- Splitter output to Register D -->
    <wire><p1 x="220" y="100"/><p2 x="300" y="100"/></wire>
    <!-- ALE to Register clock and en -->
    <wire><p1 x="100" y="180"/><p2 x="260" y="180"/></wire>
    <wire><p1 x="260" y="180"/><p2 x="260" y="120"/></wire>
    <wire><p1 x="260" y="120"/><p2 x="300" y="120"/></wire> # Clock
    <wire><p1 x="260" y="140"/><p2 x="300" y="140"/></wire> # en
    <wire><p1 x="260" y="140"/><p2 x="260" y="180"/></wire>
    <!-- Register Q to Out -->
    <wire><p1 x="360" y="120"/><p2 x="480" y="120"/></wire>
    <wire><p1 x="480" y="120"/><p2 x="480" y="100"/></wire>
    <wire><p1 x="480" y="100"/><p2 x="600" y="100"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'address_latches_8282.dig'), 'w') as f:
        f.write(content)
    print("Generated address_latches_8282.dig")

# -------------------------------------------------------------
# 11. data_transceivers_8286.dig
# -------------------------------------------------------------
def build_data_transceivers_8286():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>2x Intel 8286 / 74LS245 Octal Bidirectional Bus Transceivers</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>CPU_IN</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SYS_IN</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>DT_R</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>DEN_N</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>CPU_OUT</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="600" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SYS_OUT</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="600" y="140"/>
    </visualElement>

    <!-- Transmit: CPU -> SYS when DT_R=1 and DEN_N=0 -->
    <!-- Receive: SYS -> CPU when DT_R=0 and DEN_N=0 -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="160" y="220"/>
    </visualElement>

    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="240" y="180"/>
    </visualElement>
    <!-- en_tx = DT_R & ~DEN_N -->

    <!-- en_rx = ~DT_R & ~DEN_N -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="160" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="240" y="260"/>
    </visualElement>

    <!-- SYS_OUT Mux / Driver: CPU_IN if en_tx else 0 -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="360" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="380" y="120"/>
    </visualElement>

    <!-- CPU_OUT Mux / Driver: SYS_IN if en_rx else 0 -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="360" y="80"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="380" y="80"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
CPU_IN SYS_IN DT_R DEN_N CPU_OUT SYS_OUT
# Transmit: CPU -> SYS (DT_R=1, DEN_N=0)
0x1234 0x0000 1    0     0x0000  0x1234
# Receive: SYS -> CPU (DT_R=0, DEN_N=0)
0x0000 0xABCD 0    0     0xABCD  0x0000
# Disabled (DEN_N=1): High-Z / Inactive
0x1234 0xABCD 1    1     0x0000  0x0000
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="400" y="320"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- DEN_N inverter -->
    <wire><p1 x="100" y="220"/><p2 x="160" y="220"/></wire>
    <wire><p1 x="200" y="220"/><p2 x="220" y="220"/></wire>
    <wire><p1 x="220" y="220"/><p2 x="240" y="220"/></wire>
    <wire><p1 x="220" y="220"/><p2 x="220" y="300"/></wire>
    <wire><p1 x="220" y="300"/><p2 x="240" y="300"/></wire>

    <!-- DT_R line -->
    <wire><p1 x="100" y="180"/><p2 x="140" y="180"/></wire>
    <wire><p1 x="140" y="180"/><p2 x="160" y="180"/></wire>
    <wire><p1 x="140" y="180"/><p2 x="240" y="180"/></wire>
    <wire><p1 x="200" y="180"/><p2 x="220" y="180"/></wire>
    <wire><p1 x="220" y="180"/><p2 x="220" y="260"/></wire>
    <wire><p1 x="220" y="260"/><p2 x="240" y="260"/></wire>

    <!-- AND outputs to Mux sel lines -->
    <!-- en_tx at (300, 200) to SYS Mux at (400, 160) -->
    <wire><p1 x="300" y="200"/><p2 x="400" y="200"/></wire>
    <wire><p1 x="400" y="200"/><p2 x="400" y="160"/></wire>

    <!-- en_rx at (300, 280) to CPU Mux at (400, 120) -->
    <wire><p1 x="300" y="280"/><p2 x="360" y="280"/></wire>
    <wire><p1 x="360" y="280"/><p2 x="360" y="140"/></wire>
    <wire><p1 x="360" y="140"/><p2 x="400" y="140"/></wire>
    <wire><p1 x="400" y="140"/><p2 x="400" y="120"/></wire>

    <!-- CPU_IN to SYS Mux in_1 -->
    <wire><p1 x="100" y="100"/><p2 x="340" y="100"/></wire>
    <wire><p1 x="340" y="100"/><p2 x="340" y="160"/></wire>
    <wire><p1 x="340" y="160"/><p2 x="380" y="160"/></wire>

    <!-- SYS_IN to CPU Mux in_1 -->
    <wire><p1 x="100" y="140"/><p2 x="320" y="140"/></wire>
    <wire><p1 x="320" y="140"/><p2 x="320" y="120"/></wire>
    <wire><p1 x="320" y="120"/><p2 x="380" y="120"/></wire>

    <!-- Const 0 to in_0 of both Muxes -->
    <wire><p1 x="360" y="80"/><p2 x="380" y="80"/></wire>
    <wire><p1 x="360" y="120"/><p2 x="380" y="120"/></wire>

    <!-- Outputs -->
    <wire><p1 x="420" y="100"/><p2 x="600" y="100"/></wire>
    <wire><p1 x="420" y="140"/><p2 x="600" y="140"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'data_transceivers_8286.dig'), 'w') as f:
        f.write(content)
    print("Generated data_transceivers_8286.dig")

# -------------------------------------------------------------
# 12. address_decoder_74ls138.dig
# -------------------------------------------------------------
def build_address_decoder_74ls138():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>74LS138 Address &amp; Bus Cycle Chip Select Decoder</string></entry>
    <entry><string>Width</string><int>6</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>A19_16</string></entry>
        <entry><string>Bits</string><int>4</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes><entry><string>Label</string><string>M_IO_N</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_RAM0_N</string></entry></elementAttributes>
      <pos x="700" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_RAM1_N</string></entry></elementAttributes>
      <pos x="700" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_VIDEO_N</string></entry></elementAttributes>
      <pos x="700" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_ROM_N</string></entry></elementAttributes>
      <pos x="700" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_IO_TRAFFIC_N</string></entry></elementAttributes>
      <pos x="700" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes><entry><string>Label</string><string>CS_IO_STEPPER_N</string></entry></elementAttributes>
      <pos x="700" y="300"/>
    </visualElement>

    <!-- Memory Decoder: Enabled when M_IO_N = 1 -->
    <!-- Split A19_16 (4 bits: 0..15)
         0x0: 0x00000 - 0x0FFFF -> Low RAM (CS_RAM0_N)
         0x1..0x7: 0x10000 - 0x7FFFF -> RAM1 (CS_RAM1_N)
         0xB: 0xB8000 -> Video Text Buffer (CS_VIDEO_N)
         0xF: 0xF0000 - 0xFFFFF -> Boot ROM (CS_ROM_N) -->

    <!-- Detect 0x0 (RAM0) -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="200" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="180" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="300" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="400" y="100"/>
    </visualElement>

    <!-- Detect 0xF (Boot ROM) -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="200" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>15</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="180" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="300" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="400" y="220"/>
    </visualElement>

    <!-- Detect 0xB (Video) -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="200" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>11</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="180" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="300" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="400" y="160"/>
    </visualElement>

    <!-- Detect RAM1: A19_16 in 1..7 (A19_16 < 8 and A19_16 > 0) -->
    <visualElement>
      <elementName>Comparator</elementName>
      <elementAttributes><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="200" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>8</int></entry><entry><string>Bits</string><int>4</int></entry></elementAttributes>
      <pos x="180" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="300" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="400" y="280"/>
    </visualElement>

    <!-- I/O Ports: Enabled when M_IO_N = 0 -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="160" y="380"/>
    </visualElement>
    <!-- Port 4: Traffic lights -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="400" y="360"/>
    </visualElement>
    <!-- Port 7: Stepper motor -->
    <visualElement>
      <elementName>Not</elementName>
      <elementAttributes/>
      <pos x="400" y="420"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
A19_16 M_IO_N CS_RAM0_N CS_ROM_N CS_VIDEO_N
# Access Low RAM 0x00000: CS_RAM0_N = 0
0      1      0         1        1
# Access Boot ROM 0xF0000: CS_ROM_N = 0
0xF    1      1         0        1
# Access Video Buffer 0xB8000: CS_VIDEO_N = 0
0xB    1      1         1        0
# Access Extended RAM 0x20000: CS_RAM0_N=1, CS_ROM_N=1
2      1      1         1        1
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="500" y="480"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- A19_16 distribution -->
    <wire><p1 x="100" y="100"/><p2 x="160" y="100"/></wire>
    <wire><p1 x="160" y="100"/><p2 x="200" y="100"/></wire>
    <wire><p1 x="160" y="100"/><p2 x="160" y="160"/></wire>
    <wire><p1 x="160" y="160"/><p2 x="200" y="160"/></wire>
    <wire><p1 x="160" y="160"/><p2 x="160" y="220"/></wire>
    <wire><p1 x="160" y="220"/><p2 x="200" y="220"/></wire>
    <wire><p1 x="160" y="220"/><p2 x="160" y="280"/></wire>
    <wire><p1 x="160" y="280"/><p2 x="200" y="280"/></wire>

    <!-- Constants -->
    <wire><p1 x="180" y="120"/><p2 x="200" y="120"/></wire>
    <wire><p1 x="180" y="180"/><p2 x="200" y="180"/></wire>
    <wire><p1 x="180" y="240"/><p2 x="200" y="240"/></wire>
    <wire><p1 x="180" y="300"/><p2 x="200" y="300"/></wire>

    <!-- M_IO_N distribution -->
    <wire><p1 x="100" y="140"/><p2 x="140" y="140"/></wire>
    <wire><p1 x="140" y="140"/><p2 x="300" y="140"/></wire>
    <wire><p1 x="140" y="140"/><p2 x="140" y="200"/></wire>
    <wire><p1 x="140" y="200"/><p2 x="300" y="200"/></wire>
    <wire><p1 x="140" y="200"/><p2 x="140" y="260"/></wire>
    <wire><p1 x="140" y="260"/><p2 x="300" y="260"/></wire>
    <wire><p1 x="140" y="260"/><p2 x="140" y="380"/></wire>
    <wire><p1 x="140" y="380"/><p2 x="160" y="380"/></wire>

    <!-- Comparator outputs to AND gates -->
    <wire><p1 x="260" y="120"/><p2 x="280" y="120"/></wire>
    <wire><p1 x="280" y="120"/><p2 x="280" y="100"/></wire>
    <wire><p1 x="280" y="100"/><p2 x="300" y="100"/></wire>

    <wire><p1 x="260" y="180"/><p2 x="280" y="180"/></wire>
    <wire><p1 x="280" y="180"/><p2 x="280" y="160"/></wire>
    <wire><p1 x="280" y="160"/><p2 x="300" y="160"/></wire>

    <wire><p1 x="260" y="240"/><p2 x="280" y="240"/></wire>
    <wire><p1 x="280" y="240"/><p2 x="280" y="220"/></wire>
    <wire><p1 x="280" y="220"/><p2 x="300" y="220"/></wire>

    <!-- Inverters to Outputs -->
    <wire><p1 x="360" y="120"/><p2 x="380" y="120"/></wire>
    <wire><p1 x="380" y="120"/><p2 x="380" y="100"/></wire>
    <wire><p1 x="380" y="100"/><p2 x="400" y="100"/></wire>
    <wire><p1 x="440" y="100"/><p2 x="700" y="100"/></wire>

    <wire><p1 x="360" y="180"/><p2 x="380" y="180"/></wire>
    <wire><p1 x="380" y="180"/><p2 x="380" y="160"/></wire>
    <wire><p1 x="380" y="160"/><p2 x="400" y="160"/></wire>
    <wire><p1 x="440" y="160"/><p2 x="560" y="160"/></wire>
    <wire><p1 x="560" y="160"/><p2 x="560" y="180"/></wire>
    <wire><p1 x="560" y="180"/><p2 x="700" y="180"/></wire>

    <wire><p1 x="360" y="240"/><p2 x="380" y="240"/></wire>
    <wire><p1 x="380" y="240"/><p2 x="380" y="220"/></wire>
    <wire><p1 x="380" y="220"/><p2 x="400" y="220"/></wire>
    <wire><p1 x="440" y="220"/><p2 x="700" y="220"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'address_decoder_74ls138.dig'), 'w') as f:
        f.write(content)
    print("Generated address_decoder_74ls138.dig")

# Run generation
build_flags_register()
check_circuit('flags_register.dig')
test_circuit('flags_register.dig')

build_queue_6byte()
check_circuit('queue_6byte.dig')
test_circuit('queue_6byte.dig')

build_clock_gen_8284()
check_circuit('clock_gen_8284.dig')
test_circuit('clock_gen_8284.dig')

build_address_latches_8282()
check_circuit('address_latches_8282.dig')
test_circuit('address_latches_8282.dig')

build_data_transceivers_8286()
check_circuit('data_transceivers_8286.dig')
test_circuit('data_transceivers_8286.dig')

build_address_decoder_74ls138()
check_circuit('address_decoder_74ls138.dig')
test_circuit('address_decoder_74ls138.dig')
