"""
components.py — Premium animated CustomTkinter widgets.

Tkinter has no real shadows, per-widget opacity, or CSS transitions, so every
"animation" is built from three honest primitives:
  1. lerp_color() — interpolate two hex colors
  2. tween()      — eased value animation on a .after() loop
  3. .place()     — for things that physically slide

Place in ckd_expert_system/ui/ next to interface_ui.py.
"""

from __future__ import annotations
import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional

try:                       # works both in-package and standalone
    from .theme import theme, SP, R
except ImportError:
    from theme import theme, SP, R


# ===========================================================================
# ANIMATION PRIMITIVES
# ===========================================================================
def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r, g, b):
    return f"#{max(0,min(255,r)):02X}{max(0,min(255,g)):02X}{max(0,min(255,b)):02X}"


def lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(round(r1 + (r2 - r1) * t),
                       round(g1 + (g2 - g1) * t),
                       round(b1 + (b2 - b1) * t))


def ease_out_cubic(t: float) -> float:
    return 1 - pow(1 - t, 3)


def tween(widget, duration_ms, on_step, on_done=None,
          easing=ease_out_cubic, fps=60):
    """Drive on_step(progress 0..1) over duration via widget.after()."""
    steps = max(1, int(duration_ms / (1000 / fps)))
    state = {"i": 0, "alive": True}

    def cancel():
        state["alive"] = False

    def frame():
        if not state["alive"] or not widget.winfo_exists():
            return
        state["i"] += 1
        p = min(1.0, state["i"] / steps)
        try:
            on_step(easing(p))
        except tk.TclError:
            return
        if p < 1.0:
            widget.after(int(1000 / fps), frame)
        elif on_done:
            on_done()

    frame()
    return cancel


def bind_recursive(widget, sequence, func):
    widget.bind(sequence, func, add="+")
    for child in widget.winfo_children():
        bind_recursive(child, sequence, func)


# ===========================================================================
# CARD  — surface with hover elevation (signature interaction)
# ===========================================================================
class Card(ctk.CTkFrame):
    """`self` is the shadow layer; the real surface is packed on top with a few
    px of shadow showing at the bottom. Sizes propagate through pack (no fragile
    place geometry), so cards never collapse. Hover deepens the shadow and lights
    the border toward the accent — the eye reads it as a lift.
    """

    def __init__(self, master, *, interactive=False, on_click=None,
                 accent=None, padding=SP[5], elevation=5, **kw):
        super().__init__(master, corner_radius=R["lg"],
                         fg_color=theme.c("shadow"))   # shadow layer
        self._accent = accent or theme.c("accent")
        self._interactive = interactive or bool(on_click)
        self._on_click = on_click

        self.surface = ctk.CTkFrame(self, corner_radius=R["lg"],
                                    fg_color=theme.c("surface"),
                                    border_width=1, border_color=theme.c("border"),
                                    **kw)
        self.surface.pack(fill="both", expand=True, padx=0, pady=(0, elevation))

        self.body = ctk.CTkFrame(self.surface, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=padding, pady=padding)

        if self._interactive:
            # children are added synchronously by the caller before this fires
            self.after(16, self._wire_hover)

    def _wire_hover(self):
        def enter(_=None):
            tween(self.surface, 140, lambda p: self.surface.configure(
                border_color=lerp_color(theme.c("border"), self._accent, p)))
            tween(self, 140, lambda p: self.configure(
                fg_color=lerp_color(theme.c("shadow"), theme.c("shadow_strong"), p)))
            try: self.configure(cursor="hand2")
            except tk.TclError: pass

        def leave(_=None):
            tween(self.surface, 160, lambda p: self.surface.configure(
                border_color=lerp_color(self._accent, theme.c("border"), p)))
            tween(self, 160, lambda p: self.configure(
                fg_color=lerp_color(theme.c("shadow_strong"), theme.c("shadow"), p)))

        bind_recursive(self, "<Enter>", enter)
        bind_recursive(self, "<Leave>", leave)
        if self._on_click:
            bind_recursive(self, "<Button-1>", lambda e: self._on_click())


# ===========================================================================
# BUTTON  — eased hover + tactile press
# ===========================================================================
class Button(ctk.CTkButton):
    def __init__(self, master, text="", variant="primary", command=None, **kw):
        bg, hover, fg, border = self._palette(variant)
        self._base_bg, self._hover_bg = bg, hover
        kw.setdefault("height", 44)
        kw.setdefault("corner_radius", R["md"])
        super().__init__(
            master, text=text, command=command,
            font=theme.font("body_md"),
            fg_color=bg, hover=False, text_color=fg,
            border_width=1 if variant in ("secondary", "ghost") else 0,
            border_color=border, **kw)
        self.bind("<Enter>", self._enter, add="+")
        self.bind("<Leave>", self._leave, add="+")
        self.bind("<ButtonPress-1>", self._press, add="+")
        self.bind("<ButtonRelease-1>", self._release, add="+")

    def _palette(self, v):
        t = theme
        return {
            "primary":   (t.c("accent"), t.c("accent_hover"), t.c("text_on_accent"), ""),
            "secondary": (t.c("surface"), t.c("surface_alt"), t.c("text"), t.c("border_strong")),
            "ghost":     (t.c("accent_soft"), t.c("accent_soft"), t.c("accent"), t.c("accent_soft")),
            "danger":    (t.c("danger"), lerp_color(t.c("danger"), "#000000", .12), "#FFFFFF", ""),
        }[v]

    def _enter(self, _):
        tween(self, 120, lambda p: self._safe(lerp_color(self._base_bg, self._hover_bg, p)))

    def _leave(self, _):
        tween(self, 140, lambda p: self._safe(lerp_color(self._hover_bg, self._base_bg, p)))

    def _press(self, _):
        self._safe(lerp_color(self._hover_bg, "#000000", 0.10))

    def _release(self, _):
        self._safe(self._hover_bg)

    def _safe(self, color):
        try: self.configure(fg_color=color)
        except tk.TclError: pass


# ===========================================================================
# SPINNER — rotating arc on a Canvas
# ===========================================================================
class Spinner(ctk.CTkFrame):
    def __init__(self, master, size=48, width=4, bg=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.size, self.width = size, width
        self._angle = 0
        self._running = False
        self.canvas = tk.Canvas(self, width=size, height=size,
                                highlightthickness=0,
                                bg=bg or theme.c("bg"))
        self.canvas.pack()

    def start(self):
        self._running = True
        self._spin()

    def stop(self):
        self._running = False

    def _spin(self):
        if not self._running or not self.winfo_exists():
            return
        c, s, p = self.canvas, self.size, 6
        c.delete("all")
        c.create_arc(p, p, s - p, s - p, start=0, extent=359, style="arc",
                     outline=theme.c("border"), width=self.width)
        c.create_arc(p, p, s - p, s - p, start=self._angle, extent=100, style="arc",
                     outline=theme.c("accent"), width=self.width)
        self._angle = (self._angle - 12) % 360
        self.after(16, self._spin)


# ===========================================================================
# DRAWER — right-side slide-in panel (the WHY / HOW explanation facility)
# ===========================================================================
class Drawer(ctk.CTkFrame):
    def __init__(self, root, width_frac: float = 0.42):
        super().__init__(root, fg_color=theme.c("surface"), corner_radius=0)
        self.root = root
        self.width_frac = width_frac
        self._open = False
        self._edge = ctk.CTkFrame(root, fg_color=theme.c("shadow_strong"),
                                  corner_radius=0, width=10)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SP[6], pady=(SP[6], SP[3]))
        self.title_lbl = ctk.CTkLabel(header, text="", font=theme.font("h2"),
                                      text_color=theme.c("text"), anchor="w")
        self.title_lbl.pack(side="left")
        Button(header, text="✕", variant="ghost", width=36, height=36,
               command=self.close).pack(side="right")

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=SP[6], pady=(0, SP[6]))

    def open(self, title, body_builder: Callable[[ctk.CTkFrame], None]):
        for w in self.body.winfo_children():
            w.destroy()
        self.title_lbl.configure(text=title)
        body_builder(self.body)

        start, target = 1.0, 1.0 - self.width_frac
        self.place(relx=start, rely=0, relwidth=self.width_frac, relheight=1)
        self._edge.place(relx=start, rely=0, relheight=1)
        self.lift(); self._open = True

        def step(p):
            x = start + (target - start) * p
            self.place_configure(relx=x)
            self._edge.place_configure(relx=x - 0.008)
        tween(self, 260, step)

    def close(self):
        if not self._open:
            return
        start = 1.0 - self.width_frac
        def step(p):
            x = start + self.width_frac * p
            self.place_configure(relx=x)
            self._edge.place_configure(relx=x - 0.008)
        tween(self, 220, step,
              on_done=lambda: (self.place_forget(), self._edge.place_forget()))
        self._open = False


# ===========================================================================
# TOAST — transient confirmation sliding up from the bottom
# ===========================================================================
def toast(root, message, kind="success", ms=2600):
    tone = {"success": "success", "danger": "danger",
            "warning": "warning", "info": "info"}[kind]
    card = ctk.CTkFrame(root, fg_color=theme.c("surface"), corner_radius=R["md"],
                        border_width=1, border_color=theme.c("border"))
    ctk.CTkFrame(card, fg_color=theme.c(tone), width=4,
                 corner_radius=R["md"]).pack(side="left", fill="y", pady=2, padx=(2, 0))
    ctk.CTkLabel(card, text=message, font=theme.font("body"),
                 text_color=theme.c("text")).pack(side="left", padx=(SP[3], SP[5]),
                 pady=SP[3])
    card.place(relx=0.5, rely=1.06, anchor="s")
    card.lift()
    tween(card, 240, lambda p: card.place_configure(rely=1.06 - 0.08 * p))

    def dismiss():
        if card.winfo_exists():
            tween(card, 220, lambda p: card.place_configure(rely=0.98 + 0.08 * p),
                  on_done=card.destroy)
    root.after(ms, dismiss)


# ===========================================================================
# PAGE TRANSITION — slide-swap container content
# ===========================================================================
def slide_swap(container, build_new, direction="left"):
    """Slide old content out and new content in. build_new(parent) builds into
    the frame it's given. Returns the new frame."""
    old = list(container.winfo_children())
    new = ctk.CTkFrame(container, fg_color="transparent")
    build_new(new)

    off = 1.0 if direction == "left" else -1.0
    new.place(relx=off, rely=0, relwidth=1, relheight=1)
    for w in old:
        try: w.place(relx=0, rely=0, relwidth=1, relheight=1)
        except tk.TclError: pass

    def step(p):
        try: new.place_configure(relx=off * (1 - p))
        except tk.TclError: pass
        for w in old:
            try: w.place_configure(relx=-off * p)
            except tk.TclError: pass

    def done():
        for w in old:
            try: w.destroy()
            except tk.TclError: pass
        try: new.place_configure(relx=0)
        except tk.TclError: pass

    tween(container, 300, step, on_done=done)
    return new


# ===========================================================================
# NAV ITEM — SaaS rail item (assumes a DARK sidebar background)
# ===========================================================================
class NavItem(ctk.CTkFrame):
    def __init__(self, master, icon, label, active=False, done=False,
                 command=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self._active = active
        self.pill = ctk.CTkFrame(self, corner_radius=R["md"],
                                 fg_color=theme.c("accent") if active else "transparent")
        self.pill.pack(fill="x")
        inner = ctk.CTkFrame(self.pill, fg_color="transparent")
        inner.pack(fill="x", padx=SP[3], pady=SP[2])

        if active:
            ic_col = txt_col = theme.c("text_on_accent")
        elif done:
            ic_col = theme.c("accent"); txt_col = theme.c("text_on_dark")
        else:
            ic_col = txt_col = theme.c("text_on_dark_muted")

        ctk.CTkLabel(inner, text=("✓" if done and not active else icon), width=22,
                     font=theme.font("body_md"), text_color=ic_col).pack(
                     side="left", padx=(SP[1], SP[3]))
        ctk.CTkLabel(inner, text=label, anchor="w",
                     font=theme.font("body_md" if active else "body"),
                     text_color=txt_col).pack(side="left", fill="x", expand=True)

        clickable = command is not None
        if clickable:
            bind_recursive(self, "<Button-1>", lambda e: command())
        if not active and clickable:
            bind_recursive(self, "<Enter>", lambda e: self._hover(True))
            bind_recursive(self, "<Leave>", lambda e: self._hover(False))

    def _hover(self, on):
        try:
            self.pill.configure(fg_color=theme.c("sidebar_hover") if on else "transparent")
            self.configure(cursor="hand2" if on else "arrow")
        except tk.TclError:
            pass
