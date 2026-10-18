"""
Axentra kit - animated on/off switch.

    sw = Switch(checked=False, on_toggle=fn)     fn(bool)
    sw.isChecked()   sw.setChecked(True)   signal: sw.toggled(bool)
"""
from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRectF, QSize, Qt, pyqtProperty
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QAbstractButton

from axentra.kit._util import mix
from axentra.theme import C


class Switch(QAbstractButton):
    def __init__(self, checked=False, on_toggle=None):
        super().__init__()
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        self._pos = 1.0 if checked else 0.0
        self._anim = QPropertyAnimation(self, b"knob", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.toggled.connect(self._animate)
        if on_toggle:
            self.toggled.connect(on_toggle)

    def sizeHint(self):
        return QSize(46, 26)

    def _get_knob(self):
        return self._pos

    def _set_knob(self, v):
        self._pos = float(v)
        self.update()

    knob = pyqtProperty(float, _get_knob, _set_knob)

    def _animate(self, checked):
        self._anim.stop()
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(1.0 if checked else 0.0)
        self._anim.start()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        track = mix(C["border"], C["accent"], self._pos)
        if not self.isEnabled():
            track = QColor(C["grid"])
        p.setPen(Qt.NoPen)
        p.setBrush(track)
        p.drawRoundedRect(QRectF(0, 0, w, h), h / 2, h / 2)
        d = h - 6
        x = 3 + (w - d - 6) * self._pos
        p.setBrush(QColor("#ffffff"))
        p.drawEllipse(QRectF(x, 3, d, d))
