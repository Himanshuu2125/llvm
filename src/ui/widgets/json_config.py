import customtkinter as ctk
import tkinter as tk
from src.utils.file_operations import load_json_file

def create_json_config_frame(parent, app):
    config_frame = ctk.CTkFrame(parent, corner_radius=6, fg_color="transparent")
    config_frame.grid_columnconfigure(0, weight=1)
    
    header_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 2))
    header_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(header_frame, text="JSON Configuration Text", font=ctk.CTkFont(family='Helvetica', size=12, weight='bold')).grid(row=0, column=0, sticky="w")
    
    ctk.CTkButton(header_frame, text="Attach JSON File", command=lambda: load_json_file(app), width=120).grid(row=0, column=1, sticky="e", padx=(10, 0))

    ctk.CTkLabel(config_frame, text="Define pass settings (e.g., {'fla': {'loops': 1, 'seed': 42, 'properties': {}}})", font=ctk.CTkFont(family='Helvetica', size=11)).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 2))
    
    app.json_config_text = ctk.CTkTextbox(config_frame, height=150, font=('Consolas', 9), corner_radius=5)
    app.json_config_text.grid(row=2, column=0, sticky="ew", padx=10, pady=(2, 10))
    app.json_config_text.insert(tk.END, '''{
  "fla": {
    "loops": 1,
    "seed": 42,
    "properties": {}
  }
}''')
    
    return config_frame