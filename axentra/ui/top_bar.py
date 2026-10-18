"""Axentra - top bar: title, network status, clock, restart / shut down buttons."""
import socket

from PyQt5.QtCore import QDateTime, QSize, Qt, QTimer, pyqtSignal
from PyQt5.QtNetwork import QNetworkInterface
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from axentra import config
from axentra.core.icons import make_icon
from axentra.theme import C


class TopBar(QFrame):
    power_requested = pyqtSignal(str)  # "poweroff" | "reboot"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(44)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 12, 0)
        lay.setSpacing(14)

        title = QLabel(config.APP_NAME.upper())
        title.setObjectName("appTitle")
        host = QLabel(socket.gethostname())
        host.setObjectName("hostname")
        lay.addWidget(title)
        lay.addWidget(host)
        lay.addStretch(1)

        self.net_dot = QLabel()
        self.net_dot.setFixedSize(10, 10)
        self.net_text = QLabel("...")
        lay.addWidget(self.net_dot)
        lay.addWidget(self.net_text)
        lay.addWidget(self._vsep())

        self.clock = QLabel()
        self.clock.setObjectName("clock")
        lay.addWidget(self.clock)
        lay.addWidget(self._vsep())

        self.btn_reboot = self._power_button("Restart", "reboot", C["warn"])
        self.btn_off = self._power_button("Shut down", "off", C["bad"])
        self.btn_reboot.clicked.connect(lambda: self.power_requested.emit("reboot"))
        self.btn_off.clicked.connect(lambda: self.power_requested.emit("poweroff"))
        lay.addWidget(self.btn_reboot)
        lay.addWidget(self.btn_off)

        QTimer(self, timeout=self.update_clock).start(1000)
        QTimer(self, timeout=self.update_network).start(3000)
        self.update_clock()
        self.update_network()

    @staticmethod
    def _vsep():
        s = QFrame()
        s.setObjectName("vsep")
        s.setFixedHeight(20)
        return s

    @staticmethod
    def _power_button(text, kind, hover_color):
        b = QPushButton(text)
        b.setObjectName("powerBtn")
        b.setProperty("kind", kind)
        b.setIcon(make_icon(kind, C["text"], hover_color))
        b.setIconSize(QSize(16, 16))
        b.setCursor(Qt.PointingHandCursor)
        return b

    def update_clock(self):
        self.clock.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd   HH:mm:ss"))

    def update_network(self):
        found = None
        for itf in QNetworkInterface.allInterfaces():
            fl = itf.flags()
            if not (fl & QNetworkInterface.IsUp and fl & QNetworkInterface.IsRunning):
                continue
            if fl & QNetworkInterface.IsLoopBack:
                continue
            for entry in itf.addressEntries():
                ip = entry.ip()
                if ip.protocol() == 0:  # IPv4
                    found = (itf.name(), ip.toString())
                    break
            if found:
                break
        if found:
            self.net_dot.setStyleSheet("background:%s; border-radius:5px;" % C["ok"])
            self.net_text.setText("%s  %s" % found)
        else:
            self.net_dot.setStyleSheet("background:%s; border-radius:5px;" % C["bad"])
            self.net_text.setText("Disconnected")
