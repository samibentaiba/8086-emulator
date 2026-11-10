"""
Unit tests for Virtual Hardware Peripherals (Port 4 Traffic Lights)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from emulator.peripherals.manager import PeripheralManager
from emulator.peripherals.traffic_lights import TrafficLightsDevice
from emulator.peripherals.stepper_motor import StepperMotorDevice


class TestTrafficLightsPeripheral(unittest.TestCase):
    def setUp(self):
        # Create headless device
        self.dev = TrafficLightsDevice(enable_gui=False)
        self.mgr = PeripheralManager(enable_gui=False)
        self.mgr.register(4, self.dev)

    def tearDown(self):
        self.mgr.close_all()

    def test_initial_state(self):
        self.assertEqual(self.dev.read(byte_size=2), 0)
        self.assertEqual(self.mgr.read_port(4, byte_size=2), 0)

    def test_out_word_and_in_word(self):
        # All red pattern: 0x0249 = 0000 0010 0100 1001b
        self.mgr.write_port(4, 0x0249, byte_size=2)
        val = self.mgr.read_port(4, byte_size=2)
        self.assertEqual(val, 0x0249)
        self.assertEqual(self.dev.state, 0x0249)

    def test_bit_mapping_spec(self):
        # Test North Red (bit 0), West Red (bit 3), South Red (bit 6), East Red (bit 9)
        all_red = (1 << 0) | (1 << 3) | (1 << 6) | (1 << 9)
        self.assertEqual(all_red, 0x0249)
        self.mgr.write_port(4, all_red, byte_size=2)
        self.assertEqual(self.dev.state, 0x0249)

        # Test North Green (bit 2), West Red (bit 3), South Green (bit 8), East Red (bit 9)
        # 100b (4) on North, 001b (1) on West, 100b (4) on South, 001b (1) on East
        ns_green = (1 << 2) | (1 << 3) | (1 << 8) | (1 << 9)
        self.assertEqual(ns_green, 0x030C)
        self.mgr.write_port(4, ns_green, byte_size=2)
        self.assertEqual(self.dev.state, 0x030C)

        # Test North Red (bit 0), West Green (bit 5), South Red (bit 6), East Green (bit 11)
        # 001b (1) on North, 100b (4) on West, 001b (1) on South, 100b (4) on East
        ew_green = (1 << 0) | (1 << 5) | (1 << 6) | (1 << 11)
        self.assertEqual(ew_green, 0x0861)
        self.mgr.write_port(4, ew_green, byte_size=2)
        self.assertEqual(self.dev.state, 0x0861)

    def test_byte_operations(self):
        # Set full word first
        self.mgr.write_port(4, 0x0249, byte_size=2)
        # Update low byte (AL) to 0x12 (bits 0-7)
        self.mgr.write_port(4, 0x12, byte_size=1)
        # High byte should stay 0x02, low byte becomes 0x12 -> 0x0212
        self.assertEqual(self.mgr.read_port(4, byte_size=2), 0x0212)
        # Read byte returns low 8 bits
        self.assertEqual(self.mgr.read_port(4, byte_size=1), 0x12)


class TestStepperMotorPeripheral(unittest.TestCase):
    def setUp(self):
        self.dev = StepperMotorDevice(enable_gui=False)
        self.mgr = PeripheralManager(enable_gui=False)
        self.mgr.register(7, self.dev)

    def tearDown(self):
        self.mgr.close_all()

    def test_ready_bit(self):
        # IN AL, 7 should return ready flag (bit 7 set)
        val = self.mgr.read_port(7, byte_size=1)
        self.assertTrue(bool(val & 0x80))

    def test_clockwise_half_step_sequence(self):
        # Clockwise sequence: 0110b -> 0100b -> 0011b -> 0010b
        cw_steps = [0b0110, 0b0100, 0b0011, 0b0010]
        for step in cw_steps:
            self.mgr.write_port(7, step, byte_size=1)
        self.assertEqual(self.dev.direction_str, "CW")
        self.assertEqual(self.dev.step_count, 3) # 3 transitions
        self.assertAlmostEqual(self.dev.angle, 3 * 11.25)

    def test_counter_clockwise_sequence(self):
        # CCW sequence: 0011b -> 0001b -> 0110b -> 0010b
        ccw_steps = [0b0011, 0b0001, 0b0110, 0b0010]
        for step in ccw_steps:
            self.mgr.write_port(7, step, byte_size=1)
        self.assertEqual(self.dev.direction_str, "CCW")
        self.assertEqual(self.dev.step_count, 3) # 3 transitions
        self.assertAlmostEqual(self.dev.angle, (360.0 - 3 * 11.25) % 360.0)

    def test_full_revolution_wrap(self):
        # 32 steps * 11.25 deg = 360 deg
        cw_steps = [0b0110, 0b0100, 0b0011, 0b0010]
        for i in range(33):
            self.mgr.write_port(7, cw_steps[i % len(cw_steps)], byte_size=1)
        self.assertAlmostEqual(self.dev.angle, 0.0)


if __name__ == '__main__':
    unittest.main()
