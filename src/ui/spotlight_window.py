"""
Spotlight Window - Main UI Component

Raycast-style floating search bar powered by AI.
Built with PySide6 (Qt framework).
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QWidget, QLineEdit, 
    QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QPalette, QColor

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.ai_engine import get_provider
from src.services.clipboard import clipboard


class WorkerThread(QThread):
    """
    Background worker thread for AI requests.
    Prevents UI freezing during AI processing.
    """
    result_ready = Signal(str)
    
    def __init__(self, query: str):
        super().__init__()
        self.query = query
    
    def run(self):
        """Execute AI query in background"""
        try:
            provider = get_provider()
            command = provider.generate_command(self.query)
            self.result_ready.emit(command)
        except Exception as e:
            self.result_ready.emit(f"# Error: {str(e)}")


class SpotlightWindow(QWidget):
    """
    Main floating search bar window.
    
    Features:
    - Frameless, always-on-top design
    - Semi-transparent dark theme
    - Async AI processing with worker threads
    - Auto-copy results to clipboard
    - Keyboard-first interaction
    """
    
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self._init_ui()
        self._load_styles()
    
    def _init_ui(self):
        """Initialize UI components"""
        # Window Configuration
        self.setObjectName("SpotlightWindow")
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Layout
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        self.setLayout(layout)
        
        # Input Field
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask AI for a command...")
        self.input.setFont(QFont("Consolas", 16))
        self.input.returnPressed.connect(self._on_submit)
        layout.addWidget(self.input, stretch=1)
        
        # Close Button
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFont(QFont("Arial", 20))
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide_window)
        layout.addWidget(self.close_btn)
        
        # Window Sizing and Positioning
        self.resize(700, 70)
        self._center_window()
        
        # Keyboard Shortcuts
        self.installEventFilter(self)
    
    def _load_styles(self):
        """Load Qt stylesheet"""
        try:
            style_path = Path(__file__).parent / "styles.qss"
            if style_path.exists():
                with open(style_path, 'r') as f:
                    self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Warning: Could not load styles: {e}")
            # Fallback inline styles
            self._apply_fallback_styles()
    
    def _apply_fallback_styles(self):
        """Apply inline styles if stylesheet file not found"""
        self.setStyleSheet("""
            QWidget#SpotlightWindow {
                background-color: rgba(30, 30, 30, 0.95);
                border: 1px solid #333;
                border-radius: 10px;
            }
            QLineEdit {
                background-color: transparent;
                border: none;
                color: #00ff00;
                padding: 10px 15px;
            }
            QPushButton#CloseButton {
                background-color: transparent;
                border: none;
                color: #888;
            }
            QPushButton#CloseButton:hover {
                background-color: #333;
                color: #fff;
            }
        """)
    
    def _center_window(self):
        """Position window at top-center of screen"""
        try:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = screen.height() // 4
            self.move(x, y)
        except Exception as e:
            print(f"Warning: Could not center window: {e}")
            self.move(300, 200)  # Fallback position
    
    def show_window(self):
        """Show the window and focus input"""
        self.show()
        self.activateWindow()
        self.raise_()
        self.input.clear()
        self.input.setFocus()
    
    def hide_window(self):
        """Hide the window"""
        self.hide()
        # Cancel ongoing AI request if any
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
    
    def _on_submit(self):
        """Handle Enter key press"""
        query = self.input.text().strip()
        
        if not query:
            return
        
        # Kill switch
        if query.lower() in ['exit', 'quit']:
            QApplication.quit()
            return
        
        # Show loading state
        self.input.setText("🤔 Thinking...")
        self.input.setReadOnly(True)
        
        # Start AI processing in background thread
        self.worker_thread = WorkerThread(query)
        self.worker_thread.result_ready.connect(self._on_result)
        self.worker_thread.start()
    
    def _on_result(self, result: str):
        """Handle AI result"""
        self.input.setReadOnly(False)
        self.input.setText(result)
        self.input.selectAll()
        
        # Copy to clipboard
        if clipboard.copy(result):
            print(f"Copied to clipboard: {result}")
        
        # Auto-hide after 3 seconds (optional - can be disabled)
        # QTimer.singleShot(3000, self.hide_window)
    
    def eventFilter(self, obj, event):
        """Handle keyboard events"""
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key_Escape:
                self.hide_window()
                return True
        return super().eventFilter(obj, event)
    
    def focusOutEvent(self, event):
        """Auto-hide when focus is lost"""
        # Delayed hide to allow clicking buttons
        QTimer.singleShot(200, self._check_and_hide)
        super().focusOutEvent(event)
    
    def _check_and_hide(self):
        """Check if window should hide on focus loss"""
        if not self.isActiveWindow() and self.isVisible():
            self.hide_window()


def main():
    """Test the spotlight window independently"""
    app = QApplication(sys.argv)
    
    window = SpotlightWindow()
    window.show_window()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
