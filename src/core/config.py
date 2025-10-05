import customtkinter as ctk
import tkinter as tk

TAB_BG_INACTIVE = ("gray70", "gray30")
TAB_BG_ACTIVE = ("#1f6aa5", "#144870")
TAB_TEXT_INACTIVE = ("#222222", "#D4D4D4")

PASSES = {
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