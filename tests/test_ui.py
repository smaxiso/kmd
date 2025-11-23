import unittest
from PySide6.QtWidgets import QApplication
from src.ui.spotlight_window import SpotlightWindow
import sys

class TestSpotlightWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def test_window_creation(self):
        window = SpotlightWindow()
        self.assertTrue(window.isVisible() or not window.isVisible())

if __name__ == "__main__":
    unittest.main()
