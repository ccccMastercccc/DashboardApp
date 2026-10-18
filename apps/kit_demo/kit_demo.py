"""
Axentra UI kit demo - every ready-made widget, with live data.
Open it, find the widget you need, copy the few lines into your own app.
You can delete this whole folder when you no longer need it.
"""
import math
import random

from axentra.kit import *


class App(Page):
    def __init__(self):
        super().__init__("UI Kit Demo", "Every ready-made widget of the Axentra kit, with live demo data.")
        self.t = 0

        # ---- 1. stat cards ----------------------------------------------------------
        self.card_a = StatCard("SIGNAL", "--", "demo data")
        self.card_b = StatCard("TEMPERATURE", "--", "demo data")
        self.card_c = StatCard("STATUS", "OK", "everything fine", color=COLORS["ok"])
        self.add_row(self.card_a, self.card_b, self.card_c)

        # ---- 2. charts ----------------------------------------------------------------
        self.line = LineChart("LIVE SIGNAL", COLORS["c_cpu"], "%", 0, 100, history=60, interval_ms=500)
        self.bars = BarChart("REQUESTS PER DAY", unit="")
        self.bars.set_data(["Mon", "Tue", "Wed", "Thu", "Fri"], [12, 30, 22, 41, 18])
        self.add_row(self.line, self.bars)
        self.donut = DonutChart("STORAGE")
        self.donut.set_data([("Used", 62), ("Cache", 14), ("Free", 24)])
        self.add(self.donut)

        # ---- 3. bars and gauges -----------------------------------------------------
        self.hbar = HBar("Disk /", auto_color=True)
        self.ring = RingGauge("Memory", auto_color=True)
        self.vbar = VBar("LOAD")
        card = Card("BARS AND GAUGES", layout="h")
        self.fixed_bar = HBar("Fixed color", color=COLORS["c_ram"])
        self.fixed_bar.set_value(45)
        card.add(Column(self.hbar, self.fixed_bar, Spacer()))
        card.add(self.ring)
        card.add(self.vbar)
        self.add(card)

        # ---- 4. controls ----------------------------------------------------------------
        self.mode = SegmentedControl(["Eco", "Normal", "Turbo"], current=1,
                                     on_change=lambda i: toast(self, "Mode: %d" % i, "info"))
        self.switch = Switch(on_toggle=lambda on: toast(self, "Switch is %s" % ("ON" if on else "OFF"),
                                                        "ok" if on else "warn"))
        self.slider = Slider(0, 100, 30, suffix="%", title="Brightness")
        self.knob = Knob("Gain", 0, 100, 40, suffix="dB")
        mixer = Row(VolumeSlider("Master", value=70), VolumeSlider("Music", value=45, color=COLORS["c_ram"]),
                    VolumeSlider("Alerts", value=20, color=COLORS["warn"]), self.knob, spacing=10)
        buttons = Row(Button("Default"), Button("Primary", "primary"), Button("Success", "success"),
                      Button("Danger", "danger"), Button("Ghost", "ghost"), ToggleButton("Toggle"), Spacer())
        status = Row(StatusDot("ok"), Label("online"), StatusDot("warn"), Label("slow"), StatusDot("bad"),
                     Label("offline"), Badge("OK", "ok"), Badge("WARN", "warn"), Badge("ERROR", "bad"),
                     Badge("INFO", "info"), Spacer(), Label("Switch:"), self.switch)
        card = Card("CONTROLS")
        card.add(buttons)
        card.add(status)
        card.add(self.mode)
        card.add(self.slider)
        card.add(mixer)
        self.add(card)

        # ---- 5. inputs ---------------------------------------------------------------
        form = Form()
        form.add("Host", LineEdit("localhost", "server name"))
        form.add("Password", PasswordEdit(placeholder="secret"))
        form.add("Protocol", ComboBox(["http", "https", "ssh"]))
        form.add("Timeout", SpinBox(1, 120, 30, suffix=" s"))
        form.add("Options", CheckBox("Verbose logging", checked=True))
        form.add("Quality", RadioGroup(["Low", "High"], vertical=False))
        card = Card("INPUTS")
        card.add(form)
        self.add(card)

        # ---- 6. table, log, dialogs, background commands -------------------------------------
        table = DataTable(["Service", "Status", "CPU"])
        table.set_rows([["nginx", "running", "3%"], ["ssh", "running", "0%"], ["backup", "stopped", "-"]])
        table.setMinimumHeight(140)
        self.log = LogView()
        self.log.setMinimumHeight(140)
        self.log.log("Kit demo started", "ok")
        actions = Row(
            Button("Log a warning", on_click=lambda: self.log.log("Something looks odd", "warn")),
            Button("Ask me", on_click=self.ask),
            Button("Run `uname -a`", "primary", on_click=self.run_cmd),
            Spacer())
        card = Card("DATA, LOG AND ACTIONS")
        card.add(table)
        card.add(actions)
        card.add(self.log)
        self.add(card)

        # ---- 7. image and video ------------------------------------------------------
        self.add_row(ImageViewer(), VideoPlayer())

        self.timer = every(self, 500, self.tick)

    def tick(self):
        self.t += 1
        v = 50 + 35 * math.sin(self.t / 6.0) + random.uniform(-6, 6)
        v = min(max(v, 0), 100)
        self.line.push(v)
        self.card_a.set_value("%.0f%%" % v)
        self.card_b.set_value("%.1f°C" % (40 + v / 4.0), COLORS["warn"] if v > 70 else COLORS["ok"])
        self.hbar.set_value(40 + v / 3.0)
        self.ring.set_value(v)
        self.vbar.set_value(v, "%.0f%%" % v)

    def ask(self):
        name = ask_text(self, "What is your name?")
        if name:
            self.log.log("Hello, %s!" % name, "info")
        elif confirm(self, "No name entered. Show a toast anyway?"):
            toast(self, "Fine :)", "ok")

    def run_cmd(self):
        self.log.log("running uname -a ...")
        run_command("uname -a",
                    on_done=lambda r: self.log.log(r.stdout.strip() or r.stderr.strip(), "ok" if r.ok else "bad"),
                    on_error=lambda tb: self.log.log(tb.strip().splitlines()[-1], "bad"))
