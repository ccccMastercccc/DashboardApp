"""
Axentra kit - text and status display.

    Title("..")            big page title
    SectionTitle("..")     small uppercase caption (like "DISK" on Home)
    Label("..")            normal text   (color=, size=, bold=, muted=, wrap=)
    MutedLabel("..")       gray text
    BigValue("42")         large number     .set("43", color)
    Badge("ONLINE","ok")   colored pill      kinds: ok warn bad info muted     .set(text, kind)
    StatusDot("ok")        small colored dot .set_state("bad")
    StatCard("CPU","--")   card with a big value   .set_value("42%", color)  .set_sub("..")
"""
from PyQt5.QtCore import QRectF, QSize, Qt
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from axentra.kit._util import kind_color, repolish
from axentra.theme import C


class Title(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.setObjectName("pageTitle")


class SectionTitle(QLabel):
    def __init__(self, text=""):
        super().__init__(text.upper())
        self.setObjectName("cardTitle")


class Label(QLabel):
    def __init__(self, text="", color=None, size=None, bold=False, muted=False, wrap=False):
        super().__init__(text)
        css = []
        if muted:
            color = color or C["muted"]
        if color:
            css.append("color:%s;" % color)
        if size:
            css.append("font-size:%dpx;" % size)
        if bold:
            css.append("font-weight:600;")
        if css:
            self.setStyleSheet("".join(css))
        self.setWordWrap(wrap)


class MutedLabel(Label):
    def __init__(self, text="", **kw):
        super().__init__(text, muted=True, **kw)


class BigValue(QLabel):
    def __init__(self, text="--", color=None, size=40):
        super().__init__(text)
        self.setObjectName("bigNum")
        self._size = size
        self.set(text, color)

    def set(self, text, color=None):
        self.setText(str(text))
        self.setStyleSheet("font-size:%dpx;%s" % (self._size, ("color:%s;" % color) if color else ""))


class Badge(QLabel):
    def __init__(self, text="", kind="info"):
        super().__init__(text)
        self.setObjectName("badge")
        self.setAlignment(Qt.AlignCenter)
        self.setProperty("kind", kind)

    def set(self, text, kind=None):
        self.setText(text)
        if kind:
            self.setProperty("kind", kind)
            repolish(self)


class StatusDot(QWidget):
    def __init__(self, state="muted", size=12):
        super().__init__()
        self._size = size
        self._state = state
        self.setFixedSize(size, size)

    def set_state(self, state):
        self._state = state
        self.update()

    def sizeHint(self):
        return QSize(self._size, self._size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(kind_color(self._state))
        glow = QColor(c)
        glow.setAlpha(60)
        p.setPen(Qt.NoPen)
        p.setBrush(glow)
        p.drawEllipse(QRectF(0, 0, self._size, self._size))
        p.setBrush(c)
        m = self._size * 0.22
        p.drawEllipse(QRectF(m, m, self._size - 2 * m, self._size - 2 * m))


class StatCard(QFrame):
    def __init__(self, title="", value="--", sub="", color=None, width=None):
        super().__init__()
        self.setObjectName("card")
        if width:
            self.setFixedWidth(width)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.addWidget(SectionTitle(title))
        self._value = BigValue(value, color)
        self._sub = QLabel(sub)
        self._sub.setObjectName("cardSub")
        lay.addWidget(self._value)
        lay.addWidget(self._sub)
        lay.addStretch(1)

    def set_value(self, text, color=None):
        self._value.set(text, color)

    def set_sub(self, text):
        self._sub.setText(text)
