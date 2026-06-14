"""
theme.py — Design tokens for the CKD Expert System (premium redesign).

Single source of truth for color / type / spacing / radius. Screens never use
raw hex; they call theme.c("token"), so light/dark is one toggle and a rebrand
is one file. Place this in ckd_expert_system/ui/ next to interface_ui.py.
"""

from __future__ import annotations
import customtkinter as ctk

# ---------------------------------------------------------------------------
# COLOR — two full palettes, semantically named.
# ---------------------------------------------------------------------------
LIGHT = {
    "bg":            "#F6F8FA",
    "surface":       "#FFFFFF",
    "surface_alt":   "#F1F4F7",
    "sidebar":       "#0F1B24",   # dark rail in both modes (premium anchor)
    "sidebar_hover": "#172733",
    "scrim":         "#0B1220",

    "text":          "#0F1B24",
    "text_muted":    "#5B6B79",
    "text_faint":    "#93A1AD",
    "text_on_accent":"#FFFFFF",
    "text_on_dark":  "#E8EEF2",
    "text_on_dark_muted": "#8DA0AE",

    "border":        "#E3E8ED",
    "border_strong": "#CBD4DC",
    "focus_ring":    "#14B8A6",

    "accent":        "#0EA5A4",
    "accent_hover":  "#0B8B8A",
    "accent_press":  "#097675",
    "accent_soft":   "#E2F4F3",

    "success": "#16A34A", "success_soft": "#E4F4EA",
    "warning": "#D97706", "warning_soft": "#FBEEDD",
    "danger":  "#DC2626", "danger_soft":  "#FBE7E7",
    "info":    "#2563EB", "info_soft":    "#E5ECFD",

    "shadow":        "#DCE3E9",
    "shadow_strong": "#C2CCD4",
}

DARK = {
    "bg":            "#0B1220",
    "surface":       "#121C2B",
    "surface_alt":   "#1A2636",
    "sidebar":       "#080E18",
    "sidebar_hover": "#111A28",
    "scrim":         "#04070D",

    "text":          "#E8EEF2",
    "text_muted":    "#9DB0BE",
    "text_faint":    "#6B7E8D",
    "text_on_accent":"#FFFFFF",
    "text_on_dark":  "#E8EEF2",
    "text_on_dark_muted": "#9DB0BE",

    "border":        "#22303F",
    "border_strong": "#324252",
    "focus_ring":    "#2DD4BF",

    "accent":        "#2DD4BF",
    "accent_hover":  "#46E0CE",
    "accent_press":  "#1FB8A6",
    "accent_soft":   "#102E2C",

    "success": "#34D399", "success_soft": "#0F2A22",
    "warning": "#FBBF24", "warning_soft": "#2C2310",
    "danger":  "#F87171", "danger_soft":  "#2C1414",
    "info":    "#60A5FA", "info_soft":    "#0F1E33",

    "shadow":        "#060B14",
    "shadow_strong": "#02040A",
}

# 8px spacing grid
SP = {0: 0, 1: 4, 2: 8, 3: 12, 4: 16, 5: 20, 6: 24, 8: 32, 10: 40, 12: 48, 16: 64}

# radius
R = {"sm": 8, "md": 12, "lg": 16, "xl": 20, "pill": 999}

_FAMILY = "Inter"          # graceful fallback to system if absent
_MONO   = "JetBrains Mono"

TYPE = {
    "display": (32, "bold"),
    "h1":      (24, "bold"),
    "h2":      (19, "bold"),
    "h3":      (16, "bold"),
    "body":    (14, "normal"),
    "body_md": (14, "bold"),
    "label":   (12, "bold"),
    "caption": (12, "normal"),
    "micro":   (11, "normal"),
}


class Theme:
    def __init__(self, mode: str = "light"):
        self.mode = mode
        ctk.set_appearance_mode("light")

    @property
    def p(self) -> dict:
        return LIGHT if self.mode == "light" else DARK

    def c(self, token: str) -> str:
        return self.p[token]

    def toggle(self) -> str:
        self.mode = "dark" if self.mode == "light" else "light"
        return self.mode

    def font(self, role: str = "body", family: str | None = None) -> ctk.CTkFont:
        size, weight = TYPE[role]
        return ctk.CTkFont(family=family or _FAMILY, size=size, weight=weight)

    def mono(self, size: int = 11) -> ctk.CTkFont:
        return ctk.CTkFont(family=_MONO, size=size)


theme = Theme("light")
