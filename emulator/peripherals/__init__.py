"""
Virtual Hardware Peripherals for 8086 Emulator
EMU8086 Compatible Devices
"""

from .manager import PeripheralManager
from .traffic_lights import TrafficLightsDevice
from .stepper_motor import StepperMotorDevice

__all__ = ['PeripheralManager', 'TrafficLightsDevice', 'StepperMotorDevice']
