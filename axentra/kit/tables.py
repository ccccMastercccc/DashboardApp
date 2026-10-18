"""
Axentra kit - table and log console.

    t = DataTable(["Name", "Status", "CPU"], on_select=fn)      fn(row_values_list)
    t.set_rows([["nginx", "running", "3%"], ...])     replace everything
    t.add_row([...])   t.clear_rows()   t.selected_row() -> list or None

    log = LogView(max_lines=1000, timestamps=True)
    log.log("Service started", "ok")        kinds: ok warn bad info  (or None)
    log.clear()
"""
import html
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QHeaderView, QPlainTextEdit, QTableWidget,
                             QTableWidgetItem)

from axentra.kit._util import kind_color
from axentra.theme import C


class DataTable(QTableWidget):
    def __init__(self, headers, on_select=None):
        super().__init__(0, len(headers))
        self.setHorizontalHeaderLabels(list(headers))
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.NoFocus)
        if on_select:
            self.itemSelectionChanged.connect(lambda: on_select(self.selected_row()))

    def set_rows(self, rows):
        self.setRowCount(0)
        for r in rows:
            self.add_row(r)

    def add_row(self, values):
        i = self.rowCount()
        self.insertRow(i)
        for c, v in enumerate(values):
            self.setItem(i, c, QTableWidgetItem(str(v)))

    def clear_rows(self):
        self.setRowCount(0)

    def selected_row(self):
        r = self.currentRow()
        if r < 0 or not self.selectedItems():
            return None
        return [self.item(r, c).text() if self.item(r, c) else "" for c in range(self.columnCount())]


class LogView(QPlainTextEdit):
    def __init__(self, max_lines=1000, timestamps=True):
        super().__init__()
        self.setObjectName("logView")
        self.setReadOnly(True)
        self.setMaximumBlockCount(max_lines)
        self._ts = timestamps

    def log(self, text, kind=None):
        color = kind_color(kind) if kind else C["text"]
        stamp = datetime.now().strftime("%H:%M:%S  ") if self._ts else ""
        body = html.escape("%s%s" % (stamp, text))
        self.appendHtml('<span style="color:%s; white-space:pre;">%s</span>' % (color, body))
        bar = self.verticalScrollBar()
        bar.setValue(bar.maximum())

    def clear(self):
        self.setPlainText("")
