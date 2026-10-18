"""
Axentra kit - bars and gauges (all animate smoothly to every new value).

    HBar("Disk", auto_color=True)       horizontal bar     .set_value(percent, "text")
    VBar("CPU")                         vertical bar       .set_value(percent, "text")   (same as on Home)
    RingGauge("Memory", auto_color=True) circular gauge    .set_value(percent, "text")

percent is 0..100. The optional text replaces the default "NN%".
auto_color=True turns green -> orange -> red as the value grows; or pass color="#3b9cff".
"""
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty
from PyQt5.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget

from axentra.kit._util import level_color
from axentra.theme import C
from axentra.ui.widgets.bars import VBar  # noqa: F401  (re-exported)


class _LevelWidget(QWidget):
    def __init__(self, title, color, auto_color):
        super().__init__()
        self.title = title
        self._color = color
        self._auto = auto_color
        self._level = 0.0
        self._text = "0%"
        self._anim = QPropertyAnimation(self, b"level", self)
        self._anim.setDuration(600)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def _get_level(self):
        return self._level

    def _set_level(self, v):
        self._level = float(v)
        self.update()

    level = pyqtProperty(float, _get_level, _set_level)

    def set_value(self, percent, text=None):
        percent = min(max(float(percent), 0.0), 100.0)
        self._text = text if text is not None else "%d%%" % round(percent)
        self._anim.stop()
        self._anim.setStartValue(self._level)
        self._anim.setEndValue(percent)
        self._anim.start()

    def _fill(self):
        if self._color:
            return QColor(self._color)
        if self._auto:
            return QColor(level_color(self._level))
        return QColor(C["accent"])


class HBar(_LevelWidget):
    def __init__(self, title="", color=None, auto_color=False):
        super().__init__(title, color, auto_color)
        self.setMinimumHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def sizeHint(self):
        return QSize(200, 40)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        f = QFont(self.font())
        f.setPixelSize(12)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        p.drawText(QRectF(0, 0, w / 2, 18), Qt.AlignLeft | Qt.AlignVCenter, self.title)
        p.setPen(QColor(C["text"]))
        p.drawText(QRectF(w / 2, 0, w / 2, 18), Qt.AlignRight | Qt.AlignVCenter, self._text)

        track = QRectF(0, h - 14, w, 10)
        path = QPainterPath()
        path.addRoundedRect(track, 5, 5)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.setBrush(QColor("#10131a"))
        p.drawPath(path)

        col = self._fill()
        g = QLinearGradient(track.left(), 0, track.right(), 0)
        g.setColorAt(0, col)
        g.setColorAt(1, col.lighter(125))
        p.save()
        p.setClipPath(path)
        p.fillRect(QRectF(track.left(), track.top(), track.width() * self._level / 100.0, track.height()), QBrush(g))
        p.restore()


class RingGauge(_LevelWidget):
    def __init__(self, title="", color=None, auto_color=False):
        super().__init__(title, color, auto_color)
        self.setMinimumSize(110, 130)

    def sizeHint(self):
        return QSize(150, 170)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.setPen(QPen(QColor(C["border"]), 1))
        p.setBrush(QColor(C["card"]))
        p.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), 6, 6)

        size = min(w - 24, h - 40)
        rect = QRectF((w - size) / 2, 10, size, size)
        pen_w = 10.0
        arc = rect.adjusted(pen_w / 2, pen_w / 2, -pen_w / 2, -pen_w / 2)
        p.setPen(QPen(QColor("#10131a"), pen_w, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(arc, 225 * 16, -270 * 16)
        if self._level > 0:
            p.setPen(QPen(self._fill(), pen_w, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(arc, 225 * 16, int(-270 * 16 * self._level / 100.0))

        f = QFont(self.font())
        f.setPixelSize(max(int(size / 5), 12))
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(C["text"]))
        p.drawText(rect, Qt.AlignCenter, self._text)
        f.setPixelSize(11)
        f.setBold(False)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        p.drawText(QRectF(2, h - 26, w - 4, 20), Qt.AlignCenter, self.title)
