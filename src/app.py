"""
This file contains the main application class.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from dotenv import load_dotenv

from src.core.config import TAB_BG_INACTIVE, TAB_BG_ACTIVE, TAB_TEXT_INACTIVE
from src.ui.views.pass_config_view import create_pass_config_frame
from src.ui.views.json_config_view import create_json_config_frame
from src.services.llvm_service import LLVMService
from src.services.llvm_pass_service import LLVMPassService
from src.services.pdf_fin_service import save_report_placeholder, view_pdf
from src.utils.file_operations import save_obfuscated_file_placeholder
from pathlib import Path

class ObfuscationApp:
    def __init__(self, root):
        # 1. Main Window Setup
        self.root = root
        self.root.title("RMOR")
        script_dir = os.path.dirname(__file__)
        icon_path = os.path.join(script_dir, "..", "logo.ico")
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
        self.obfuscated_filepath = None # To store the path of the obfuscated file
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
                if key == 'bcf':
                    params["boguscfg-seed"] = int(seed_str) if seed_str else 0
                elif key == 'mba':
                    params["linearmba-seed"] = int(seed_str) if seed_str else 0
                else: 
                    params["seed"] = int(seed_str) if seed_str else 0
                
                # Get other properties
                for prop_id, info in self.property_widgets.get(key, {}).items():
                    widget = info["widget"]
                    if info["type"] == "str": value = widget.get()
                    elif info["type"] == "bool": value = widget.get()
                    elif info["type"] == "int": value = int(widget.get() or "0")
                    else: value = None
                    if key == "bcf" and prop_id == "prob":
                        params["boguscfg-prob"] = value
                    else:
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
        """Starts the obfuscation process using LLVM services."""
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

        enabled_passes = [p for p in config_data["passes"] if p.get("enabled")]
        if not enabled_passes:
            messagebox.showinfo("Info", "No passes are enabled. Process aborted.")
            self.reset_gui()
            return

        try:
            # 1. Initialize services
            load_dotenv()
            clang_path = os.getenv("CLANG_PATH")
            print(clang_path)
            llvm_service = LLVMService(clang_path)
            llvm_pass_service = LLVMPassService(clang_path)

            # 2. Compile to bytecode
            input_path = Path(self.attached_filepath)
            bytecode_path = input_path.with_suffix(".bc")
            llvm_service.compile_to_bytecode(str(input_path), str(bytecode_path))

            # 3. Apply passes
            obfuscated_path = input_path.with_name(f"{input_path.stem}_obf.bc")
            llvm_pass_service.apply_json_conf(config_data, str(bytecode_path), str(obfuscated_path))

            # 4. Store results
            self.final_report_content = llvm_pass_service.stats
            self.obfuscated_filepath = str(obfuscated_path)

            print("Report available and obfuscated file generated. Ready to save.")
            self.save_button.configure(state="normal")
            self.save_report_button.configure(state="normal")
            messagebox.showinfo("Success", f"File Obfuscation Completed Successfully")
        except Exception as e:
            messagebox.showerror("Obfuscation Error", f"An error occurred: {e}")
        finally:
            self.start_button.configure(text="Start Obfuscation", state="normal")


    def save_report(self):
        """Saves the generated report content to a PDF file."""
        if not self.final_report_content:
            messagebox.showerror("Report Error", "No report content to save.")
            return

        self.save_report_button.configure(state="disabled", text="Saving...")
        self.root.update_idletasks()

        # Create a new ordered dictionary for the report
        ordered_report_data = {}

        # Add input file parameters first
        if self.attached_filepath:
            try:
                file_size = str(os.path.getsize(self.attached_filepath))+" bytes"
                file_name = os.path.basename(self.attached_filepath)
                obf_file_size = str(os.path.getsize(self.obfuscated_filepath))+" bytes"
                obf_file_name = os.path.basename(self.obfuscated_filepath)
                
                file_type = os.path.splitext(file_name)[1].upper().replace(".", "")
                if not file_type:
                    file_type = "Unknown"
                elif file_type == "CPP":
                    file_type = "C++"
                
                ordered_report_data["input file parameters"] = {
                    "filename": file_name,
                    "filesize": file_size,
                    "filetype": file_type,
                }
                ordered_report_data["output file parameters"] = {
                    "filename": obf_file_name,
                    "filesize": obf_file_size,
                }
            except Exception as e:
                print(f"Could not add input file parameters: {e}")

        # Deep copy the original report content to avoid modifying it
        original_report_data = json.loads(json.dumps(self.final_report_content))

        # Add the rest of the report data, excluding unwanted keys
        for key, value in original_report_data.items():
            if key not in ["bitcode-reader", "file-search"]:
                ordered_report_data[key] = value

        if save_report_placeholder(ordered_report_data, self.report_filepath):
            self.view_pdf_button.configure(state="normal")
        
        self.save_report_button.configure(state="normal", text="Save Report as PDF")

    def view_pdf(self):
        """Opens the saved PDF report using the system's default viewer."""
        view_pdf(self.report_filepath)

    def save_obfuscated_file(self):
        """Saves the obfuscated file to a user-specified location."""
        if not self.obfuscated_filepath:
            messagebox.showerror("Save Error", "No obfuscated file to save.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".bc",
            filetypes=[("LLVM bytecode", "*.bc"), ("All files", "*.*")],
            initialfile=Path(self.obfuscated_filepath).name,
        )
        if not filepath:
            return

        self.save_button.configure(state="disabled", text="Saving...")
        self.root.update_idletasks()

        try:
            import shutil
            shutil.copy(self.obfuscated_filepath, filepath)
            messagebox.showinfo("Success", f"Obfuscated file saved to: {filepath}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")
        finally:
            self.save_button.configure(state="normal", text="Generate obfuscated object file")


    def reset_gui(self):
        """Resets the state of the GUI."""
        self.start_button.configure(text="Start Obfuscation", state="normal")
        self.save_button.configure(state="disabled")
        self.save_report_button.configure(state="disabled") 
        self.view_pdf_button.configure(state="disabled")
        self.final_report_content = None
        print("Process reset. Awaiting user input...")
