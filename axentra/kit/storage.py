"""
Axentra kit - remember settings between runs.

    self.cfg = Settings(__file__)               # creates settings.json next to your app file
    volume = self.cfg.get("volume", 50)         # second argument = default
    self.cfg.set("volume", 70)                  # saved immediately

Values must be JSON-friendly: numbers, text, True/False, lists, dicts.
(Saving a .json file does NOT trigger the app's auto-reload; only .py files do.)
"""
import json
import os
from pathlib import Path


class Settings:
    def __init__(self, app_file, name="settings.json"):
        self.path = Path(app_file).resolve().with_name(name)
        self._data = {}
        try:
            self._data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self._data = {}

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def all(self):
        return dict(self._data)

    def save(self):
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(str(tmp), str(self.path))
