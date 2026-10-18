"""
Axentra kit - charts.

    LineChart("CPU", COLORS["c_cpu"], unit="%", vmin=0, vmax=100, history=60, interval_ms=1000)
        .push(value)                      call it every interval_ms; the line slides left smoothly
    BarChart("Requests", unit=" req")
        .set_data(["Mon","Tue"], [12, 30])
    DonutChart("Storage")
        .set_data([("Used", 70), ("Free", 30)])         optional 3rd item = color
"""
from PyQt5.QtCore import QPointF, QRectF, QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

from axentra.theme import C
from axentra.ui.widgets.charts import LineChart  # noqa: F401  (re-exported)

PALETTE = [C["accent"], C["c_ram"], C["ok"], C["c_temp"], C["warn"], C["bad"]]


def _card(p, w, h):
    p.setPen(QPen(QColor(C["border"]), 1))
    p.setBrush(QColor(C["card"]))
    p.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 6, 6)


class BarChart(QWidget):
    def __init__(self, title="", color=None, unit="", vmax=None, decimals=0):
        super().__init__()
        self.title, self.unit, self.vmax, self.decimals = title, unit, vmax, decimals
        self.color = color
        self.labels, self.values = [], []
        self.setMinimumHeight(140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self):
        return QSize(320, 200)

    def set_data(self, labels, values):
        self.labels, self.values = list(labels), [float(v) for v in values]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        _card(p, w, h)
        f = QFont(self.font())
        f.setPixelSize(11)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        p.drawText(QRectF(12, 8, w - 24, 18), Qt.AlignLeft | Qt.AlignVCenter, self.title.upper())

        n = len(self.values)
        if n == 0:
            return
        plot = QRectF(12, 38, w - 24, h - 38 - 26)
        vmax = self.vmax or max(max(self.values) * 1.15, 1.0)
        slot = plot.width() / n
        bw = min(slot * 0.6, 56)
        for i, v in enumerate(self.values):
            bh = plot.height() * min(v / vmax, 1.0)
            x = plot.left() + slot * i + (slot - bw) / 2
            col = QColor(self.color or PALETTE[i % len(PALETTE)])
            g = QLinearGradient(0, plot.bottom() - bh, 0, plot.bottom())
            g.setColorAt(0, col.lighter(125))
            g.setColorAt(1, col)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(g))
            p.drawRoundedRect(QRectF(x, plot.bottom() - bh, bw, bh), 3, 3)
            p.setPen(QColor(C["text"]))
            p.drawText(QRectF(x - 10, plot.bottom() - bh - 18, bw + 20, 16), Qt.AlignCenter,
                       "%.*f%s" % (self.decimals, v, self.unit))
            p.setPen(QColor(C["muted"]))
            lab = self.labels[i] if i < len(self.labels) else ""
            p.drawText(QRectF(plot.left() + slot * i, plot.bottom() + 6, slot, 16), Qt.AlignCenter, lab)


class DonutChart(QWidget):
    def __init__(self, title=""):
        super().__init__()
        self.title = title
        self.items = []
        self.setMinimumSize(260, 150)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self):
        return QSize(340, 190)

    def set_data(self, items):
        self.items = [tuple(i) for i in items]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        _card(p, w, h)
        f = QFont(self.font())
        f.setPixelSize(11)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        p.drawText(QRectF(12, 8, w - 24, 18), Qt.AlignLeft | Qt.AlignVCenter, self.title.upper())

        total = sum(i[1] for i in self.items)
        size = min(h - 46, w * 0.5)
        rect = QRectF(16, 34, size, size)
        thick = max(size * 0.16, 8.0)
        ring = rect.adjusted(thick / 2, thick / 2, -thick / 2, -thick / 2)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#10131a"), thick, Qt.SolidLine, Qt.FlatCap))
        p.drawArc(ring, 0, 360 * 16)

        angle = 90.0
        for idx, item in enumerate(self.items):
            if total <= 0:
                break
            span = 360.0 * item[1] / total
            col = QColor(item[2]) if len(item) > 2 else QColor(PALETTE[idx % len(PALETTE)])
            p.setPen(QPen(col, thick, Qt.SolidLine, Qt.FlatCap))
            p.drawArc(ring, int(angle * 16), int(-span * 16))
            angle -= span

        # legend
        lx, ly = rect.right() + 24, 40
        for idx, item in enumerate(self.items):
            col = QColor(item[2]) if len(item) > 2 else QColor(PALETTE[idx % len(PALETTE)])
            p.setPen(Qt.NoPen)
            p.setBrush(col)
            p.drawRoundedRect(QRectF(lx, ly + idx * 22 + 3, 10, 10), 2, 2)
            pct = (100.0 * item[1] / total) if total else 0.0
            p.setPen(QColor(C["text"]))
            p.drawText(QRectF(lx + 18, ly + idx * 22, w - lx - 24, 16), Qt.AlignLeft | Qt.AlignVCenter,
                       "%s   %.0f%%" % (item[0], pct))
