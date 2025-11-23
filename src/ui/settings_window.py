"""
Settings Window UI

Configuration interface for Kmd application.
Allows users to change AI provider, API keys, hotkey, etc.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import cfg


class SettingsWindow(QWidget):
    """
    Settings configuration window.
    
    Features:
    - Provider selection (Ollama, OpenAI, Gemini)
    - API key management
    - Ollama URL configuration
    - Model selection
    - Hotkey customization (future)
    """
    
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._load_current_settings()
    
    def _init_ui(self):
        """Initialize UI components"""
        self.setObjectName("SettingsWindow")
        self.setWindowTitle("Kmd Settings")
        self.setMinimumSize(500, 400)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        self.setLayout(layout)
        
        # Header
        header = QLabel("Kmd Settings")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        layout.addWidget(header)
        
        # Provider Section
        provider_group = self._create_provider_section()
        layout.addWidget(provider_group)
        
        # Ollama Section
        ollama_group = self._create_ollama_section()
        layout.addWidget(ollama_group)
        
        # API Keys Section
        api_keys_group = self._create_api_keys_section()
        layout.addWidget(api_keys_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Apply styles
        self._apply_styles()
    
    def _create_provider_section(self):
        """Create provider selection group"""
        group = QGroupBox("AI Provider")
        layout = QVBoxLayout()
        
        label = QLabel("Select AI Provider:")
        layout.addWidget(label)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["Ollama (Local)", "OpenAI", "Google Gemini"])
        self.provider_combo.currentTextChanged.connect(self._on_provider_changed)
        layout.addWidget(self.provider_combo)
        
        group.setLayout(layout)
        return group
    
    def _create_ollama_section(self):
        """Create Ollama configuration group"""
        group = QGroupBox("Ollama Configuration")
        layout = QVBoxLayout()
        
        # URL
        url_label = QLabel("Ollama URL:")
        layout.addWidget(url_label)
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setPlaceholderText("http://localhost:11434")
        layout.addWidget(self.ollama_url_input)
        
        # Model
        model_label = QLabel("Model:")
        layout.addWidget(model_label)
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("llama3.2")
        layout.addWidget(self.model_input)
        
        group.setLayout(layout)
        self.ollama_group = group
        return group
    
    def _create_api_keys_section(self):
        """Create API keys configuration group"""
        group = QGroupBox("API Keys")
        layout = QVBoxLayout()
        
        # OpenAI
        openai_label = QLabel("OpenAI API Key:")
        layout.addWidget(openai_label)
        
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.Password)
        self.openai_key_input.setPlaceholderText("sk-...")
        layout.addWidget(self.openai_key_input)
        
        # Gemini
        gemini_label = QLabel("Google Gemini API Key:")
        layout.addWidget(gemini_label)
        
        self.gemini_key_input = QLineEdit()
        self.gemini_key_input.setEchoMode(QLineEdit.Password)
        self.gemini_key_input.setPlaceholderText("Your Gemini API key")
        layout.addWidget(self.gemini_key_input)
        
        group.setLayout(layout)
        self.api_keys_group = group
        return group
    
    def _load_current_settings(self):
        """Load current settings from config"""
        # Provider
        provider = cfg.get('provider', 'ollama')
        provider_map = {
            'ollama': 0,
            'openai': 1,
            'gemini': 2
        }
        self.provider_combo.setCurrentIndex(provider_map.get(provider, 0))
        
        # Ollama
        self.ollama_url_input.setText(cfg.get('ollama_url', 'http://localhost:11434'))
        self.model_input.setText(cfg.get('model', 'llama3.2'))
        
        # API Keys
        api_keys = cfg.get('api_keys', {})
        self.openai_key_input.setText(api_keys.get('openai', ''))
        self.gemini_key_input.setText(api_keys.get('gemini', ''))
        
        self._on_provider_changed(self.provider_combo.currentText())
    
    def _on_provider_changed(self, provider_text):
        """Handle provider selection change"""
        # Show/hide relevant sections based on provider
        is_ollama = "Ollama" in provider_text
        is_openai = "OpenAI" in provider_text
        is_gemini = "Gemini" in provider_text
        
        self.ollama_group.setVisible(is_ollama)
        # Could add more conditional UI updates here
    
    def _save_settings(self):
        """Save settings to config"""
        # Map combo box to provider name
        provider_text = self.provider_combo.currentText()
        provider_map = {
            "Ollama (Local)": "ollama",
            "OpenAI": "openai",
            "Google Gemini": "gemini"
        }
        provider = provider_map.get(provider_text, "ollama")
        
        # Save provider
        cfg.set('provider', provider)
        
        # Save Ollama settings
        cfg.set('ollama_url', self.ollama_url_input.text())
        cfg.set('model', self.model_input.text())
        
        # Save API keys
        api_keys = {
            'openai': self.openai_key_input.text(),
            'gemini': self.gemini_key_input.text()
        }
        cfg.set('api_keys', api_keys)
        
        print("Settings saved successfully!")
        self.close()
    
    def _apply_styles(self):
        """Apply dark theme styles"""
        self.setStyleSheet("""
            QWidget#SettingsWindow {
                background-color: #1e1e1e;
                color: #fff;
            }
            QLabel {
                color: #ccc;
                font-size: 12px;
            }
            QGroupBox {
                color: #fff;
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                color: #fff;
            }
            QLineEdit:focus {
                border: 1px solid #00ff00;
            }
            QComboBox {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px;
                color: #fff;
            }
            QComboBox:hover {
                border: 1px solid #666;
            }
            QComboBox::drop-down {
                border: none;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #444;
                border-radius: 5px;
                padding: 8px 20px;
                color: #fff;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #333;
                border: 1px solid #00ff00;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
        """)


def main():
    """Test the settings window independently"""
    app = QApplication(sys.argv)
    
    window = SettingsWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
