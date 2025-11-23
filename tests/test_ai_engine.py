"""
Unit Tests for AI Engine

Tests AI provider abstraction and factory function.
"""

import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ai_engine import (
    AIProvider, OllamaProvider, OpenAIProvider, 
    GeminiProvider, get_provider
)


class TestAIProviderFactory(unittest.TestCase):
    """Test suite for AI provider factory"""
    
    @patch('src.services.ai_engine.cfg')
    def test_get_ollama_provider(self, mock_cfg):
        """Test factory returns OllamaProvider when configured"""
        mock_cfg.get.return_value = 'ollama'
        
        provider = get_provider()
        
        self.assertIsInstance(provider, OllamaProvider)
    
    @patch('src.services.ai_engine.cfg')
    def test_get_openai_provider(self, mock_cfg):
        """Test factory returns OpenAIProvider when configured"""
        mock_cfg.get.return_value = 'openai'
        
        provider = get_provider()
        
        self.assertIsInstance(provider, OpenAIProvider)
    
    @patch('src.services.ai_engine.cfg')
    def test_get_gemini_provider(self, mock_cfg):
        """Test factory returns GeminiProvider when configured"""
        mock_cfg.get.return_value = 'gemini'
        
        provider = get_provider()
        
        self.assertIsInstance(provider, GeminiProvider)
    
    @patch('src.services.ai_engine.cfg')
    def test_default_to_ollama(self, mock_cfg):
        """Test factory defaults to OllamaProvider for unknown providers"""
        mock_cfg.get.return_value = 'unknown_provider'
        
        provider = get_provider()
        
        self.assertIsInstance(provider, OllamaProvider)


class TestOllamaProvider(unittest.TestCase):
    """Test suite for OllamaProvider"""
    
    @patch('src.services.ai_engine.requests.post')
    @patch('src.services.ai_engine.cfg')
    def test_successful_command_generation(self, mock_cfg, mock_post):
        """Test successful command generation"""
        mock_cfg.get.side_effect = lambda key, default=None: {
            'ollama_url': 'http://localhost:11434',
            'model': 'llama3.2'
        }.get(key, default)
        
        mock_response = Mock()
        mock_response.json.return_value = {'response': 'ls -la'}
        mock_post.return_value = mock_response
        
        provider = OllamaProvider()
        result = provider.generate_command("list files")
        
        self.assertEqual(result, 'ls -la')
        mock_post.assert_called_once()
    
    @patch('src.services.ai_engine.requests.post')
    @patch('src.services.ai_engine.cfg')
    def test_connection_error_handling(self, mock_cfg, mock_post):
        """Test handling of connection errors"""
        mock_cfg.get.side_effect = lambda key, default=None: {
            'ollama_url': 'http://localhost:11434',
            'model': 'llama3.2'
        }.get(key, default)
        
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        provider = OllamaProvider()
        result = provider.generate_command("test query")
        
        self.assertIn("Error", result)
        self.assertIn("Ollama not running", result)


class TestOpenAIProvider(unittest.TestCase):
    """Test suite for OpenAIProvider"""
    
    @patch('src.services.ai_engine.cfg')
    def test_missing_api_key(self, mock_cfg):
        """Test handling of missing API key"""
        mock_cfg.get.return_value = {'openai': ''}
        
        provider = OpenAIProvider()
        result = provider.generate_command("test query")
        
        self.assertIn("Error", result)
        self.assertIn("API key not configured", result)


class TestGeminiProvider(unittest.TestCase):
    """Test suite for GeminiProvider"""
    
    @patch('src.services.ai_engine.cfg')
    def test_missing_api_key(self, mock_cfg):
        """Test handling of missing API key"""
        mock_cfg.get.return_value = {'gemini': ''}
        
        provider = GeminiProvider()
        result = provider.generate_command("test query")
        
        self.assertIn("Error", result)
        self.assertIn("API key not configured", result)


if __name__ == '__main__':
    unittest.main()
