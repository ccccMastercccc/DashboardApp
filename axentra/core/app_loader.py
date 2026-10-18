"""
Axentra - apps/ discovery and loading (no drawing here, only logic).

apps/ rules
    apps/<name>/<name>.py    folder app. The main file must have EXACTLY the folder's name.
                             Its sibling files are imported by the main file
                             (either  `from .helper import x`  or  `import helper`).
                             Shown in the menu as <name>.
    apps/<name>.py           single-file app (still supported). Shown in the menu as <name>.
    apps/_something.py       background module: executed by the panel at startup (and again
                             when edited), NEVER shown in the menu. It may define
                             start() or start(window), and stop(), which the panel calls.
                             Other files can `import _something` as a normal helper too.

An app's main file must define ONE of:
    def create_widget() -> QWidget
    class App(QWidget)
"""
import importlib
import importlib.util
import inspect
import os
import re
import sys
import traceback
import types

from axentra import config

_SKIP_DIRS = {"__pycache__", "venv", ".venv", "env", "node_modules"}


class AppEntry:
    def __init__(self, name, kind, path):
        self.name = name              # menu text
        self.kind = kind              # "folder" | "file"
        self.path = path              # folder path or .py path
        self.key = "app:" + name
        self.signature = None         # changes whenever any .py of the app changes
        self.widget = None            # filled lazily by the UI
        self.safe = re.sub(r"\W", "_", name)
        self.pkg_name = "axentra_app_" + self.safe

    @property
    def main_file(self):
        if self.kind == "folder":
            return self.path / (self.name + ".py")
        return self.path


def _signature(kind, path):
    try:
        if kind == "file":
            return (1, path.stat().st_mtime)
        count, newest = 0, 0.0
        for root, dirs, files in os.walk(str(path)):
            dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
            for f in files:
                if f.endswith(".py"):
                    count += 1
                    newest = max(newest, os.stat(os.path.join(root, f)).st_mtime)
        return (count, newest)
    except OSError:
        return None


class AppManager:
    def __init__(self, context=None):
        self.context = context        # passed to start(window) of background modules
        self.entries = {}             # key -> AppEntry
        self._background = {}         # module name -> {"mtime", "module"}
        self.apps_dir = config.APPS_DIR
        self.apps_dir.mkdir(parents=True, exist_ok=True)
        if str(self.apps_dir) not in sys.path:
            sys.path.append(str(self.apps_dir))   # so `import _helper` works anywhere

    # ------------------------------------------------------------------ scan
    def scan(self):
        """Look at apps/ once. Returns (added, removed, modified) lists of AppEntry."""
        added, removed, modified = [], [], []
        try:
            children = sorted(self.apps_dir.iterdir())
        except OSError:
            return added, removed, modified

        found, background = {}, {}
        for p in children:
            n = p.name
            if n.startswith("."):
                continue
            if p.is_dir():
                if not n.startswith("_"):
                    found[n] = ("folder", p)
            elif p.suffix == ".py":
                if n.startswith("_"):
                    background[p.stem] = p
                elif p.stem not in found:      # a folder with the same name wins
                    found[p.stem] = ("file", p)

        for key, entry in list(self.entries.items()):
            if entry.name not in found or found[entry.name][0] != entry.kind:
                self.entries.pop(key)
                self._forget(entry)
                removed.append(entry)

        for name, (kind, path) in found.items():
            key = "app:" + name
            sig = _signature(kind, path)
            entry = self.entries.get(key)
            if entry is None:
                entry = AppEntry(name, kind, path)
                entry.signature = sig
                self.entries[key] = entry
                added.append(entry)
            elif sig is not None and sig != entry.signature:
                entry.signature = sig
                modified.append(entry)

        self._scan_background(background)
        return added, removed, modified

    # ----------------------------------------------------------- build widget
    def build_widget(self, entry):
        """Import the app and return its QWidget. Raises on any error (UI shows it)."""
        from PyQt5.QtWidgets import QWidget

        self._purge(entry)
        main_file = entry.main_file
        if not main_file.exists():
            raise FileNotFoundError(
                "Main file not found.\nExpected: %s\n"
                "(the main file must have exactly the same name as its folder)" % main_file)

        if entry.kind == "folder":
            pkg = types.ModuleType(entry.pkg_name)       # synthetic package -> relative imports work
            pkg.__path__ = [str(entry.path)]
            pkg.__package__ = entry.pkg_name
            sys.modules[entry.pkg_name] = pkg
            if str(entry.path) not in sys.path:
                sys.path.insert(0, str(entry.path))      # -> plain `import helper` works too
            mod_name = "%s.%s" % (entry.pkg_name, entry.safe)
        else:
            mod_name = entry.pkg_name

        importlib.invalidate_caches()
        spec = importlib.util.spec_from_file_location(mod_name, str(main_file))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)

        if hasattr(mod, "create_widget"):
            widget = mod.create_widget()
        elif hasattr(mod, "App"):
            widget = mod.App()
        else:
            raise RuntimeError("%s must define create_widget() or class App(QWidget)." % main_file.name)
        if not isinstance(widget, QWidget):
            raise TypeError("The app returned %s, expected a QWidget." % type(widget).__name__)
        return widget

    # ------------------------------------------------------------ housekeeping
    def _purge(self, entry):
        """Forget every module that belongs to this app so it can be re-imported fresh."""
        root = (str(entry.path) + os.sep) if entry.kind == "folder" else None
        for name, mod in list(sys.modules.items()):
            if name == entry.pkg_name or name.startswith(entry.pkg_name + "."):
                sys.modules.pop(name, None)
                continue
            f = getattr(mod, "__file__", None)
            if root and f and str(f).startswith(root):
                sys.modules.pop(name, None)

    def _forget(self, entry):
        self._purge(entry)
        if entry.kind == "folder" and str(entry.path) in sys.path:
            sys.path.remove(str(entry.path))

    # --------------------------------------------------- "_" background modules
    def _call_hook(self, fn):
        try:
            params = [p for p in inspect.signature(fn).parameters.values()
                      if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
        except (TypeError, ValueError):
            params = []
        return fn(self.context) if params else fn()

    def _scan_background(self, files):
        for name in [n for n in self._background if n not in files]:
            self._stop_background(name)
        for name, path in files.items():
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            rec = self._background.get(name)
            if rec is None or rec["mtime"] != mtime:
                if rec is not None:
                    self._stop_background(name)
                self._start_background(name, mtime)

    def _start_background(self, name, mtime):
        rec = {"mtime": mtime, "module": None}
        self._background[name] = rec
        try:
            importlib.invalidate_caches()
            sys.modules.pop(name, None)
            mod = importlib.import_module(name)
            rec["module"] = mod
            start = getattr(mod, "start", None)
            if callable(start):
                self._call_hook(start)
            print("[axentra] background module running: %s" % name)
        except Exception:
            print("[axentra] background module failed: %s" % name)
            traceback.print_exc()

    def _stop_background(self, name):
        rec = self._background.pop(name, None)
        if rec and rec["module"] is not None:
            stop = getattr(rec["module"], "stop", None)
            if callable(stop):
                try:
                    self._call_hook(stop)
                except Exception:
                    traceback.print_exc()
        sys.modules.pop(name, None)

    def shutdown(self):
        for name in list(self._background):
            self._stop_background(name)
