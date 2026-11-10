"""
Peripheral Manager for 8086 I/O Bus
Routes IN and OUT instruction cycles to virtual hardware peripherals.
"""

import sys


class PeripheralManager(object):
    """
    Central I/O Port Dispatcher.
    Maps 8086 port addresses (0x0000 - 0xFFFF) to virtual peripheral devices.
    """
    _instance = None

    @classmethod
    def get_instance(cls, enable_gui=True):
        if cls._instance is None:
            cls._instance = PeripheralManager(enable_gui=enable_gui)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        if cls._instance is not None:
            cls._instance.close_all()
            cls._instance = None

    def __init__(self, enable_gui=True):
        self.enable_gui = enable_gui
        self.devices = {}
        self._init_default_peripherals()

    def _init_default_peripherals(self):
        """Register default EMU8086 hardware peripherals."""
        try:
            from .traffic_lights import TrafficLightsDevice
            # Port 4: Standard EMU8086 Traffic Lights
            self.register(4, TrafficLightsDevice(enable_gui=self.enable_gui))
        except Exception as e:
            print(f"[PeripheralManager] Warning initializing default devices: {e}", file=sys.stderr)

    def register(self, port, device):
        """Register a peripheral device to a specific I/O port."""
        self.devices[port] = device

    def unregister(self, port):
        """Unregister device from port and clean up."""
        if port in self.devices:
            dev = self.devices.pop(port)
            if hasattr(dev, 'close'):
                dev.close()

    def has_device(self, port):
        """Check if an active peripheral is attached to the given port."""
        return port in self.devices

    def get_device(self, port):
        """Get the device instance attached to a port, if any."""
        return self.devices.get(port)

    def write_port(self, port, value, byte_size=2):
        """
        Handle 'OUT port, value' instruction.
        Returns True if handled by a virtual peripheral, False otherwise.
        """
        if port in self.devices:
            self.devices[port].write(value, byte_size)
            return True
        return False

    def read_port(self, port, byte_size=2):
        """
        Handle 'IN dest, port' instruction.
        Returns integer value if handled by a peripheral, or None otherwise.
        """
        if port in self.devices:
            return self.devices[port].read(byte_size)
        return None

    def close_all(self):
        """Clean up and close all peripheral windows/processes."""
        for port, device in list(self.devices.items()):
            if hasattr(device, 'close'):
                try:
                    device.close()
                except Exception:
                    pass
        self.devices.clear()
