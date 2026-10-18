"""Axentra - scrolling line chart (RAM, CPU, network, temperature)."""
from collections import deque

from PyQt5.QtCore import QPointF, QRectF, QSize, Qt, QVariantAnimation
from PyQt5.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

from axentra import config
from axentra.theme import C


class LineChart(QWidget):
    """Line chart that slides smoothly to the left with every new sample."""

    def __init__(self, title, color, unit="", vmin=0.0, vmax=None, decimals=0,
                 history=None, interval_ms=None):
        """history = number of points on screen, interval_ms = how often you call push()."""
        super().__init__()
        self.title, self.color, self.unit = title, QColor(color), unit
        self.vmin, self.vmax, self.decimals = vmin, vmax, decimals
        self.history = history or config.HISTORY
        self._sub = ""
        self.data = deque([vmin] * (self.history + 1), maxlen=self.history + 1)
        self._shift = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setDuration(interval_ms or config.STATS_MS)
        self._anim.valueChanged.connect(self._on_shift)
        self.setMinimumHeight(110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self):
        return QSize(360, 170)

    def _on_shift(self, v):
        self._shift = float(v)
        self.update()

    def push(self, value, sub=""):
        self.data.append(self.vmin if value is None else float(value))
        self._sub = sub
        self._anim.stop()
        self._anim.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.setBrush(QColor(C["card"]))
        p.drawRoundedRect(r, 6, 6)

        # header: title (left) + current value (right)
        f = QFont(self.font())
        f.setPixelSize(11)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        head = self.title if not self._sub else "%s   %s" % (self.title, self._sub)
        p.drawText(QRectF(12, 8, r.width() - 110, 18), Qt.AlignLeft | Qt.AlignVCenter, head)
        f.setPixelSize(16)
        f.setBold(True)
        p.setFont(f)
        p.setPen(self.color)
        cur = self.data[-1]
        p.drawText(QRectF(r.width() - 112, 6, 100, 22), Qt.AlignRight | Qt.AlignVCenter,
                   "%.*f%s" % (self.decimals, cur, self.unit))

        plot = QRectF(12, 34, r.width() - 24, r.height() - 46)
        if plot.height() < 10:
            return

        # grid
        p.setPen(QPen(QColor(C["grid"]), 1))
        for i in range(5):
            y = plot.top() + plot.height() * i / 4
            p.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))

        vmax = self.vmax if self.vmax is not None else max(max(self.data) * 1.25, 1.0)
        span = max(vmax - self.vmin, 1e-6)
        step = plot.width() / (self.history - 1)
        pts = []
        for i, v in enumerate(self.data):
            x = plot.left() + (i - 1 + self._shift) * step
            frac = min(max((v - self.vmin) / span, 0.0), 1.0)
            pts.append(QPointF(x, plot.bottom() - frac * plot.height()))

        p.setClipRect(plot.adjusted(-1, -3, 1, 3))
        line = QPainterPath(pts[0])
        for pt in pts[1:]:
            line.lineTo(pt)
        area = QPainterPath(line)
        area.lineTo(pts[-1].x(), plot.bottom())
        area.lineTo(pts[0].x(), plot.bottom())
        area.closeSubpath()

        g = QLinearGradient(0, plot.top(), 0, plot.bottom())
        top = QColor(self.color)
        top.setAlpha(100)
        bottom = QColor(self.color)
        bottom.setAlpha(0)
        g.setColorAt(0, top)
        g.setColorAt(1, bottom)
        p.fillPath(area, QBrush(g))
        p.setPen(QPen(self.color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        p.setBrush(Qt.NoBrush)
        p.drawPath(line)
