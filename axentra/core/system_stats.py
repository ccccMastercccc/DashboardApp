"""
Axentra - system data collection.
Only READS values from the OS (CPU, RAM, network, temperature, disk, users).
No Qt and no drawing here, so it can be tested on its own.
"""
import time
from collections import deque
from pathlib import Path

try:
    import psutil
except ImportError:
    raise SystemExit("psutil is missing:  pip install psutil")

from axentra import config


class SystemStats:
    def __init__(self):
        psutil.cpu_percent(None)  # prime the counter
        self._last_bytes = self._net_bytes()
        self._last_t = time.monotonic()
        self._net_peak = deque(maxlen=config.HISTORY)

    # ---- individual readers ----
    @staticmethod
    def _net_bytes():
        total = 0
        for name, io in psutil.net_io_counters(pernic=True).items():
            if name != "lo":
                total += io.bytes_sent + io.bytes_recv
        return total

    @staticmethod
    def _cpu_temp():
        try:
            temps = psutil.sensors_temperatures()
        except Exception:
            temps = {}
        for key in ("coretemp", "k10temp", "zenpower", "cpu_thermal", "cpu-thermal", "acpitz"):
            vals = [t.current for t in temps.get(key, []) if t.current]
            if vals:
                return max(vals)
        for entries in temps.values():
            vals = [t.current for t in entries if t.current]
            if vals:
                return max(vals)
        best = None
        for f in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
            try:
                v = int(f.read_text().strip()) / 1000.0
                best = v if best is None else max(best, v)
            except Exception:
                pass
        return best

    # ---- one snapshot ----
    def sample(self):
        now = time.monotonic()
        cur = self._net_bytes()
        dt = max(now - self._last_t, 1e-3)
        mbps = max(0.0, (cur - self._last_bytes) * 8 / dt / 1e6)
        self._last_bytes, self._last_t = cur, now
        self._net_peak.append(mbps)

        vm = psutil.virtual_memory()
        du = psutil.disk_usage("/")
        names = sorted({u.name for u in psutil.users()})

        return {
            "cpu": psutil.cpu_percent(None),
            "ram": vm.percent, "ram_used": vm.used, "ram_total": vm.total,
            "net": mbps, "net_peak": max(self._net_peak),
            "temp": self._cpu_temp(),
            "disk_pct": du.percent, "disk_used": du.used,
            "disk_free": du.free, "disk_total": du.total,
            "users": names,
        }
