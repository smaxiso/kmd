"""
Unit Tests for Configuration Manager

Tests config file creation, get/set operations, and persistence.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import ConfigManager, DEFAULT_CONFIG


class TestConfigManager(unittest.TestCase):
    """Test suite for ConfigManager"""
    
    def setUp(self):
        """Set up test environment with temporary config directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_config_file = Path(self.test_dir) / "config.json"
        
        # Override config paths for testing
        import src.config as config_module
        self.original_config_dir = config_module.CONFIG_DIR
        self.original_config_file = config_module.CONFIG_FILE
        
        config_module.CONFIG_DIR = Path(self.test_dir)
        config_module.CONFIG_FILE = self.test_config_file
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
        # Restore original paths
        import src.config as config_module
        config_module.CONFIG_DIR = self.original_config_dir
        config_module.CONFIG_FILE = self.original_config_file
    
    def test_config_file_creation(self):
        """Test that config file is created with defaults"""
        cfg = ConfigManager()
        
        self.assertTrue(self.test_config_file.exists())
        
        with open(self.test_config_file, 'r') as f:
            config_data = json.load(f)
        
        self.assertEqual(config_data['provider'], DEFAULT_CONFIG['provider'])
        self.assertEqual(config_data['model'], DEFAULT_CONFIG['model'])
    
    def test_get_operation(self):
        """Test getting configuration values"""
        cfg = ConfigManager()
        
        self.assertEqual(cfg.get('provider'), 'ollama')
        self.assertEqual(cfg.get('model'), 'llama3.2')
        self.assertEqual(cfg.get('nonexistent', 'default'), 'default')
    
    def test_set_operation(self):
        """Test setting configuration values"""
        cfg = ConfigManager()
        
        cfg.set('provider', 'openai')
        self.assertEqual(cfg.get('provider'), 'openai')
        
        # Verify persistence
        with open(self.test_config_file, 'r') as f:
            config_data = json.load(f)
        
        self.assertEqual(config_data['provider'], 'openai')
    
    def test_update_operation(self):
        """Test updating multiple values at once"""
        cfg = ConfigManager()
        
        updates = {
            'provider': 'gemini',
            'model': 'gemini-pro'
        }
        cfg.update(updates)
        
        self.assertEqual(cfg.get('provider'), 'gemini')
        self.assertEqual(cfg.get('model'), 'gemini-pro')
    
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults"""
        cfg = ConfigManager()
        
        cfg.set('provider', 'openai')
        cfg.reset_to_defaults()
        
        self.assertEqual(cfg.get('provider'), DEFAULT_CONFIG['provider'])
    
    def test_singleton_pattern(self):
        """Test that ConfigManager is a singleton"""
        cfg1 = ConfigManager()
        cfg2 = ConfigManager()
        
        self.assertIs(cfg1, cfg2)
        
        cfg1.set('test_key', 'test_value')
        self.assertEqual(cfg2.get('test_key'), 'test_value')


if __name__ == '__main__':
    unittest.main()
