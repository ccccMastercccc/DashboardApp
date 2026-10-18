"""Axentra - Home page: assembles the widgets and feeds them live data."""
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QWidget

from axentra import config
from axentra.core.system_stats import SystemStats
from axentra.core.utils import human_bytes
from axentra.theme import C
from axentra.ui.widgets.bars import VBar
from axentra.ui.widgets.charts import LineChart
from axentra.ui.widgets.info_cards import DiskCard, TempCard, UsersCard


class HomePage(QWidget):
    RIGHT_COL = 250

    def __init__(self):
        super().__init__()
        self.stats = SystemStats()

        # line charts (2 x 2, top / middle)
        self.ch_cpu = LineChart("CPU", C["c_cpu"], "%", 0, 100)
        self.ch_ram = LineChart("RAM", C["c_ram"], "%", 0, 100)
        self.ch_net = LineChart("NETWORK", C["c_net"], " Mb/s", 0, None, 1)
        self.ch_temp = LineChart("CPU TEMPERATURE", C["c_temp"], " °C", 20, 100)
        charts = QWidget()
        cg = QGridLayout(charts)
        cg.setContentsMargins(0, 0, 0, 0)
        cg.setSpacing(12)
        cg.addWidget(self.ch_cpu, 0, 0)
        cg.addWidget(self.ch_ram, 0, 1)
        cg.addWidget(self.ch_net, 1, 0)
        cg.addWidget(self.ch_temp, 1, 1)

        # vertical bars (top right)
        self.bar_cpu = VBar("CPU")
        self.bar_net = VBar("NETWORK", fixed_color=C["accent"])
        bars = QWidget()
        bars.setFixedWidth(self.RIGHT_COL)
        bl = QHBoxLayout(bars)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(12)
        bl.addWidget(self.bar_cpu)
        bl.addWidget(self.bar_net)

        # cards (bottom row)
        self.card_users = UsersCard()
        self.card_disk = DiskCard()
        self.card_temp = TempCard(width=self.RIGHT_COL)
        bottom = QHBoxLayout()
        bottom.setSpacing(12)
        bottom.addWidget(self.card_users, 1)
        bottom.addWidget(self.card_disk, 1)

        grid = QGridLayout(self)
        grid.setContentsMargins(16, 16, 16, 16)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.addWidget(charts, 0, 0)
        grid.addWidget(bars, 0, 1)
        grid.addLayout(bottom, 1, 0)
        grid.addWidget(self.card_temp, 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setRowStretch(0, 3)
        grid.setRowStretch(1, 1)
        grid.setRowMinimumHeight(1, 150)

        self.timer = QTimer(self, timeout=self.refresh)
        self.timer.start(config.STATS_MS)
        self.refresh()

    def refresh(self):
        s = self.stats.sample()

        self.ch_cpu.push(s["cpu"])
        self.ch_ram.push(s["ram"], "%s / %s" % (human_bytes(s["ram_used"]), human_bytes(s["ram_total"])))
        self.ch_net.push(s["net"])
        self.ch_temp.push(s["temp"])

        self.bar_cpu.set_value(s["cpu"], "%.0f%%" % s["cpu"])
        full = config.NET_BAR_FULL_MBPS or max(s["net_peak"], 1.0)
        self.bar_net.set_value(s["net"] / full * 100, "%.1f Mb/s" % s["net"])

        self.card_temp.update_stats(s)
        self.card_disk.update_stats(s)
        self.card_users.update_stats(s)
