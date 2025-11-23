"""
Global Hotkey Listener

Monitors system-wide keyboard events to trigger the spotlight window.
Runs in a background daemon thread.
"""

import keyboard
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import cfg


class HotkeyListener:
    """
    Manages global hotkey registration and handling.
    
    Default hotkey: Ctrl+Shift+Space
    """
    
    def __init__(self, toggle_callback):
        """
        Initialize hotkey listener
        
        Args:
            toggle_callback: Function to call when hotkey is pressed
        """
        self.toggle_callback = toggle_callback
        self.hotkey = cfg.get('hotkey', 'ctrl+shift+space')
        self._registered = False
    
    def start(self):
        """Start listening for hotkey"""
        try:
            keyboard.add_hotkey(self.hotkey, self.toggle_callback)
            self._registered = True
            print(f"Hotkey registered: {self.hotkey}")
            
            # Block forever, keeping the listener active
            keyboard.wait()
            
        except ImportError:
            print("Error: 'keyboard' module requires admin/root privileges")
            raise
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            raise
    
    def stop(self):
        """Stop listening for hotkey"""
        if self._registered:
            try:
                keyboard.remove_hotkey(self.hotkey)
                self._registered = False
                print("Hotkey unregistered")
            except Exception as e:
                print(f"Error unregistering hotkey: {e}")


if __name__ == "__main__":
    # Test hotkey listener
    def test_callback():
        print("Hotkey pressed! (Ctrl+Shift+Space)")
    
    print("Testing HotkeyListener...")
    print("Press Ctrl+Shift+Space to test")
    print("Press Ctrl+C to exit")
    
    listener = HotkeyListener(test_callback)
    
    try:
        listener.start()
    except KeyboardInterrupt:
        print("\nStopping...")
        listener.stop()
