"""
This file contains the JSON configuration view.
"""

import customtkinter as ctk
import tkinter as tk
import json

def create_json_config_frame(parent, load_json_file_callback):
    """Creates and populates the JSON configuration frame."""
    config_frame = ctk.CTkFrame(parent, corner_radius=6, fg_color="transparent")
    config_frame.grid_columnconfigure(0, weight=1)
    config_frame.grid_rowconfigure(1, weight=1) # Let the textbox expand
    
    header_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
    header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 10))
    header_frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(header_frame, text="JSON Configuration Text", font=ctk.CTkFont(family='Helvetica', size=12, weight='bold')).grid(row=0, column=0, sticky="w")
    ctk.CTkButton(header_frame, text="Attach JSON File", command=load_json_file_callback, width=120).grid(row=0, column=1, sticky="e")
    
    json_config_text = ctk.CTkTextbox(config_frame, font=('Consolas', 10), corner_radius=5)
    json_config_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    # Default text matching the new format
    default_json = {
        "input_file": "path/to/source.c",
        "platform": "Windows x64 (64-bit)",
        "passes": [
            {"name": "fla", "enabled": True, "params": {"seed": 12345, "cycles": 1}},
            {"name": "gvenc", "enabled": True, "params": {"keylen": 4, "seed": 0, "process-arrays": True, "cycles": 1}},
            {"name": "indcall", "enabled": False, "params": {"seed": 7, "cycles": 1}},
            {"name": "indbr", "enabled": True, "params": {"seed": 99, "cond-only": False, "cycles": 1}},
            {"name": "alias", "enabled": True, "params": {"seed": 2025, "branch-num": 4, "reuse-getters": False, "cycles": 1}},
            {"name": "bcf", "enabled": True, "params": {"seed": 777, "prob": 30, "cycles": 1}},
            {"name": "sub", "enabled": True, "params": {"seed": 314159, "cycles": 1}},
            {"name": "merge", "enabled": True, "params": {"seed": 888, "ratio": 100, "cycles": 1}},
            {"name": "mba", "enabled": True, "params": {"seed": 999, "linearmba-prob": 100, "linearmba-extra": 5, "cycles": 1}}
        ]
    }
    json_config_text.insert(tk.END, json.dumps(default_json, indent=4))
    return config_frame, json_config_text
