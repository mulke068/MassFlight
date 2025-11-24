"Main run for the app"

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
import MainWindow
import sys

def main():
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow.MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()