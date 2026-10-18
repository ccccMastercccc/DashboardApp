"""Axentra kit - rotary volume control.

    VolumeKnob("Master", value=65, on_change=fn)
    CompactVolumeKnob("Master", value=65, on_change=fn)  # VolumeSlider width
    .value()  .set_value(v)  signal .changed(int)
"""
import math

from PyQt5.QtCore import QPointF, QRectF, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPainter, QPen, QRadialGradient
from PyQt5.QtWidgets import QWidget

from axentra.theme import C


class VolumeKnob(QWidget):
    changed = pyqtSignal(int)

    def __init__(self, title="", minimum=0, maximum=100, value=50, suffix="%",
                 color=None, step=1, on_change=None):
        super().__init__()
        if minimum >= maximum:
            raise ValueError("minimum must be less than maximum")
        if step <= 0:
            raise ValueError("step must be greater than zero")

        self.title = title
        self.suffix = suffix
        self._min = int(minimum)
        self._max = int(maximum)
        self._step = int(step)
        self._value = self._clamp(value)
        self._color = color or C["accent"]
        self._press_y = 0
        self._press_value = self._value
        self.setMinimumSize(64, 110)
        self.setFocusPolicy(Qt.StrongFocus)
        if on_change:
            self.changed.connect(on_change)

    def sizeHint(self):
        return QSize(76, 130)

    def value(self):
        return self._value

    def set_value(self, value):
        value = self._clamp(value)
        if value != self._value:
            self._value = value
            self.update()
            self.changed.emit(value)

    def _clamp(self, value):
        return min(max(int(value), self._min), self._max)

    def _fraction(self):
        return (self._value - self._min) / float(self._max - self._min)

    @staticmethod
    def _point_on_arc(center, radius, fraction):
        angle = math.radians(225 - 270 * fraction)
        return QPointF(center.x() + radius * math.cos(angle),
                       center.y() - radius * math.sin(angle))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setFocus()
            self._press_y = event.y()
            self._press_value = self._value
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            per_pixel = (self._max - self._min) / 160.0
            self.set_value(round(self._press_value + (self._press_y - event.y()) * per_pixel))
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta:
            self.set_value(self._value + (self._step if delta > 0 else -self._step))
            event.accept()
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Up, Qt.Key_Right):
            self.set_value(self._value + self._step)
        elif event.key() in (Qt.Key_Down, Qt.Key_Left):
            self.set_value(self._value - self._step)
        else:
            super().keyPressEvent(event)

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()

        panel = QRectF(0.5, 0.5, width - 1, height - 1)
        painter.setPen(QPen(QColor(C["border"]), 1))
        painter.setBrush(QColor("#191d23"))
        painter.drawRoundedRect(panel, 9, 9)

        value_font = QFont(self.font())
        value_font.setPixelSize(15 if width >= 100 else 13)
        value_font.setBold(True)
        painter.setFont(value_font)
        painter.setPen(QColor(C["text"]))
        painter.drawText(QRectF(6, 3, width - 12, 20), Qt.AlignCenter,
                         "%d%s" % (self._value, self.suffix))

        title_font = QFont(self.font())
        title_font.setPixelSize(11 if width >= 100 else 10)
        painter.setFont(title_font)
        painter.setPen(QColor(C["muted"]))
        painter.drawText(QRectF(6, height - 22, width - 12, 17), Qt.AlignCenter,
                         self.title)

        knob_radius = min((width - 22) / 2, (height - 50) / 2, 54)
        center = QPointF(width / 2, height / 2 + 2)
        gauge_radius = knob_radius + 5
        gauge = QRectF(center.x() - gauge_radius, center.y() - gauge_radius,
                       gauge_radius * 2, gauge_radius * 2)
        fraction = self._fraction()

        painter.setPen(QPen(QColor("#303640"), 2, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(gauge, 225 * 16, -270 * 16)
        if fraction > 0:
            painter.setPen(QPen(QColor(self._color), 2, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(gauge, 225 * 16, int(-270 * 16 * fraction))

        for index in range(11):
            tick_fraction = index / 10
            inner = self._point_on_arc(center, gauge_radius - 3, tick_fraction)
            outer = self._point_on_arc(center, gauge_radius + 1, tick_fraction)
            tick_color = QColor(self._color) if tick_fraction <= fraction else QColor("#59616b")
            painter.setPen(QPen(tick_color, 1))
            painter.drawLine(inner, outer)

        knob = QRectF(center.x() - knob_radius, center.y() - knob_radius,
                      knob_radius * 2, knob_radius * 2)
        painter.setPen(QPen(QColor("#090b0e"), 2))
        painter.setBrush(QColor("#11151a"))
        painter.drawEllipse(knob.adjusted(-3, -3, 3, 3))

        gradient = QRadialGradient(center.x() - knob_radius * 0.3,
                                   center.y() - knob_radius * 0.4,
                                   knob_radius * 1.8)
        gradient.setColorAt(0, QColor("#505965"))
        gradient.setColorAt(0.55, QColor("#343b45"))
        gradient.setColorAt(1, QColor("#1b2027"))
        painter.setPen(QPen(QColor("#69727e"), 1))
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(knob)

        painter.setPen(QPen(QColor("#606a76"), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(knob.adjusted(4, 4, -4, -4))
        painter.setPen(QPen(QColor("#20262e"), 1))
        painter.drawEllipse(knob.adjusted(7, 7, -7, -7))

        angle = math.radians(225 - 270 * fraction)
        marker_start = QPointF(center.x() + knob_radius * 0.12 * math.cos(angle),
                               center.y() - knob_radius * 0.12 * math.sin(angle))
        marker_end = QPointF(center.x() + knob_radius * 0.73 * math.cos(angle),
                             center.y() - knob_radius * 0.73 * math.sin(angle))
        painter.setPen(QPen(QColor("#edf2f8"), max(1.5, knob_radius / 24),
                            Qt.SolidLine, Qt.RoundCap))
        painter.drawLine(marker_start, marker_end)


class CompactVolumeKnob(VolumeKnob):
    """A rotary volume control sized to match VolumeSlider."""

    def __init__(self, title="", minimum=0, maximum=100, value=50, suffix="%",
                 color=None, step=1, on_change=None):
        super().__init__(title, minimum, maximum, value, suffix, color, step, on_change)
        self.setMinimumSize(64, 170)
        self.setMaximumWidth(64)

    def sizeHint(self):
        return QSize(64, 230)
