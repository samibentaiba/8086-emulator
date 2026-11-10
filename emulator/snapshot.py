"""
8086 CPU State Snapshot & Time-Travel Debugging Architecture
Captures point-in-time microarchitectural state for reverse execution.
"""

class CPUSnapshot(object):
    """
    Immutable snapshot of the 8086 processor state at a specific clock cycle.
    Enables single-step rewind (reverse step) and reverse continuous execution.
    """
    def __init__(self, cycle_count, biu_reg, biu_pre_fetch_ip, biu_queue,
                 eu_reg, flags_int, ir, opcode, opd, opbyte, eo, interrupt, shutdown,
                 output, memory_changes=None, peripheral_state=None):
        self.cycle_count = cycle_count
        self.biu_reg = dict(biu_reg)
        self.biu_pre_fetch_ip = biu_pre_fetch_ip
        self.biu_queue = list(biu_queue)
        self.eu_reg = dict(eu_reg)
        self.flags_int = flags_int
        self.ir = list(ir) if isinstance(ir, list) else ir
        self.opcode = opcode
        self.opd = list(opd) if isinstance(opd, list) else opd
        self.opbyte = opbyte
        self.eo = list(eo) if isinstance(eo, list) else [0] * 5
        self.interrupt = interrupt
        self.shutdown = shutdown
        self.output = output
        self.memory_changes = list(memory_changes) if memory_changes else []
        self.peripheral_state = peripheral_state or {}

    def __repr__(self):
        return f"<CPUSnapshot Cycle={self.cycle_count} IP={self.biu_reg.get('IP', 0):04X}h Writes={len(self.memory_changes)}>"
