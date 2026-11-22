"""
Unit tests for Intel 8086 Complete Pure Digital Logic Circuits (Helmut Neemann's Digital).
Validates all 17 circuit models, checks pin wiring, netlists, and runs embedded test vectors.
"""

import os
import unittest
import subprocess

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIGITAL_DIR = os.path.join(REPO_DIR, "digital-circuit")
JAR_PATH = os.path.join(DIGITAL_DIR, "bin/Digital/Digital.jar")
LIBS_PATH = os.path.join(DIGITAL_DIR, "bin/Digital/lib/*")

ALL_CIRCUITS = [
    "alu_slice.dig",
    "alu_16bit.dig",
    "register_file.dig",
    "segment_registers.dig",
    "instruction_pointer.dig",
    "address_adder_20bit.dig",
    "flags_register.dig",
    "address_latches_8282.dig",
    "queue_6byte.dig",
    "clock_gen_8284.dig",
    "data_transceivers_8286.dig",
    "address_decoder_74ls138.dig",
    "ram_16bit.dig",
    "boot_rom_2764.dig",
    "instruction_decoder.dig",
    "i8086_cpu.dig",
    "i8086_system_board.dig",
]

CIRCUITS_WITH_TEST_VECTORS = [
    "alu_slice.dig",
    "alu_16bit.dig",
    "register_file.dig",
    "segment_registers.dig",
    "instruction_pointer.dig",
    "address_adder_20bit.dig",
    "flags_register.dig",
    "address_latches_8282.dig",
    "data_transceivers_8286.dig",
    "address_decoder_74ls138.dig",
    "ram_16bit.dig",
    "boot_rom_2764.dig",
]


class TestDigitalCircuits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Verify Java and Digital.jar exist
        if not os.path.exists(JAR_PATH):
            raise unittest.SkipTest("Digital.jar not found")
        try:
            res = subprocess.run(["java", "-version"], capture_output=True)
            if res.returncode != 0:
                raise unittest.SkipTest("Java runtime not available")
        except FileNotFoundError:
            raise unittest.SkipTest("Java runtime not available")

    def test_all_17_circuit_files_exist(self):
        """Verify that all 17 circuit files exist in digital-circuit directory."""
        for c in ALL_CIRCUITS:
            path = os.path.join(DIGITAL_DIR, c)
            self.assertTrue(os.path.isfile(path), f"Circuit file {c} must exist")

    def test_circuit_stats_and_model_loading(self):
        """Verify all 17 circuit models compile, load, and validate nets without errors."""
        cp = f"{JAR_PATH}:{LIBS_PATH}"
        for c in ALL_CIRCUITS:
            path = os.path.join(DIGITAL_DIR, c)
            cmd = [
                "java", "-Djava.awt.headless=true",
                "-cp", cp,
                "CLI", "stats", "-dig", path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(
                res.returncode, 0,
                f"Circuit {c} failed stats/compilation check:\n{res.stderr or res.stdout}"
            )

    def test_circuit_test_vectors(self):
        """Run all embedded truth table and hardware timing test vectors in Digital CLI."""
        cp = f"{JAR_PATH}:{LIBS_PATH}"
        for c in CIRCUITS_WITH_TEST_VECTORS:
            path = os.path.join(DIGITAL_DIR, c)
            cmd = [
                "java", "-Djava.awt.headless=true",
                "-cp", cp,
                "CLI", "test", "-circ", path
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(
                res.returncode, 0,
                f"Circuit {c} failed truth table test vectors:\n{res.stderr or res.stdout}"
            )


if __name__ == "__main__":
    unittest.main()
