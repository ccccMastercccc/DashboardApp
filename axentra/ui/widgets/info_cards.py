"""Axentra - info cards: CPU temperature, disk usage, logged-in users."""
from PyQt5.QtWidgets import QFrame, QLabel, QProgressBar, QVBoxLayout

from axentra.core.utils import human_bytes
from axentra.theme import C


def _title(text):
    l = QLabel(text)
    l.setObjectName("cardTitle")
    return l


class _Card(QFrame):
    def __init__(self, title):
        super().__init__()
        self.setObjectName("card")
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(16, 12, 16, 12)
        self.lay.addWidget(_title(title))


class TempCard(_Card):
    def __init__(self, width=None):
        super().__init__("CPU TEMPERATURE")
        if width:
            self.setFixedWidth(width)
        self.lbl = QLabel("--")
        self.lbl.setObjectName("bigNum")
        self.sub = QLabel("")
        self.sub.setObjectName("cardSub")
        self.lay.addWidget(self.lbl)
        self.lay.addWidget(self.sub)
        self.lay.addStretch(1)

    def update_stats(self, s):
        t = s["temp"]
        if t is None:
            self.lbl.setText("--")
            self.lbl.setStyleSheet("color:%s;" % C["muted"])
            self.sub.setText("No sensor found")
            return
        if t < 60:
            col, word = C["ok"], "Normal"
        elif t < 75:
            col, word = C["warn"], "Warm"
        else:
            col, word = C["bad"], "Hot"
        self.lbl.setText("%.0f°C" % t)
        self.lbl.setStyleSheet("color:%s;" % col)
        self.sub.setText(word)


class DiskCard(_Card):
    def __init__(self):
        super().__init__("DISK")
        self.free = QLabel("--")
        self.free.setObjectName("bigNum")
        self.sub = QLabel("")
        self.sub.setObjectName("cardSub")
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 100)
        self.used = QLabel("")
        self.used.setObjectName("cardSub")
        self.lay.addWidget(self.free)
        self.lay.addWidget(self.sub)
        self.lay.addStretch(1)
        self.lay.addWidget(self.bar)
        self.lay.addWidget(self.used)

    def update_stats(self, s):
        self.free.setText(human_bytes(s["disk_free"]))
        self.sub.setText("free of %s" % human_bytes(s["disk_total"]))
        self.bar.setValue(int(s["disk_pct"]))
        self.used.setText("Used %s  (%.0f%%)" % (human_bytes(s["disk_used"]), s["disk_pct"]))


class UsersCard(_Card):
    def __init__(self):
        super().__init__("LOGGED-IN USERS")
        self.count = QLabel("0")
        self.count.setObjectName("bigNum")
        self.names = QLabel("")
        self.names.setObjectName("cardSub")
        self.names.setWordWrap(True)
        self.lay.addWidget(self.count)
        self.lay.addWidget(self.names)
        self.lay.addStretch(1)

    def update_stats(self, s):
        self.count.setText(str(len(s["users"])))
        self.names.setText(", ".join(s["users"]) if s["users"] else "nobody logged in")
