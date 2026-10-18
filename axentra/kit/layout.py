"""
Axentra kit - layout building blocks.

    Page    the root of every app: a scrollable page with a title
    Card    a titled panel (the same boxes you see on Home)
    Row     widgets side by side          Row(a, b, c)
    Column  widgets stacked               Column(a, b, c)
    Grid    widgets in a grid             Grid(columns=3)
    Spacer  flexible empty space          Row(label, Spacer(), button)
    Divider a thin line
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QScrollArea, QSizePolicy,
                             QVBoxLayout, QWidget)

from axentra.kit.display import MutedLabel, SectionTitle, Title


_H_ALIGN = {"left": Qt.AlignLeft, "center": Qt.AlignHCenter, "right": Qt.AlignRight}
_V_ALIGN = {"top": Qt.AlignTop, "center": Qt.AlignVCenter, "bottom": Qt.AlignBottom}


def align_flags(halign="fill", valign="fill"):
    """'fill' = stretch to the whole cell (no alignment flag)."""
    flags = Qt.Alignment()
    if halign in _H_ALIGN:
        flags |= _H_ALIGN[halign]
    if valign in _V_ALIGN:
        flags |= _V_ALIGN[valign]
    return flags


class Spacer(QWidget):
    """Flexible empty space (size=0) or a fixed gap (size=20 px). Pushes the widgets next to it apart."""
    def __init__(self, size=0):
        super().__init__()
        self.size_px = int(size)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class Divider(QFrame):
    def __init__(self, vertical=False):
        super().__init__()
        self.setObjectName("vsep" if vertical else "hsep")
        if vertical:
            self.setFixedHeight(20)


class Row(QWidget):
    """
    Widgets side by side.
        equal=True     every widget gets the same width
        align_y        what children do with extra HEIGHT: fill | top | center | bottom
        pack=True      children keep their natural width and are pushed to the left
    """
    def __init__(self, *widgets, spacing=12, margins=0, equal=False, align_y="fill", pack=False):
        super().__init__()
        self.lay = QHBoxLayout(self)
        self.lay.setContentsMargins(margins, margins, margins, margins)
        self.lay.setSpacing(spacing)
        self._equal = equal
        self._pack = pack
        self.child_h, self.child_v = "fill", align_y
        if pack:
            self.lay.addStretch(1)
        for w in widgets:
            self.add(w)

    def add(self, widget, stretch=0, align=None):
        flags = align if align is not None else Qt.Alignment()
        stretch = 1 if self._equal else stretch
        if self._pack:
            self.lay.insertWidget(self.lay.count() - 1, widget, stretch, flags)
        else:
            self.lay.addWidget(widget, stretch, flags)
        return widget


class Column(QWidget):
    """
    Widgets stacked top to bottom.
        align_x        what children do with extra WIDTH: fill | left | center | right
        pack=True      children keep their natural height and are pushed to the top
    """
    def __init__(self, *widgets, spacing=10, margins=0, align_x="fill", pack=False):
        super().__init__()
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(margins, margins, margins, margins)
        self.lay.setSpacing(spacing)
        self._pack = pack
        self.child_h, self.child_v = align_x, "fill"
        if pack:
            self.lay.addStretch(1)
        for w in widgets:
            self.add(w)

    def add(self, widget, stretch=0, align=None):
        flags = align if align is not None else Qt.Alignment()
        if self._pack:
            self.lay.insertWidget(self.lay.count() - 1, widget, stretch, flags)
        else:
            self.lay.addWidget(widget, stretch, flags)
        return widget


class Grid(QWidget):
    """
    Widgets in a grid, columns of equal width.
        g = Grid(columns=3)
        g.add(w1); g.add(w2); g.add(w3)          # fills left->right, top->bottom
        g.add(wide, colspan=2)                   # takes two columns
        g.add(big, row=1, col=0, colspan=3)      # or place it explicitly
    """
    def __init__(self, columns=2, spacing=12, margins=0, align_x="fill", align_y="fill"):
        super().__init__()
        self.columns = max(int(columns), 1)
        self.child_h, self.child_v = align_x, align_y
        self._i = 0
        self.lay = QGridLayout(self)
        self.lay.setContentsMargins(margins, margins, margins, margins)
        self.lay.setSpacing(spacing)
        for c in range(self.columns):
            self.lay.setColumnStretch(c, 1)

    def add(self, widget, row=None, col=None, rowspan=1, colspan=1, align=None):
        if row is None or col is None:
            colspan = max(1, min(colspan, self.columns))
            c = self._i % self.columns
            if c + colspan > self.columns:          # does not fit in this row -> next row
                self._i += self.columns - c
            row, col = divmod(self._i, self.columns)
            self._i += colspan
        self.lay.addWidget(widget, row, col, rowspan, colspan, align if align is not None else Qt.Alignment())
        return widget


class Card(QFrame):
    """
    A titled box that holds widgets.
        card = Card("Network")                          # vertical
        card = Card("Controls", layout="h")             # horizontal
        card = Card("Tiles", layout="grid", columns=3)  # grid
        card.add(some_widget)
    """
    def __init__(self, title="", layout="v", spacing=10, columns=2, align_x="fill", align_y="fill", pack=False):
        super().__init__()
        self.setObjectName("card")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 14)
        outer.setSpacing(8)
        if title:
            outer.addWidget(SectionTitle(title))
        if layout == "h":
            self.inner = Row(spacing=spacing, align_y=align_y, pack=pack)
        elif layout == "grid":
            self.inner = Grid(columns=columns, spacing=spacing, align_x=align_x, align_y=align_y)
        else:
            self.inner = Column(spacing=spacing, align_x=align_x, pack=pack)
        self.body = self.inner.lay
        outer.addWidget(self.inner, 1)

    def add(self, widget, *args, **kwargs):
        return self.inner.add(widget, *args, **kwargs)


def put(container, widget, stretch=0, halign="auto", valign="auto",
        fixed_w=0, fixed_h=0, min_w=0, min_h=0, colspan=1):
    """
    Add `widget` to a Row / Column / Grid / Card with layout options (used by generated Ui code).
        stretch   share of the free space (0 = natural size)
        halign    auto | fill | left | center | right      valign   auto | fill | top | center | bottom
                  ("auto" = follow the container's own "children align" setting)
        fixed_w / fixed_h / min_w / min_h   pixels (0 = automatic)
        colspan   columns taken inside a Grid
    """
    target = container.inner if isinstance(container, Card) else container
    if isinstance(widget, Spacer) and widget.size_px > 0:
        n = widget.size_px
        if isinstance(target, Row):
            widget.setFixedWidth(n)
            widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        elif isinstance(target, Column):
            widget.setFixedHeight(n)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        else:
            widget.setFixedSize(n, n)
    if fixed_w:
        widget.setFixedWidth(fixed_w)
    if fixed_h:
        widget.setFixedHeight(fixed_h)
    if min_w:
        widget.setMinimumWidth(min_w)
    if min_h:
        widget.setMinimumHeight(min_h)
    if halign == "auto":
        halign = getattr(target, "child_h", "fill")
    if valign == "auto":
        valign = getattr(target, "child_v", "fill")
    align = align_flags(halign, valign)
    if isinstance(target, Grid):
        target.add(widget, colspan=colspan, align=align)
    else:
        target.add(widget, stretch, align)
    return widget


class Page(QScrollArea):
    """
    Base of every app. Scrolls automatically when the content is taller than the screen.

        class App(Page):
            def __init__(self):
                super().__init__("My Tool", "what it does")
                self.add(Card("Hello"))
    """
    def __init__(self, title="", subtitle="", margins=24, spacing=14):
        super().__init__()
        self.setObjectName("page")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        body = QWidget()
        body.setObjectName("pageBody")
        self.setWidget(body)
        self.content = QVBoxLayout(body)
        self.content.setContentsMargins(margins, margins - 4, margins, margins)
        self.content.setSpacing(spacing)
        if title:
            self.content.addWidget(Title(title))
        if subtitle:
            sub = MutedLabel(subtitle)
            sub.setObjectName("pageSubtitle")
            self.content.addWidget(sub)
        self.content.addStretch(1)      # keeps everything packed at the top

    def add(self, widget, stretch=0):
        """Add a widget at the bottom of the page. stretch>0 makes it fill the free height."""
        self.content.insertWidget(self.content.count() - 1, widget, stretch)
        if stretch > 0:
            self.content.setStretch(self.content.count() - 1, 0)   # no spacer when something fills
        return widget

    def add_row(self, *widgets, equal=True):
        return self.add(Row(*widgets, equal=equal))
