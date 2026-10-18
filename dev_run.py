"""
Preview ONE app on its own, without the whole panel (handy on your own PC).
It reloads automatically every time you save a .py file of the app.

    python3 dev_run.py template
    python3 dev_run.py kit_demo
"""
import sys
import traceback

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow

from axentra.core.app_loader import AppManager
from axentra.theme import STYLE
from axentra.ui.error_page import ErrorPage


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 dev_run.py <app_name>")
    name = sys.argv[1]
    sys.excepthook = lambda t, v, tb: traceback.print_exception(t, v, tb)

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    win = QMainWindow()
    win.setWindowTitle("Axentra dev - " + name)
    win.resize(1000, 620)

    mgr = AppManager(context=win)
    mgr.scan()
    key = "app:" + name
    if key not in mgr.entries:
        sys.exit("No app called '%s'. Available: %s" % (name, ", ".join(sorted(e.name for e in mgr.entries.values()))))
    entry = mgr.entries[key]

    def load():
        try:
            widget = mgr.build_widget(entry)
        except Exception:
            widget = ErrorPage(name, traceback.format_exc())
        win.setCentralWidget(widget)      # replaces (and deletes) the previous one

    def check():
        _, _, modified = mgr.scan()
        if any(e.key == key for e in modified):
            load()

    load()
    win.show()
    timer = QTimer(win)
    timer.timeout.connect(check)
    timer.start(1000)
    app.aboutToQuit.connect(mgr.shutdown)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
