"""
This file contains the PDF generation logic.
"""

import os
import sys
import subprocess
from tkinter import messagebox

# --- Attempt to import FPDF for PDF generation ---
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

def save_report_placeholder(final_report_content, report_filepath):
    """Saves the generated report content to a PDF file."""
    if not final_report_content:
        messagebox.showerror("Error", "No report has been generated yet.")
        return
    
    if not FPDF_AVAILABLE:
        messagebox.showerror("Dependency Error", "FPDF library is not installed.\nPlease run 'pip install fpdf' to save reports as PDF.")
        return

    try:
        os.makedirs("artifacts", exist_ok=True)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(0, 5, txt=final_report_content)
        pdf.output(report_filepath)
        
        messagebox.showinfo("Success", f"Report saved successfully to:\n{os.path.abspath(report_filepath)}")
        return True
    except Exception as e:
        messagebox.showerror("Save Error", f"Failed to save PDF report.\nError: {e}")
        return False

def view_pdf(report_filepath):
    """Opens the saved PDF report using the system's default viewer."""
    if not os.path.exists(report_filepath):
        messagebox.showwarning("File Not Found", "The PDF report does not exist.\nPlease save the report first.")
        return
    try:
        if sys.platform == "win32":
            os.startfile(report_filepath)
        elif sys.platform == "darwin":
            subprocess.run(["open", report_filepath], check=True)
        else:
            subprocess.run(["xdg-open", report_filepath], check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        messagebox.showerror("Error", f"Could not open the PDF file.\nError: {e}\n\nPlease ensure you have a default PDF viewer.")
