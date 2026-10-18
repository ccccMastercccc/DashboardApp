"""
Axentra - shut down / restart.
Asks "Are you sure?", then runs `sudo systemctl poweroff|reboot` with the
password from config.SUDO_PASSWORD.
"""
import subprocess
import threading

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

from axentra import config


class _Runner(QObject):
    failed = pyqtSignal(str)

    def run(self, action):
        threading.Thread(target=self._exec, args=(action,), daemon=True).start()

    def _exec(self, action):
        try:
            proc = subprocess.run(
                ["sudo", "-S", "-k", "-p", "", "systemctl", action],
                input=config.SUDO_PASSWORD + "\n",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=20,
            )
            if proc.returncode != 0:
                self.failed.emit(proc.stderr.strip() or "exit code %d" % proc.returncode)
        except Exception as ex:
            self.failed.emit(str(ex))


class PowerController(QObject):
    LABELS = {"poweroff": "Shut down", "reboot": "Restart"}

    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self._widget = parent_widget
        self._runner = _Runner(self)
        self._runner.failed.connect(self._on_failed)

    def request(self, action):
        label = self.LABELS.get(action, action)
        box = QMessageBox(self._widget)
        box.setWindowTitle(label)
        box.setIcon(QMessageBox.Warning)
        box.setText("Are you sure you want to %s the server?" % label.lower())
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        box.setDefaultButton(QMessageBox.Cancel)
        if box.exec_() != QMessageBox.Yes:
            return
        if config.DRY_RUN:
            print("[DRY RUN] sudo systemctl %s" % action)
        else:
            self._runner.run(action)

    @pyqtSlot(str)
    def _on_failed(self, msg):
        QMessageBox.critical(self._widget, "Power command failed", msg)
