import signal
import sys
import traceback

from PyQt5.QtWidgets import QApplication

from axentra import config
from axentra.theme import STYLE
from axentra.ui.main_window import MainWindow
from axentra.ui.splash import SplashScreen


def main():
    sys.excepthook = lambda t, v, tb: traceback.print_exception(t, v, tb)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setStyleSheet(STYLE)

    splash = None
    if config.SPLASH_ENABLED and config.LOGO_PATH.exists():
        splash = SplashScreen(config.LOGO_PATH, config.SPLASH_HOLD_MS, config.SPLASH_FADE_MS)
        splash.start()
        for _ in range(3):              
            app.processEvents()

    win = MainWindow()               
    app.aboutToQuit.connect(win.shutdown)

    def reveal():
        win.present()
        if splash is not None:
            splash.close()

    if splash is None:
        reveal()
    else:
        splash.finished.connect(reveal)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
