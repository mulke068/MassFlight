import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Set up the window
        self.setWindowTitle('Simple PyQt5 Example')
        self.setGeometry(100, 100, 300, 200)

        # Create a label
        self.label = QLabel('Hello, PyQt5!', self)

        # Create a button and connect it to a function
        self.button = QPushButton('Click Me', self)
        self.button.clicked.connect(self.on_click)

        # Create a layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        # Set the layout to the window
        self.setLayout(layout)

    def on_click(self):
        # Change the label text when the button is clicked
        self.label.setText('Button Clicked!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())
