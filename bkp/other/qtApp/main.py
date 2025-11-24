import MainWindow

import logging
LOG = logging.getLogger(__name__)
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
import sys

def main():
    # Only show warnings and errors, not debug messages
    logging.basicConfig(
        level=logging.WARNING,  # Changed from DEBUG to WARNING
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Optionally, make matplotlib even quieter
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow.MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()