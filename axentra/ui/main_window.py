"""Axentra - main window: top bar + sidebar + page stack. Wires everything together."""
import traceback

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QMainWindow, QShortcut,
                             QStackedWidget, QVBoxLayout, QWidget)

from axentra import config
from axentra.core.app_loader import AppManager
from axentra.core.power import PowerController
from axentra.ui.error_page import ErrorPage
from axentra.ui.home_page import HomePage
from axentra.ui.sidebar import Sidebar
from axentra.ui.top_bar import TopBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.resize(1100, 640)

        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.topbar = TopBar()
        outer.addWidget(self.topbar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        outer.addLayout(body, 1)

        self.sidebar = Sidebar()
        self.stack = QStackedWidget()
        self.stack.setObjectName("content")
        body.addWidget(self.sidebar)
        body.addWidget(self.stack, 1)

        self.home = HomePage()
        self.stack.addWidget(self.home)
        self.current_key = "home"

        self.power = PowerController(self)
        self.topbar.power_requested.connect(self.power.request)

        self.sidebar.selected.connect(self.show_page)
        self.sidebar.select("home")

        QShortcut(QKeySequence("F11"), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Q"), self, activated=self.close)

        # apps/ watcher (last, so background modules get a fully built window)
        self.apps = AppManager(context=self)
        self.scan_apps()
        QTimer(self, timeout=self.scan_apps).start(config.APPS_SCAN_MS)

    # ---------------------------------------------------------------- display
    def present(self):
        if config.FULLSCREEN:
            self.setWindowFlag(Qt.FramelessWindowHint, True)   # no title bar / X / square / minus
            screen = QApplication.primaryScreen()
            if screen is not None:
                self.setGeometry(screen.geometry())
            self.showFullScreen()
        else:
            self.show()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def shutdown(self):
        self.apps.shutdown()

    # ------------------------------------------------------------------ pages
    def show_page(self, key):
        self.current_key = key
        if key == "home":
            self.stack.setCurrentWidget(self.home)
            return
        entry = self.apps.entries.get(key)
        if entry is None:
            self.sidebar.select("home")
            return
        if entry.widget is None:
            entry.widget = self._make_page(entry)
            self.stack.addWidget(entry.widget)
        self.stack.setCurrentWidget(entry.widget)

    def _make_page(self, entry):
        try:
            return self.apps.build_widget(entry)
        except Exception:
            return ErrorPage(entry.name, traceback.format_exc())

    def _drop_widget(self, entry):
        if entry.widget is not None:
            self.stack.removeWidget(entry.widget)
            entry.widget.deleteLater()
            entry.widget = None

    def scan_apps(self):
        try:
            added, removed, modified = self.apps.scan()
        except Exception:
            traceback.print_exc()
            return

        for entry in removed:
            self._drop_widget(entry)
            if self.current_key == entry.key:
                self.sidebar.select("home")
        for entry in modified:                      # app edited -> reload it
            was_open = self.current_key == entry.key
            self._drop_widget(entry)
            if was_open:
                self.show_page(entry.key)
        if added or removed:
            self.sidebar.set_apps([(e.key, e.name) for e in self.apps.entries.values()])
