"""
Global Hotkey Listener

Monitors system-wide keyboard events to trigger the spotlight window.
Runs in a background daemon thread.
"""

from pynput import keyboard
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
        self.listener = None
        self.running = False

    def start(self):
        """Start listening for hotkey using pynput (rootless)"""
        self.running = True
        key_map = {
            'ctrl': keyboard.Key.ctrl,
            'shift': keyboard.Key.shift,
            'alt': keyboard.Key.alt,
            'space': keyboard.Key.space
        }
        keys = self.hotkey.lower().split('+')
        combo = set(key_map[k] for k in keys if k in key_map)
        pressed = set()

        def on_press(key):
            if key in combo:
                pressed.add(key)
                if pressed == combo:
                    self.toggle_callback()

        def on_release(key):
            if key in pressed:
                pressed.remove(key)

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.start()
        self.listener.join()

    def stop(self):
        """Stop listening for hotkey"""
        self.running = False
        if self.listener:
            self.listener.stop()


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
