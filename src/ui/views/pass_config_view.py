"""
This file contains the pass configuration view.
"""

import customtkinter as ctk
import tkinter as tk

def create_pass_config_frame(parent, toggle_pass_visibility_callback, toggle_common_seed_callback, update_json_from_passes_callback):
    """Creates and populates the standard pass configuration frame with enhanced options."""
    scrollable_frame = ctk.CTkScrollableFrame(parent, corner_radius=6, fg_color="transparent")
    scrollable_frame.grid(row=0, column=0, sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)
    config_frame = scrollable_frame

    ctk.CTkLabel(config_frame, text="Select Passes and Loop Count", font=ctk.CTkFont(family='Helvetica', size=12, weight='bold')).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2), columnspan=3)

    common_seed_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
    common_seed_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5, columnspan=3)
    common_seed_frame.grid_columnconfigure(1, weight=1) # Allow entry to align right
    common_seed_var = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(common_seed_frame, text="Use Common Seed for All Passes", variable=common_seed_var, command=toggle_common_seed_callback).grid(row=0, column=0, sticky="w")
    common_seed_entry = ctk.CTkEntry(common_seed_frame, width=120, placeholder_text="Seed (e.g., 42)")
    common_seed_entry.insert(0, "42")
    common_seed_entry.grid(row=0, column=1, sticky="e")
    common_seed_entry.bind('<KeyRelease>', lambda e: update_json_from_passes_callback())
    common_seed_var.trace('w', lambda *args: update_json_from_passes_callback())

    ctk.CTkFrame(config_frame, height=2, fg_color="#3a3a3a").grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    
    pass_vars, loop_entries, seed_entries, property_widgets, pass_display, properties_frames, seed_labels = {}, {}, {}, {}, {}, {}, {}
    passes = {
        "FLA (Flattening)": {"key": "fla", "properties": []},
        "GVENC (Global Value Encryption)": {"key": "gvenc", "properties": [
            {"name": "Key Length", "type": "dropdown", "options": ["1", "2", "3", "4"], "default": "4", "json_key": "keylen"}, 
            {"name": "Process Arrays", "type": "bool", "default": True, "json_key": "process-arrays"}
        ]},
        "INDCALL (Indirect Calls)": {"key": "indcall", "properties": []},
        "INDBR (Indirect Branches)": {"key": "indbr", "properties": [
            {"name": "Condition Only", "type": "bool", "default": False, "json_key": "cond-only"}
        ]},
        "ALIAS (Alias Obfuscation)": {"key": "alias", "properties": [
            {"name": "Branch Number", "type": "int", "default": 4, "placeholder": "4 (>=1)", "json_key": "branch-num"}, 
            {"name": "Reuse Getters", "type": "bool", "default": False, "json_key": "reuse-getters"}
        ]},
        "BCF (Bogus Control Flow)": {"key": "bcf", "properties": [
            {"name": "Probability (%)", "type": "int", "default": 30, "placeholder": "30 (1-100)", "json_key": "prob"}
        ]},
        "SUB (Substitution)": {"key": "sub", "properties": []},
        "MERGE (Merge)": {"key": "merge", "properties": [
            {"name": "Ratio (%)", "type": "int", "default": 100, "placeholder": "100 (0-100)", "json_key": "ratio"}
        ]},
        "MBA (Mixed Boolean Arithmetic)": {"key": "mba", "properties": [
            {"name": "Linear MBA Prob (%)", "type": "int", "default": 100, "placeholder": "100 (0-100)", "json_key": "linearmba-prob"}, 
            {"name": "Linear MBA Extra", "type": "int", "default": 5, "placeholder": "5 (>=1)", "json_key": "linearmba-extra"}
        ]}
    }
    
    row_num = 3
    for name, data in passes.items():
        key = data["key"]
        pass_display[key] = name
        
        pass_row_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        pass_row_frame.grid(row=row_num, column=0, sticky="ew", padx=0, pady=2, columnspan=3)
        pass_row_frame.grid_columnconfigure(0, weight=1)
        
        var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(pass_row_frame, text=name, variable=var, command=lambda k=key: toggle_pass_visibility_callback(k)).grid(row=0, column=0, sticky="w", padx=10, pady=2)
        
        properties_frame = ctk.CTkFrame(pass_row_frame, fg_color="transparent")
        properties_frame.grid_columnconfigure(0, minsize=180) # Column for labels
        properties_frames[key] = properties_frame

        prop_row = 0
        
        # --- Cycles (Loops) ---
        ctk.CTkLabel(properties_frame, text="Cycles:").grid(row=prop_row, column=0, sticky="w", padx=30, pady=2)
        loop_entry = ctk.CTkEntry(properties_frame, width=80, placeholder_text="1")
        loop_entry.insert(0, "1")
        loop_entry.grid(row=prop_row, column=1, sticky="w", padx=5, pady=2)
        loop_entries[key] = loop_entry
        loop_entry.bind('<KeyRelease>', lambda e, k=key: update_json_from_passes_callback())
        prop_row += 1

        # --- Seed ---
        seed_labels[key] = ctk.CTkLabel(properties_frame, text="Seed:")
        seed_entry = ctk.CTkEntry(properties_frame, width=100, placeholder_text="42")
        seed_entry.insert(0, "42")
        seed_entries[key] = seed_entry
        seed_entry.bind('<KeyRelease>', lambda e, k=key: update_json_from_passes_callback())
        prop_row += 1

        # --- Other Properties ---
        property_widgets[key] = {}
        for prop in data["properties"]:
            prop_id = prop["json_key"]
            ctk.CTkLabel(properties_frame, text=prop["name"] + ":").grid(row=prop_row, column=0, sticky="w", padx=30, pady=2)
            if prop["type"] == "dropdown":
                # Convert default to string for dropdown
                pvar = tk.StringVar(value=str(prop["default"]))
                widget = ctk.CTkOptionMenu(properties_frame, values=prop["options"], variable=pvar, width=100)
                widget.grid(row=prop_row, column=1, sticky="w", padx=5, pady=2)
                property_widgets[key][prop_id] = {"type": "str", "widget": pvar}
                pvar.trace('w', lambda *args, pid=prop_id, k=key: update_json_from_passes_callback())
            elif prop["type"] == "bool":
                pvar = tk.BooleanVar(value=prop["default"])
                widget = ctk.CTkCheckBox(properties_frame, text="", variable=pvar)
                widget.grid(row=prop_row, column=1, sticky="w", padx=5, pady=2)
                property_widgets[key][prop_id] = {"type": "bool", "widget": pvar}
                pvar.trace('w', lambda *args, pid=prop_id, k=key: update_json_from_passes_callback())
            elif prop["type"] == "int":
                widget = ctk.CTkEntry(properties_frame, width=100, placeholder_text=prop.get("placeholder", str(prop["default"])))
                widget.insert(0, str(prop["default"]))
                widget.grid(row=prop_row, column=1, sticky="w", padx=5, pady=2)
                property_widgets[key][prop_id] = {"type": "int", "widget": widget}
                widget.bind('<KeyRelease>', lambda e, pid=prop_id, k=key: update_json_from_passes_callback())
            prop_row += 1

        pass_vars[key] = var
        var.trace('w', lambda *args, k=key: update_json_from_passes_callback())
        row_num += 1
    return config_frame, pass_vars, loop_entries, seed_entries, property_widgets, pass_display, properties_frames, seed_labels, common_seed_var, common_seed_entry
