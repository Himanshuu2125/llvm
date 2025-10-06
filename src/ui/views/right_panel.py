import time
import customtkinter as ctk
import tkinter as tk
from src.ui.widgets.pass_config import create_pass_config_frame
from src.ui.widgets.json_config import create_json_config_frame
from src.core.config import TAB_BG_ACTIVE, TAB_BG_INACTIVE, TAB_TEXT_INACTIVE

def create_right_pane(parent, app):
    right_pane = ctk.CTkFrame(parent, corner_radius=10)
    right_pane.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    right_pane.grid_columnconfigure(0, weight=1)
    right_pane.grid_rowconfigure(5, weight=1)
    
    app.config_container = ctk.CTkFrame(right_pane, corner_radius=8)
    app.config_container.grid(row=0, column=0, sticky="ew", pady=(15, 0), padx=15)
    app.config_container.grid_columnconfigure(0, weight=1)
    app.config_container.grid_columnconfigure(1, weight=1)
    app.config_container.grid_rowconfigure(1, weight=1)

    app.tab_passes = ctk.CTkButton(
        app.config_container,
        text="Checkbox Pass Configuration",
        command=lambda: app.toggle_config_mode('passes'),
        fg_color=TAB_BG_ACTIVE[ctk.get_appearance_mode() == "Dark"], 
        text_color=TAB_TEXT_INACTIVE[ctk.get_appearance_mode() == "Dark"], 
        hover_color=TAB_BG_ACTIVE[ctk.get_appearance_mode() == "Dark"],
        corner_radius=6,
        height=35
    )
    app.tab_passes.grid(row=0, column=0, sticky="ew", padx=(5, 2), pady=5)
    
    app.tab_json = ctk.CTkButton(
        app.config_container,
        text="Custom JSON Configuration",
        command=lambda: app.toggle_config_mode('json'),
        fg_color=TAB_BG_INACTIVE[ctk.get_appearance_mode() == "Dark"], 
        text_color=TAB_TEXT_INACTIVE[ctk.get_appearance_mode() == "Dark"],
        hover_color=TAB_BG_INACTIVE[ctk.get_appearance_mode() == "Dark"],
        corner_radius=6,
        height=35
    )
    app.tab_json.grid(row=0, column=1, sticky="ew", padx=(2, 5), pady=5)

    app.config_area_frame = ctk.CTkFrame(app.config_container, corner_radius=6, height=220, fg_color="transparent")
    app.config_area_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))
    app.config_area_frame.grid_columnconfigure(0, weight=1)
    app.config_area_frame.grid_rowconfigure(0, weight=1)

    app.json_config_frame = create_json_config_frame(app.config_area_frame, app)
    app.pass_config_frame = create_pass_config_frame(app.config_area_frame, app)

    app.pass_config_frame.grid(row=0, column=0, sticky="nsew")
    
    app.start_button = ctk.CTkButton(
        right_pane,
        text="Start Obfuscation",
        command=app.start_obfuscation_placeholder,
        font=ctk.CTkFont(family='Helvetica', size=15, weight='bold')
    )
    app.start_button.grid(row=2, column=0, sticky="ew", pady=(5, 15), padx=15)
    
    ctk.CTkFrame(right_pane, height=2, fg_color="#3a3a3a").grid(row=3, column=0, sticky="ew", padx=15, pady=10)

    ctk.CTkLabel(
        right_pane,
        text="Obfuscation Logs",
        font=ctk.CTkFont(family='Helvetica', size=16, weight='bold')
    ).grid(row=4, column=0, sticky="w", padx=15, pady=(5, 5))
    
    app.log_text = ctk.CTkTextbox(
        right_pane,
        height=15,
        font=('Consolas', 10),
        activate_scrollbars=True,
        corner_radius=8,
        fg_color="#0a0a0a",
        text_color="#00ff00"
    )
    app.log_text.grid(row=5, column=0, sticky="nsew", padx=15, pady=5)
    
    # Initial log lines (use proper time.strftime calls)
    app.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Initializing Obfuscator v1.2...\n")
    app.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Awaiting user input...\n")
    app.log_text.configure(state="disabled")

    return right_pane
