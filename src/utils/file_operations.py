import json
from tkinter import messagebox, filedialog
import tkinter as tk
from src.utils.logging import log_message

def load_code_file(app):
    filepath = filedialog.askopenfilename(
        defaultextension=".cpp",
        filetypes=[("C/C++ files", "*.c *.cpp *.h *.hpp"), ("All files", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                app.code_text.delete(1.0, tk.END)
                app.code_text.insert(tk.END, content)
                log_message(app, f"C/C++ code loaded from: {filepath}")
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read file: {e}")

def load_json_file(app):
    filepath = filedialog.askopenfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                json.loads(content)
                app.json_config_text.delete(1.0, tk.END)
                app.json_config_text.insert(tk.END, content)
                log_message(app, f"JSON configuration loaded from: {filepath}")
        except json.JSONDecodeError:
            messagebox.showerror("File Error", "The selected file is not valid JSON.")
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read file: {e}")
