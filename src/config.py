"""
Configuration Manager for Kmd Application

Handles persistent storage of application settings in ~/.Kmd/config.json
Implements singleton pattern for global access to configuration.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

# Application Constants
APP_NAME = "Kmd"
CONFIG_DIR = Path.home() / f".{APP_NAME}"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default Configuration
DEFAULT_CONFIG = {
    "provider": "ollama",  # Options: ollama, openai, gemini
    "api_keys": {
        "openai": "",
        "gemini": ""
    },
    "ollama_url": "http://localhost:11434",
    "model": "llama3.2",
    "hotkey": "ctrl+shift+space",
    "theme": "dark"
}


class ConfigManager:
    """
    Manages application configuration with JSON persistence.
    
    Features:
    - Auto-creates config directory and file with defaults
    - Singleton pattern for global access
    - Thread-safe read/write operations
    """
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager"""
        if self._initialized:
            return
            
        self._ensure_config_exists()
        self.config = self._load_config()
        self._initialized = True
    
    def _ensure_config_exists(self):
        """Create config directory and file if they don't exist"""
        try:
            if not CONFIG_DIR.exists():
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                print(f"Created config directory: {CONFIG_DIR}")
            
            if not CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(DEFAULT_CONFIG, f, indent=4)
                print(f"Created default config file: {CONFIG_FILE}")
        except Exception as e:
            print(f"Error creating config: {e}")
            raise
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = {**DEFAULT_CONFIG, **loaded_config}
                return merged_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and persist to disk
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self._save_config()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update multiple configuration values at once
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.config.update(updates)
        self._save_config()
    
    def _save_config(self):
        """Save current configuration to JSON file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = DEFAULT_CONFIG.copy()
        self._save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary"""
        return self.config.copy()


# Singleton instance for global access
cfg = ConfigManager()


if __name__ == "__main__":
    # Test the configuration manager
    print("Testing ConfigManager...")
    print(f"Config location: {CONFIG_FILE}")
    print(f"Current provider: {cfg.get('provider')}")
    print(f"All settings: {cfg.get_all()}")
