# Axentra App Development Guide

Build apps that match the Axentra panel's look and feel, without needing to know the details of PyQt or Qt.

Axentra ships with a small widget toolkit (`axentra.kit`) that wraps the common building blocks: layouts, cards, charts, tables, inputs, dialogs, background workers, and settings storage. A live example of every widget is included in `apps/kit_demo`, which also appears in the panel menu.

## Table of Contents

1. [Your First App](#1-your-first-app)
2. [Testing on Your Laptop](#2-testing-on-your-laptop)
3. [Five PyQt Concepts You Need](#3-five-pyqt-concepts-you-need)
4. [Widget Reference](#4-widget-reference)
5. [Common Patterns](#5-common-patterns)
6. [Common Mistakes](#6-common-mistakes)
7. [Kit Structure](#7-kit-structure)

---

## 1. Your First App

1. Copy the `apps/template` folder and rename it, for example `monitor`.
2. Rename `template.py` inside it to `monitor.py`. **The main file must have exactly the same name as its folder.**
3. Edit `monitor.py`:

```python
from axentra.kit import *

class App(Page):
    def __init__(self):
        super().__init__("Monitor", "A one-line description")
        self.card = StatCard("CPU", "--", "Processor usage")
        self.add(self.card)
        self.timer = every(self, 1000, self.refresh)     # refresh() is called every second

    def refresh(self):
        import psutil
        self.card.set_value("%.0f%%" % psutil.cpu_percent())
```

Within about two seconds, `monitor` appears in the panel menu. Every time you save the file, the app reloads automatically.

### The `apps` folder rules

| Item | Behavior |
|---|---|
| `apps/<name>/<name>.py` | An app. The folder name is shown in the menu. |
| Other files in the same folder | Helper modules, imported from the main file: `from .helper import x` |
| `apps/<name>.py` | A single-file app (still supported). |
| `apps/_something.py` | Runs without a menu entry (background service). Optional hooks: `start()` or `start(window)`, and `stop()`. |

The main file must provide **one of the following**:

- a `class App(...)`, or
- a `def create_widget()` function that returns a widget.

If your app raises an error, the panel does not crash. The error text is displayed on the app's page instead.

> **Note:** If two different apps have helper files with the same name (for example, both have `helper.py`), always use `from .helper import ...` rather than `import helper`.

---

## 2. Testing on Your Laptop

You can develop without the panel running:

```bash
pip install PyQt5 psutil
python dev_run.py monitor
```

Only the selected app opens, in a standalone window with the same styling as the panel, and it reloads automatically on every save. This also works on Windows.

When you're happy with the result, copy the app folder into `apps` on the server.

---

## 3. Five PyQt Concepts You Need

**1. Store anything you need later on `self`.**

```python
self.card = StatCard(...)      # Correct: later you can call self.card.set_value(...)
card = StatCard(...)           # Wrong: once __init__ finishes, you lose access to it
```

**2. Buttons and controls use callbacks.** Pass the function you want to run, *without* parentheses:

```python
Button("Save", on_click=self.save)      # self.save, not self.save()
```

**3. Layout is done with `Row`, `Column`, and `Card`:**

```python
Row(a, b, c)                     # side by side
Row(a, b, equal=True)            # side by side, equal widths
Column(a, b)                     # stacked vertically
Row(label, Spacer(), button)     # pushes the button to the right
Grid(columns=3)                  # grid layout
```

**4. Repeated work uses `every`:**

```python
self.timer = every(self, 1000, self.refresh)    # every 1000 ms
```

**5. Never run slow work directly in a button handler.** `time.sleep`, network requests, system commands, and heavy loops will freeze the panel. Use `run_async` and `run_command` instead (see [Background work](#timers-background-work-and-system-commands--workerspy)).

---

## 4. Widget Reference

Everything is available through `from axentra.kit import *`. Each widget lives in its own file under `axentra/kit/`, and every file has a full description at the top.

### Layout — `layout.py`

| Widget | Usage |
|---|---|
| `Page(title, subtitle)` | Base of every app. Scrolls vertically and horizontally when needed. Use `self.add(widget)` and `self.add_row(a, b)`. |
| `Card("Title", layout="v"/"h"/"grid")` | A titled container. `card.add(widget)` |
| `Row(...)`, `Column(...)`, `Grid(columns=3)` | Layouts |
| `Spacer()`, `Divider()` | Flexible space, separator line |

### Text and Status — `display.py`

| Widget | Usage |
|---|---|
| `Title`, `SectionTitle`, `Label(text, color=, size=, bold=, muted=, wrap=)`, `MutedLabel` | Text |
| `BigValue("42")` | Large number. `.set("43", color)` |
| `Badge("ONLINE", "ok")` | Colored label. Kinds: `ok` `warn` `bad` `info` `muted`. `.set(text, kind)` |
| `StatusDot("ok")` | Status indicator. `.set_state("bad")` |
| `StatCard("CPU", "--", "Description")` | Card with a large value. `.set_value(text, color)` and `.set_sub(text)` |

### Buttons and Controls — `buttons.py`, `switch.py`, `sliders.py`, `volume.py`

| Widget | Usage |
|---|---|
| `Button("Save", kind="primary", on_click=fn)` | Kinds: `default` `primary` `success` `danger` `ghost`. `.set_kind(...)` |
| `ToggleButton("Mute", on_toggle=fn)` | Two-state button. `fn(bool)` |
| `SegmentedControl(["1h","6h","24h"], on_change=fn)` | Choose between several options. `fn(index)`. `.index()` `.text()` |
| `Switch(checked, on_toggle=fn)` | Animated on/off switch. `.isChecked()` |
| `Slider(0, 100, value, suffix="%", title="")` | Horizontal slider |
| `VolumeSlider("Master", value=60)` | Vertical mixer-style fader. Click, drag, mouse wheel, or arrow keys. |
| `Knob("Gain", 0, 100, value, suffix="dB")` | Rotary knob. Drag up/down or use the mouse wheel. |
| `VolumeKnob("Master", value=65, on_change=fn)` | Rotary volume control with a value readout, a lit arc, and tick marks. Drag up/down, mouse wheel, or arrow keys. |
| `CompactVolumeKnob("Master", value=65, on_change=fn)` | A `VolumeKnob` sized to match `VolumeSlider` (fixed 64 px width), so the two can sit side by side in a mixer layout. |

All of these controls (`Slider`, `VolumeSlider`, `Knob`, `VolumeKnob`, `CompactVolumeKnob`) support `.value()`, `.set_value(v)`, and either the `.changed(int)` signal or `on_change=fn`.

`VolumeKnob` and `CompactVolumeKnob` take the full signature `(title="", minimum=0, maximum=100, value=50, suffix="%", color=None, step=1, on_change=None)`. `step` sets how much one wheel notch or arrow-key press changes the value, and `color` overrides the accent color of the arc and ticks. Dragging a full 160 px vertically sweeps the entire range.

```python
self.master = CompactVolumeKnob("Master", value=65, on_change=self.set_master)
self.add(Row(self.master, VolumeSlider("Music", value=40)))
```

### Inputs — `inputs.py`

`LineEdit`, `PasswordEdit`, `TextArea`, `ComboBox(["a","b"])`, `SpinBox(min,max,value)`, `DoubleSpinBox`, `CheckBox("text")`, `RadioGroup([...])`, and `Form()` for "label + input" rows:

```python
form = Form()
host = form.add("Host", LineEdit("localhost"))
port = form.add("Port", SpinBox(1, 65535, 22))
# later: host.text(), port.value()
```

### Charts and Bars — `charts.py`, `bars.py`

| Widget | Usage |
|---|---|
| `LineChart("CPU", COLORS["c_cpu"], "%", 0, 100, history=60, interval_ms=1000)` | Live line chart. Call `.push(value)` once every `interval_ms`. |
| `BarChart("Title")` | `.set_data(["Mon","Tue"], [12, 30])` |
| `DonutChart("Title")` | `.set_data([("Used",70), ("Free",30)])` |
| `HBar("Disk", auto_color=True)` | Horizontal bar. `.set_value(percent, "optional text")` |
| `VBar("CPU")` | Vertical bar (as used on the Home page) |
| `RingGauge("Memory", auto_color=True)` | Circular gauge |

Percentages are always 0–100. `auto_color=True` shifts the color from green to orange to red as the value rises.

### Tables and Logs — `tables.py`

```python
t = DataTable(["Name", "Status"], on_select=fn)
t.set_rows([["nginx", "running"], ["ssh", "stopped"]])
t.add_row([...]);  t.clear_rows();  t.selected_row()

log = LogView()
log.log("Started", "ok")        # kinds: ok warn bad info
```

### Images, Video, and Live Frames — `media.py`

```python
image = ImageViewer("images/photo.jpg")  # the image fills the whole widget
image.set_image("images/other.jpg")      # swap the image from code; returns False if it can't be loaded
image.clear()                            # back to a black surface

video = VideoPlayer("videos/demo.mp4")   # loads and autoplays; local path or URL
video.set_source("videos/other.mp4")     # load another video; returns False if the local file is missing
video.pause();  video.play();  video.stop()
video.set_volume(80)                     # 0-100
video.set_muted(False)                   # video audio is muted by default
video.playback_error.connect(print)      # signal: error text

frame = FrameWidget()
frame.set_frame(qimage)                  # QImage or QPixmap
# inside an image-processing loop:
frame.set_frame(opencv_frame)                        # uint8 OpenCV array, BGR by default
frame.set_frame(rgb_array, color_format="RGB")       # other channel orders
```

These widgets have no title, border, filename, or built-in controls. The image or video fills the whole widget surface while preserving aspect ratio, and any overflow is cropped.

**Supported inputs**

| Widget | Accepted sources |
|---|---|
| `ImageViewer` | Image path, `QImage`, `QPixmap`, or a `uint8` array |
| `FrameWidget` | `QImage`, `QPixmap`, image path, or a `uint8` array |
| `VideoPlayer` | Local file path, or a URL starting with `http`, `https`, `rtsp`, or `rtmp` |

**Frame array formats.** Arrays must be `uint8` with shape `(height, width)` or `(height, width, channels)`. Pass `color_format` to match your data:

| Channels | `color_format` |
|---|---|
| 1 (grayscale) | `"GRAY"` (used automatically for 1-channel arrays) |
| 3 | `"BGR"` (default, OpenCV order) or `"RGB"` |
| 4 | `"RGBA"` or `"BGRA"` |

**Threading.** `FrameWidget.set_frame()` copies the frame, and updates from `QImage` or `uint8` arrays are thread-safe, so you can call it from a background thread. Convert a `QPixmap` on the UI thread instead. Run your capture loop with a `QTimer` or background work so the UI is never blocked.

**Video format.** Playback goes through Qt's multimedia backend. If a file loads but no video stream can be decoded, `playback_error` fires with a hint to re-encode the file as H.264 MP4 (`yuv420p`).

### Dialogs — `dialogs.py`

```python
if confirm(self, "Delete this item?"): ...
info(self, "Saved");  warning(self, "...");  error(self, "...")
name = ask_text(self, "Name?")             # None if the user cancels
toast(self, "Saved", "ok")                 # small message that disappears on its own
```

### Timers, Background Work, and System Commands — `workers.py`

```python
self.timer = every(self, 1000, self.refresh)

run_async(slow_function, arg, on_done=self.show, on_error=self.fail)     # show(result)

run_command("df -h", on_done=self.show_df)                               # result.ok .stdout .stderr
run_command("systemctl restart nginx", sudo=True, on_done=fn)            # uses the sudo password from config.py
run_command("ls /var | wc -l", shell=True, on_done=fn)                   # when you need a pipe
```

`on_done` and `on_error` are always called on the main thread, so it is safe to update widgets inside them.

### Settings Storage — `storage.py`

```python
self.cfg = Settings(__file__)              # a settings.json file next to your app
vol = self.cfg.get("volume", 50)           # the second argument is the default value
self.cfg.set("volume", 70)                 # saved immediately
```

### Colors

`COLORS["accent"]`, `["ok"]`, `["warn"]`, `["bad"]`, `["text"]`, `["muted"]`, `["card"]`, `["border"]`, `["c_cpu"]`, `["c_ram"]`, `["c_net"]`, `["c_temp"]`.

---

## 5. Common Patterns

**Live display of a system value**

```python
self.chart = LineChart("RAM", COLORS["c_ram"], "%", 0, 100)
self.add(self.chart)
self.timer = every(self, 1000, lambda: self.chart.push(psutil.virtual_memory().percent))
```

**A button that runs a heavy command**

```python
Button("Restart nginx", "danger", on_click=self.restart)

def restart(self):
    if not confirm(self, "Restart nginx?"):
        return
    run_command("systemctl restart nginx", sudo=True, on_done=self.restarted)

def restarted(self, result):
    toast(self, "Done" if result.ok else result.stderr, "ok" if result.ok else "bad")
```

**Multiple sections with tabs** (tabs are already styled)

```python
from PyQt5.QtWidgets import QTabWidget
tabs = QTabWidget()
tabs.addTab(Column(a, b), "General")
tabs.addTab(Column(c), "Advanced")
self.add(tabs, stretch=1)         # stretch=1 fills all remaining height
```

**An auto-updating list**

```python
self.table = DataTable(["PID", "Name"])
self.add(self.table, stretch=1)
self.timer = every(self, 2000, self.update_table)

def update_table(self):
    self.table.set_rows([[p.pid, p.name()] for p in psutil.process_iter()][:20])
```

---

## 6. Common Mistakes

| Problem | Cause and fix |
|---|---|
| A widget or timer disappears | You didn't store it on `self`. Use `self.timer = every(...)`. |
| The panel freezes for a few seconds | Slow work in a button handler. Use `run_async` / `run_command`. |
| `on_click=self.save()` doesn't work | Remove the parentheses: `on_click=self.save` |
| The app doesn't show up in the menu | The main file name doesn't match the folder name, or the name starts with `_`. |
| Importing a helper file raises an error | Use `from .helper import x`. |
| The chart jumps around | Set `interval_ms` equal to the interval at which you call `push`. |
| An error page appears | Read it: the last line shows the error type and the line number. |

---

## 7. Kit Structure

If you want to add your own widgets, this is how the kit is organized:

```
axentra/kit/
├── __init__.py   Index of everything exported by `import *` (__all__)
├── layout.py     Page Card Row Column Grid Spacer Divider
├── display.py    Title Label BigValue Badge StatusDot StatCard
├── buttons.py    Button ToggleButton SegmentedControl
├── switch.py     Switch
├── sliders.py    Slider VolumeSlider Knob
├── volume.py     VolumeKnob CompactVolumeKnob
├── bars.py       HBar VBar RingGauge
├── charts.py     LineChart BarChart DonutChart
├── inputs.py     LineEdit ComboBox SpinBox CheckBox RadioGroup Form ...
├── tables.py     DataTable LogView
├── media.py      ImageViewer FrameWidget VideoPlayer
├── dialogs.py    confirm info warning error ask_text toast
├── workers.py    every run_async run_command
├── storage.py    Settings
└── _util.py      Internal helpers
```

The colors and styling for the whole panel (including plain Qt widgets such as `QPushButton` and `QLineEdit`) live in `axentra/theme.py`.

To add a new widget, write a class in the appropriate file and add its name to `__init__.py` (both the import and `__all__`).
