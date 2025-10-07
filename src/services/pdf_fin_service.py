import json
import os
import subprocess
import sys
from tkinter import filedialog, messagebox

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
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
            # Use indent=2 for readability in the PDF
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


def _add_passes_table(story, title, passes_list, styles):
    """Add a detailed table for the list of obfuscation passes."""
    story.append(Paragraph(title, styles["heading"]))
    story.append(Spacer(1, 4 * mm))

    table_data = [["Pass Name", "Enabled", "Parameters"]]
    for p in passes_list:
        # Format params dict into a readable pre-formatted string
        params_str = json.dumps(p.get("params", {}), indent=2)
        # Use a specific 'code' style for monospaced font
        params_paragraph = Paragraph(
            params_str.replace(" ", "&nbsp;").replace("\n", "<br/>"), styles["code"]
        )
        table_data.append(
            [
                p.get("name", "N/A"),
                str(p.get("enabled", "N/A")),
                params_paragraph,
            ]
        )

    # Adjusted column widths for the new content
    col_widths = [30 * mm, 25 * mm, 115 * mm]
    tbl = Table(table_data, colWidths=col_widths, hAlign="LEFT")
    tbl_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7AB7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#444444")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
    )
    tbl.setStyle(tbl_style)
    story.append(tbl)
    story.append(Spacer(1, 8 * mm))


def save_report_placeholder(report_content, config_data=None, default_path=None):
    """
    Prompts user to save a PDF report from statistics (report_content)
    and optional configuration (config_data). Returns True if saved.
    """
    try:
        # --- Process Statistics Data ---
        if report_content is None:
            messagebox.showerror("Save Error", "No report statistics available to save.")
            return False
        if isinstance(report_content, str):
            report = json.loads(report_content)
        elif isinstance(report_content, dict):
            report = report_content
        else:
            report = {"report_data": str(report_content)}
            
        # --- Process Configuration Data ---
        config = None
        if config_data:
            if isinstance(config_data, str):
                config = json.loads(config_data)
            elif isinstance(config_data, dict):
                config = config_data

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
                "title", parent=base_styles["h1"], fontName="Helvetica-Bold", fontSize=16, spaceAfter=8
            ),
            "heading": ParagraphStyle(
                "heading", parent=base_styles["h2"], fontName="Helvetica-Bold", fontSize=12,
                textColor=colors.HexColor("#2E7AB7"), spaceAfter=6,
            ),
            "normal": base_styles["BodyText"],
            "code": ParagraphStyle(
                "code", parent=base_styles["Normal"], fontName="Courier", fontSize=8, leading=10,
            ),
        }

        story = []
        story.append(Paragraph("Obfuscation Report", styles["title"]))
        story.append(Spacer(1, 6 * mm))

        # --- Add Configuration Section if available ---
        if config:
            config_details = {
                k: v for k, v in config.items() if k != "passes"
            }
            if config_details:
                 _add_section_table(story, "Configuration Details", config_details, styles)
            
            if "passes" in config and isinstance(config["passes"], list):
                _add_passes_table(story, "Obfuscation Passes Applied", config["passes"], styles)
            
            story.append(PageBreak())
            story.append(Paragraph("Obfuscation Statistics", styles["title"]))
            story.append(Spacer(1, 6 * mm))


        # --- Add Statistics Section ---
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