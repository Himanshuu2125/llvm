import customtkinter as ctk
import tkinter as tk
from src.utils.file_operations import load_code_file

def create_left_pane(parent, app):
    left_pane = ctk.CTkFrame(parent, corner_radius=10)
    left_pane.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    left_pane.grid_columnconfigure(0, weight=1)
    left_pane.grid_rowconfigure(1, weight=3)
    left_pane.grid_rowconfigure(4, weight=1)

    code_header_frame = ctk.CTkFrame(left_pane, fg_color="transparent")
    code_header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
    code_header_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(code_header_frame, text="C/C++ Source Code Input", font=ctk.CTkFont(family='Helvetica', size=16, weight='bold')).grid(row=0, column=0, sticky="w")
    
    ctk.CTkButton(code_header_frame, text="Attach Code File", command=lambda: load_code_file(app), width=120).grid(row=0, column=1, sticky="e", padx=(10, 0))

    app.code_text = ctk.CTkTextbox(left_pane, height=20, font=('Consolas', 10), corner_radius=8)
    app.code_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=5, columnspan=2)
    
    app.code_text.insert(tk.END, "// Example C++ Code\n#include <iostream>\n\nint main() {\n    int a = 10;\n    int b = 20;\n    int sum = a + b;\n    std::cout << \"Sum: \" << sum << std::endl;\n    return 0;\n}")
    
    ctk.CTkFrame(left_pane, height=2, fg_color="#3a3a3a").grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=10)

    ctk.CTkLabel(left_pane, text="Obfuscation Report & Obfuscated Output", font=ctk.CTkFont(family='Helvetica', size=16, weight='bold')).grid(row=3, column=0, sticky="w", padx=15, pady=(5, 5))
    
    app.report_text = ctk.CTkTextbox(left_pane, height=10, font=('Consolas', 10), corner_radius=8, activate_scrollbars=True, fg_color=("#F0F0F0", "#333333"), text_color=("#333333", "#D4D4D4"))
    app.report_text.grid(row=4, column=0, sticky="nsew", padx=15, pady=5, columnspan=2)
    
    app.report_text.insert(tk.END, "--- Demo PDF Report ---\n\nStatus: Pending...\nOriginal Lines: 7\nEstimated Obfuscated Lines: N/A\nComplexity Score: N/A")
    app.report_text.configure(state="disabled")

    button_frame = ctk.CTkFrame(left_pane, fg_color="transparent")
    button_frame.grid(row=5, column=0, sticky="w", padx=15, pady=15)
    
    app.save_button = ctk.CTkButton(button_frame, text="Save Final Obfuscated File", command=app.save_obfuscated_file_placeholder, state="disabled", fg_color="green", hover_color="darkgreen")
    app.save_button.grid(row=0, column=0, sticky="w", padx=(0, 10))

    app.save_report_button = ctk.CTkButton(button_frame, text="Save Report as PDF", command=app.save_report_placeholder, state="disabled")
    app.save_report_button.grid(row=0, column=1, sticky="w")

    return left_pane