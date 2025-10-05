import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog 
import random
import time
import json 

# --- Constants for UI Styling ---
TAB_BG_INACTIVE = ("gray70", "gray30") # Light and Dark mode colors for inactive tab
TAB_BG_ACTIVE = ("#1f6aa5", "#144870") # Default CTk button blue/active color
TAB_TEXT_INACTIVE = ("#222222", "#D4D4D4") # Dark text for light mode, light text for dark mode

# --- Main Application Class ---
class ObfuscationApp:
    def __init__(self, root):
        # 1. Main Window Setup
        self.root = root
        self.root.title("C/C++ Code Obfuscation Tool GUI (CustomTkinter)")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        # Apply CustomTkinter Theme
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Configure Grid weights for resizing
        self.root.grid_columnconfigure(0, weight=3) # Code Input/Report Pane (Wider)
        self.root.grid_columnconfigure(1, weight=1) # Controls/Logs Pane
        self.root.grid_rowconfigure(0, weight=1)

        # Initial Configuration Mode
        self.config_mode = "passes" # 'passes' or 'json'

        # Additional attributes for pass configuration
        self.properties_frames = {}
        self.seed_labels = {}
        self.property_widgets = {}
        self.pass_display = {}

        # --- Main Panes (using CTkFrame) ---
        
        # Left Pane: Code Input and Report
        self.left_pane = ctk.CTkFrame(root, corner_radius=10)
        self.left_pane.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_pane.grid_columnconfigure(0, weight=1)
        self.left_pane.grid_rowconfigure(1, weight=3)  # Code Input Area
        self.left_pane.grid_rowconfigure(4, weight=1)  # Report Area

        # Right Pane: Controls and Logs
        self.right_pane = ctk.CTkFrame(root, corner_radius=10)
        self.right_pane.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_pane.grid_columnconfigure(0, weight=1)
        self.right_pane.grid_rowconfigure(5, weight=1) # Log Area
        
        # --- 2. Left Pane: Code Input Area with Attach Button ---
        code_header_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        code_header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        code_header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(code_header_frame, text="C/C++ Source Code Input", font=ctk.CTkFont(family='Helvetica', size=16, weight='bold')).grid(row=0, column=0, sticky="w")
        
        # Attach Code Button
        ctk.CTkButton(code_header_frame, text="Attach Code File", command=self.load_code_file, width=120).grid(row=0, column=1, sticky="e", padx=(10, 0))

        # Textbox widget for code input
        self.code_text = ctk.CTkTextbox(self.left_pane, height=20, font=('Consolas', 10), corner_radius=8)
        self.code_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=5, columnspan=2)
        
        # Placeholder code
        self.code_text.insert(tk.END, "// Example C++ Code\n#include <iostream>\n\nint main() {\n    int a = 10;\n    int b = 20;\n    int sum = a + b;\n    std::cout << \"Sum: \" << sum << std::endl;\n    return 0;\n}")
        
        # Separator
        ctk.CTkFrame(self.left_pane, height=2, fg_color="#3a3a3a").grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=10)


        # --- 6. Left Pane: Report Area & Save Buttons ---
        ctk.CTkLabel(self.left_pane, text="Obfuscation Report & Obfuscated Output", font=ctk.CTkFont(family='Helvetica', size=16, weight='bold')).grid(row=3, column=0, sticky="w", padx=15, pady=(5, 5))
        
        # Textbox widget for report view
        self.report_text = ctk.CTkTextbox(self.left_pane, height=10, font=('Consolas', 10), corner_radius=8, activate_scrollbars=True, fg_color=("#F0F0F0", "#333333"), text_color=("#333333", "#D4D4D4"))
        self.report_text.grid(row=4, column=0, sticky="nsew", padx=15, pady=5, columnspan=2)
        
        # Demo Report Content
        self.report_text.insert(tk.END, "--- Demo PDF Report ---\n\nStatus: Pending...\nOriginal Lines: 7\nEstimated Obfuscated Lines: N/A\nComplexity Score: N/A")
        self.report_text.configure(state="disabled")

        # Button Frame for Save options
        button_frame = ctk.CTkFrame(self.left_pane, fg_color="transparent")
        button_frame.grid(row=5, column=0, sticky="w", padx=15, pady=15)
        
        # Save Obfuscated Button
        self.save_button = ctk.CTkButton(button_frame, text="Save Final Obfuscated File", command=self.save_obfuscated_file_placeholder, state="disabled", fg_color="green", hover_color="darkgreen")
        self.save_button.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # Save Report Button
        self.save_report_button = ctk.CTkButton(button_frame, text="Save Report as PDF", command=self.save_report_placeholder, state="disabled")
        self.save_report_button.grid(row=0, column=1, sticky="w")


        # --- 3. Right Pane: Configuration Tabs and Panels ---
        
        self.config_container = ctk.CTkFrame(self.right_pane, corner_radius=8)
        self.config_container.grid(row=0, column=0, sticky="ew", pady=(15, 0), padx=15)
        self.config_container.grid_columnconfigure(0, weight=1)
        self.config_container.grid_columnconfigure(1, weight=1)
        self.config_container.grid_rowconfigure(1, weight=1) # Ensure content area stretches vertically

        # --- Tab Selector ---
        
        # Checkbox Tab
        self.tab_passes = ctk.CTkButton(self.config_container, text="Checkbox Pass Configuration", command=lambda: self.toggle_config_mode('passes'),
                                        fg_color=TAB_BG_ACTIVE[ctk.get_appearance_mode() == "Dark"], 
                                        text_color=TAB_TEXT_INACTIVE[ctk.get_appearance_mode() == "Dark"], 
                                        hover_color=TAB_BG_ACTIVE[ctk.get_appearance_mode() == "Dark"],
                                        corner_radius=6, height=35)
        self.tab_passes.grid(row=0, column=0, sticky="ew", padx=(5, 2), pady=5)
        
        # JSON Tab
        self.tab_json = ctk.CTkButton(self.config_container, text="Custom JSON Configuration", command=lambda: self.toggle_config_mode('json'),
                                      fg_color=TAB_BG_INACTIVE[ctk.get_appearance_mode() == "Dark"], 
                                      text_color=TAB_TEXT_INACTIVE[ctk.get_appearance_mode() == "Dark"],
                                      hover_color=TAB_BG_INACTIVE[ctk.get_appearance_mode() == "Dark"],
                                      corner_radius=6, height=35)
        self.tab_json.grid(row=0, column=1, sticky="ew", padx=(2, 5), pady=5)

        # --- Fixed Size Content Area (Prevents CLS/Jump) ---
        # The height is set to accommodate the taller JSON editor frame
        self.config_area_frame = ctk.CTkFrame(self.config_container, corner_radius=6, height=220, fg_color="transparent")
        self.config_area_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(0, 5))
        self.config_area_frame.grid_columnconfigure(0, weight=1)
        self.config_area_frame.grid_rowconfigure(0, weight=1)


        # Create configuration sub-frames and place them inside the content area
        # Create JSON frame first to ensure json_config_text exists
        self.json_config_frame = self._create_json_config_frame(self.config_area_frame)
        self.pass_config_frame = self._create_pass_config_frame(self.config_area_frame)

        # Initially show the passes configuration panel
        self.pass_config_frame.grid(row=0, column=0, sticky="nsew")
        
        # --- 4. Right Pane: Control Button ---
        self.start_button = ctk.CTkButton(self.right_pane, text="Start Obfuscation", command=self.start_obfuscation_placeholder, font=ctk.CTkFont(family='Helvetica', size=15, weight='bold'))
        # Moved to row 2
        self.start_button.grid(row=2, column=0, sticky="ew", pady=(5, 15), padx=15)
        
        # Separator
        ctk.CTkFrame(self.right_pane, height=2, fg_color="#3a3a3a").grid(row=3, column=0, sticky="ew", padx=15, pady=10)

        # --- 5. Right Pane: Logs Area ---
        ctk.CTkLabel(self.right_pane, text="Obfuscation Logs", font=ctk.CTkFont(family='Helvetica', size=16, weight='bold')).grid(row=4, column=0, sticky="w", padx=15, pady=(5, 5))
        
        # Log Textbox (Dark theme, neon green text)
        self.log_text = ctk.CTkTextbox(self.right_pane, height=15, font=('Consolas', 10), activate_scrollbars=True, corner_radius=8, fg_color="#0a0a0a", text_color="#00ff00")
        self.log_text.grid(row=5, column=0, sticky="nsew", padx=15, pady=5)
        
        # Demo Log Content
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Initializing Obfuscator v1.2...\n")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Awaiting user input...\n")
        self.log_text.configure(state="disabled")

        # Initial JSON update from passes
        self.update_json_from_passes()
    
    # --- Configuration Frame Creation Methods ---

    def _create_pass_config_frame(self, parent):
        """Creates and populates the standard pass configuration frame with enhanced options."""
        # Wrap in a scrollable frame for vertical scrolling (horizontal via grid weights if needed)
        scrollable_frame = ctk.CTkScrollableFrame(parent, corner_radius=6, fg_color="transparent")
        scrollable_frame.grid(row=0, column=0, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)
        config_frame = scrollable_frame  # Use scrollable_frame as config_frame

        ctk.CTkLabel(config_frame, text="Select Passes and Loop Count", font=ctk.CTkFont(family='Helvetica', size=12, weight='bold')).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2), columnspan=3)

        # Common Seed Section at Top
        common_seed_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        common_seed_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5, columnspan=3)
        common_seed_frame.grid_columnconfigure(0, weight=1)

        self.common_seed_var = tk.BooleanVar(value=True)
        common_cb = ctk.CTkCheckBox(common_seed_frame, text="Use Common Seed for All Passes", variable=self.common_seed_var, command=self.toggle_common_seed)
        common_cb.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.common_seed_entry = ctk.CTkEntry(common_seed_frame, width=100, placeholder_text="Seed (e.g., 42)")
        self.common_seed_entry.insert(0, "42")
        self.common_seed_entry.grid(row=0, column=1, sticky="e")
        # Bind change event
        self.common_seed_entry.bind('<KeyRelease>', lambda e: self.update_json_from_passes())

        # Trace for common seed checkbox
        self.common_seed_var.trace('w', lambda *args: self.update_json_from_passes())

        # Separator for passes
        ctk.CTkFrame(config_frame, height=2, fg_color="#3a3a3a").grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

        # Header Row for Passes
        ctk.CTkLabel(config_frame, text="Pass", font=ctk.CTkFont(family='Helvetica', size=11, weight='normal', underline=True)).grid(row=3, column=0, sticky="w", padx=10, pady=(5, 2))
        ctk.CTkLabel(config_frame, text="Configuration", font=ctk.CTkFont(family='Helvetica', size=11, weight='normal', underline=True)).grid(row=3, column=1, sticky="w", padx=10, pady=(5, 2), columnspan=2)

        self.pass_vars = {}
        self.loop_entries = {}
        self.seed_entries = {}

        # Expanded list of passes with configs
        passes = {
            "FLA (Flattening)": {"key": "fla", "properties": []},
            "GVENC (Global Value Encryption)": {"key": "gvenc", "properties": [
                {"name": "Key Length", "type": "dropdown", "options": ["1", "2", "3", "4"], "default": "4"},
                {"name": "Process Arrays", "type": "bool", "default": True}
            ]},
            "INDCALL (Indirect Calls)": {"key": "indcall", "properties": []},
            "INDBR (Indirect Branches)": {"key": "indbr", "properties": [
                {"name": "Condition Only", "type": "bool", "default": False}
            ]},
            "ALIAS (Alias Obfuscation)": {"key": "alias", "properties": [
                {"name": "Branch Number", "type": "int", "default": 4, "placeholder": "4 (>=1)"},
                {"name": "Reuse Getters", "type": "bool", "default": False}
            ]},
            "BCF (Bogus Control Flow)": {"key": "bcf", "properties": [
                {"name": "Probability (%)", "type": "int", "default": 30, "placeholder": "30 (1-100)"}
            ]},
            "SUB (Substitution)": {"key": "sub", "properties": []},
            "MERGE (Merge)": {"key": "merge", "properties": [
                {"name": "Ratio (%)", "type": "int", "default": 100, "placeholder": "100 (0-100)"}
            ]},
            "MBA (Mixed Boolean Arithmetic)": {"key": "mba", "properties": [
                {"name": "Linear MBA Probability (%)", "type": "int", "default": 100, "placeholder": "100 (0-100)"},
                {"name": "Linear MBA Extra", "type": "int", "default": 5, "placeholder": "5 (>=1)"}
            ]}
        }
        
        row_num = 4
        for name, data in passes.items():
            key = data["key"]
            self.pass_display[key] = name

            # Frame for this pass's row (spans columns)
            pass_row_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
            pass_row_frame.grid(row=row_num, column=0, sticky="ew", padx=10, pady=2, columnspan=3)
            pass_row_frame.grid_columnconfigure(0, weight=1)

            # Checkbox for enabling pass (top row, left-aligned)
            var = tk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(pass_row_frame, text=name, variable=var, command=lambda k=key: self.toggle_pass_visibility(k))
            cb.grid(row=0, column=0, sticky="w", padx=10, pady=2)

            # Properties sub-frame (below checkbox, initially hidden)
            properties_frame = ctk.CTkFrame(pass_row_frame, fg_color="transparent")
            properties_frame.grid_columnconfigure(0, weight=1)
            properties_frame.grid_columnconfigure(1, weight=0)
            self.properties_frames[key] = properties_frame

            # Create widgets inside properties_frame (vertically stacked, left-aligned)
            prop_row = 0

            # Loops
            ctk.CTkLabel(properties_frame, text="Loops:").grid(row=prop_row, column=0, sticky="w", padx=10, pady=2)
            loop_entry = ctk.CTkEntry(properties_frame, width=50, placeholder_text="1")
            loop_entry.insert(0, "1")
            loop_entry.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
            self.loop_entries[key] = loop_entry
            # Bind change event
            loop_entry.bind('<KeyRelease>', lambda e, k=key: self.update_json_from_passes())
            prop_row += 1

            # Seed (conditionally shown)
            seed_label = ctk.CTkLabel(properties_frame, text="Seed:")
            self.seed_labels[key] = seed_label
            seed_entry = ctk.CTkEntry(properties_frame, width=80, placeholder_text="42")
            seed_entry.insert(0, "42")
            self.seed_entries[key] = seed_entry
            # Bind change event
            seed_entry.bind('<KeyRelease>', lambda e, k=key: self.update_json_from_passes())
            prop_row += 1

            # Pass-specific properties
            self.property_widgets[key] = {}
            for prop in data["properties"]:
                prop_label = ctk.CTkLabel(properties_frame, text=prop["name"] + ":")
                prop_label.grid(row=prop_row, column=0, sticky="w", padx=10, pady=2)

                prop_id = '_'.join(prop["name"].lower().split())
                if prop["type"] == "dropdown":
                    pvar = tk.StringVar(value=prop["default"])
                    pmenu = ctk.CTkOptionMenu(properties_frame, values=prop["options"], variable=pvar, width=80)
                    pmenu.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
                    self.property_widgets[key][prop_id] = {"type": "str", "widget": pvar}
                    # Trace for dropdown changes
                    pvar.trace('w', lambda *args, pid=prop_id, k=key: self.update_json_from_passes())
                elif prop["type"] == "bool":
                    pvar = tk.BooleanVar(value=prop["default"])
                    pcb = ctk.CTkCheckBox(properties_frame, text="", variable=pvar)
                    pcb.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
                    self.property_widgets[key][prop_id] = {"type": "bool", "widget": pvar}
                    # Trace for checkbox changes
                    pvar.trace('w', lambda *args, pid=prop_id, k=key: self.update_json_from_passes())
                elif prop["type"] == "int":
                    placeholder = prop.get("placeholder", str(prop["default"]))
                    pentry = ctk.CTkEntry(properties_frame, width=80, placeholder_text=placeholder)
                    pentry.insert(0, str(prop["default"]))
                    pentry.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
                    self.property_widgets[key][prop_id] = {"type": "int", "widget": pentry}
                    # Bind change event
                    pentry.bind('<KeyRelease>', lambda e, pid=prop_id, k=key: self.update_json_from_passes())

                prop_row += 1

            self.pass_vars[key] = var
            # Trace for pass checkbox
            var.trace('w', lambda *args, k=key: self.update_json_from_passes())

            # Initially hide properties frame (now safe since json_config_text exists)
            self.toggle_pass_visibility(key, show=False)

            row_num += 1

        return config_frame

    def update_json_from_passes(self):
        """Updates the JSON configuration text based on the current passes configuration."""
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
                    # Ignore invalid values during update
                    pass

        json_str = json.dumps(config, indent=2)
        self.json_config_text.delete(1.0, tk.END)
        self.json_config_text.insert(tk.END, json_str)

    def toggle_pass_visibility(self, key, show=None):
        """Toggles visibility of pass details when checkbox is toggled."""
        if show is None:
            show = self.pass_vars[key].get()
        frame = self.properties_frames[key]
        if show:
            frame.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
            # Position seed widgets
            seed_row = 1  # Loops is at row 0, seed at row 1
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
        """Toggles between common seed and individual seeds."""
        use_common = self.common_seed_var.get()
        if use_common:
            self.common_seed_entry.grid(row=0, column=1, sticky="e")
            # Hide all individual seeds for enabled passes
            for key in self.pass_vars:
                if self.pass_vars[key].get():
                    self.seed_labels[key].grid_remove()
                    self.seed_entries[key].grid_remove()
        else:
            self.common_seed_entry.grid_remove()
            # Show individual seeds for enabled passes
            for key in self.pass_vars:
                if self.pass_vars[key].get():
                    self.seed_labels[key].grid(row=1, column=0, sticky="w", padx=10, pady=2)
                    self.seed_entries[key].grid(row=1, column=1, sticky="w", padx=(5, 0), pady=2)
        self.update_json_from_passes()

    def _create_json_config_frame(self, parent):
        """Creates and populates the JSON configuration frame."""
        # Note: This frame fills the parent config_area_frame
        config_frame = ctk.CTkFrame(parent, corner_radius=6, fg_color="transparent")
        config_frame.grid_columnconfigure(0, weight=1)
        
        header_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 2))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="JSON Configuration Text", font=ctk.CTkFont(family='Helvetica', size=12, weight='bold')).grid(row=0, column=0, sticky="w")
        
        # Attach JSON Button
        ctk.CTkButton(header_frame, text="Attach JSON File", command=self.load_json_file, width=120).grid(row=0, column=1, sticky="e", padx=(10, 0))

        ctk.CTkLabel(config_frame, text="Define pass settings (e.g., {'fla': {'loops': 1, 'seed': 42, 'properties': {}}})", font=ctk.CTkFont(family='Helvetica', size=11)).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 2))
        
        # Textbox for JSON input
        self.json_config_text = ctk.CTkTextbox(config_frame, height=150, font=('Consolas', 9), corner_radius=5)
        self.json_config_text.grid(row=2, column=0, sticky="ew", padx=10, pady=(2, 10))
        # Placeholder for JSON configuration
        self.json_config_text.insert(tk.END, '{\n  "fla": {\n    "loops": 1,\n    "seed": 42,\n    "properties": {}\n  }\n}')
        
        return config_frame

    # --- File Loading Helper Functions ---

    def load_code_file(self):
        """Opens a file dialog to load C/C++ code."""
        filepath = filedialog.askopenfilename(
            defaultextension=".cpp",
            filetypes=[("C/C++ files", "*.c *.cpp *.h *.hpp"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    self.code_text.delete(1.0, tk.END)
                    self.code_text.insert(tk.END, content)
                    self.log_message(f"C/C++ code loaded from: {filepath}")
            except Exception as e:
                messagebox.showerror("File Error", f"Could not read file: {e}")

    def load_json_file(self):
        """Opens a file dialog to load JSON configuration."""
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    # Basic validation: check if it's valid JSON before inserting
                    json.loads(content)
                    self.json_config_text.delete(1.0, tk.END)
                    self.json_config_text.insert(tk.END, content)
                    self.log_message(f"JSON configuration loaded from: {filepath}")
            except json.JSONDecodeError:
                messagebox.showerror("File Error", "The selected file is not valid JSON.")
            except Exception as e:
                messagebox.showerror("File Error", f"Could not read file: {e}")

    # --- Toggle Function ---

    def toggle_config_mode(self, mode):
        """Toggles the configuration panel between checkboxes ('passes') and JSON input ('json')."""
        if mode == self.config_mode:
            return # Already in this mode

        # Get current appearance mode for dynamic colors
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        if mode == "json":
            self.pass_config_frame.grid_forget()
            self.json_config_frame.grid(row=0, column=0, sticky="nsew")
            self.config_mode = "json"
            
            # Update Tab Styles
            self.tab_json.configure(fg_color=TAB_BG_ACTIVE[is_dark], hover_color=TAB_BG_ACTIVE[is_dark])
            self.tab_passes.configure(fg_color=TAB_BG_INACTIVE[is_dark], hover_color=TAB_BG_INACTIVE[is_dark])
            self.log_message("Switched to Custom JSON Configuration mode.")
            
        elif mode == "passes":
            self.json_config_frame.grid_forget()
            self.pass_config_frame.grid(row=0, column=0, sticky="nsew")
            self.config_mode = "passes"
            
            # Update Tab Styles
            self.tab_passes.configure(fg_color=TAB_BG_ACTIVE[is_dark], hover_color=TAB_BG_ACTIVE[is_dark])
            self.tab_json.configure(fg_color=TAB_BG_INACTIVE[is_dark], hover_color=TAB_BG_INACTIVE[is_dark])
            self.log_message("Switched to Checkbox Passes Configuration mode.")
            # Sync JSON when switching back to passes (in case JSON was edited)
            self.update_json_from_passes()

    # --- Placeholder Functions ---

    def log_message(self, message):
        """Helper to append a message to the log area."""
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END) # Scroll to bottom
        self.log_text.configure(state="disabled")
        self.root.update_idletasks() # Ensure GUI updates

    def start_obfuscation_placeholder(self):
        """Simulates the start of the obfuscation process."""
        self.log_message("Starting obfuscation process...")
        self.start_button.configure(state="disabled", text="Obfuscating...")
        self.save_button.configure(state="disabled")
        self.save_report_button.configure(state="disabled") 
        
        self.report_text.configure(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "--- Demo PDF Report ---\n\nStatus: Running...")
        self.report_text.configure(state="disabled")

        # --- Configuration Retrieval Logic ---
        config = {}

        if self.config_mode == 'json':
            json_input = self.json_config_text.get("1.0", tk.END).strip()
            if not json_input or json_input == '{}':
                 self.log_message("Error: JSON configuration is empty. Process aborted.")
                 self.reset_gui()
                 return
            try:
                config = json.loads(json_input)
                self.log_message("Using Custom JSON configuration.")
            except json.JSONDecodeError:
                messagebox.showerror("Input Error", "Invalid JSON configuration provided.")
                self.reset_gui()
                return
        
        elif self.config_mode == 'passes':
            # Retrieve selected passes, loops, seeds, and properties from checkboxes
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
            self.log_message("Using Checkbox Passes configuration.")

        if not config:
            self.log_message("Error: No passes selected/configured. Process aborted.")
            self.reset_gui()
            return
        
        # Simulate processing time and logging for each pass
        self.log_message(f"Configuration received: {config}")
        time.sleep(0.5)

        # Simulate applying passes (using keys from the final config)
        for pass_key, pass_data in config.items():
            display_name = self.pass_display.get(pass_key, pass_key.upper())
            loop_count = pass_data["loops"]
            props_str = ', '.join(f"{k}={v}" for k, v in pass_data.get("properties", {}).items()) if pass_data.get("properties") else "None"
            seed = pass_data["seed"]

            self.log_message(f"Applying '{display_name}' (Props: {props_str}, Seed: {seed}) for {loop_count} iteration(s)...")
            time.sleep(1 + (loop_count * 0.1)) 
            self.log_message(f"Pass '{display_name}' completed.")

        # Simulate completion
        self.log_message("Obfuscation complete! Generating report...")
        time.sleep(1)

        # Update Report
        total_loops = sum(v["loops"] for v in config.values())
        obfuscated_lines = 7 + total_loops * random.randint(3, 7)
        complexity_score = random.uniform(5.5, 9.8)

        applied_passes = "\n".join([f"- {self.pass_display.get(k, k.upper())}: {v['loops']} loops (Props: {', '.join(f'{kk}={vv}' for kk, vv in v.get('properties', {}).items())}, Seed: {v['seed']})" for k, v in config.items()])

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

        self.log_message("Report available and obfuscated file generated. Ready to save.")
        self.save_button.configure(state="normal")
        self.save_report_button.configure(state="normal") 
        self.start_button.configure(text="Start Obfuscation", state="normal")

    def save_report_placeholder(self):
        """Simulates saving the final report file."""
        self.log_message("Generating and saving report.pdf...")
        self.save_report_button.configure(state="disabled", text="Generating...")
        self.root.after(1000, lambda: self._save_report_complete())

    def _save_report_complete(self):
        """Finishes the report save simulation."""
        self.log_message("Report successfully saved to artifacts/obfuscation_report.pdf.")
        self.save_report_button.configure(state="normal", text="Save Report as PDF")

    def save_obfuscated_file_placeholder(self):
        """Simulates saving the final output file."""
        self.log_message("Saving obfuscated_code.cpp...")
        self.save_button.configure(state="disabled", text="Saving...")
        self.root.after(1000, lambda: self._save_complete())

    def _save_complete(self):
        """Finishes the save simulation."""
        self.log_message("File successfully saved to artifacts/obfuscated_code.cpp.")
        self.save_button.configure(state="normal", text="Save Final Obfuscated File")

    def reset_gui(self):
        """Resets the state of the GUI."""
        self.start_button.configure(text="Start Obfuscation", state="normal")
        self.save_button.configure(state="disabled")
        self.save_report_button.configure(state="disabled") 
        self.report_text.configure(state="normal")
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "--- Demo PDF Report ---\n\nStatus: Ready...")
        self.report_text.configure(state="disabled")

if __name__ == '__main__':
    root = ctk.CTk()
    app = ObfuscationApp(root)
    root.mainloop()