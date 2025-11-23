This is a comprehensive architectural document and implementation guide to transforming your simple Python script into **"Kmd"**, a professional, OS-level application for Windows and macOS.

To achieve **Best UI**, **Performance**, and **Scalability**, we will move away from `tkinter` (which is limited) to **PySide6 (Qt)**. Qt is the industry standard for Python desktop apps; it allows for transparency, rounded corners, CSS-like styling, and high-performance rendering.

-----

# 🚀 Project Kmd: Architecture & Implementation Guide

## 1\. The Technology Stack

To ensure the app is lightweight yet powerful, we will use the following stack:

* **Language:** Python 3.10+
* **GUI Framework:** **PySide6 (Qt)**. *Why?* Native look, GPU acceleration, CSS styling, and support for complex layouts.
* **System Hooks:** `pynput` or `keyboard` (Global Hotkeys), `pystray` (System Tray Icon).
* **State Management:** `pydantic` (Robust configuration & data validation).
* **Packaging:** `PyInstaller` (Bundling) + `Inno Setup` (Windows Installer) / `DMG` (macOS).
* **AI Layer:** Abstract Factory Pattern (Seamless switching between OpenAI, Gemini, Ollama).

-----

## 2\. Scalable Folder Structure

Do not put everything in one file. A scalable app requires separation of concerns.

```text
Kmd/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Settings manager (JSON/Env handling)
│   ├── core/
│   │   ├── hotkey_listener.py  # Global keyboard hooks
│   │   └── system_tray.py      # Tray icon & context menu
│   ├── services/
│   │   ├── ai_engine.py     # The "Brain" (Provider logic)
│   │   └── clipboard.py     # Clipboard manager
│   └── ui/
│       ├── spotlight_window.py # The main floating bar
│       ├── settings_window.py  # Configuration UI
│       └── styles.qss          # CSS styling for the app
├── assets/
│   └── icon.ico             # App Icon
├── tests/                   # Unit tests
└── requirements.txt
```

-----

## 3\. Implementation: The Backend (Logic Layer)

### A. The Configuration Manager (`src/config.py`)

This handles saving API keys securely to a JSON file in the user's AppData folder, so settings persist after restarts.

```python
import json
import os
from pathlib import Path

APP_NAME = "KmdAI"
CONFIG_DIR = Path.home() / ".Kmd"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "provider": "ollama", # ollama, openai, gemini
    "api_keys": {
        "openai": "",
        "gemini": ""
    },
    "ollama_url": "http://localhost:11434",
    "model": "llama3.2"
}

class ConfigManager:
    def __init__(self):
        self._ensure_config_exists()
        self.config = self._load_config()

    def _ensure_config_exists(self):
        if not CONFIG_DIR.exists():
            CONFIG_DIR.mkdir(parents=True)
        if not CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)

    def _load_config(self):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

# Singleton instance
cfg = ConfigManager()
```

### B. The AI Engine (`src/services/ai_engine.py`)

This uses the **Strategy Pattern**. It allows you to add Claude, Groq, or HuggingFace later without breaking existing code.

```python
from abc import ABC, abstractmethod
import requests
from src.config import cfg

# 1. The Interface
class AIProvider(ABC):
    @abstractmethod
    def generate_command(self, query: str) -> str:
        pass

# 2. Concrete Implementations
class OllamaProvider(AIProvider):
    def generate_command(self, query: str):
        url = f"{cfg.get('ollama_url')}/api/generate"
        prompt = f"Return CLI command only for: {query}"
        try:
            res = requests.post(url, json={"model": cfg.get("model"), "prompt": prompt, "stream": False})
            return res.json()['response'].strip()
        except:
            return "Error: Check Ollama connection."

class OpenAIProvider(AIProvider):
    def generate_command(self, query: str):
        key = cfg.get("api_keys")['openai']
        if not key: return "Error: Missing OpenAI API Key"
        # ... (Implementation similar to previous chat) ...
        return "git status" # Placeholder

class GeminiProvider(AIProvider):
    def generate_command(self, query: str):
        key = cfg.get("api_keys")['gemini']
        # ... (Gemini Implementation) ...
        return "ls -la" # Placeholder

# 3. The Factory
def get_provider():
    provider_name = cfg.get("provider")
    if provider_name == "openai": return OpenAIProvider()
    if provider_name == "gemini": return GeminiProvider()
    return OllamaProvider()
```

-----

## 4\. Implementation: The Frontend (Best UI)

We use **PySide6** to create a window that looks like Raycast (Dark, semi-transparent, frameless).

### A. The Floating Window (`src/ui/spotlight_window.py`)

```python
import sys
from PySide6.QtWidgets import QApplication, QLineEdit, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QColor, QPalette
from src.services.ai_engine import get_provider

class WorkerThread(QThread):
    result_ready = Signal(str)
    def __init__(self, query):
        super().__init__()
        self.query = query
    def run(self):
        provider = get_provider()
        cmd = provider.generate_command(self.query)
        self.result_ready.emit(cmd)

class SpotlightWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # UI Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Input Field
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask AI for a command...")
        self.input.setFont(QFont("Segoe UI", 16))
        self.input.returnPressed.connect(self.process_query)
        self.layout.addWidget(self.input)

        # Styling (CSS)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 10px;
            }
            QLineEdit {
                background-color: transparent;
                border: none;
                color: white;
                padding: 10px;
            }
        """)
        
        # Positioning
        self.resize(700, 70)
        self.center_window()

    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() // 4
        self.move(x, y)

    def process_query(self):
        query = self.input.text()
        if query == "exit":
            sys.exit()
        
        self.input.setText("Thinking...")
        self.thread = WorkerThread(query)
        self.thread.result_ready.connect(self.on_result)
        self.thread.start()

    def on_result(self, result):
        self.input.setText(result)
        self.input.selectAll()
        # Add clipboard copy logic here
```

-----

## 5\. System Integration (Global Hotkeys)

This is the "glue" that connects the background process to the UI.

### `src/main.py`

```python
import sys
import threading
import keyboard
from PySide6.QtWidgets import QApplication
from src.ui.spotlight_window import SpotlightWindow
from src.core.system_tray import setup_tray # Implementation of pystray

app = QApplication(sys.argv)
window = SpotlightWindow()

def toggle_window():
    if window.isVisible():
        window.hide()
    else:
        window.show()
        window.activateWindow()
        window.input.setFocus()

def start_hotkey_listener():
    # This runs in a background thread to listen for Ctrl+Space
    keyboard.add_hotkey('ctrl+shift+space', toggle_window)
    keyboard.wait()

if __name__ == "__main__":
    # 1. Start Hotkey Thread
    t = threading.Thread(target=start_hotkey_listener, daemon=True)
    t.start()
    
    # 2. Setup System Tray (Optional but recommended)
    # setup_tray(app, window) 

    # 3. Run UI Loop
    sys.exit(app.exec())
```

-----

## 6\. Packaging (Making it Installable)

This is the step that makes it a real "App".

### Step A: Bundle to `.exe` (Windows) or `.app` (Mac)

We use `PyInstaller`. Create a file named `build.spec` (or let PyInstaller generate it) and run:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the Single File Executable
pyinstaller --noconsole --onefile --name="Kmd" --icon=assets/icon.ico src/main.py
```

**Optimization Tip:** To make the app start instantly (Python can be slow to start), look into **Nuitka**. It compiles Python to C++ code.
`python -m nuitka --onefile --windows-disable-console --enable-plugin=pyside6 src/main.py`

### Step B: Create an Installer

**For Windows (Inno Setup):**

1. Download [Inno Setup Compiler](https://jrsoftware.org/isinfo.php).
2. Create a new script.
3. Point it to your `dist/Kmd.exe`.
4. Tick "Create a desktop shortcut" and "Add to startup".
5. Build. You now have `KmdSetup.exe`.

**For macOS:**

1. Use `create-dmg` (a CLI tool) to wrap your `.app` bundle into a drag-and-drop installer.
2. *Note:* You will likely need to sign your app with an Apple Developer ID ($99/year) if you want to distribute it to others without "Unidentified Developer" warnings.

-----

## 7\. Future Scalability & Enhancements

Because we used the **Provider Pattern** and **PySide6**, you can easily add:

1. **Plugins System:** Create a `plugins/` folder where Python scripts can be dropped to add new commands (e.g., "Spotify Control").
2. **Context Awareness:** Pass the currently focused window title (using `pygetwindow`) to the AI prompt.
      * *Prompt:* "User is in VS Code. They asked 'undo'. What is the command?" -\> Returns `Ctrl+Z`.
      * *Prompt:* "User is in Terminal. They asked 'undo'. What is the command?" -\> Returns `git reset...`.
3. **Voice Mode:** Add a microphone button in `spotlight_window.py` that streams audio to OpenAI Whisper API, then pipes the text to your existing logic.

This architecture ensures your app is robust, looks professional, and is ready for growth.
