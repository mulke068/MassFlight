import sys
import Mhome, Msphere
from PyQt5 import QtWidgets


if __name__ == '__main__':
    # Create the QApplication before any QWidget is constructed
    #app = QtWidgets.QApplication(sys.argv)

    # Create and show the main window
    #window = Mhome.MainWindow()
    #window.show()

    # Start the Qt event loop
    #sys.exit(app.exec_())
    Msphere.SphereWindow.show_sphere()
