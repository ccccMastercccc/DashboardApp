"""Axentra - vertical animated progress bar (used for CPU and network)."""
from PyQt5.QtCore import QEasingCurve, QPointF, QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty
from PyQt5.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

from axentra.theme import C


class VBar(QWidget):
    """Vertical progress bar whose fill animates smoothly to each new value."""

    def __init__(self, title, fixed_color=None):
        super().__init__()
        self.title = title
        self.fixed_color = fixed_color
        self._level = 0.0
        self._text = "0"
        self.setMinimumSize(100, 200)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._anim = QPropertyAnimation(self, b"level", self)
        self._anim.setDuration(700)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def sizeHint(self):
        return QSize(110, 230)

    def _get_level(self):
        return self._level

    def _set_level(self, v):
        self._level = float(v)
        self.update()

    level = pyqtProperty(float, _get_level, _set_level)

    def set_value(self, percent, text):
        self._text = text
        self._anim.stop()
        self._anim.setStartValue(self._level)
        self._anim.setEndValue(min(max(float(percent), 0.0), 100.0))
        self._anim.start()

    def _color(self):
        if self.fixed_color:
            return QColor(self.fixed_color)
        if self._level < 60:
            return QColor(C["ok"])
        if self._level < 85:
            return QColor(C["warn"])
        return QColor(C["bad"])

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.setPen(QPen(QColor(C["border"]), 1))
        p.setBrush(QColor(C["card"]))
        p.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 6, 6)

        f = QFont(self.font())
        f.setPixelSize(16)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(C["text"]))
        p.drawText(QRectF(0, 8, w, 26), Qt.AlignCenter, self._text)

        f.setPixelSize(11)
        f.setBold(False)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        p.drawText(QRectF(0, h - 28, w, 20), Qt.AlignCenter, self.title)

        tw = 36
        track = QRectF((w - tw) / 2, 44, tw, h - 44 - 36)
        path = QPainterPath()
        path.addRoundedRect(track, 8, 8)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.setBrush(QColor("#10131a"))
        p.drawPath(path)

        # fill
        fh = track.height() * self._level / 100.0
        col = self._color()
        g = QLinearGradient(0, track.top(), 0, track.bottom())
        g.setColorAt(0, QColor(col).lighter(130))
        g.setColorAt(1, col)
        p.save()
        p.setClipPath(path)
        p.fillRect(QRectF(track.left(), track.bottom() - fh, track.width(), fh), QBrush(g))
        p.restore()

        # ticks
        p.setPen(QPen(QColor(C["muted"]), 1))
        for i in range(5):
            y = track.top() + track.height() * i / 4
            p.drawLine(QPointF(track.right() + 6, y), QPointF(track.right() + 11, y))
