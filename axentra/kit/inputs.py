"""
Axentra kit - input widgets (thin, friendlier versions of the Qt ones).

    LineEdit(text="", placeholder="", on_change=fn, on_enter=fn)     .text()  .setText()
    PasswordEdit(placeholder="")                                     same as LineEdit, hides the text
    TextArea(text="", placeholder="", read_only=False)               .toPlainText()  .setPlainText()
    ComboBox(["a","b","c"], current=0, on_change=fn)                 fn(text)   .currentText()  .currentIndex()
    SpinBox(0, 100, value=10, suffix=" s", on_change=fn)             fn(int)    .value()
    DoubleSpinBox(0, 1, value=0.5, decimals=2, step=0.1)             fn(float)  .value()
    CheckBox("Enable logging", checked=True, on_toggle=fn)           fn(bool)   .isChecked()
    RadioGroup(["Low","High"], current=0, on_change=fn)              fn(index)  .index()  .text()
    Form(label_width=120)  ->  form.add("Host", LineEdit())          label + input rows
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox, QGridLayout, QLabel,
                             QLineEdit, QPlainTextEdit, QRadioButton, QSpinBox, QVBoxLayout, QHBoxLayout,
                             QWidget)


class LineEdit(QLineEdit):
    def __init__(self, text="", placeholder="", on_change=None, on_enter=None):
        super().__init__(text)
        self.setPlaceholderText(placeholder)
        if on_change:
            self.textChanged.connect(on_change)
        if on_enter:
            self.returnPressed.connect(lambda: on_enter(self.text()))


class PasswordEdit(LineEdit):
    def __init__(self, text="", placeholder="", on_change=None, on_enter=None):
        super().__init__(text, placeholder, on_change, on_enter)
        self.setEchoMode(QLineEdit.Password)


class TextArea(QPlainTextEdit):
    def __init__(self, text="", placeholder="", read_only=False):
        super().__init__(text)
        self.setPlaceholderText(placeholder)
        self.setReadOnly(read_only)


class ComboBox(QComboBox):
    def __init__(self, items=(), current=0, on_change=None):
        super().__init__()
        self.addItems([str(i) for i in items])
        if items:
            self.setCurrentIndex(current)
        if on_change:
            self.currentTextChanged.connect(on_change)
        self.setCursor(Qt.PointingHandCursor)


class SpinBox(QSpinBox):
    def __init__(self, minimum=0, maximum=100, value=0, suffix="", on_change=None):
        super().__init__()
        self.setRange(minimum, maximum)
        self.setValue(value)
        self.setSuffix(suffix)
        if on_change:
            self.valueChanged.connect(on_change)


class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, minimum=0.0, maximum=100.0, value=0.0, decimals=2, step=0.1, suffix="", on_change=None):
        super().__init__()
        self.setRange(minimum, maximum)
        self.setDecimals(decimals)
        self.setSingleStep(step)
        self.setValue(value)
        self.setSuffix(suffix)
        if on_change:
            self.valueChanged.connect(on_change)


class CheckBox(QCheckBox):
    def __init__(self, text="", checked=False, on_toggle=None):
        super().__init__(text)
        self.setChecked(checked)
        self.setCursor(Qt.PointingHandCursor)
        if on_toggle:
            self.toggled.connect(on_toggle)


class RadioGroup(QWidget):
    changed = pyqtSignal(int)

    def __init__(self, options, current=0, vertical=True, on_change=None):
        super().__init__()
        lay = QVBoxLayout(self) if vertical else QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self._group = QButtonGroup(self)
        self._buttons = []
        for i, text in enumerate(options):
            b = QRadioButton(text)
            b.setCursor(Qt.PointingHandCursor)
            self._group.addButton(b, i)
            lay.addWidget(b)
            self._buttons.append(b)
        self._group.buttonClicked[int].connect(self.changed.emit)
        if self._buttons:
            self._buttons[min(max(current, 0), len(self._buttons) - 1)].setChecked(True)
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


class Form(QWidget):
    """Label + input rows, aligned in two columns."""
    def __init__(self, label_width=120, spacing=10):
        super().__init__()
        self._row = 0
        self._label_width = label_width
        self.lay = QGridLayout(self)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setHorizontalSpacing(14)
        self.lay.setVerticalSpacing(spacing)
        self.lay.setColumnStretch(1, 1)

    def add(self, label, widget):
        lab = QLabel(label)
        lab.setObjectName("cardSub")
        lab.setFixedWidth(self._label_width)
        self.lay.addWidget(lab, self._row, 0, Qt.AlignVCenter)
        self.lay.addWidget(widget, self._row, 1)
        self._row += 1
        return widget
