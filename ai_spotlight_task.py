import tkinter as tk
import keyboard
import threading
import requests
import json
import sys

# CONFIGURATION
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2" # Matches the model you have installed

def get_ai_command(user_query):
    """Sends query to local Ollama instance in WSL"""
    clean_query = user_query.strip()
    if not clean_query:
        return ""

    # Strict prompt to force ONLY code output
    system_instruction = (
        "You are a command line expert. The user needs a terminal command. "
        "Return ONLY the exact command string. Do not use markdown. "
        "Do not explain. Do not add quotes. "
        "Example User: 'list files' -> Response: ls -la"
    )
    
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_instruction}\nUser: {clean_query}\nResponse:",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json().get('response', '').strip()
        # Clean up any accidental markdown code blocks if the model hallucinates them
        return result.replace('```bash', '').replace('```', '').strip()
    except requests.exceptions.ConnectionError:
        return "# Error: Ensure Ollama is running in WSL (curl localhost:11434)"
    except Exception as e:
        return f"# Error: {str(e)}"

class FloatingAI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() # Start hidden
        
        # Window Configuration (Frameless, On Top)
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg="#1e1e1e")
        
        # Dimensions and Centering
        window_width = 700
        window_height = 60
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_c = int((screen_width / 2) - (window_width / 2))
        y_c = int(screen_height / 4) # Position at top quarter of screen
        self.root.geometry(f"{window_width}x{window_height}+{x_c}+{y_c}")

        # --- CLOSE BUTTON (Right Side) ---
        self.close_btn = tk.Button(self.root, text="×", font=("Arial", 20), 
                                   bg="#1e1e1e", fg="#888", bd=0, 
                                   activebackground="#333", activeforeground="#fff",
                                   command=self.hide_window, cursor="hand2")
        self.close_btn.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))

        # --- INPUT FIELD (Left Side) ---
        self.entry = tk.Entry(self.root, font=("Consolas", 16), bg="#1e1e1e", fg="#00ff00", 
                              bd=0, insertbackground="white")
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(15, 5), pady=10)
        
        # Bindings
        self.entry.bind("<Return>", self.on_submit)
        
        # Bind Escape to the ROOT window so it catches it everywhere
        self.root.bind("<Escape>", self.hide_window)
        
        # Focus out hook (auto-hide if you click away)
        self.root.bind("<FocusOut>", self.hide_window)

    def show_window(self):
        self.root.deiconify()
        self.entry.delete(0, tk.END)
        self.entry.focus_force() # Force focus so typing starts immediately

    def hide_window(self, event=None):
        self.root.withdraw()

    def on_submit(self, event):
        query = self.entry.get()
        
        # --- KILL SWITCH ---
        # Typing 'exit' or 'quit' kills the background process
        if query.lower() in ['exit', 'quit']:
            self.root.destroy()
            sys.exit()

        self.entry.delete(0, tk.END)
        self.entry.insert(0, "Thinking...")
        self.root.update() # Force UI refresh

        command = get_ai_command(query)
        
        self.entry.delete(0, tk.END)
        self.entry.insert(0, command)
        
        # Auto-copy to clipboard
        try:
            import pyperclip
            pyperclip.copy(command)
        except ImportError:
            pass # pyperclip not installed

def listen_for_hotkey(app):
    # HOTKEY: Ctrl + Shift + Space
    # Note: On Windows, this hooks globally. 
    try:
        keyboard.add_hotkey('ctrl+shift+space', app.show_window)
        keyboard.wait()
    except ImportError:
        print("Error: 'keyboard' module requires root/admin on some systems.")

if __name__ == "__main__":
    app = FloatingAI()
    
    # Run hotkey listener in separate thread
    t = threading.Thread(target=listen_for_hotkey, args=(app,), daemon=True)
    t.start()
    
    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        sys.exit()