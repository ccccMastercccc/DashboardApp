"""
Axentra app template.

Folder rule: apps/<name>/<name>.py  -> the main file has EXACTLY the folder's name.
Put every other file of your app next to it and import it from here.
The main file must define create_widget() OR class App(QWidget).
The panel's dark theme is applied automatically to everything you build here.
"""
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from .helper import greeting          # sibling file (plain `from helper import greeting` also works)


class App(QWidget):
    def __init__(self):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.addWidget(QLabel(greeting()))
        lay.addStretch(1)
