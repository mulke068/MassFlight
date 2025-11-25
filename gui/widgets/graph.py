

from PyQt5.QtWidgets import QWidget

class GraphWidget(QWidget):
    def __init__(self, title, graph_values, data_type='altitude', parent=None):
        super().__init__(parent)
        self.title = title
        self.data_type = data_type
        self.values = graph_values 
        
        self.draw()
