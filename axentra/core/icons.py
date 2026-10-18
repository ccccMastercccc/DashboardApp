"""Axentra - icons painted in code (no image files needed)."""
import math

from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QIcon, QPainter, QPen, QPixmap, QPolygonF


def make_icon(kind, normal, hover):
    """kind: 'off' (power symbol) or 'reboot' (circular arrow)."""
    icon = QIcon()
    for color, mode in ((normal, QIcon.Normal), (hover, QIcon.Active)):
        pm = QPixmap(64, 64)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(color), 6, Qt.SolidLine, Qt.RoundCap))
        if kind == "off":
            p.drawArc(QRectF(12, 14, 40, 40), 120 * 16, 300 * 16)
            p.drawLine(QPointF(32, 6), QPointF(32, 30))
        else:
            start, span = 60, 270
            p.drawArc(QRectF(12, 12, 40, 40), start * 16, span * 16)
            a = math.radians(start + span)
            end = QPointF(32 + 20 * math.cos(a), 32 - 20 * math.sin(a))
            d = QPointF(-math.sin(a), -math.cos(a))      # direction of travel
            n = QPointF(-d.y(), d.x())                   # perpendicular
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(color))
            p.drawPolygon(QPolygonF([end + n * 9, end - n * 9, end + d * 12]))
        p.end()
        icon.addPixmap(pm, mode)
    return icon
