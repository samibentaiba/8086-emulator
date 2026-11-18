from pathlib import Path
from emulator.assembler import Assembler

SEG_INIT = {
    'DS': int('0000', 16), # Initial value of data segment
    'CS': int('1000', 16), # Initial value of code segment
    'SS': int('0000', 16), # Initial value of stack segment
    'ES': int('0000', 16) # Initial value of extra segment
}



def load_ivt(memory): # load Interrupt Vector Table
    # 0000:0000 ~ 0000:03FF 
    for i in range(256):        # 0 ~ FF
        memory.wb(i * 4, ['0x00'])      # IP
        memory.wb(i * 4 + 1, ['0x00'])
        memory.wb(i * 4 + 2, [str(hex(i % 16)) + '0'])  # CS
        memory.wb(i * 4 + 3, ['0x1' + str(hex(i // 16))[-1]])

def load_isr(memory, verbose=False):
    load_ivt(memory)
    if verbose:
        print("loading ISR...")

    routines = Path(__file__).with_name('interrupt_routines')
    for i in ['0', '1', '2', '3', '4', '7c']:
        assembler = Assembler(SEG_INIT)
        isr = assembler.compile((routines / f'isr{i}.asm').read_text(encoding='utf-8'))
        base = (SEG_INIT['CS'] << 4) + 0x100 * int(i, 16)
        memory.load_segment(base, isr.space['CS'][:isr.seg_len['CS']])
