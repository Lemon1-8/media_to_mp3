import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from .ui.main_window import MainWindow


def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("Qoder")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
