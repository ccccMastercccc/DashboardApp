"""Axentra kit - tiny internal helpers (you normally never touch this file)."""
from PyQt5.QtGui import QColor

from axentra.theme import C

_KIND_COLORS = {
    "ok": C["ok"], "warn": C["warn"], "bad": C["bad"],
    "info": C["accent"], "accent": C["accent"], "muted": C["muted"],
}


def kind_color(kind):
    """'ok' / 'warn' / 'bad' / 'info' / 'muted' -> hex color string."""
    return _KIND_COLORS.get(kind, C["accent"])


def level_color(percent):
    """Green below 60, orange below 85, red above."""
    if percent < 60:
        return C["ok"]
    if percent < 85:
        return C["warn"]
    return C["bad"]


def mix(c1, c2, t):
    """Blend two colors. t=0 -> c1, t=1 -> c2."""
    a, b = QColor(c1), QColor(c2)
    return QColor(
        int(a.red() + (b.red() - a.red()) * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue() + (b.blue() - a.blue()) * t),
    )


def repolish(widget):
    """Re-apply the stylesheet after a dynamic property (like `kind`) changed."""
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
