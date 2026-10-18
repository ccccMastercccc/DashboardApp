"""
Axentra kit - buttons.

    Button("Save", kind="primary", on_click=self.save)
        kinds: default  primary  success  danger  ghost
    ToggleButton("Mute", checked=False, on_toggle=fn)      fn(bool)
    SegmentedControl(["1h", "6h", "24h"], current=0, on_change=fn)   fn(index)
        .index()  .text()  .set_index(i)
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

from axentra.kit._util import repolish


class Button(QPushButton):
    def __init__(self, text="", kind="default", on_click=None):
        super().__init__(text)
        self.setProperty("kind", kind)
        self.setCursor(Qt.PointingHandCursor)
        if on_click:
            self.clicked.connect(lambda _=False: on_click())

    def set_kind(self, kind):
        self.setProperty("kind", kind)
        repolish(self)


class ToggleButton(QPushButton):
    """A button that stays pressed. Use .isChecked() / .setChecked()."""
    def __init__(self, text="", checked=False, on_toggle=None):
        super().__init__(text)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        if on_toggle:
            self.toggled.connect(on_toggle)


class SegmentedControl(QWidget):
    changed = pyqtSignal(int)

    def __init__(self, options, current=0, on_change=None):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons = []
        n = len(options)
        for i, text in enumerate(options):
            b = QPushButton(text)
            b.setObjectName("segBtn")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setProperty("pos", "only" if n == 1 else "first" if i == 0 else "last" if i == n - 1 else "mid")
            self._group.addButton(b, i)
            lay.addWidget(b)
            self._buttons.append(b)
        self._group.buttonClicked[int].connect(self.changed.emit)
        if self._buttons:
            self._buttons[min(max(current, 0), n - 1)].setChecked(True)
        if on_change:
            self.changed.connect(on_change)

    def index(self):
        return self._group.checkedId()

    def text(self):
        b = self._group.checkedButton()
        return b.text() if b else ""

    def set_index(self, i):
        if 0 <= i < len(self._buttons):
            self._buttons[i].setChecked(True)
            self.changed.emit(i)
