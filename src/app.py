import customtkinter as ctk
import tkinter as tk
import random
import time
import json
from tkinter import messagebox

from src.core.config import TAB_BG_INACTIVE, TAB_BG_ACTIVE, TAB_TEXT_INACTIVE, PASSES
from src.utils.logging import log_message
from src.ui.views.left_panel import create_left_pane
from src.ui.views.right_panel import create_right_pane

class ObfuscationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("C/C++ Code Obfuscation Tool GUI (CustomTkinter)")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.config_mode = "passes"

        self.properties_frames = {}
        self.seed_labels = {}
        self.property_widgets = {}
        self.pass_display = {}

        self.left_pane = create_left_pane(root, self)
        self.right_pane = create_right_pane(root, self)

        self.update_json_from_passes()
    
    def update_json_from_passes(self):
        config = {}
        use_common_seed = self.common_seed_var.get()
        common_seed_str = self.common_seed_entry.get() if use_common_seed else None

        for key in self.pass_vars:
            if self.pass_vars[key].get():
                display_name = self.pass_display[key]
                try:
                    loops = int(self.loop_entries[key].get() or 1)
                    seed_str = common_seed_str if use_common_seed else self.seed_entries[key].get()
                    seed = int(seed_str) if seed_str else 0

                    properties = {}
                    for prop_id, info in self.property_widgets.get(key, {}).items():
                        w = info["widget"]
                        if info["type"] == "str":
                            properties[prop_id] = w.get()
                        elif info["type"] == "bool":
                            properties[prop_id] = w.get()
                        elif info["type"] == "int":
                            val = w.get() or "0"
                            properties[prop_id] = int(val)

                    pass_config = {
                        "loops": loops,
                        "properties": properties,
                        "seed": seed
                    }
                    config[key] = pass_config
                except ValueError:
                    pass

        json_str = json.dumps(config, indent=2)
        self.json_config_text.delete(1.0, tk.END)
        self.json_config_text.insert(tk.END, json_str)

    def toggle_pass_visibility(self, key, show=None):
        if show is None:
            show = self.pass_vars[key].get()
        frame = self.properties_frames[key]
        if show:
            frame.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
            seed_row = 1
            if not self.common_seed_var.get():
                self.seed_labels[key].grid(row=seed_row, column=0, sticky="w", padx=10, pady=2)
                self.seed_entries[key].grid(row=seed_row, column=1, sticky="w", padx=(5, 0), pady=2)
            else:
                self.seed_labels[key].grid_remove()
                self.seed_entries[key].grid_remove()
        else:
            frame.grid_forget()
        self.update_json_from_passes()

    def toggle_common_seed(self):
        use_common = self.common_seed_var.get()
        if use_common:
            self.common_seed_entry.grid(row=0, column=1, sticky="e")
            for key in self.pass_vars:
                if self.pass_vars[key].get():
                    self.seed_labels[key].grid_remove()
                    self.seed_entries[key].grid_remove()
        else:
            self.common_seed_entry.grid_remove()
            for key in self.pass_vars:
                if self.pass_vars[key].get():
                    self.seed_labels[key].grid(row=1, column=0, sticky="w", padx=10, pady=2)
                    self.seed_entries[key].grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)
        self.update_json_from_passes()

    def toggle_config_mode(self, mode):
        if mode == self.config_mode:
            return

        is_dark = ctk.get_appearance_mode() == "Dark"
        
        if mode == "json":
            self.pass_config_frame.grid_forget()
            self.json_config_frame.grid(row=0, column=0, sticky="nsew")
            self.config_mode = "json"
            
            self.tab_json.configure(fg_color=TAB_BG_ACTIVE[is_dark], hover_color=TAB_BG_ACTIVE[is_dark])
            self.tab_passes.configure(fg_color=TAB_BG_INACTIVE[is_dark], hover_color=TAB_BG_INACTIVE[is_dark])
            log_message(self, "Switched to Custom JSON Configuration mode.")
            
        elif mode == "passes":
            self.json_config_frame.grid_forget()
            self.pass_config_frame.grid(row=0, column=0, sticky="nsew")
            self.config_mode = "passes"
            
            self.tab_passes.configure(fg_color=TAB_BG_ACTIVE[is_dark], hover_color=TAB_BG_ACTIVE[is_dark])
            self.tab_json.configure(fg_color=TAB_BG_INACTIVE[is_dark], hover_color=TAB_BG_INACTIVE[is_dark])
            log_message(self, "Switched to Checkbox Passes Configuration mode.")
            self.update_json_from_passes()

    def start_obfuscation_placeholder(self):
        log_message(self, "Starting obfuscation process...")
        self.start_button.configure(state="disabled", text="Obfuscating...")
        self.save_button.configure(state="disabled")
        self.save_report_button.configure(state="disabled") 
        
        self.report_text.configure(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "--- Demo PDF Report ---\n\nStatus: Running...")
        self.report_text.configure(state="disabled")

        config = {}

        if self.config_mode == 'json':
            json_input = self.json_config_text.get("1.0", tk.END).strip()
            if not json_input or json_input == '{}':
                 log_message(self, "Error: JSON configuration is empty. Process aborted.")
                 self.reset_gui()
                 return
            try:
                config = json.loads(json_input)
                log_message(self, "Using Custom JSON configuration.")
            except json.JSONDecodeError:
                messagebox.showerror("Input Error", "Invalid JSON configuration provided.")
                self.reset_gui()
                return
        
        elif self.config_mode == 'passes':
            use_common_seed = self.common_seed_var.get()
            common_seed_str = self.common_seed_entry.get() if use_common_seed else None

            for key in self.pass_vars:
                if self.pass_vars[key].get():
                    display_name = self.pass_display[key]
                    try:
                        loops = int(self.loop_entries[key].get() or 1)
                        seed_str = common_seed_str if use_common_seed else self.seed_entries[key].get()
                        seed = int(seed_str) if seed_str else 0

                        properties = {}
                        for prop_id, info in self.property_widgets.get(key, {}).items():
                            w = info["widget"]
                            if info["type"] == "str":
                                properties[prop_id] = w.get()
                            elif info["type"] == "bool":
                                properties[prop_id] = w.get()
                            elif info["type"] == "int":
                                val = w.get() or "0"
                                properties[prop_id] = int(val)

                        pass_config = {
                            "loops": loops,
                            "properties": properties,
                            "seed": seed
                        }
                        config[key] = pass_config
                    except ValueError:
                        messagebox.showerror("Input Error", f"Invalid numeric value in configuration for {display_name}.")
                        self.reset_gui()
                        return
            log_message(self, "Using Checkbox Passes configuration.")

        if not config:
            log_message(self, "Error: No passes selected/configured. Process aborted.")
            self.reset_gui()
            return
        
        log_message(self, f"Configuration received: {config}")
        time.sleep(0.5)

        for pass_key, pass_data in config.items():
            display_name = self.pass_display.get(pass_key, pass_key.upper())
            loop_count = pass_data["loops"]
            props_str = ', '.join(f"{k}={v}" for k, v in pass_data.get("properties", {}).items()) if pass_data.get("properties") else "None"
            seed = pass_data["seed"]

            log_message(self, f"Applying '{display_name}' (Props: {props_str}, Seed: {seed}) for {loop_count} iteration(s)...")
            time.sleep(1 + (loop_count * 0.1)) 
            log_message(self, f"Pass '{display_name}' completed.")

        log_message(self, "Obfuscation complete! Generating report...")
        time.sleep(1)

        total_loops = sum(v["loops"] for v in config.values())
        obfuscated_lines = 7 + total_loops * random.randint(3, 7)
        complexity_score = random.uniform(5.5, 9.8)

        applied_passes_list = []
        for k, v in config.items():
            props_str = ', '.join(f'{kk}={vv}' for kk, vv in v.get('properties', {}).items())
            applied_passes_list.append(f"- {self.pass_display.get(k, k.upper())}: {v['loops']} loops (Props: {{{props_str}}}, Seed: {v['seed']})")
        applied_passes = "\n".join(applied_passes_list)

        final_report = f"""
--- Obfuscation Report (Demo PDF) ---

Status: COMPLETED SUCCESSFULLY
Date: {time.strftime('%Y-%m-%d %H:%M:%S')}
Configuration Source: {'Custom JSON' if self.config_mode == 'json' else 'Checkbox Selections'}
Original Lines of Code: 7
Obfuscated Lines of Code: {obfuscated_lines}
Final Complexity Score (estimated): {complexity_score:.2f}

Applied Passes:
{applied_passes}

--- Obfuscated Code Preview (1st Line) ---
#define _(x) x / 0x1f34b + 0x5a1b3...
"""
        self.report_text.configure(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, final_report)
        self.report_text.configure(state="disabled")

        log_message(self, "Report available and obfuscated file generated. Ready to save.")
        self.save_button.configure(state="normal")
        self.save_report_button.configure(state="normal") 
        self.start_button.configure(text="Start Obfuscation", state="normal")

    def save_report_placeholder(self):
        log_message(self, "Generating and saving report.pdf...")
        self.save_report_button.configure(state="disabled", text="Generating...")
        self.root.after(1000, lambda: self._save_report_complete())

    def _save_report_complete(self):
        log_message(self, "Report successfully saved to artifacts/obfuscation_report.pdf.")
        self.save_report_button.configure(state="normal", text="Save Report as PDF")

    def save_obfuscated_file_placeholder(self):
        log_message(self, "Saving obfuscated_code.cpp...")
        self.save_button.configure(state="disabled", text="Saving...")
        self.root.after(1000, lambda: self._save_complete())

    def _save_complete(self):
        log_message(self, "File successfully saved to artifacts/obfuscated_code.cpp.")
        self.save_button.configure(state="normal", text="Save Final Obfuscated File")

    def reset_gui(self):
        self.start_button.configure(text="Start Obfuscation", state="normal")
        self.save_button.configure(state="disabled")
        self.save_report_button.configure(state="disabled") 
        self.report_text.configure(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "--- Demo PDF Report ---\n\nStatus: Ready...")
        self.report_text.configure(state="disabled")