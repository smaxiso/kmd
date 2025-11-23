"""
AI Engine - Provider Abstraction Layer

Implements the Strategy Pattern for multiple AI providers:
- Ollama (local)
- OpenAI (cloud)
- Gemini (cloud)

Allows seamless switching between providers without code changes.
"""

from abc import ABC, abstractmethod
import requests
from typing import Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from src.config import cfg


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    def generate_command(self, query: str) -> str:
        """
        Generate a terminal command from natural language query
        
        Args:
            query: Natural language description of desired command
            
        Returns:
            Generated terminal command string
        """
        pass


class OllamaProvider(AIProvider):
    """
    Ollama Provider - Local AI model
    
    Requires Ollama to be running locally (default: localhost:11434)
    """
    
    def generate_command(self, query: str) -> str:
        """Generate command using local Ollama instance"""
        url = f"{cfg.get('ollama_url')}/api/generate"
        model = cfg.get('model', 'llama3.2')
        
        # Strict prompt to get only the command
        system_instruction = (
            "You are a command line expert. The user needs a terminal command. "
            "Return ONLY the exact command string. Do not use markdown. "
            "Do not explain. Do not add quotes. "
            "Example - User: 'list files' -> Response: ls -la"
        )
        
        prompt = f"{system_instruction}\nUser: {query}\nResponse:"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json().get('response', '').strip()
            # Clean up any markdown artifacts
            result = result.replace('```bash', '').replace('```', '').strip()
            
            return result if result else "# Error: Empty response from Ollama"
            
        except requests.exceptions.ConnectionError:
            return "# Error: Ollama not running. Start with 'ollama serve'"
        except requests.exceptions.Timeout:
            return "# Error: Ollama request timed out"
        except Exception as e:
            return f"# Error: {str(e)}"


class OpenAIProvider(AIProvider):
    """
    OpenAI Provider - ChatGPT API
    
    Requires OpenAI API key in configuration
    """
    
    def generate_command(self, query: str) -> str:
        """Generate command using OpenAI API"""
        api_key = cfg.get('api_keys', {}).get('openai', '')
        
        if not api_key:
            return "# Error: OpenAI API key not configured. Add in settings."
        
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a command line expert. Return ONLY the exact terminal command, no explanations, no markdown."
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.3,
            "max_tokens": 100
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()['choices'][0]['message']['content'].strip()
            # Clean markdown if present
            result = result.replace('```bash', '').replace('```', '').strip()
            
            return result if result else "# Error: Empty response from OpenAI"
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return "# Error: Invalid OpenAI API key"
            elif e.response.status_code == 429:
                return "# Error: OpenAI rate limit exceeded"
            else:
                return f"# Error: OpenAI API error ({e.response.status_code})"
        except requests.exceptions.Timeout:
            return "# Error: OpenAI request timed out"
        except Exception as e:
            return f"# Error: {str(e)}"


class GeminiProvider(AIProvider):
    """
    Google Gemini Provider
    
    Requires Gemini API key in configuration
    """
    
    def generate_command(self, query: str) -> str:
        """Generate command using Google Gemini API"""
        api_key = cfg.get('api_keys', {}).get('gemini', '')
        
        if not api_key:
            return "# Error: Gemini API key not configured. Add in settings."
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"You are a command line expert. Return ONLY the exact terminal command for this request, no explanations, no markdown:\n\n{query}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 100
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            # Clean markdown if present
            result = result.replace('```bash', '').replace('```', '').strip()
            
            return result if result else "# Error: Empty response from Gemini"
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return "# Error: Invalid Gemini API key"
            elif e.response.status_code == 429:
                return "# Error: Gemini rate limit exceeded"
            else:
                return f"# Error: Gemini API error ({e.response.status_code})"
        except requests.exceptions.Timeout:
            return "# Error: Gemini request timed out"
        except Exception as e:
            return f"# Error: {str(e)}"


def get_provider() -> AIProvider:
    """
    Factory function to get the configured AI provider
    
    Returns:
        AIProvider instance based on configuration
    """
    provider_name = cfg.get('provider', 'ollama').lower()
    
    providers = {
        'openai': OpenAIProvider,
        'gemini': GeminiProvider,
        'ollama': OllamaProvider
    }
    
    provider_class = providers.get(provider_name, OllamaProvider)
    return provider_class()


if __name__ == "__main__":
    # Test the AI engine
    print("Testing AI Engine...")
    provider = get_provider()
    print(f"Using provider: {type(provider).__name__}")
    
    test_query = "list all files"
    print(f"\nQuery: {test_query}")
    result = provider.generate_command(test_query)
    print(f"Result: {result}")
