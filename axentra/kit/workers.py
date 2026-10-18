"""
Axentra kit - timers, background work, system commands.

IMPORTANT: never run slow code (network calls, time.sleep, big loops, subprocess) directly in a
button handler - the whole panel freezes. Use these helpers instead.

    every(self, 1000, self.refresh)                      call self.refresh every second (also once now)
    run_async(func, arg, on_done=fn, on_error=fn)        run func(arg) in the background; fn(result) afterwards
    run_command("df -h", on_done=fn)                     fn(result)  result.ok  .stdout  .stderr  .returncode
    run_command("systemctl restart nginx", sudo=True, on_done=fn)    uses SUDO_PASSWORD from config.py
    run_command("ls /var | head", shell=True, on_done=fn)            when you need pipes / redirects

on_done / on_error are always called in the UI thread, so you can touch widgets inside them.
"""
import shlex
import subprocess
import threading
import traceback

from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot

from axentra import config

_ACTIVE = set()     # keeps running jobs alive until they finish


def every(owner, ms, func, immediate=True):
    """Call func every `ms` milliseconds. `owner` is usually `self`; the timer dies with it."""
    t = QTimer(owner)
    t.timeout.connect(func)
    t.start(ms)
    if immediate:
        func()
    return t


class _Job(QObject):
    done = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, func, args, kwargs, on_done, on_error):
        super().__init__()
        self._func, self._args, self._kwargs = func, args, kwargs
        self._on_done, self._on_error = on_done, on_error
        self.done.connect(self._ok)
        self.failed.connect(self._err)

    def start(self):
        _ACTIVE.add(self)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            result = self._func(*self._args, **self._kwargs)
        except Exception:
            self.failed.emit(traceback.format_exc())
            return
        self.done.emit(result)

    @pyqtSlot(object)
    def _ok(self, result):
        try:
            if self._on_done:
                self._on_done(result)
        finally:
            self._release()

    @pyqtSlot(str)
    def _err(self, tb):
        try:
            if self._on_error:
                self._on_error(tb)
            else:
                print(tb)
        finally:
            self._release()

    def _release(self):
        _ACTIVE.discard(self)
        self.deleteLater()


def run_async(func, *args, on_done=None, on_error=None, **kwargs):
    """Run func(*args, **kwargs) in a background thread."""
    _Job(func, args, kwargs, on_done, on_error).start()


class CommandResult:
    def __init__(self, returncode, stdout, stderr):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr

    @property
    def ok(self):
        return self.returncode == 0

    def __repr__(self):
        return "<CommandResult code=%s>" % self.returncode


def _run_command(command, sudo, shell, timeout):
    if isinstance(command, (list, tuple)):
        cmd = [str(c) for c in command]
    elif shell:
        cmd = ["sh", "-c", command]
    else:
        cmd = shlex.split(command)
    stdin = None
    if sudo:
        cmd = ["sudo", "-S", "-k", "-p", ""] + cmd
        stdin = config.SUDO_PASSWORD + "\n"
    p = subprocess.run(cmd, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       universal_newlines=True, timeout=timeout)
    return CommandResult(p.returncode, p.stdout, p.stderr)


def run_command(command, on_done=None, on_error=None, sudo=False, shell=False, timeout=30):
    """Run a system command in the background. command = "text" or ["list", "of", "args"]."""
    run_async(_run_command, command, sudo, shell, timeout, on_done=on_done, on_error=on_error)
