"""
Kmd - AI Command Assistant
Main Application Entry Point

Integrates all components:
- PySide6 UI (Spotlight Window)
- Global Hotkey Listener
- System Tray Icon
- AI Provider Services
"""

import sys
import threading
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.spotlight_window import SpotlightWindow
from src.core.hotkey_listener import HotkeyListener
from src.core.system_tray import SystemTray
from src.config import cfg


class KmdApplication:
    """
    Main application coordinator.
    
    Manages:
    - Qt application lifecycle
    - Hotkey listener thread
    - System tray integration
    - Component communication
    """
    
    def __init__(self):
        self.app = None
        self.window = None
        self.hotkey_listener = None
        self.system_tray = None
        self._setup_qt_app()
    
    def _setup_qt_app(self):
        """Initialize Qt application and main window"""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Kmd")
        self.app.setQuitOnLastWindowClosed(False)  # Keep running when window closes
        
        self.window = SpotlightWindow()
    
    def toggle_window(self):
        """Show or hide the spotlight window"""
        if self.window.isVisible():
            self.window.hide_window()
        else:
            self.window.show_window()
    
    def show_window(self):
        """Show the spotlight window"""
        self.window.show_window()
    
    def quit_application(self):
        """Clean shutdown of all components"""
        print("Shutting down Kmd...")
        
        # Stop hotkey listener
        if self.hotkey_listener:
            self.hotkey_listener.stop()
        
        # Stop system tray
        if self.system_tray:
            self.system_tray.stop()
        
        # Quit Qt application
        QApplication.quit()
    
    def start_hotkey_listener(self):
        """Start global hotkey listener in background thread"""
        self.hotkey_listener = HotkeyListener(self.toggle_window)
        
        # Run in daemon thread so it stops when main thread exits
        hotkey_thread = threading.Thread(
            target=self.hotkey_listener.start,
            daemon=True
        )
        hotkey_thread.start()
        print(f"Hotkey listener started: {cfg.get('hotkey')}")
    
    def start_system_tray(self):
        """Start system tray icon in background thread"""
        self.system_tray = SystemTray(
            show_callback=self.show_window,
            quit_callback=self.quit_application
        )
        
        # Run in daemon thread
        tray_thread = threading.Thread(
            target=self.system_tray.run,
            daemon=True
        )
        tray_thread.start()
        print("System tray started")
    
    def run(self):
        """Start the application"""
        print("=" * 50)
        print("Kmd - AI Command Assistant")
        print("=" * 50)
        print(f"Provider: {cfg.get('provider')}")
        print(f"Model: {cfg.get('model')}")
        print(f"Hotkey: {cfg.get('hotkey')}")
        print(f"Config: {cfg.CONFIG_FILE}")
        print("=" * 50)
        
        try:
            # Start background services
            self.start_hotkey_listener()
            self.start_system_tray()
            
            # Show window initially
            self.window.show_window()
            
            # Start Qt event loop (blocking)
            sys.exit(self.app.exec())
            
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")
            self.quit_application()
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            self.quit_application()


def main():
    """Application entry point"""
    app = KmdApplication()
    app.run()


if __name__ == "__main__":
    main()
