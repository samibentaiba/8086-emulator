#!/usr/bin/env python3
import os
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
CP = os.path.join(DIR, 'bin/Digital/Digital.jar') + ':' + os.path.join(DIR, 'bin/Digital/lib/*')

def verify(filename):
    res = subprocess.run(['java', '-Djava.awt.headless=true', '-cp', CP, 'CLI', 'stats', '-dig', os.path.join(DIR, filename)], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED {filename}:\n" + (res.stderr or res.stdout))
        return False
    print(f"OK {filename}")
    return True

def run_tests():
    # 1. Update boot_rom_2764.dig with executable demo code at 0x0000 and reset vector at 0xFFF0
    rom_data = "5,603,10c0,204,6000,7200,d008,9020,f000,65511*0,e0ea,1200,9090"
    
    rom_xml = f'''<?xml version="1.0" encoding="utf-8"?>
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
        f.write(rom_xml)
    print("Wrote boot_rom_2764.dig")
    verify('boot_rom_2764.dig')

if __name__ == '__main__':
    run_tests()
