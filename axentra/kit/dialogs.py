"""
Axentra kit - dialogs and toast messages.

    if confirm(self, "Delete this item?"):  ...          -> True / False
    info(self, "Saved.")      warning(self, "..")      error(self, "..")
    name = ask_text(self, "Name:", default="x")          -> str, or None if cancelled
    toast(self, "Saved", "ok")                           small message that disappears (ok warn bad info)

`self` can be any widget of your app.
"""
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QInputDialog, QLabel, QMessageBox


def _box(parent, icon, title, text):
    box = QMessageBox(parent)
    box.setIcon(icon)
    box.setWindowTitle(title)
    box.setText(text)
    return box


def confirm(parent, text, title="Confirm", yes="Yes", no="Cancel"):
    box = _box(parent, QMessageBox.Question, title, text)
    y = box.addButton(yes, QMessageBox.YesRole)
    box.addButton(no, QMessageBox.NoRole)
    box.exec_()
    return box.clickedButton() is y


def info(parent, text, title="Information"):
    _box(parent, QMessageBox.Information, title, text).exec_()


def warning(parent, text, title="Warning"):
    _box(parent, QMessageBox.Warning, title, text).exec_()


def error(parent, text, title="Error"):
    _box(parent, QMessageBox.Critical, title, text).exec_()


def ask_text(parent, label, default="", title="Input"):
    value, ok = QInputDialog.getText(parent, title, label, text=default)
    return value if ok else None


def toast(widget, text, kind="info", ms=2500):
    win = widget.window()
    lab = QLabel(text, win)
    lab.setObjectName("toast")
    lab.setProperty("kind", kind)
    lab.show()
    lab.adjustSize()
    lab.move((win.width() - lab.width()) // 2, win.height() - lab.height() - 30)
    lab.raise_()
    QTimer.singleShot(ms, lab.deleteLater)
