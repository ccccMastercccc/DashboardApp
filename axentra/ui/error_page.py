"""Axentra - shown instead of an app that failed to load (the panel never crashes)."""
from PyQt5.QtWidgets import QLabel, QPlainTextEdit, QVBoxLayout, QWidget


class ErrorPage(QWidget):
    def __init__(self, name, tb):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        t = QLabel("App error: %s" % name)
        t.setObjectName("pageTitle")
        box = QPlainTextEdit(tb)
        box.setObjectName("errorBox")
        box.setReadOnly(True)
        lay.addWidget(t)
        lay.addWidget(box, 1)
