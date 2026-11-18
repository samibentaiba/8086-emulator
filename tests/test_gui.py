"""
Unit tests for PyQt5 Desktop GUI application (CodeEditor, MainWindow, Paint Events).
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPixmap, QPaintEvent
    from PyQt5.QtCore import QRect
    from ui.codeeditor import CodeEditor
    from ui.mainwindow import MainWindow
    from emulator.peripherals.manager import PeripheralManager
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False


@unittest.skipUnless(PYQT5_AVAILABLE, "PyQt5 is not available in test environment")
class TestGUIComponents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create singleton QApplication for GUI tests
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication([])

    def test_01_code_editor_line_number_paint(self):
        """Verify lineNumberAreaPaintEvent does not raise TypeError on float coordinates."""
        editor = CodeEditor()
        editor.setPlainText("MOV AX, 1\nMOV BX, 2\nADD AX, BX\n")
        
        # Simulate paint event on line number area
        paint_event = QPaintEvent(QRect(0, 0, editor.lineNumberArea.width(), 300))
        # Should not raise TypeError: drawText argument 2 has unexpected type 'float'
        editor.lineNumberAreaPaintEvent(paint_event)

    def test_02_mainwindow_initialization_and_render(self):
        """Verify MainWindow initializes and renders cleanly to QPixmap."""
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        sample_asm = os.path.join(repo_root, "tests", "Requirement", "bubble_sort.asm")
        
        w = MainWindow(self.app, initial_file=sample_asm)
        self.assertIsNotNone(w.gui)
        self.assertIsNotNone(w.asmEdit)
        self.assertIn("bubble", w.asmEdit.toPlainText().lower())

        # Render full window to pixmap
        pixmap = QPixmap(w.gui.size())
        w.gui.render(pixmap)
        self.assertFalse(pixmap.isNull())

    def test_save_to_new_path_and_open_preserve_utf8_source(self):
        window = MainWindow.__new__(MainWindow)
        window.gui = None
        window.asmEdit = CodeEditor()
        window.console = Mock()
        window.stopAction = Mock()
        source = "; programme de démonstration\nHLT"
        window.asmEdit.setPlainText(source)
        window.asmEdit.document().setModified(True)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "new.asm"
            with patch('ui.mainwindow.QFileDialog.getSaveFileName', return_value=(str(path), '')):
                window.saveAction()
            self.assertFalse(window.asmEdit.document().isModified())
            self.assertEqual(path.read_bytes(), source.encode('utf-8'))
            window.asmEdit.setPlainText('')
            with patch('ui.mainwindow.QFileDialog.getOpenFileName', return_value=(str(path), '')):
                window.openAction()
            self.assertEqual(window.asmEdit.toPlainText(), source)

    def test_load_recovers_after_assembly_error(self):
        PeripheralManager.reset_instance()
        PeripheralManager.get_instance(enable_gui=False)
        self.addCleanup(PeripheralManager.reset_instance)
        window = MainWindow(self.app)
        self.addCleanup(window.gui.close)
        invalid = "CODE SEGMENT\nSTART:\nVALUE DB BAD\nHLT\nCODE ENDS\nEND START"
        window.asmEdit.setPlainText(invalid)
        window.actionLoad.trigger()
        self.assertIn("Could not assemble the program", window.console.toPlainText())
        self.assertEqual(window.asmEdit.toPlainText(), invalid)
        self.assertFalse(window.asmEdit.isReadOnly())
        self.assertTrue(window.actionLoad.isEnabled())
        self.assertFalse(window.actionRun.isEnabled())
        window.asmEdit.setPlainText(invalid.replace("VALUE DB BAD", "MOV AX, 42"))
        window.actionLoad.trigger()
        self.assertTrue(window.actionRun.isEnabled())
        window.actionStep.trigger()
        self.assertEqual(window.EU.reg['AX'], 42)


if __name__ == '__main__':
    unittest.main()
