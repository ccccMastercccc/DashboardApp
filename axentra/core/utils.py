"""Axentra - small shared helpers."""


def human_bytes(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return "%.0f %s" % (n, unit) if unit in ("B", "KB") else "%.1f %s" % (n, unit)
        n /= 1024
