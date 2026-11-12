"""
Unit tests for PyQt5 Desktop GUI application (CodeEditor, MainWindow, Paint Events).
"""

import os
import unittest

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QPixmap, QPaintEvent
    from PyQt5.QtCore import QRect
    from ui.codeeditor import CodeEditor
    from ui.mainwindow import MainWindow
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


if __name__ == '__main__':
    unittest.main()
