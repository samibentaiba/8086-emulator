#!/usr/bin/env python3
"""
8086 Digital Circuit Suite Builder
Generates 100% pure digital logic circuit files (.dig) for HNeemann's Digital simulator.
Builds the complete Intel 8086 microprocessor + motherboard system from scratch.
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
# 2. register_file.dig
# -------------------------------------------------------------
def build_register_file():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>Dual-Port 16-Bit General Purpose &amp; Pointer Registers (AX, BX, CX, DX, SP, BP, SI, DI) with Byte-Write Masking</string></entry>
    <entry><string>Width</string><int>6</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DataIn</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>RegWr</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>WrHigh</string></entry>
      </elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>WrLow</string></entry>
      </elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SelA</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SelB</string></entry>
        <entry><string>Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Clock</string></entry>
      </elementAttributes>
      <pos x="100" y="340"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>OutA</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>OutB</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>AX</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>CX</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DX</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>BX</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SP</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="340"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>BP</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SI</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="420"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DI</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="900" y="460"/>
    </visualElement>

    <!-- Tunnels for Inputs -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RegWr_bus</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WrHigh_in</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WrLow_in</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SelA_bus</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SelB_bus</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="100" y="340"/>
    </visualElement>

    <!-- Decode 3-bit RegWr into 8 write selects -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RegWr_bus</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="140" y="580"/>
    </visualElement>
    <visualElement>
      <elementName>Decoder</elementName>
      <elementAttributes><entry><string>Selector Bits</string><int>3</int></entry></elementAttributes>
      <pos x="120" y="440"/>
    </visualElement>
'''

    reg_names = ["AX", "CX", "DX", "BX", "SP", "BP", "SI", "DI"]
    wires = []

    # Decoder outputs (8 pins: 160, 440 + i*20)
    for i, name in enumerate(reg_names):
        content += f'''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>sel_wr_{i}</string></entry></elementAttributes>
      <pos x="160" y="{440 + i*20}"/>
    </visualElement>
'''

    # Split DataIn into High and Low bytes
    content += '''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="100" y="640"/>
    </visualElement>
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16</string></entry>
        <entry><string>Output Splitting</string><string>8,8</string></entry>
      </elementAttributes>
      <pos x="120" y="640"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="140" y="640"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="140" y="660"/>
    </visualElement>
'''
    wires.append('<wire><p1 x="100" y="640"/><p2 x="120" y="640"/></wire>')

    # 8 Registers
    base_x = 340
    base_y = 100
    for i, name in enumerate(reg_names):
        ry = base_y + i * 160
        content += f'''
    <!-- Register {name} (ID {i}) -->
    <!-- Write enable high byte: sel_wr_{i} & WrHigh -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>sel_wr_{i}</string></entry></elementAttributes>
      <pos x="{base_x - 80}" y="{ry}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WrHigh_in</string></entry></elementAttributes>
      <pos x="{base_x - 80}" y="{ry + 40}"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="{base_x - 60}" y="{ry}"/>
    </visualElement>
    <!-- Mux for High Byte: current high or DataIn_H -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 20}" y="{ry}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 20}" y="{ry + 40}"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 40}" y="{ry}"/>
    </visualElement>

    <!-- Write enable low byte: sel_wr_{i} & WrLow -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>sel_wr_{i}</string></entry></elementAttributes>
      <pos x="{base_x - 80}" y="{ry + 60}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>WrLow_in</string></entry></elementAttributes>
      <pos x="{base_x - 80}" y="{ry + 100}"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="{base_x - 60}" y="{ry + 60}"/>
    </visualElement>
    <!-- Mux for Low Byte: current low or DataIn_L -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 20}" y="{ry + 60}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 20}" y="{ry + 100}"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 40}" y="{ry + 60}"/>
    </visualElement>

    <!-- Combine next high and low bytes into 16-bit word -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>8,8</string></entry>
        <entry><string>Output Splitting</string><string>16</string></entry>
      </elementAttributes>
      <pos x="{base_x + 100}" y="{ry + 40}"/>
    </visualElement>

    <!-- Overall write enable: wr_h | wr_l -->
    <visualElement>
      <elementName>Or</elementName>
      <elementAttributes/>
      <pos x="{base_x + 40}" y="{ry + 120}"/>
    </visualElement>

    <!-- 16-Bit Register -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>{name}</string></entry>
      </elementAttributes>
      <pos x="{base_x + 140}" y="{ry + 40}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="{base_x + 120}" y="{ry + 60}"/>
    </visualElement>

    <!-- Split Register Q into high and low byte tunnels for next-state feedback -->
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16</string></entry>
        <entry><string>Output Splitting</string><string>8,8</string></entry>
      </elementAttributes>
      <pos x="{base_x + 220}" y="{ry + 60}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_L</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 240}" y="{ry + 60}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_H</string></entry><entry><string>Bits</string><int>8</int></entry></elementAttributes>
      <pos x="{base_x + 240}" y="{ry + 80}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{base_x + 240}" y="{ry + 40}"/>
    </visualElement>
'''
        # Connect AND gates inputs
        wires.append(f'<wire><p1 x="{base_x - 80}" y="{ry}"/><p2 x="{base_x - 60}" y="{ry}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x - 80}" y="{ry + 40}"/><p2 x="{base_x - 60}" y="{ry + 40}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x - 80}" y="{ry + 60}"/><p2 x="{base_x - 60}" y="{ry + 60}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x - 80}" y="{ry + 100}"/><p2 x="{base_x - 60}" y="{ry + 100}"/></wire>')

        # AND high output is at (base_x, ry+20) -> goes to High Mux sel at (base_x + 60, ry + 40)
        wires.append(f'<wire><p1 x="{base_x}" y="{ry + 20}"/><p2 x="{base_x + 10}" y="{ry + 20}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 10}" y="{ry + 20}"/><p2 x="{base_x + 10}" y="{ry + 120}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 10}" y="{ry + 120}"/><p2 x="{base_x + 40}" y="{ry + 120}"/></wire>') # into OR in_0
        wires.append(f'<wire><p1 x="{base_x + 10}" y="{ry + 40}"/><p2 x="{base_x + 60}" y="{ry + 40}"/></wire>') # into High Mux sel

        # AND low output is at (base_x, ry+80) -> goes to Low Mux sel at (base_x + 60, ry + 100)
        wires.append(f'<wire><p1 x="{base_x}" y="{ry + 80}"/><p2 x="{base_x + 16}" y="{ry + 80}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 16}" y="{ry + 80}"/><p2 x="{base_x + 16}" y="{ry + 160}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 16}" y="{ry + 160}"/><p2 x="{base_x + 40}" y="{ry + 160}"/></wire>') # into OR in_1
        wires.append(f'<wire><p1 x="{base_x + 16}" y="{ry + 100}"/><p2 x="{base_x + 60}" y="{ry + 100}"/></wire>') # into Low Mux sel

        # MUX data inputs
        wires.append(f'<wire><p1 x="{base_x + 20}" y="{ry}"/><p2 x="{base_x + 40}" y="{ry}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 20}" y="{ry + 40}"/><p2 x="{base_x + 40}" y="{ry + 40}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 20}" y="{ry + 60}"/><p2 x="{base_x + 40}" y="{ry + 60}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 20}" y="{ry + 100}"/><p2 x="{base_x + 40}" y="{ry + 100}"/></wire>')

        # High byte Mux output at (base_x + 80, ry + 20) -> Splitter in_1 at (base_x + 100, ry + 60)
        wires.append(f'<wire><p1 x="{base_x + 80}" y="{ry + 20}"/><p2 x="{base_x + 90}" y="{ry + 20}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 90}" y="{ry + 20}"/><p2 x="{base_x + 90}" y="{ry + 60}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 90}" y="{ry + 60}"/><p2 x="{base_x + 100}" y="{ry + 60}"/></wire>')

        # Low byte Mux output at (base_x + 80, ry + 80) -> Splitter in_0 at (base_x + 100, ry + 40)
        wires.append(f'<wire><p1 x="{base_x + 80}" y="{ry + 80}"/><p2 x="{base_x + 96}" y="{ry + 80}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 96}" y="{ry + 80}"/><p2 x="{base_x + 96}" y="{ry + 40}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 96}" y="{ry + 40}"/><p2 x="{base_x + 100}" y="{ry + 40}"/></wire>')

        # Splitter output at (base_x + 120, ry + 40) to Register D at (base_x + 140, ry + 40)
        wires.append(f'<wire><p1 x="{base_x + 120}" y="{ry + 40}"/><p2 x="{base_x + 140}" y="{ry + 40}"/></wire>')

        # OR gate output at (base_x + 100, ry + 140) to Register en at (base_x + 140, ry + 80)
        wires.append(f'<wire><p1 x="{base_x + 100}" y="{ry + 140}"/><p2 x="{base_x + 110}" y="{ry + 140}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 110}" y="{ry + 140}"/><p2 x="{base_x + 110}" y="{ry + 80}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 110}" y="{ry + 80}"/><p2 x="{base_x + 140}" y="{ry + 80}"/></wire>')

        # Clock wire
        wires.append(f'<wire><p1 x="{base_x + 120}" y="{ry + 60}"/><p2 x="{base_x + 140}" y="{ry + 60}"/></wire>')

        # Register Q at (base_x + 200, ry + 60)
        wires.append(f'<wire><p1 x="{base_x + 200}" y="{ry + 60}"/><p2 x="{base_x + 220}" y="{ry + 60}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 200}" y="{ry + 60}"/><p2 x="{base_x + 200}" y="{ry + 40}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 200}" y="{ry + 40}"/><p2 x="{base_x + 240}" y="{ry + 40}"/></wire>')

    # Dual-Port Read Multiplexers (8:1 16-bit MUX for Port A and Port B)
    mux_x = 640
    content += f'''
    <!-- Port A 8:1 Multiplexer -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Selector Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="{mux_x}" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SelA_bus</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="{mux_x + 20}" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OutA_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{mux_x + 60}" y="180"/>
    </visualElement>

    <!-- Port B 8:1 Multiplexer -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Selector Bits</string><int>3</int></entry>
      </elementAttributes>
      <pos x="{mux_x}" y="320"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SelB_bus</string></entry><entry><string>Bits</string><int>3</int></entry></elementAttributes>
      <pos x="{mux_x + 20}" y="480"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OutB_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{mux_x + 60}" y="400"/>
    </visualElement>
'''
    wires.append(f'<wire><p1 x="{mux_x + 40}" y="180"/><p2 x="{mux_x + 60}" y="180"/></wire>')
    wires.append(f'<wire><p1 x="{mux_x + 40}" y="400"/><p2 x="{mux_x + 60}" y="400"/></wire>')

    for i, name in enumerate(reg_names):
        content += f'''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{mux_x - 40}" y="{100 + i*20}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{mux_x - 40}" y="{320 + i*20}"/>
    </visualElement>
'''
        wires.append(f'<wire><p1 x="{mux_x - 40}" y="{100 + i*20}"/><p2 x="{mux_x}" y="{100 + i*20}"/></wire>')
        wires.append(f'<wire><p1 x="{mux_x - 40}" y="{320 + i*20}"/><p2 x="{mux_x}" y="{320 + i*20}"/></wire>')

    # Connect to Top Outputs
    content += '''
    <!-- Output Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OutA_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="880" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>OutB_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="880" y="140"/>
    </visualElement>
'''
    wires.append('<wire><p1 x="880" y="100"/><p2 x="900" y="100"/></wire>')
    wires.append('<wire><p1 x="880" y="140"/><p2 x="900" y="140"/></wire>')

    for i, name in enumerate(reg_names):
        content += f'''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{name}_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="880" y="{180 + i*40}"/>
    </visualElement>
'''
        wires.append(f'<wire><p1 x="880" y="{180 + i*40}"/><p2 x="900" y="{180 + i*40}"/></wire>')

    # Verification Testcase
    content += '''
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Clock DataIn RegWr WrHigh WrLow SelA SelB OutA   OutB
# Step 1: Write 0x1234 to AX (RegWr=0)
C     0x1234 0     1      1     0    0    0x1234 0x1234
# Step 2: Write 0x5678 to BX (RegWr=3)
C     0x5678 3     1      1     0    3    0x1234 0x5678
# Step 3: Write low byte 0xAA to AL (RegWr=0, WrHigh=0, WrLow=1, DataIn=0x00AA) -> AX becomes 0x12AA
C     0x00AA 0     0      1     0    3    0x12AA 0x5678
# Step 4: Write high byte 0xBB to AH (RegWr=0, WrHigh=1, WrLow=0, DataIn=0xBB00) -> AX becomes 0xBBAA
C     0xBB00 0     1      0     0    3    0xBBAA 0x5678
# Step 5: Read CX (SelA=1) and DX (SelB=2)
0     0x0000 0     0      0     1    2    0x0000 0x0000
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="700" y="600"/>
    </visualElement>
  </visualElements>
'''
    content += '  <wires>\n'
    for w in wires:
        content += f'    {w}\n'
    content += '  </wires>\n</circuit>\n'

    with open(os.path.join(OUT_DIR, 'register_file.dig'), 'w') as f:
        f.write(content)
    print("Generated register_file.dig")

# -------------------------------------------------------------
# 3. segment_registers.dig
# -------------------------------------------------------------
def build_segment_registers():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>8086 Segment Registers (CS, DS, SS, ES) and 20-Bit Physical Base Address Generator</string></entry>
    <entry><string>Width</string><int>6</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DataIn</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SegSel</string></entry>
        <entry><string>Bits</string><int>2</int></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SegWr</string></entry>
      </elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Clock</string></entry>
      </elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SegOut</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="800" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Base20</string></entry>
        <entry><string>Bits</string><int>20</int></entry>
      </elementAttributes>
      <pos x="800" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>CS</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="800" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>DS</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="800" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>SS</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="800" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>ES</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="800" y="300"/>
    </visualElement>

    <!-- Input Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegSel_bus</string></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegWr_in</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>

    <!-- 2-to-4 Decoder for Segment Selection -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegSel_bus</string></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="140" y="380"/>
    </visualElement>
    <visualElement>
      <elementName>Decoder</elementName>
      <elementAttributes><entry><string>Selector Bits</string><int>2</int></entry></elementAttributes>
      <pos x="120" y="320"/>
    </visualElement>
'''
    seg_names = ["CS", "DS", "SS", "ES"]
    wires = []

    for i, sname in enumerate(seg_names):
        content += f'''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>sel_{i}</string></entry></elementAttributes>
      <pos x="160" y="{320 + i*20}"/>
    </visualElement>
'''

    # 4 Registers: CS, DS, SS, ES
    base_x = 300
    base_y = 100
    for i, sname in enumerate(seg_names):
        sy = base_y + i * 100
        content += f'''
    <!-- {sname} Register -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>sel_{i}</string></entry></elementAttributes>
      <pos x="{base_x}" y="{sy}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegWr_in</string></entry></elementAttributes>
      <pos x="{base_x}" y="{sy + 40}"/>
    </visualElement>
    <visualElement>
      <elementName>And</elementName>
      <elementAttributes/>
      <pos x="{base_x + 20}" y="{sy}"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>DataIn_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{base_x + 100}" y="{sy}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="{base_x + 100}" y="{sy + 20}"/>
    </visualElement>
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>{sname}</string></entry>
      </elementAttributes>
      <pos x="{base_x + 120}" y="{sy}"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{sname}_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{base_x + 200}" y="{sy + 20}"/>
    </visualElement>
'''
        wires.append(f'<wire><p1 x="{base_x}" y="{sy}"/><p2 x="{base_x + 20}" y="{sy}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x}" y="{sy + 40}"/><p2 x="{base_x + 20}" y="{sy + 40}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 80}" y="{sy + 20}"/><p2 x="{base_x + 120}" y="{sy + 40}"/></wire>') # into reg en
        wires.append(f'<wire><p1 x="{base_x + 100}" y="{sy}"/><p2 x="{base_x + 120}" y="{sy}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 100}" y="{sy + 20}"/><p2 x="{base_x + 120}" y="{sy + 20}"/></wire>')
        wires.append(f'<wire><p1 x="{base_x + 180}" y="{sy + 20}"/><p2 x="{base_x + 200}" y="{sy + 20}"/></wire>')

    # 4:1 Multiplexer for SegOut
    mux_x = 560
    content += f'''
    <!-- 4:1 Multiplexer for SegOut -->
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Selector Bits</string><int>2</int></entry>
      </elementAttributes>
      <pos x="{mux_x}" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegSel_bus</string></entry><entry><string>Bits</string><int>2</int></entry></elementAttributes>
      <pos x="{mux_x + 20}" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegOut_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{mux_x + 60}" y="140"/>
    </visualElement>
'''
    wires.append(f'<wire><p1 x="{mux_x + 40}" y="140"/><p2 x="{mux_x + 60}" y="140"/></wire>')

    for i, sname in enumerate(seg_names):
        content += f'''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{sname}_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{mux_x - 40}" y="{100 + i*20}"/>
    </visualElement>
'''
        wires.append(f'<wire><p1 x="{mux_x - 40}" y="{100 + i*20}"/><p2 x="{mux_x}" y="{100 + i*20}"/></wire>')

    # 20-bit Base Address Generator: (SegOut << 4)
    # Merging 4-bit ground 0x0 at bits 3..0 and SegOut[15:0] at bits 19..4
    content += f'''
    <!-- Base20 Generator: SegOut &lt;&lt; 4 -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes>
        <entry><string>Value</string><int>0</int></entry>
        <entry><string>Bits</string><int>4</int></entry>
      </elementAttributes>
      <pos x="{mux_x}" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegOut_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="{mux_x}" y="280"/>
    </visualElement>
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>4,16</string></entry>
        <entry><string>Output Splitting</string><string>20</string></entry>
      </elementAttributes>
      <pos x="{mux_x + 40}" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Base20_net</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="{mux_x + 80}" y="260"/>
    </visualElement>
'''
    wires.append(f'<wire><p1 x="{mux_x}" y="260"/><p2 x="{mux_x + 40}" y="260"/></wire>')
    wires.append(f'<wire><p1 x="{mux_x}" y="280"/><p2 x="{mux_x + 40}" y="280"/></wire>')
    wires.append(f'<wire><p1 x="{mux_x + 60}" y="260"/><p2 x="{mux_x + 80}" y="260"/></wire>')

    # Connect to Outputs
    content += '''
    <!-- Outputs -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>SegOut_net</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="780" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Base20_net</string></entry><entry><string>Bits</string><int>20</int></entry></elementAttributes>
      <pos x="780" y="140"/>
    </visualElement>
'''
    wires.append('<wire><p1 x="780" y="100"/><p2 x="800" y="100"/></wire>')
    wires.append('<wire><p1 x="780" y="140"/><p2 x="800" y="140"/></wire>')

    for i, sname in enumerate(seg_names):
        content += f'''
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>{sname}_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="780" y="{180 + i*40}"/>
    </visualElement>
'''
        wires.append(f'<wire><p1 x="780" y="{180 + i*40}"/><p2 x="800" y="{180 + i*40}"/></wire>')

    # Verification Testcase
    content += '''
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Clock DataIn SegSel SegWr SegOut Base20
# Write CS = 0x1000 -> Base20 = 0x10000
C     0x1000 0      1     0x1000 0x10000
# Write DS = 0x2000 -> Base20 = 0x20000
C     0x2000 1      1     0x2000 0x20000
# Write SS = 0x5000 -> Base20 = 0x50000
C     0x5000 2      1     0x5000 0x50000
# Write ES = 0x7000 -> Base20 = 0x70000
C     0x7000 3      1     0x7000 0x70000
# Read back CS (SegSel=0) with SegWr=0
0     0x0000 0      0     0x1000 0x10000
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="700" y="440"/>
    </visualElement>
  </visualElements>
'''
    content += '  <wires>\n'
    for w in wires:
        content += f'    {w}\n'
    content += '  </wires>\n</circuit>\n'

    with open(os.path.join(OUT_DIR, 'segment_registers.dig'), 'w') as f:
        f.write(content)
    print("Generated segment_registers.dig")

# -------------------------------------------------------------
# 4. instruction_pointer.dig
# -------------------------------------------------------------
def build_instruction_pointer():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>16-Bit Instruction Pointer (IP) with Sequential Step (+1, +2) and Parallel Load</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>JumpAddr</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Load</string></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Inc1</string></entry>
      </elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Inc2</string></entry>
      </elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Clock</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Clock</string></entry>
      </elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Reset</string></entry>
      </elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>IP</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="700" y="100"/>
    </visualElement>

    <!-- Input Tunnels -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>JumpAddr_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Load_in</string></entry></elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Inc1_in</string></entry></elementAttributes>
      <pos x="100" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Inc2_in</string></entry></elementAttributes>
      <pos x="100" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>CLK</string></entry></elementAttributes>
      <pos x="100" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RST</string></entry></elementAttributes>
      <pos x="100" y="300"/>
    </visualElement>

    <!-- Adders: IP + 1 and IP + 2 -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="200" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>1</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="200" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="220" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="200" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_plus_1</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="280" y="100"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="200" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>2</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="200" y="200"/>
    </visualElement>
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="220" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>0</int></entry></elementAttributes>
      <pos x="200" y="220"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_plus_2</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="280" y="180"/>
    </visualElement>

    <!-- Priority MUX for Next IP:
         Mux 1 (Inc2): if Inc2 then IP_plus_2 else IP_plus_1
         Mux 2 (Load): if Load then JumpAddr else (Mux 1)
         Mux 3 (Reset): if Reset then 0x0100 else (Mux 2) -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_plus_1</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="320" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_plus_2</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="320" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="340" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Inc2_in</string></entry></elementAttributes>
      <pos x="360" y="140"/>
    </visualElement>

    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>JumpAddr_bus</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="400" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="420" y="120"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Load_in</string></entry></elementAttributes>
      <pos x="440" y="160"/>
    </visualElement>

    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes><entry><string>Value</string><int>256</int></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="480" y="180"/>
    </visualElement>
    <visualElement>
      <elementName>Multiplexer</elementName>
      <elementAttributes><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="500" y="140"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RST</string></entry></elementAttributes>
      <pos x="520" y="180"/>
    </visualElement>

    <!-- Enable signal: Load | Inc1 | Inc2 | Reset -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Load_in</string></entry></elementAttributes>
      <pos x="360" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Inc1_in</string></entry></elementAttributes>
      <pos x="360" y="260"/>
    </visualElement>
    <visualElement>
      <elementName>Or</elementName>
      <elementAttributes><entry><string>Inputs</string><int>4</int></entry></elementAttributes>
      <pos x="380" y="240"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>Inc2_in</string></entry></elementAttributes>
      <pos x="360" y="300"/>
    </visualElement>
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>RST</string></entry></elementAttributes>
      <pos x="360" y="320"/>
    </visualElement>

    <!-- IP Register -->
    <visualElement>
      <elementName>Register</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>16</int></entry>
        <entry><string>Label</string><string>IP</string></entry>
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
      <elementAttributes><entry><string>NetName</string><string>IP_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="660" y="180"/>
    </visualElement>

    <!-- Output -->
    <visualElement>
      <elementName>Tunnel</elementName>
      <elementAttributes><entry><string>NetName</string><string>IP_val</string></entry><entry><string>Bits</string><int>16</int></entry></elementAttributes>
      <pos x="680" y="100"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Clock Reset Load Inc1 Inc2 JumpAddr IP
# Step 1: Reset to 0x0100
C     1     0    0    0    0x0000   0x0100
# Step 2: Step +1 -> 0x0101
C     0     0    1    0    0x0000   0x0101
# Step 3: Step +2 -> 0x0103
C     0     0    0    1    0x0000   0x0103
# Step 4: Step +2 -> 0x0105
C     0     0    0    1    0x0000   0x0105
# Step 5: Jump to 0x0500
C     0     1    0    0    0x0500   0x0500
# Step 6: Step +1 -> 0x0501
C     0     0    1    0    0x0000   0x0501
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="500" y="320"/>
    </visualElement>
  </visualElements>
  <wires>
    <!-- Add 1 -->
    <wire><p1 x="200" y="100"/><p2 x="220" y="100"/></wire>
    <wire><p1 x="200" y="120"/><p2 x="220" y="120"/></wire>
    <wire><p1 x="200" y="140"/><p2 x="220" y="140"/></wire>
    <!-- Add 2 -->
    <wire><p1 x="200" y="180"/><p2 x="220" y="180"/></wire>
    <wire><p1 x="200" y="200"/><p2 x="220" y="200"/></wire>
    <wire><p1 x="200" y="220"/><p2 x="220" y="220"/></wire>
    <!-- Mux 1 -->
    <wire><p1 x="320" y="100"/><p2 x="340" y="100"/></wire>
    <wire><p1 x="320" y="140"/><p2 x="340" y="140"/></wire>
    <wire><p1 x="380" y="120"/><p2 x="420" y="120"/></wire>
    <!-- Mux 2 -->
    <wire><p1 x="400" y="160"/><p2 x="420" y="160"/></wire>
    <wire><p1 x="460" y="140"/><p2 x="500" y="140"/></wire>
    <!-- Mux 3 -->
    <wire><p1 x="480" y="180"/><p2 x="500" y="180"/></wire>
    <wire><p1 x="540" y="160"/><p2 x="580" y="160"/></wire>
    <!-- OR gate inputs -->
    <wire><p1 x="360" y="240"/><p2 x="380" y="240"/></wire>
    <wire><p1 x="360" y="260"/><p2 x="380" y="260"/></wire>
    <wire><p1 x="360" y="300"/><p2 x="380" y="300"/></wire>
    <wire><p1 x="360" y="320"/><p2 x="380" y="320"/></wire>
    <!-- OR gate to Reg en -->
    <wire><p1 x="440" y="280"/><p2 x="560" y="280"/></wire>
    <wire><p1 x="560" y="200"/><p2 x="580" y="200"/></wire>
    <wire><p1 x="560" y="200"/><p2 x="560" y="280"/></wire>
    <!-- Reg Clock -->
    <wire><p1 x="560" y="180"/><p2 x="580" y="180"/></wire>
    <!-- Reg Out -->
    <wire><p1 x="640" y="180"/><p2 x="660" y="180"/></wire>
    <!-- Out -->
    <wire><p1 x="680" y="100"/><p2 x="700" y="100"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'instruction_pointer.dig'), 'w') as f:
        f.write(content)
    print("Generated instruction_pointer.dig")

# -------------------------------------------------------------
# 5. address_adder_20bit.dig
# -------------------------------------------------------------
def build_address_adder_20bit():
    content = '''<?xml version="1.0" encoding="utf-8"?>
<circuit>
  <version>1</version>
  <attributes>
    <entry><string>Description</string><string>Dedicated 20-Bit Physical Address Adder (Physical Address = Base20 + Offset16)</string></entry>
    <entry><string>Width</string><int>5</int></entry>
  </attributes>
  <visualElements>
    <!-- Inputs in exact order -->
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Base20</string></entry>
        <entry><string>Bits</string><int>20</int></entry>
      </elementAttributes>
      <pos x="100" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>In</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>Offset16</string></entry>
        <entry><string>Bits</string><int>16</int></entry>
      </elementAttributes>
      <pos x="100" y="140"/>
    </visualElement>

    <!-- Outputs in exact order -->
    <visualElement>
      <elementName>Out</elementName>
      <elementAttributes>
        <entry><string>Label</string><string>PhysAddr</string></entry>
        <entry><string>Bits</string><int>20</int></entry>
      </elementAttributes>
      <pos x="500" y="100"/>
    </visualElement>

    <!-- Zero extend Offset16 to 20 bits: merge with 4 ground bits -->
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes>
        <entry><string>Value</string><int>0</int></entry>
        <entry><string>Bits</string><int>4</int></entry>
      </elementAttributes>
      <pos x="160" y="160"/>
    </visualElement>
    <visualElement>
      <elementName>Splitter</elementName>
      <elementAttributes>
        <entry><string>Input Splitting</string><string>16,4</string></entry>
        <entry><string>Output Splitting</string><string>20</string></entry>
      </elementAttributes>
      <pos x="200" y="140"/>
    </visualElement>

    <!-- 20-Bit Adder -->
    <visualElement>
      <elementName>Add</elementName>
      <elementAttributes>
        <entry><string>Bits</string><int>20</int></entry>
      </elementAttributes>
      <pos x="280" y="100"/>
    </visualElement>
    <visualElement>
      <elementName>Const</elementName>
      <elementAttributes>
        <entry><string>Value</string><int>0</int></entry>
      </elementAttributes>
      <pos x="260" y="140"/>
    </visualElement>

    <!-- Verification Testcase -->
    <visualElement>
      <elementName>Testcase</elementName>
      <elementAttributes>
        <entry>
          <string>Testdata</string>
          <testData>
            <dataString>
Base20  Offset16 PhysAddr
# Test 1: Standard segment 0x10000 + 0x0100 = 0x10100
0x10000 0x0100   0x10100
# Test 2: Data segment 0x20000 + 0x0020 = 0x20020
0x20000 0x0020   0x20020
# Test 3: Reset vector: 0xF0000 + 0xFFF0 = 0xFFFF0
0xF0000 0xFFF0   0xFFFF0
# Test 4: Segment wraparound
0xF0000 0x0000   0xF0000
</dataString>
          </testData>
        </entry>
      </elementAttributes>
      <pos x="200" y="240"/>
    </visualElement>
  </visualElements>
  <wires>
    <wire><p1 x="100" y="100"/><p2 x="280" y="100"/></wire>
    <wire><p1 x="100" y="140"/><p2 x="200" y="140"/></wire>
    <wire><p1 x="160" y="160"/><p2 x="200" y="160"/></wire>
    <wire><p1 x="220" y="140"/><p2 x="240" y="140"/></wire>
    <wire><p1 x="240" y="120"/><p2 x="280" y="120"/></wire>
    <wire><p1 x="240" y="120"/><p2 x="240" y="140"/></wire>
    <wire><p1 x="260" y="140"/><p2 x="280" y="140"/></wire>
    <wire><p1 x="340" y="100"/><p2 x="500" y="100"/></wire>
  </wires>
</circuit>
'''
    with open(os.path.join(OUT_DIR, 'address_adder_20bit.dig'), 'w') as f:
        f.write(content)
    print("Generated address_adder_20bit.dig")

# Run generation of circuits 2 to 5
build_register_file()
check_circuit('register_file.dig')
test_circuit('register_file.dig')

build_segment_registers()
check_circuit('segment_registers.dig')
test_circuit('segment_registers.dig')

build_instruction_pointer()
check_circuit('instruction_pointer.dig')
test_circuit('instruction_pointer.dig')

build_address_adder_20bit()
check_circuit('address_adder_20bit.dig')
test_circuit('address_adder_20bit.dig')
