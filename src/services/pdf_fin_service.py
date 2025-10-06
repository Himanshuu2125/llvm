# src/services/pdf_fin_service.py

import json
import os
import subprocess
import sys
from tkinter import filedialog, messagebox

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def _format_value(v):
    """Format basic types for printable PDF cells."""
    if isinstance(v, float):
        return f"{v:.3f}"
    if isinstance(v, (dict, list)):
        try:
            return json.dumps(v, indent=2)
        except Exception:
            return str(v)
    return str(v)


def _add_section_table(story, title, data_dict, styles):
    """Add a section header and a two-column table for data_dict to the story."""

    story.append(Paragraph(title.replace("_", " ").title(), styles["heading"]))
    story.append(Spacer(1, 4))

    table_data = [["Metric", "Value"]]
    for k, v in data_dict.items():
        table_data.append([str(k), _format_value(v)])


    col_widths = [90 * mm, 90 * mm]
    tbl = Table(table_data, colWidths=col_widths, hAlign="LEFT")
    tbl_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7AB7")),  # header
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#444444")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]
    )
    tbl.setStyle(tbl_style)
    story.append(tbl)
    story.append(Spacer(1, 10))


def save_report_placeholder(report_content, default_path=None):
    """
    Prompts the user to choose a save location then writes a PDF report
    created from report_content (dict or JSON string). Returns True if saved.
    """
    try:
        if report_content is None:
            messagebox.showerror("Save Error", "No report content available to save.")
            return False

        if isinstance(report_content, str):
            try:
                report = json.loads(report_content)
            except json.JSONDecodeError:
                report = {"report": report_content}
        elif isinstance(report_content, dict):
            report = report_content
        else:
            try:
                report = dict(report_content)
            except Exception:
                report = {"report": str(report_content)}

        initialfile = os.path.basename(default_path) if default_path else "obfuscation_report.pdf"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=initialfile,
        )
        if not save_path:
            return False

        doc = SimpleDocTemplate(
            save_path,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
        )

        base_styles = getSampleStyleSheet()
        styles = {
            "title": ParagraphStyle(
                "title",
                parent=base_styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=16,
                spaceAfter=8,
            ),
            "heading": ParagraphStyle(
                "heading",
                parent=base_styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=12,
                textColor=colors.HexColor("#2E7AB7"),
                spaceAfter=6,
            ),
            "normal": base_styles["BodyText"],
        }

        story = []
        story.append(Paragraph("Obfuscation Report", styles["title"]))
        story.append(Spacer(1, 6))

        for section_name, section_value in report.items():
            if isinstance(section_value, dict):
                _add_section_table(story, section_name, section_value, styles)
            else:
                story.append(Paragraph(f"<b>{section_name}:</b> {_format_value(section_value)}", styles["normal"]))
                story.append(Spacer(1, 6))

        doc.build(story)

        messagebox.showinfo("Saved", f"Report saved to:\n{save_path}")
        return True

    except Exception as e:
        messagebox.showerror("Error saving report", f"An error occurred while saving the PDF:\n{e}")
        return False


def view_pdf(path):
    """Open the PDF file with the system default viewer."""
    if not os.path.exists(path):
        messagebox.showerror("File not found", f"Could not find file:\n{path}")
        return

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.call(["open", path])
        else:
            subprocess.call(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Open Error", f"Unable to open file:\n{e}")
