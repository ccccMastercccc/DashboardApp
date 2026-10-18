"""
Axentra - central settings.
Everything you may want to tweak lives here; no other file needs editing for that.
"""
from pathlib import Path

APP_NAME = "main"
TAGLINE = "Engineered for Control."

# ---- paths -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent      # .../axentra
PROJECT_DIR = BASE_DIR.parent                   # folder that holds main.py
APPS_DIR = PROJECT_DIR / "apps"
LOGO_PATH = BASE_DIR / "assets" / "axentra_logo.png"

# ---- display ---------------------------------------------------------------
FULLSCREEN = False        # borderless full screen (no title bar / window buttons)
SPLASH_ENABLED = False    # show the logo before the panel loads
SPLASH_HOLD_MS = 3000    # how long the logo stays fully visible
SPLASH_FADE_MS = 700     # fade-in and fade-out duration

# ---- power buttons ---------------------------------------------------------
DRY_RUN = False                  # True: buttons only print to the terminal, nothing is executed
SUDO_PASSWORD = "CHANGE_ME"      # the server's sudo password

# ---- timing / data ---------------------------------------------------------
APPS_SCAN_MS = 2000      # how often the apps/ folder is checked
STATS_MS = 1000          # how often the Home dashboard refreshes
HISTORY = 60             # number of points kept in each line chart
NET_BAR_FULL_MBPS = None # None = network bar auto-scales to the recent peak; or e.g. 100.0
