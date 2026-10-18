"""Axentra - left menu: Home fixed on top, apps listed below it."""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QButtonGroup, QFrame, QLabel, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)


class Sidebar(QFrame):
    selected = pyqtSignal(str)  # key: "home" or "app:<name>"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(200)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons = {}

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        h = QLabel("MENU")
        h.setObjectName("sideHeader")
        lay.addWidget(h)
        lay.addWidget(self._make_button("home", "Home"))

        self.apps_header = QLabel("APPS")
        self.apps_header.setObjectName("sideHeader")
        self.apps_header.hide()
        lay.addWidget(self.apps_header)

        self.container = QWidget()
        self.container.setObjectName("appsContainer")
        self.apps_lay = QVBoxLayout(self.container)
        self.apps_lay.setContentsMargins(0, 0, 0, 0)
        self.apps_lay.setSpacing(0)
        self.apps_lay.addStretch(1)

        scroll = QScrollArea()
        scroll.setObjectName("appsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidget(self.container)
        lay.addWidget(scroll, 1)

    def _make_button(self, key, text):
        b = QPushButton(text)
        b.setObjectName("menuBtn")
        b.setCheckable(True)
        b.setCursor(Qt.PointingHandCursor)
        b.clicked.connect(lambda _=False, k=key: self.selected.emit(k))
        self.group.addButton(b)
        self.buttons[key] = b
        return b

    def set_apps(self, items):
        """items: list of (key, text). Reconciles the app buttons, sorted by text."""
        wanted = {k for k, _ in items}
        for key in [k for k in self.buttons if k != "home" and k not in wanted]:
            b = self.buttons.pop(key)
            self.group.removeButton(b)
            b.deleteLater()
        for key, text in items:
            if key not in self.buttons:
                self._make_button(key, text)

        while self.apps_lay.count():
            self.apps_lay.takeAt(0)
        for key, _ in sorted(items, key=lambda kv: kv[1].lower()):
            self.apps_lay.addWidget(self.buttons[key])
        self.apps_lay.addStretch(1)
        self.apps_header.setVisible(bool(items))

    def select(self, key):
        b = self.buttons.get(key)
        if b:
            b.setChecked(True)
            self.selected.emit(key)
