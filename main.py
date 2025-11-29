from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from gui.window import MainWindow
import logging
import sys
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

if __name__ == "__main__":
    LOG = logging.getLogger("main")
    app = QApplication(sys.argv)
    app.setFont(QFont("Casual", 10))
    win = MainWindow()
    win.show()

    sys.exit(app.exec_()) 