"""Axentra - colors and the global dark stylesheet."""

C = {
    "bg":        "#14171c",
    "card":      "#1a1e25",
    "topbar":    "#1b1f26",
    "sidebar":   "#181c22",
    "border":    "#2a303a",
    "grid":      "#242a33",
    "text":      "#d8dee9",
    "muted":     "#7b8494",
    "hover":     "#222833",
    "active_bg": "#232b38",
    "accent":    "#3b9cff",
    "ok":        "#3ddc84",
    "bad":       "#ff5c5c",
    "warn":      "#f5a623",
    # chart colors
    "c_cpu":     "#3b9cff",
    "c_ram":     "#b57bff",
    "c_net":     "#3ddc84",
    "c_temp":    "#ff7a45",
}

STYLE = f"""
* {{
    font-family: "Ubuntu", "DejaVu Sans", sans-serif;
    font-size: 13px;
    color: {C['text']};
}}
QMainWindow, QWidget#content {{ background: {C['bg']}; }}

/* ---------- top bar ---------- */
QFrame#topbar {{ background: {C['topbar']}; border-bottom: 1px solid {C['border']}; }}
QLabel#appTitle {{ font-size: 14px; font-weight: 600; letter-spacing: 3px; }}
QLabel#hostname {{ color: {C['muted']}; }}
QLabel#clock {{ font-size: 13px; font-weight: 500; }}
QFrame#vsep {{ background: {C['border']}; max-width: 1px; min-width: 1px; }}

QPushButton#powerBtn {{
    background: transparent; border: 1px solid {C['border']};
    border-radius: 4px; padding: 4px 12px 4px 8px; color: {C['text']};
}}
QPushButton#powerBtn:hover {{ background: {C['hover']}; border-color: {C['muted']}; }}
QPushButton#powerBtn[kind="off"]:hover {{ border-color: {C['bad']}; color: {C['bad']}; }}
QPushButton#powerBtn[kind="reboot"]:hover {{ border-color: {C['warn']}; color: {C['warn']}; }}

/* ---------- sidebar ---------- */
QFrame#sidebar {{ background: {C['sidebar']}; border-right: 1px solid {C['border']}; }}
QLabel#sideHeader {{
    color: {C['muted']}; font-size: 11px; letter-spacing: 2px;
    padding: 14px 18px 8px 18px;
}}
QPushButton#menuBtn {{
    background: transparent; border: none; border-left: 3px solid transparent;
    text-align: left; padding: 11px 18px; color: {C['text']};
}}
QPushButton#menuBtn:hover {{ background: {C['hover']}; }}
QPushButton#menuBtn:checked {{
    background: {C['active_bg']}; border-left: 3px solid {C['accent']};
    color: #ffffff; font-weight: 600;
}}
QScrollArea#appsScroll {{ background: transparent; border: none; }}
QWidget#appsContainer {{ background: transparent; }}
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {C['border']}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ---------- home cards ---------- */
QFrame#card {{ background: {C['card']}; border: 1px solid {C['border']}; border-radius: 6px; }}
QFrame#card QLabel {{ background: transparent; }}
QLabel#cardTitle {{ color: {C['muted']}; font-size: 11px; letter-spacing: 2px; }}
QLabel#bigNum {{ font-size: 40px; font-weight: 600; }}
QLabel#cardSub {{ color: {C['muted']}; }}
QProgressBar {{
    background: #10131a; border: 1px solid {C['border']}; border-radius: 4px;
    max-height: 8px; min-height: 8px;
}}
QProgressBar::chunk {{ background: {C['accent']}; border-radius: 3px; }}

/* ---------- error page ---------- */
QLabel#pageTitle {{ font-size: 18px; font-weight: 600; }}
QPlainTextEdit#errorBox {{
    background: #10131a; border: 1px solid {C['border']}; border-radius: 4px;
    font-family: "DejaVu Sans Mono", monospace; font-size: 12px; color: {C['bad']};
}}

/* ---------- dialogs ---------- */
QMessageBox, QDialog {{ background: {C['topbar']}; }}
QMessageBox QPushButton {{
    background: {C['active_bg']}; border: 1px solid {C['border']};
    border-radius: 4px; padding: 6px 18px; min-width: 70px;
}}
QMessageBox QPushButton:hover {{ border-color: {C['accent']}; }}
"""


# ===========================================================================
# Extra styles: Axentra UI kit + ordinary Qt widgets (so apps look right even
# if they use plain QPushButton / QLineEdit / QComboBox ...)
# ===========================================================================
def _rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    return "rgba(%d, %d, %d, %s)" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


STYLE += f"""
/* ---------- buttons ---------- */
QPushButton {{
    background: {C['active_bg']}; border: 1px solid {C['border']};
    border-radius: 4px; padding: 7px 16px;
}}
QPushButton:hover {{ background: {C['hover']}; border-color: {C['muted']}; }}
QPushButton:pressed {{ background: {C['bg']}; }}
QPushButton:disabled {{ color: {C['muted']}; border-color: {C['grid']}; }}
QPushButton:checked {{ background: {C['accent']}; border-color: {C['accent']}; color: #ffffff; }}
QPushButton[kind="primary"] {{ background: {C['accent']}; border-color: {C['accent']}; color: #ffffff; font-weight: 600; }}
QPushButton[kind="primary"]:hover {{ background: #5aaeff; border-color: #5aaeff; }}
QPushButton[kind="success"] {{ background: transparent; border-color: {C['ok']}; color: {C['ok']}; }}
QPushButton[kind="success"]:hover {{ background: {C['ok']}; color: #0b0f14; }}
QPushButton[kind="danger"] {{ background: transparent; border-color: {C['bad']}; color: {C['bad']}; }}
QPushButton[kind="danger"]:hover {{ background: {C['bad']}; color: #ffffff; }}
QPushButton[kind="ghost"] {{ background: transparent; border-color: transparent; }}
QPushButton[kind="ghost"]:hover {{ background: {C['hover']}; }}

QPushButton#segBtn {{ border-radius: 0; padding: 6px 16px; }}
QPushButton#segBtn[pos="first"] {{ border-top-left-radius: 4px; border-bottom-left-radius: 4px; }}
QPushButton#segBtn[pos="last"] {{ border-top-right-radius: 4px; border-bottom-right-radius: 4px; }}
QPushButton#segBtn[pos="only"] {{ border-radius: 4px; }}

/* ---------- inputs ---------- */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QPlainTextEdit, QTextEdit {{
    background: #10131a; border: 1px solid {C['border']}; border-radius: 4px;
    padding: 6px 10px; selection-background-color: {C['accent']}; selection-color: #ffffff;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus,
QPlainTextEdit:focus, QTextEdit:focus {{ border-color: {C['accent']}; }}
QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{ color: {C['muted']}; }}

QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox::down-arrow {{
    image: none; width: 0; height: 0; margin-right: 8px;
    border-left: 4px solid transparent; border-right: 4px solid transparent;
    border-top: 5px solid {C['muted']};
}}
QComboBox QAbstractItemView {{
    background: {C['card']}; border: 1px solid {C['border']};
    selection-background-color: {C['active_bg']}; selection-color: #ffffff; outline: 0;
}}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 20px; border: none; background: transparent; }}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    image: none; width: 0; height: 0;
    border-left: 4px solid transparent; border-right: 4px solid transparent;
    border-bottom: 5px solid {C['muted']};
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    image: none; width: 0; height: 0;
    border-left: 4px solid transparent; border-right: 4px solid transparent;
    border-top: 5px solid {C['muted']};
}}

QCheckBox, QRadioButton {{ spacing: 8px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border: 1px solid {C['muted']}; border-radius: 3px; background: #10131a;
}}
QCheckBox::indicator:hover {{ border-color: {C['accent']}; }}
QCheckBox::indicator:checked {{ background: {C['accent']}; border-color: {C['accent']}; }}
QRadioButton::indicator {{
    width: 16px; height: 16px; border: 1px solid {C['muted']}; border-radius: 9px; background: #10131a;
}}
QRadioButton::indicator:hover {{ border-color: {C['accent']}; }}
QRadioButton::indicator:checked {{
    border-color: {C['accent']};
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 {C['accent']}, stop:0.45 {C['accent']}, stop:0.5 #10131a, stop:1 #10131a);
}}

/* ---------- slider (horizontal) ---------- */
QSlider::groove:horizontal {{
    height: 6px; background: #10131a; border: 1px solid {C['border']}; border-radius: 3px;
}}
QSlider::sub-page:horizontal {{ background: {C['accent']}; border-radius: 3px; }}
QSlider::handle:horizontal {{
    background: #e8eefc; border: 2px solid {C['accent']};
    width: 14px; height: 14px; margin: -7px 0; border-radius: 9px;
}}
QSlider::handle:horizontal:hover {{ background: #ffffff; }}

/* ---------- tables / lists / tabs ---------- */
QTableWidget, QListWidget, QTreeWidget {{
    background: {C['card']}; border: 1px solid {C['border']}; border-radius: 6px;
    gridline-color: {C['grid']}; alternate-background-color: #1e232b;
    selection-background-color: {C['active_bg']}; selection-color: #ffffff; outline: 0;
}}
QTableWidget::item, QListWidget::item, QTreeWidget::item {{ padding: 4px 8px; }}
QTreeWidget::branch {{ background: transparent; }}
QHeaderView::section {{
    background: {C['topbar']}; color: {C['muted']}; border: none;
    border-bottom: 1px solid {C['border']}; padding: 7px 8px; font-size: 11px; letter-spacing: 1px;
}}
QTableCornerButton::section {{ background: {C['topbar']}; border: none; }}
QTabWidget::pane {{ border: 1px solid {C['border']}; border-radius: 6px; top: -1px; }}
QTabBar::tab {{
    background: transparent; padding: 8px 18px; border: none; color: {C['muted']};
    border-bottom: 2px solid transparent;
}}
QTabBar::tab:hover {{ color: {C['text']}; }}
QTabBar::tab:selected {{ color: #ffffff; border-bottom: 2px solid {C['accent']}; }}

/* ---------- scrollbars / tooltip ---------- */
QScrollBar:horizontal {{ background: transparent; height: 8px; margin: 0; }}
QScrollBar::handle:horizontal {{ background: {C['border']}; border-radius: 4px; min-width: 24px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QToolTip {{ background: {C['card']}; color: {C['text']}; border: 1px solid {C['border']}; padding: 4px 8px; }}

/* ---------- kit: page, labels, misc ---------- */
QScrollArea#page {{ background: transparent; border: none; }}
QScrollArea#page > QWidget > QWidget {{ background: transparent; }}
QWidget#pageBody {{ background: transparent; }}
QLabel#pageSubtitle {{ color: {C['muted']}; }}
QFrame#hsep {{ background: {C['border']}; max-height: 1px; min-height: 1px; }}
QPlainTextEdit#logView {{
    font-family: "DejaVu Sans Mono", monospace; font-size: 12px; background: #10131a;
}}
QLabel#badge {{ border-radius: 9px; padding: 2px 10px; font-size: 11px; font-weight: 600; }}
QLabel#toast {{
    background: {C['card']}; border: 1px solid {C['border']}; border-radius: 6px; padding: 10px 18px;
}}
"""

_KINDS = {"ok": C["ok"], "warn": C["warn"], "bad": C["bad"], "info": C["accent"], "muted": C["muted"]}
for _k, _c in _KINDS.items():
    STYLE += """
QLabel#badge[kind="%s"] { background: %s; color: %s; border: 1px solid %s; }
QLabel#toast[kind="%s"] { border-color: %s; }
""" % (_k, _rgba(_c, 0.15), _c, _c, _k, _c)
