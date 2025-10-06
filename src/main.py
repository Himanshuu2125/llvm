"""
This file is the main entry point of the application.
"""

import customtkinter as ctk
from src.app import ObfuscationApp

if __name__ == '__main__':
    root = ctk.CTk()
    app = ObfuscationApp(root)
    root.mainloop()
