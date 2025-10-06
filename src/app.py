"""
This file contains the main application class.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

from src.core.config import TAB_BG_INACTIVE, TAB_BG_ACTIVE, TAB_TEXT_INACTIVE
from src.ui.views.pass_config_view import create_pass_config_frame
from src.ui.views.json_config_view import create_json_config_frame
from src.services.obfuscation_service import start_obfuscation_placeholder
from src.services.pdf_service import save_report_placeholder, view_pdf
from src.utils.file_operations import save_obfuscated_file_placeholder

class ObfuscationApp:
    def __init__(self, root):
        # 1. Main Window Setup
        self.root = root
        self.root.title("RMOR")
        script_dir = os.path.dirname(__file__)
        icon_path = os.path.join(script_dir, "..", "..", "logo.ico")
        self.root.iconbitmap(icon_path)
        self.root.geometry("740x560")
        self.root.resizable(True, True)

        # Apply CustomTkinter Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Configure Grid for a single, expanding vertical column
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) # The config area should expand

        # --- State Attributes ---
        self.config_mode = "passes"
        self.attached_filepath = None
        self.final_report_content = None # To store the generated report text
        self.report_filepath = os.path.join("artifacts", "obfuscation_report.pdf")
        self.platform_var = tk.StringVar(value="Windows x64 (64-bit)")

        # --- Pass Configuration Attributes ---
        self.properties_frames = {}
        self.seed_labels = {}
        self.property_widgets = {}
        self.pass_display = {}

        # ==============================================================================
        # --- 2. Main Vertical Layout
        # ==============================================================================

        # --- File Attachment Area ---
        file_header_frame = ctk.CTkFrame(root, fg_color="transparent")
        file_header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        file_header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(file_header_frame, text="Attach Code File", command=self.load_code_file, width=150).grid(row=0, column=0, sticky="w")
        
        self.file_name_label = ctk.CTkLabel(file_header_frame, text="No file attached.", font=ctk.CTkFont(family='Helvetica', size=12, slant='italic'), text_color="gray")
        self.file_name_label.grid(row=0, column=1, sticky="w", padx=15)
        
        # --- Configuration Tabs and Panels ---
        self.config_container = ctk.CTkFrame(root, corner_radius=8)
        self.config_container.grid(row=1, column=0, sticky="nsew", pady=(0, 15), padx=15)
        self.config_container.grid_columnconfigure(0, weight=1)
        self.config_container.grid_columnconfigure(1, weight=1)
        self.config_container.grid_rowconfigure(1, weight=1) 

        # --- Tab Selector ---
        self.tab_passes = ctk.CTkButton(self.config_container, text="Checkbox Pass Configuration", command=lambda: self.toggle_config_mode('passes'),
                                        fg_color=TAB_BG_ACTIVE[1], text_color=TAB_TEXT_INACTIVE[1], hover_color=TAB_BG_ACTIVE[1],
                                        corner_radius=6, height=35)
        self.tab_passes.grid(row=0, column=0, sticky="ew", padx=(5, 2), pady=5)
        
        self.tab_json = ctk.CTkButton(self.config_container, text="Custom JSON Configuration", command=lambda: self.toggle_config_mode('json'),
                                      fg_color=TAB_BG_INACTIVE[1], text_color=TAB_TEXT_INACTIVE[1], hover_color=TAB_BG_INACTIVE[1],
                                      corner_radius=6, height=35)
        self.tab_json.grid(row=0, column=1, sticky="ew", padx=(2, 5), pady=5)

        # --- Fixed Size Content Area for Configs ---
        self.config_area_frame = ctk.CTkFrame(self.config_container, corner_radius=6, fg_color="transparent")
        self.config_area_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))
        self.config_area_frame.grid_columnconfigure(0, weight=1)
        self.config_area_frame.grid_rowconfigure(0, weight=1)

        # Create configuration sub-frames
        self.json_config_frame, self.json_config_text = create_json_config_frame(self.config_area_frame, self.load_json_file)
        self.pass_config_frame, self.pass_vars, self.loop_entries, self.seed_entries, self.property_widgets, self.pass_display, self.properties_frames, self.seed_labels, self.common_seed_var, self.common_seed_entry = create_pass_config_frame(self.config_area_frame, self.toggle_pass_visibility, self.toggle_common_seed, self.update_json_from_passes)

        # Initially show the passes configuration panel
        self.pass_config_frame.grid(row=0, column=0, sticky="nsew")

        for key in self.pass_vars:
            self.toggle_pass_visibility(key, show=False)

        # --- Platform Selection ---
        platform_frame = ctk.CTkFrame(root, fg_color="transparent")
        platform_frame.grid(row=2, column=0, sticky="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(platform_frame, text="Target Platform:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.platform_dropdown = ctk.CTkOptionMenu(platform_frame, values=["Windows x64 (64-bit)", "Windows x86 (32-bit)","Windows on Arm (ARM64)","Linux x86_64","Linux Arm64"], variable=self.platform_var)
        self.platform_dropdown.grid(row=0, column=1, sticky="w")
        self.platform_var.trace('w', lambda *args: self.update_json_from_passes())

        # --- Control Button ---
        self.start_button = ctk.CTkButton(root, text="Start Obfuscation", command=self.start_obfuscation, font=ctk.CTkFont(family='Helvetica', size=15, weight='bold'))
        self.start_button.grid(row=3, column=0, sticky="ew", pady=15, padx=15)
        
        # --- Save Buttons ---
        button_frame = ctk.CTkFrame(root, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="w", padx=15, pady=(0, 15))
        
        self.save_button = ctk.CTkButton(button_frame, text="Generate obfuscated object file", command=self.save_obfuscated_file, state="disabled", fg_color="green", hover_color="darkgreen")
        self.save_button.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.save_report_button = ctk.CTkButton(button_frame, text="Save Report as PDF", command=self.save_report, state="disabled")
        self.save_report_button.grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        self.view_pdf_button = ctk.CTkButton(button_frame, text="View PDF Report", command=self.view_pdf, state="disabled")
        self.view_pdf_button.grid(row=0, column=2, sticky="w")

        # --- Final Initialization ---
        self.update_json_from_passes() # Sync JSON with default passes view

    def update_json_from_passes(self):
        """Updates the JSON text based on the checkbox configuration, using the new format."""
        final_config = {
            "input_file": self.attached_filepath if self.attached_filepath else "path/to/source.c",
            "platform": self.platform_var.get(),
            "passes": []
        }
        use_common_seed = self.common_seed_var.get()
        common_seed_str = self.common_seed_entry.get() if use_common_seed else None

        for key in self.pass_vars:
            try:
                is_enabled = self.pass_vars[key].get()
                params = {}
                
                # Get cycles
                params["cycles"] = int(self.loop_entries[key].get() or 1)
                
                # Get seed
                seed_str = common_seed_str if use_common_seed and is_enabled else self.seed_entries[key].get()
                params["seed"] = int(seed_str) if seed_str else 0
                
                # Get other properties
                for prop_id, info in self.property_widgets.get(key, {}).items():
                    widget = info["widget"]
                    if info["type"] == "str": value = widget.get()
                    elif info["type"] == "bool": value = widget.get()
                    elif info["type"] == "int": value = int(widget.get() or "0")
                    else: value = None
                    params[prop_id] = value

                final_config["passes"].append({
                    "name": key,
                    "enabled": is_enabled,
                    "params": params
                })
            except (ValueError, KeyError):
                # If a value is invalid during sync, skip this pass in the JSON
                continue
                
        json_str = json.dumps(final_config, indent=4)
        current_text = self.json_config_text.get(1.0, tk.END).strip()
        # Only update if text is different to avoid cursor reset on every keypress
        if current_text != json_str.strip():
            self.json_config_text.delete(1.0, tk.END)
            self.json_config_text.insert(tk.END, json_str)

    def toggle_pass_visibility(self, key, show=None):
        """Toggles visibility of pass details when checkbox is toggled."""
        if show is None: show = self.pass_vars[key].get()
        frame = self.properties_frames[key]
        
        if show:
            frame.grid(row=1, column=0, sticky="ew", padx=0, pady=2) # Use padx=0 for alignment
            if not self.common_seed_var.get():
                self.seed_labels[key].grid(row=1, column=0, sticky="w", padx=30, pady=2)
                self.seed_entries[key].grid(row=1, column=1, sticky="w", padx=5, pady=2)
            else:
                self.seed_labels[key].grid_remove()
                self.seed_entries[key].grid_remove()
        else:
            frame.grid_forget()
            
        self.update_json_from_passes()

    def toggle_common_seed(self):
        """Toggles between common seed and individual seeds."""
        use_common = self.common_seed_var.get()
        if use_common:
             self.common_seed_entry.grid()
        else:
             self.common_seed_entry.grid_remove()

        for key, var in self.pass_vars.items():
            if var.get(): # Update visibility only for active passes
                self.toggle_pass_visibility(key, show=True)
                
        self.update_json_from_passes()

    # --- File Loading Helper Functions ---
    def load_code_file(self):
        filepath = filedialog.askopenfilename(defaultextension=".cpp", filetypes=[("C/C++ files", "*.c *.cpp *.h *.hpp"), ("All files", "*.*")])
        if filepath:
            self.attached_filepath = filepath
            filename = os.path.basename(filepath)
            self.file_name_label.configure(text=filename, text_color=("#333333", "#D4D4D4"), font=ctk.CTkFont(family='Helvetica', size=12, slant='roman'))
            print(f"C/C++ code loaded from: {filename}")
            self.update_json_from_passes() # Update JSON with new file path

    def load_json_file(self):
        filepath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    json.loads(content) # Validate JSON
                    self.json_config_text.delete(1.0, tk.END)
                    self.json_config_text.insert(tk.END, content)
                    print(f"JSON configuration loaded from: {os.path.basename(filepath)}")
            except json.JSONDecodeError: messagebox.showerror("File Error", "The selected file is not valid JSON.")
            except Exception as e: messagebox.showerror("File Error", f"Could not read file: {e}")

    # --- UI Toggle Function ---
    def toggle_config_mode(self, mode):
        if mode == self.config_mode: return
        is_dark = ctk.get_appearance_mode() == "Dark"
        if mode == "json":
            self.pass_config_frame.grid_forget()
            self.json_config_frame.grid(row=0, column=0, sticky="nsew")
            self.tab_json.configure(fg_color=TAB_BG_ACTIVE[is_dark], hover_color=TAB_BG_ACTIVE[is_dark])
            self.tab_passes.configure(fg_color=TAB_BG_INACTIVE[is_dark], hover_color=TAB_BG_INACTIVE[is_dark])
        else: # passes
            self.json_config_frame.grid_forget()
            self.pass_config_frame.grid(row=0, column=0, sticky="nsew")
            self.tab_passes.configure(fg_color=TAB_BG_ACTIVE[is_dark], hover_color=TAB_BG_ACTIVE[is_dark])
            self.tab_json.configure(fg_color=TAB_BG_INACTIVE[is_dark], hover_color=TAB_BG_INACTIVE[is_dark])
            self.update_json_from_passes()
        self.config_mode = mode

    # --- Main Action and Placeholder Functions ---
    def start_obfuscation(self):
        """Simulates the start of the obfuscation process."""
        if not self.attached_filepath:
            messagebox.showerror("Input Error", "Please attach a C/C++ code file before starting.")
            return

        self.start_button.configure(state="disabled", text="Obfuscating...")
        self.root.update_idletasks()
        
        config_data = {}
        try:
            json_input = self.json_config_text.get("1.0", tk.END).strip()
            config_data = json.loads(json_input)
            if not config_data.get("passes"):
                 messagebox.showinfo("Info", "Configuration has no passes defined. Process aborted.")
                 self.reset_gui()
                 return
        except json.JSONDecodeError:
            messagebox.showerror("Input Error", "Invalid JSON configuration provided.")
            self.reset_gui()
            return
        
        # Filter for enabled passes
        enabled_passes = [p for p in config_data["passes"] if p.get("enabled")]
        if not enabled_passes:
            messagebox.showinfo("Info", "No passes are enabled. Process aborted.")
            self.reset_gui()
            return
        
        self.final_report_content = start_obfuscation_placeholder(config_data, self.pass_display)
        print("Report available and obfuscated file generated. Ready to save.")
        self.save_button.configure(state="normal")
        self.save_report_button.configure(state="normal") 
        self.start_button.configure(text="Start Obfuscation", state="normal")

    def save_report(self):
        """Saves the generated report content to a PDF file."""
        self.save_report_button.configure(state="disabled", text="Saving...")
        self.root.update_idletasks()
        if save_report_placeholder(self.final_report_content, self.report_filepath):
            self.view_pdf_button.configure(state="normal")
        self.save_report_button.configure(state="normal", text="Save Report as PDF")

    def view_pdf(self):
        """Opens the saved PDF report using the system's default viewer."""
        view_pdf(self.report_filepath)

    def save_obfuscated_file(self):
        """Simulates saving the final obfuscated file."""
        self.save_button.configure(state="disabled", text="Saving...")
        self.root.update_idletasks()
        
        def complete():
            save_obfuscated_file_placeholder()
            self.save_button.configure(state="normal", text="Generate obfuscated object file")
        self.root.after(1000, complete)

    def reset_gui(self):
        """Resets the state of the GUI."""
        self.start_button.configure(text="Start Obfuscation", state="normal")
        self.save_button.configure(state="disabled")
        self.save_report_button.configure(state="disabled") 
        self.view_pdf_button.configure(state="disabled")
        self.final_report_content = None
        print("Process reset. Awaiting user input...")
