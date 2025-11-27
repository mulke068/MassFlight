from PyQt5 import QtWidgets, QtCore
import Msphere



class MainWindow(QtWidgets.QMainWindow):
    """  Main application window  """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 700, 500)

        self.button = QtWidgets.QPushButton("ALTITUDE", self)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.sphere)

    @QtCore.pyqtSlot()
    def sphere(self):
        Msphere.SphereWindow.show_sphere()