import time
import tkinter as tk

def log_message(app, message):
    app.log_text.configure(state="normal")
    app.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
    app.log_text.see(tk.END)
    app.log_text.configure(state="disabled")
    app.root.update_idletasks()
