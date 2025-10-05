import customtkinter as ctk
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import ObfuscationApp

if __name__ == '__main__':
    root = ctk.CTk()
    app = ObfuscationApp(root)
    root.mainloop()
