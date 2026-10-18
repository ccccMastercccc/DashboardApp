"""
Axentra kit - pages for apps built with Axentra Designer.

    DesignPage   responsive page (layouts that adapt to any screen)  <- used by the Designer
    CanvasPage   old fixed-size page with absolute positions (kept so older apps still work)

Fixed-size canvas details:

    class App(CanvasPage):
        def __init__(self):
            super().__init__(Ui.WIDTH, Ui.HEIGHT)
            self.ui = Ui(self.canvas)

CanvasPage keeps the design at its exact size: centered when the screen is bigger,
scrollable when the screen is smaller.
`place(widget, parent, x, y, w, h)` puts one widget at an exact position (the generated Ui code uses it).
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget


def place(widget, parent, x, y, w, h):
    widget.setParent(parent)
    widget.setMinimumSize(0, 0)
    widget.setMaximumSize(16777215, 16777215)
    widget.setGeometry(x, y, w, h)
    widget.show()
    return widget


class CanvasPage(QScrollArea):
    def __init__(self, width=800, height=500):
        super().__init__()
        self.setObjectName("page")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        body = QWidget()
        body.setObjectName("pageBody")
        self.setWidget(body)
        lay = QVBoxLayout(body)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.canvas = QWidget()
        self.canvas.setFixedSize(width, height)
        lay.addWidget(self.canvas, 0, Qt.AlignHCenter | Qt.AlignTop)
        lay.addStretch(1)


class DesignPage(QScrollArea):
    """
    Responsive page for apps built with Axentra Designer.
    The layouts fill whatever screen size is available and the page scrolls only when the
    content really does not fit.

        class App(DesignPage):
            def __init__(self):
                super().__init__()
                self.ui = Ui(self.body)
    """
    def __init__(self):
        super().__init__()
        self.setObjectName("page")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.body = QWidget()
        self.body.setObjectName("pageBody")
        self.setWidget(self.body)


def mount(parent, widget):
    """Make `widget` fill `parent` completely (used by generated Ui code)."""
    lay = QVBoxLayout(parent)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(widget)
    return widget
