import time
import re
from pprint import pprint
from emulator.assembler import Assembler, AssemblyError, to_decimal
from emulator.snapshot import CPUSnapshot

class CPU(object):
    
    def __init__(self, BIU, EU, gui_mode):
        self.cycle_count = 0
        self.BIU = BIU
        self.EU = EU
        self.gui_mode = gui_mode
        self.history = []
        self.max_history = 10000
        self.history_enabled = True

    def take_snapshot(self):
        """Capture an exact microarchitectural snapshot of the CPU before a step."""
        biu_reg = dict(self.BIU.reg)
        biu_pre_fetch_ip = getattr(self.BIU, 'pre_fetch_ip', biu_reg.get('IP', 0))
        biu_queue = list(self.BIU.instruction_queue.queue)

        eu_reg = dict(self.EU.reg)
        flags_int = self.EU.FR.get_int()
        ir = self.EU.IR
        opcode = getattr(self.EU, 'opcode', '')
        opd = getattr(self.EU, 'opd', [])
        opbyte = getattr(self.EU, 'opbyte', 2)
        eo = getattr(self.EU, 'eo', [0] * 5)
        interrupt = self.EU.interrupt
        shutdown = self.EU.shutdown
        output = getattr(self.EU, 'output', '')

        periph_state = {}
        if hasattr(self.EU, 'peripherals') and self.EU.peripherals:
            pm = self.EU.peripherals
            dev4 = pm.get_device(4)
            if dev4 is not None:
                periph_state['port4'] = dev4.state
            dev7 = pm.get_device(7)
            if dev7 is not None:
                periph_state['port7'] = {
                    'state': dev7.state,
                    'prev_coils': dev7.prev_coils,
                    'angle': dev7.angle,
                    'step_count': dev7.step_count,
                    'direction_str': dev7.direction_str
                }
        if hasattr(self.EU, 'video_display') and self.EU.video_display:
            vd = self.EU.video_display
            periph_state['video'] = {
                'cursor_row': vd.cursor_row,
                'cursor_col': vd.cursor_col,
                'cursor_visible': vd.cursor_visible,
                'video_mode': vd.video_mode
            }

        return CPUSnapshot(
            cycle_count=self.cycle_count,
            biu_reg=biu_reg,
            biu_pre_fetch_ip=biu_pre_fetch_ip,
            biu_queue=biu_queue,
            eu_reg=eu_reg,
            flags_int=flags_int,
            ir=ir,
            opcode=opcode,
            opd=opd,
            opbyte=opbyte,
            eo=eo,
            interrupt=interrupt,
            shutdown=shutdown,
            output=output,
            memory_changes=[],
            peripheral_state=periph_state
        )

    def restore_snapshot(self, snapshot):
        """Restore CPU, memory, and peripheral state from a snapshot."""
        # 1. Restore memory modifications in reverse chronological order
        if hasattr(self.BIU, 'memory') and self.BIU.memory:
            old_listener = getattr(self.BIU.memory, 'write_listener', None)
            self.BIU.memory.write_listener = None
            try:
                for loc, val in reversed(snapshot.memory_changes):
                    self.BIU.memory.space[loc] = val
            finally:
                self.BIU.memory.write_listener = old_listener

        # 2. Restore BIU registers & prefetch queue
        self.BIU.reg.clear()
        self.BIU.reg.update(snapshot.biu_reg)
        self.BIU.pre_fetch_ip = snapshot.biu_pre_fetch_ip
        self.BIU.instruction_queue.queue.clear()
        for item in snapshot.biu_queue:
            self.BIU.instruction_queue.queue.append(item)

        # 3. Restore EU registers, flags, and internal control circuit state
        self.EU.reg.clear()
        self.EU.reg.update(snapshot.eu_reg)
        self.EU.FR.set_int(snapshot.flags_int)
        self.EU.IR = list(snapshot.ir) if isinstance(snapshot.ir, list) else snapshot.ir
        self.EU.opcode = snapshot.opcode
        self.EU.opd = list(snapshot.opd) if isinstance(snapshot.opd, list) else snapshot.opd
        self.EU.opbyte = snapshot.opbyte
        self.EU.eo = list(snapshot.eo) if isinstance(snapshot.eo, list) else [0] * 5
        self.EU.interrupt = snapshot.interrupt
        self.EU.shutdown = snapshot.shutdown
        if hasattr(self.EU, 'output'):
            self.EU.output = snapshot.output

        # 4. Restore cycle count
        self.cycle_count = snapshot.cycle_count

        # 5. Restore Virtual Peripherals
        if hasattr(self.EU, 'peripherals') and self.EU.peripherals:
            pm = self.EU.peripherals
            if 'port4' in snapshot.peripheral_state:
                dev4 = pm.get_device(4)
                if dev4 is not None:
                    dev4.state = snapshot.peripheral_state['port4']
                    if dev4.pipe:
                        try:
                            dev4.pipe.send(dev4.state)
                        except (BrokenPipeError, OSError):
                            pass
            if 'port7' in snapshot.peripheral_state:
                dev7 = pm.get_device(7)
                if dev7 is not None:
                    p7 = snapshot.peripheral_state['port7']
                    dev7.state = p7['state']
                    dev7.prev_coils = p7['prev_coils']
                    dev7.angle = p7['angle']
                    dev7.step_count = p7['step_count']
                    dev7.direction_str = p7['direction_str']
                    if dev7.pipe:
                        try:
                            dev7.pipe.send({
                                "coils": dev7.state,
                                "angle": dev7.angle,
                                "direction": dev7.direction_str,
                                "step_count": dev7.step_count
                            })
                        except (BrokenPipeError, OSError):
                            pass
        if hasattr(self.EU, 'video_display') and self.EU.video_display:
            vd = self.EU.video_display
            if 'video' in snapshot.peripheral_state:
                v_info = snapshot.peripheral_state['video']
                vd.cursor_row = v_info['cursor_row']
                vd.cursor_col = v_info['cursor_col']
                vd.cursor_visible = v_info['cursor_visible']
                vd.video_mode = v_info['video_mode']
                if vd.pipe:
                    try:
                        vd.pipe.send({"cursor": (vd.cursor_row, vd.cursor_col)})
                    except (BrokenPipeError, OSError):
                        pass

    def step_back(self):
        """Rewind CPU execution by one instruction cycle."""
        if not self.history:
            return False
        snapshot = self.history.pop()
        self.restore_snapshot(snapshot)
        return True

    def can_step_back(self):
        """Check if execution history has states available to rewind."""
        return len(self.history) > 0

    def iterate(self, debug=False):
        snapshot = self.take_snapshot() if self.history_enabled else None
        mem_changes = []
        old_listener = getattr(self.BIU.memory, 'write_listener', None) if self.history_enabled else None

        if self.history_enabled and hasattr(self.BIU, 'memory') and self.BIU.memory:
            def _mem_recorder(loc, old_val):
                mem_changes.append((loc, old_val))
                if old_listener:
                    old_listener(loc, old_val)
            self.BIU.memory.write_listener = _mem_recorder

        try:
            self.cycle_count += 1
            if debug:
                self.EU.print(f"clock cycle {self.cycle_count}: fetching...\n")

            self.fetch_cycle()

            self.cycle_count += 1
            if debug:
                print(f"clock cycle {self.cycle_count}: executing...\n")

            self.execute_cycle()
        finally:
            if self.history_enabled and hasattr(self.BIU, 'memory') and self.BIU.memory:
                self.BIU.memory.write_listener = old_listener
                if snapshot is not None:
                    snapshot.memory_changes = mem_changes
                    self.history.append(snapshot)
                    if len(self.history) > self.max_history:
                        self.history.pop(0)

        if (debug or self.EU.interrupt):
            if not self.gui_mode and not getattr(self, 'tui_mode', False):
                self.print_state()
                self.debug()
                self.EU.interrupt = False

    def debug(self):
        while True:
            cmd = input("Press Enter to continue...\n> ").strip()
            if not cmd:
                return
            cmd = cmd.upper().split()
            if cmd[0] in ['U', 'B']: # Step backward (Undo / Back)
                if self.step_back():
                    print(f"⏪ Stepped backward to cycle {self.cycle_count}. IP={self.BIU.reg.get('IP', 0):04X}h")
                    self.print_state()
                else:
                    print("Already at start of program (cycle 0).")
                return

            if cmd[0] == 'A': # input and run the code (simple code)
                asm_code = input("Run code > ")
                ins = [s for s in re.split(" |,", asm_code.strip().upper()) if s]
                self.EU.print(ins)
                self.EU.opcode = ins[0]
                if len(ins) > 1:
                    self.EU.opd = ins[1:]
                self.EU.get_opbyte()
                self.EU.control_circuit()
                return

            if cmd[0] == 'D': # show memory:  d 0x20000
                if len(cmd) == 2:
                    adr1 = self.EU.get_int(cmd[1])
                    self.show_memory(adr1, adr1 + 50)
                elif len(cmd) == 3:
                    adr1 = to_decimal(cmd[1])
                    adr2 = to_decimal(cmd[2])
                    self.show_memory(adr1, adr2)

            elif cmd[0] == 'R': # show registers
                self.show_regs()

        

    def fetch_cycle(self):
        # Instruction fetch cycle
        self.BIU.run()
        pass

    def execute_cycle(self):
        # Instruction execution cycle
        self.EU.run()
        pass
    
    def check_done(self):
        # Check if there are no more instructions to stop CPU execution
        if self.EU.interrupt or self.EU.shutdown:
            return True
        return  self.BIU.instruction_queue.empty() and \
                not self.BIU.remain_instruction()

    def show_regs(self):
        for key, val in list(self.EU.reg.items())[:4]:
            print(key, '0x{:0>4x}'.format(val), end='   ')
        print()
        for key, val in list(self.EU.reg.items())[4:]:
            print(key, '0x{:0>4x}'.format(val), end='   ')
        print()
        for key, val in self.BIU.reg.items():
            print(key, '0x{:0>4x}'.format(val), end='   ')
        print()
        print('S ', self.EU.FR.sign, end='  ')
        print('Z', self.EU.FR.zero, end='   ')
        print('AC', self.EU.FR.auxiliary, end='  ')
        print('P', self.EU.FR.parity, end='   ')
        print('CY', self.EU.FR.carry, end='  ')
        print('O', self.EU.FR.overflow, end='   ')
        print('D ', self.EU.FR.direction, end='  ')
        print('I', self.EU.FR.interrupt, end='   ')
        print('T ', self.EU.FR.trap, end='  ')
        print()

    def show_memory(self, begin, end):
        pprint(self.BIU.memory.space[begin: end], compact=True)

    def print_state(self):
        # Print runtime state
        print("\nPipeline:")
        pprint(list(self.BIU.instruction_queue.queue))
        print("\nMemory of CS:IP:")
        self.show_memory(self.BIU.cs_ip, self.BIU.cs_ip + 10)
        print("\nMemory of DS:")
        self.show_memory(self.BIU.reg['DS']*16, self.BIU.reg['DS']*16 + 40)
        print("\nRegisters:")
        self.show_regs()
        print("\nIR:  ", self.EU.IR)
        print("Next:", self.BIU.next_ins)
        print('-' * 80)
    
    def print_end_state(self):
        # Print termination state
        self.EU.print("Clock ended\n")
        self.EU.print(f"CPU ran a total of {self.cycle_count} clock cycles\n")
        if hasattr(self.EU, 'peripherals') and self.EU.peripherals:
            self.EU.peripherals.close_all()
        if hasattr(self.EU, 'video_display') and self.EU.video_display:
            self.EU.video_display.close()
        if hasattr(self.EU, 'file_handles'):
            for f in list(self.EU.file_handles.values()):
                try:
                    f.close()
                except Exception:
                    pass
            self.EU.file_handles.clear()