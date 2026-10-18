"""
Axentra UI kit - ready-made widgets in the panel's own style.

In your app:
    from axentra.kit import *

Everything listed in __all__ below becomes available.
See DEVELOPER_GUIDE_FA.md for the full guide and apps/kit_demo for a live example.
"""
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QWidget

from axentra.kit.bars import HBar, RingGauge, VBar
from axentra.kit.canvas import CanvasPage, DesignPage, mount, place
from axentra.kit.buttons import Button, SegmentedControl, ToggleButton
from axentra.kit.charts import BarChart, DonutChart, LineChart
from axentra.kit.dialogs import ask_text, confirm, error, info, toast, warning
from axentra.kit.display import (Badge, BigValue, Label, MutedLabel, SectionTitle, StatCard,
                                 StatusDot, Title)
from axentra.kit.inputs import (CheckBox, ComboBox, DoubleSpinBox, Form, LineEdit, PasswordEdit,
                                RadioGroup, SpinBox, TextArea)
from axentra.kit.layout import Card, Column, Divider, Grid, Page, Row, Spacer, put
from axentra.kit.media import FrameWidget, ImageViewer, VideoPlayer
from axentra.kit.sliders import Knob, Slider, VolumeSlider
from axentra.kit.storage import Settings
from axentra.kit.switch import Switch
from axentra.kit.tables import DataTable, LogView
from axentra.kit.volume import CompactVolumeKnob, VolumeKnob
from axentra.kit.workers import every, run_async, run_command
from axentra.theme import C as COLORS

__all__ = [
    # layout
    "Page", "Card", "Row", "Column", "Grid", "Spacer", "Divider", "put", "DesignPage", "mount", "CanvasPage", "place",
    # text / status
    "Title", "SectionTitle", "Label", "MutedLabel", "BigValue", "Badge", "StatusDot", "StatCard",
    # controls
    "Button", "ToggleButton", "SegmentedControl", "Switch", "Slider", "VolumeSlider", "Knob",
    "VolumeKnob", "CompactVolumeKnob",
    # inputs
    "LineEdit", "PasswordEdit", "TextArea", "ComboBox", "SpinBox", "DoubleSpinBox", "CheckBox",
    "RadioGroup", "Form",
    # data display
    "HBar", "VBar", "RingGauge", "LineChart", "BarChart", "DonutChart", "DataTable", "LogView",
    # media
    "ImageViewer", "FrameWidget", "VideoPlayer",
    # dialogs
    "confirm", "info", "warning", "error", "ask_text", "toast",
    # background work, timers, storage
    "every", "run_async", "run_command", "Settings",
    # colors + a few Qt names so beginners need fewer imports
    "COLORS", "Qt", "QTimer", "QWidget", "pyqtSignal",
]
