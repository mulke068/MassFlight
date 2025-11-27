

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config.app_config import THEME

class GraphWidget(QWidget):
    def __init__(self, graph_values=[(0,0)], graph_type='Altitude', parent=None):
        super().__init__(parent)
        self.graph_type = graph_type
        self.values = graph_values 
        self.x_axis, self.y_axis = zip(*self.values) #all x and y values individually
        self.period = len(self.values)

        self.background_color = '#1e1e1e'
        
        self.draw()
        self.UI()

    def UI(self): 
        ax = self.figure.add_subplot(111)
        
        if "Altitude" in self.graph_type:
            color = THEME['content']
            ax.set_ylabel('Meters (m)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        elif "Latitude" in self.graph_type:
            color = THEME['content']
            ax.set_ylabel('Meters (m)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        elif "Velocity" in self.graph_type:
            color = THEME['content']
            ax.set_ylabel('Velocity (m/s)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        else:
            color = THEME['content']
            ax.set_xlabel('Time (s)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        
        ax.plot(self.values, marker='o', linewidth=3, markersize=8, color=color)
        ax.set_title(self.graph_type, color='white', fontsize=14, fontweight='bold')
        ax.set_facecolor(THEME['background'])
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()

    def draw(self):
        layout = QVBoxLayout()
        self.figure = Figure(facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background-color: ;")
        self.create_plot()
        layout.addWidget(self.canvas)
        self.setLayout(layout)



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    demo = GraphWidget(graph_values=[(0,150),(1,220),(2,180),(3,300)], graph_type='Altitude over Time')
    demo.show()
    sys.exit(app.exec_())