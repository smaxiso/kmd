"""
System Tray Icon

Provides system tray integration with context menu.
Keeps the application running in the background.
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

try:
    import pystray
    from pystray import MenuItem as item
except ImportError:
    print("Warning: pystray not installed. System tray will not be available.")
    pystray = None


class SystemTray:
    """
    Manages system tray icon and menu.
    
    Features:
    - Always visible in system tray
    - Context menu (Show, Settings, Quit)
    - Prevents app termination when window closes
    """
    
    def __init__(self, show_callback, quit_callback):
        """
        Initialize system tray
        
        Args:
            show_callback: Function to show main window
            quit_callback: Function to quit application
        """
        self.show_callback = show_callback
        self.quit_callback = quit_callback
        self.icon = None
    
    def _create_icon_image(self):
        """Generate a simple 'K' icon"""
        # Create 64x64 image with dark background
        img = Image.new('RGB', (64, 64), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Draw 'K' in green
        try:
            # Try to use a nice font
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw the 'K' character
        draw.text((18, 10), "K", fill=(0, 255, 0), font=font)
        
        return img
    
    def _on_show(self, icon, item):
        """Handle 'Show' menu item"""
        self.show_callback()
    
    def _on_quit(self, icon, item):
        """Handle 'Quit' menu item"""
        self.icon.stop()
        self.quit_callback()
    
    def run(self):
        """Start the system tray icon"""
        if pystray is None:
            print("System tray not available (pystray not installed)")
            return
        
        icon_image = self._create_icon_image()
        
        menu = pystray.Menu(
            item('Show Kmd', self._on_show, default=True),
            item('Settings', lambda: print("Settings - Coming soon")),
            pystray.Menu.SEPARATOR,
            item('Quit', self._on_quit)
        )
        
        self.icon = pystray.Icon(
            "Kmd",
            icon_image,
            "Kmd - AI Command Assistant",
            menu
        )
        
        # Run in current thread (blocking)
        self.icon.run()
    
    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            self.icon.stop()


if __name__ == "__main__":
    # Test system tray
    def show_test():
        print("Show callback triggered")
    
    def quit_test():
        print("Quit callback triggered")
        sys.exit(0)
    
    print("Testing SystemTray...")
    print("Right-click the tray icon to see menu")
    
    tray = SystemTray(show_test, quit_test)
    tray.run()
