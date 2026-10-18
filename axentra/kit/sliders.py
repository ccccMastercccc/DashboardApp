"""
Axentra kit - sliders and knob.

    Slider(0, 100, value=30, suffix="%", title="Brightness", on_change=fn)   horizontal
    VolumeSlider("Master", 0, 100, value=60, on_change=fn)                   vertical (mixer style)
    Knob("Gain", 0, 100, value=40, suffix="dB", on_change=fn)                rotary dial (drag up/down or use the wheel)

All three: .value()   .set_value(v)   signal .changed(int)   on_change callback receives the int.
"""
import math

from PyQt5.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSlider, QWidget

from axentra.theme import C


class Slider(QWidget):
    changed = pyqtSignal(int)

    def __init__(self, minimum=0, maximum=100, value=0, suffix="", title="", on_change=None):
        super().__init__()
        self.suffix = suffix
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)
        if title:
            t = QLabel(title)
            t.setObjectName("cardSub")
            lay.addWidget(t)
        self._s = QSlider(Qt.Horizontal)
        self._s.setRange(minimum, maximum)
        self._s.setValue(value)
        self._lbl = QLabel()
        self._lbl.setMinimumWidth(52)
        self._lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(self._s, 1)
        lay.addWidget(self._lbl)
        self._s.valueChanged.connect(self._on_value)
        self._lbl.setText("%d%s" % (value, suffix))
        if on_change:
            self.changed.connect(on_change)

    def _on_value(self, v):
        self._lbl.setText("%d%s" % (v, self.suffix))
        self.changed.emit(v)

    def value(self):
        return self._s.value()

    def set_value(self, v):
        self._s.setValue(int(v))


class _ValueWidget(QWidget):
    """Shared logic of VolumeSlider and Knob: an integer value with min / max."""
    changed = pyqtSignal(int)

    def __init__(self, title, minimum, maximum, value, suffix, color, on_change):
        super().__init__()
        self.title, self.suffix = title, suffix
        self._min, self._max = minimum, maximum
        self._v = min(max(value, minimum), maximum)
        self._color = color
        self.setFocusPolicy(Qt.StrongFocus)
        if on_change:
            self.changed.connect(on_change)

    def value(self):
        return self._v

    def set_value(self, v):
        v = int(min(max(v, self._min), self._max))
        if v != self._v:
            self._v = v
            self.update()
            self.changed.emit(v)

    def _frac(self):
        return (self._v - self._min) / float(max(self._max - self._min, 1))

    def _qcolor(self):
        return QColor(self._color or C["accent"])

    def _paint_card(self, p):
        p.setPen(QPen(QColor(C["border"]), 1))
        p.setBrush(QColor(C["card"]))
        p.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, self.height() - 1), 6, 6)

    def wheelEvent(self, e):
        step = max((self._max - self._min) // 100, 1)
        self.set_value(self._v + (step if e.angleDelta().y() > 0 else -step))


class VolumeSlider(_ValueWidget):
    def __init__(self, title="", minimum=0, maximum=100, value=50, suffix="%", color=None, on_change=None):
        super().__init__(title, minimum, maximum, value, suffix, color, on_change)
        self.setMinimumSize(64, 170)

    def sizeHint(self):
        return QSize(76, 230)

    def _track(self):
        return QRectF(self.width() / 2 - 9, 40, 18, self.height() - 40 - 32)

    def _set_from_y(self, y):
        tr = self._track()
        frac = 1.0 - (y - tr.top()) / max(tr.height(), 1.0)
        frac = min(max(frac, 0.0), 1.0)
        self.set_value(round(self._min + frac * (self._max - self._min)))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.setFocus()
            self._set_from_y(e.y())

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self._set_from_y(e.y())

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Up, Qt.Key_Right):
            self.set_value(self._v + 1)
        elif e.key() in (Qt.Key_Down, Qt.Key_Left):
            self.set_value(self._v - 1)
        else:
            super().keyPressEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        self._paint_card(p)

        f = QFont(self.font())
        f.setPixelSize(15)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(C["text"]))
        p.drawText(QRectF(0, 8, w, 24), Qt.AlignCenter, "%d%s" % (self._v, self.suffix))
        f.setPixelSize(11)
        f.setBold(False)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        p.drawText(QRectF(2, h - 26, w - 4, 20), Qt.AlignCenter, self.title)

        tr = self._track()
        path = QPainterPath()
        path.addRoundedRect(tr, 9, 9)
        p.setPen(QPen(QColor(C["border"]), 1))
        p.setBrush(QColor("#10131a"))
        p.drawPath(path)

        fy = tr.bottom() - tr.height() * self._frac()
        col = self._qcolor()
        g = QLinearGradient(0, tr.top(), 0, tr.bottom())
        g.setColorAt(0, col.lighter(130))
        g.setColorAt(1, col)
        p.save()
        p.setClipPath(path)
        p.fillRect(QRectF(tr.left(), fy, tr.width(), tr.bottom() - fy), QBrush(g))
        p.restore()

        p.setPen(QPen(QColor(C["muted"]), 1))
        for i in range(5):
            y = tr.top() + tr.height() * i / 4
            p.drawLine(QPointF(tr.left() - 10, y), QPointF(tr.left() - 5, y))
            p.drawLine(QPointF(tr.right() + 5, y), QPointF(tr.right() + 10, y))

        hr = QRectF(tr.center().x() - 17, fy - 7, 34, 14)
        p.setPen(QPen(col, 2))
        p.setBrush(QColor("#e8eefc"))
        p.drawRoundedRect(hr, 5, 5)


class Knob(_ValueWidget):
    def __init__(self, title="", minimum=0, maximum=100, value=0, suffix="", color=None, on_change=None):
        super().__init__(title, minimum, maximum, value, suffix, color, on_change)
        self.setMinimumSize(96, 112)
        self._press_y = 0
        self._press_v = 0

    def sizeHint(self):
        return QSize(120, 136)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.setFocus()
            self._press_y = e.y()
            self._press_v = self._v

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            per_pixel = (self._max - self._min) / 160.0       # 160 px of dragging = full range
            self.set_value(round(self._press_v + (self._press_y - e.y()) * per_pixel))

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Up, Qt.Key_Right):
            self.set_value(self._v + 1)
        elif e.key() in (Qt.Key_Down, Qt.Key_Left):
            self.set_value(self._v - 1)
        else:
            super().keyPressEvent(e)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        self._paint_card(p)

        size = min(w - 16, h - 36)
        rect = QRectF((w - size) / 2, 8, size, size)
        pen_w = 8.0
        arc = rect.adjusted(pen_w / 2, pen_w / 2, -pen_w / 2, -pen_w / 2)

        p.setPen(QPen(QColor("#10131a"), pen_w, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(arc, 225 * 16, -270 * 16)
        col = self._qcolor()
        frac = self._frac()
        if frac > 0:
            p.setPen(QPen(col, pen_w, Qt.SolidLine, Qt.RoundCap))
            p.drawArc(arc, 225 * 16, int(-270 * 16 * frac))

        a = math.radians(225 - 270 * frac)
        r = arc.width() / 2
        dot = QPointF(rect.center().x() + r * math.cos(a), rect.center().y() - r * math.sin(a))
        p.setPen(QPen(col, 2))
        p.setBrush(QColor("#e8eefc"))
        p.drawEllipse(dot, 4.5, 4.5)

        f = QFont(self.font())
        f.setPixelSize(15)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor(C["text"]))
        p.drawText(rect, Qt.AlignCenter, "%d%s" % (self._v, self.suffix))
        f.setPixelSize(11)
        f.setBold(False)
        p.setFont(f)
        p.setPen(QColor(C["muted"]))
        p.drawText(QRectF(2, h - 24, w - 4, 20), Qt.AlignCenter, self.title)
