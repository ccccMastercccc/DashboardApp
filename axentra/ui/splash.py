"""Axentra - logo splash screen: fade in, hold, fade out, then emits `finished`."""
from PyQt5.QtCore import (QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, Qt,
                          pyqtProperty, pyqtSignal)
from PyQt5.QtGui import QColor, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget


class SplashScreen(QWidget):
    finished = pyqtSignal()
    BG = QColor("#000208")      # same near-black as the logo image edges

    def __init__(self, logo_path, hold_ms=3000, fade_ms=700):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setCursor(Qt.BlankCursor)
        self._pix = QPixmap(str(logo_path))
        self._scaled = QPixmap()
        self._opacity = 0.0

        fade_in = QPropertyAnimation(self, b"logoOpacity", self)
        fade_in.setDuration(fade_ms)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)
        fade_out = QPropertyAnimation(self, b"logoOpacity", self)
        fade_out.setDuration(fade_ms)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)

        self._group = QSequentialAnimationGroup(self)
        self._group.addAnimation(fade_in)
        self._group.addPause(hold_ms)
        self._group.addAnimation(fade_out)
        self._group.finished.connect(self.finished)

    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, v):
        self._opacity = float(v)
        self.update()

    logoOpacity = pyqtProperty(float, _get_opacity, _set_opacity)

    def start(self):
        screen = QApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.geometry())
        self.showFullScreen()
        self._group.start()

    def resizeEvent(self, _):
        if not self._pix.isNull():
            self._scaled = self._pix.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), self.BG)
        if self._scaled.isNull():
            return
        p.setOpacity(self._opacity)
        x = (self.width() - self._scaled.width()) // 2
        y = (self.height() - self._scaled.height()) // 2
        p.drawPixmap(x, y, self._scaled)
