import customtkinter as ctk
import tkinter as tk
from src.core.config import PASSES

def create_pass_config_frame(parent, app):
    scrollable_frame = ctk.CTkScrollableFrame(parent, corner_radius=6, fg_color="transparent")
    scrollable_frame.grid(row=0, column=0, sticky="nsew")
    scrollable_frame.grid_columnconfigure(0, weight=1)
    config_frame = scrollable_frame

    ctk.CTkLabel(config_frame, text="Select Passes and Loop Count", font=ctk.CTkFont(family='Helvetica', size=12, weight='bold')).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 2), columnspan=3)

    common_seed_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
    common_seed_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5, columnspan=3)
    common_seed_frame.grid_columnconfigure(0, weight=1)

    app.common_seed_var = tk.BooleanVar(value=True)
    common_cb = ctk.CTkCheckBox(common_seed_frame, text="Use Common Seed for All Passes", variable=app.common_seed_var, command=app.toggle_common_seed)
    common_cb.grid(row=0, column=0, sticky="w", padx=(0, 10))

    app.common_seed_entry = ctk.CTkEntry(common_seed_frame, width=100, placeholder_text="Seed (e.g., 42)")
    app.common_seed_entry.insert(0, "42")
    app.common_seed_entry.grid(row=0, column=1, sticky="e")
    app.common_seed_entry.bind('<KeyRelease>', lambda e: app.update_json_from_passes())

    app.common_seed_var.trace('w', lambda *args: app.update_json_from_passes())

    ctk.CTkFrame(config_frame, height=2, fg_color="#3a3a3a").grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)

    ctk.CTkLabel(config_frame, text="Pass", font=ctk.CTkFont(family='Helvetica', size=11, weight='normal', underline=True)).grid(row=3, column=0, sticky="w", padx=10, pady=(5, 2))
    ctk.CTkLabel(config_frame, text="Configuration", font=ctk.CTkFont(family='Helvetica', size=11, weight='normal', underline=True)).grid(row=3, column=1, sticky="w", padx=10, pady=(5, 2), columnspan=2)

    app.pass_vars = {}
    app.loop_entries = {}
    app.seed_entries = {}

    row_num = 4
    for name, data in PASSES.items():
        key = data["key"]
        app.pass_display[key] = name

        pass_row_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        pass_row_frame.grid(row=row_num, column=0, sticky="ew", padx=10, pady=2, columnspan=3)
        pass_row_frame.grid_columnconfigure(0, weight=1)

        var = tk.BooleanVar(value=False)
        cb = ctk.CTkCheckBox(pass_row_frame, text=name, variable=var, command=lambda k=key: app.toggle_pass_visibility(k))
        cb.grid(row=0, column=0, sticky="w", padx=10, pady=2)

        properties_frame = ctk.CTkFrame(pass_row_frame, fg_color="transparent")
        properties_frame.grid_columnconfigure(0, weight=1)
        properties_frame.grid_columnconfigure(1, weight=0)
        app.properties_frames[key] = properties_frame

        prop_row = 0

        ctk.CTkLabel(properties_frame, text="Loops:").grid(row=prop_row, column=0, sticky="w", padx=10, pady=2)
        loop_entry = ctk.CTkEntry(properties_frame, width=50, placeholder_text="1")
        loop_entry.insert(0, "1")
        loop_entry.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
        app.loop_entries[key] = loop_entry
        loop_entry.bind('<KeyRelease>', lambda e, k=key: app.update_json_from_passes())
        prop_row += 1

        seed_label = ctk.CTkLabel(properties_frame, text="Seed:")
        app.seed_labels[key] = seed_label
        seed_entry = ctk.CTkEntry(properties_frame, width=80, placeholder_text="42")
        seed_entry.insert(0, "42")
        app.seed_entries[key] = seed_entry
        seed_entry.bind('<KeyRelease>', lambda e, k=key: app.update_json_from_passes())
        prop_row += 1

        app.property_widgets[key] = {}
        for prop in data["properties"]:
            prop_label = ctk.CTkLabel(properties_frame, text=prop["name"] + ":")
            prop_label.grid(row=prop_row, column=0, sticky="w", padx=10, pady=2)

            prop_id = '_'.join(prop["name"].lower().split())
            if prop["type"] == "dropdown":
                pvar = tk.StringVar(value=prop["default"])
                pmenu = ctk.CTkOptionMenu(properties_frame, values=prop["options"], variable=pvar, width=80)
                pmenu.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
                app.property_widgets[key][prop_id] = {"type": "str", "widget": pvar}
                pvar.trace('w', lambda *args, pid=prop_id, k=key: app.update_json_from_passes())
            elif prop["type"] == "bool":
                pvar = tk.BooleanVar(value=prop["default"])
                pcb = ctk.CTkCheckBox(properties_frame, text="", variable=pvar)
                pcb.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
                app.property_widgets[key][prop_id] = {"type": "bool", "widget": pvar}
                pvar.trace('w', lambda *args, pid=prop_id, k=key: app.update_json_from_passes())
            elif prop["type"] == "int":
                placeholder = prop.get("placeholder", str(prop["default"]))
                pentry = ctk.CTkEntry(properties_frame, width=80, placeholder_text=placeholder)
                pentry.insert(0, str(prop["default"]))
                pentry.grid(row=prop_row, column=1, sticky="w", padx=(5, 0), pady=2)
                app.property_widgets[key][prop_id] = {"type": "int", "widget": pentry}
                pentry.bind('<KeyRelease>', lambda e, pid=prop_id, k=key: app.update_json_from_passes())

            prop_row += 1

        app.pass_vars[key] = var
        var.trace('w', lambda *args, k=key: app.update_json_from_passes())

        app.toggle_pass_visibility(key, show=False)

        row_num += 1

    return config_frame