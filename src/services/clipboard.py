"""
Clipboard Operations Wrapper

Provides cross-platform clipboard functionality with graceful fallback.
"""

import pyperclip
from typing import Optional


class ClipboardManager:
    """
    Manages clipboard operations with error handling.
    """
    
    @staticmethod
    def copy(text: str) -> bool:
        """
        Copy text to clipboard
        
        Args:
            text: Text to copy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"Clipboard copy failed: {e}")
            return False
    
    @staticmethod
    def paste() -> Optional[str]:
        """
        Get text from clipboard
        
        Returns:
            Clipboard text or None if error
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Clipboard paste failed: {e}")
            return None
    
    @staticmethod
    def clear() -> bool:
        """
        Clear clipboard contents
        
        Returns:
            True if successful, False otherwise
        """
        try:
            pyperclip.copy('')
            return True
        except Exception as e:
            print(f"Clipboard clear failed: {e}")
            return False


# Singleton instance
clipboard = ClipboardManager()
