# kmd

A floating AI-powered command generator for your terminal.

## Features
- Summon with hotkey (Ctrl+Shift+Space)
- Enter natural language queries (e.g., "list files")
- Returns exact terminal command (e.g., `ls -la`)
- Auto-copies command to clipboard
- Minimal, always-on-top GUI (Tkinter)
- Uses local Ollama instance (configurable model)

## Requirements
- Python 3.x
- Tkinter
- keyboard
- requests
- pyperclip (optional, for clipboard)
- Ollama running locally (see https://ollama.com)

## Usage
1. Start Ollama locally and ensure your model is installed.
2. Run `python ai_spotlight_task.py`.
3. Use Ctrl+Shift+Space to open the floating window.
4. Type your query and get the command instantly.

## Configuration
- Edit `MODEL_NAME` and `OLLAMA_URL` in `ai_spotlight_task.py` as needed.

## License
MIT
