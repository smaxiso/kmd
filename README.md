# Kmd - AI Command Assistant 🚀

A professional desktop application that uses AI to generate terminal commands from natural language queries. Summon it anywhere with a global hotkey, describe what you want, and get the exact command instantly.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Qt](https://img.shields.io/badge/UI-PySide6-red)

## ✨ Features

- **🔥 Global Hotkey**: Press `Ctrl+Shift+Space` anywhere to summon the floating search bar
- **🤖 Multi-Provider AI**: Supports Ollama (local), OpenAI, and Google Gemini
- **⚡ Lightning Fast**: Async processing with worker threads - UI never freezes
- **🎨 Beautiful UI**: Raycast-style dark theme with frameless, transparent window
- **📋 Auto-Copy**: Generated commands are automatically copied to clipboard
- **🔄 System Tray**: Runs in background with tray icon
- **⚙️ Configurable**: JSON-based configuration in `~/.Kmd/config.json`

## 🎯 Quick Start

### Prerequisites

- Python 3.10 or higher
- Ollama running locally (or OpenAI/Gemini API keys)

### Installation

1. **Clone or navigate to the repository:**
   ```bash
   cd ~/workspace/kmd
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Ollama** (if using local AI):
   ```bash
   ollama serve
   ```

4. **Run Kmd:**
   ```bash
   python src/main.py
   ```

5. **Use the app:**
   - Press `Ctrl+Shift+Space` to summon
   - Type your query (e.g., "find all python files")
   - Press Enter
   - Command is generated and copied to clipboard!

## 🏗️ Architecture

```
Kmd/
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration manager
│   ├── core/
│   │   ├── hotkey_listener.py  # Global keyboard hooks
│   │   └── system_tray.py      # System tray icon
│   ├── services/
│   │   ├── ai_engine.py     # AI provider abstraction
│   │   └── clipboard.py     # Clipboard operations
│   └── ui/
│       ├── spotlight_window.py # Main floating window
│       └── styles.qss          # Qt stylesheet
├── tests/
└── requirements.txt
```

## ⚙️ Configuration

Configuration is stored in `~/.Kmd/config.json`:

```json
{
    "provider": "ollama",
    "api_keys": {
        "openai": "",
        "gemini": ""
    },
    "ollama_url": "http://localhost:11434",
    "model": "llama3.2",
    "hotkey": "ctrl+shift+space",
    "theme": "dark"
}
```

### Switching Providers

**For Ollama (Local - Free):**
```bash
# Already configured by default
# Just make sure Ollama is running: ollama serve
```

**For OpenAI:**
1. Edit `~/.Kmd/config.json`
2. Set `"provider": "openai"`
3. Add your API key: `"openai": "sk-..."`

**For Gemini:**
1. Edit `~/.Kmd/config.json`
2. Set `"provider": "gemini"`
3. Add your API key: `"gemini": "YOUR_KEY"`



## 🎮 Usage Examples

| Query                        | Generated Command                |
|------------------------------|----------------------------------|
| list all files               | `ls -la`                         |
| find python files            | `find . -name "*.py"`            |
| disk usage                   | `df -h`                          |
| kill process on port 3000    | `lsof -ti:3000 \| xargs kill -9` |
| git status                   | `git status`                     |

## 🐛 Troubleshooting


### "Ollama not running" error

```bash
# Start Ollama in a separate terminal
ollama serve
```


### Hotkey not working

- The app requires proper permissions for global hotkeys
- On Linux, you may need to run with appropriate permissions
- Check if another app is using `Ctrl+Shift+Space`


### PySide6 / Qt display issues in WSL

```bash
# Install X server for Windows (e.g., VcXsrv)
# Set DISPLAY environment variable
export DISPLAY=:0
```


### Dependencies installation failed

```bash
# Make sure pip is up to date
pip install --upgrade pip

# Install dependencies one by one to identify issues
pip install PySide6
pip install keyboard
pip install pystray
```

## 🔧 Development


### Running Tests

```bash
# Test configuration manager
python src/config.py

# Test AI engine
python src/services/ai_engine.py

# Test spotlight window (standalone)
python src/ui/spotlight_window.py

# Test hotkey listener
python src/core/hotkey_listener.py
```

### Adding a New AI Provider


1. Create a new class in `src/services/ai_engine.py`:

```python
class ClaudeProvider(AIProvider):
    def generate_command(self, query: str) -> str:
        # Implementation
        pass
```

2. Add to the factory function:

```python
def get_provider() -> AIProvider:
    providers = {
        'claude': ClaudeProvider,
        # Add your provider here
    }
```


## 📦 Future Enhancements

- [x] Settings UI window
- [x] Custom hotkey configuration via GUI (via config file)
- [ ] Command history
- [ ] Favorite commands
- [ ] Plugin system
- [ ] Context awareness (detect focused app)
- [ ] Voice input mode
- [x] Package as executable (PyInstaller)
- [ ] Auto-updater

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! This is a personal project but feel free to fork and customize.

---


---

Made with ❤️ for developers who love the command line
