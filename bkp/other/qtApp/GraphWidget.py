"All grpahs that will be displayed"

from PyQt5.QtWidgets import (QWidget, QVBoxLayout)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from OpenGL.GL import *
from OpenGL.GLU import *

class GraphWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.figure = Figure(facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1e1e1e;")
        self.create_plot()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def create_plot(self):
        ax = self.figure.add_subplot(111)
        
        if "Altitude" in self.title:
            time_seconds = [0, 1, 2, 3]
            values = [150, 220, 180, 300]
            color = '#4ecdc4'
            ax.set_ylabel('Meters (m)', color='white')
        elif "Latitude" in self.title:
            time_seconds = [0, 1, 2, 3, 4, 5, 6]
            values = [1200, 1400, 1300, 1600, 1500, 1700, 1900]
            color = '#45b7d1'
            ax.set_ylabel('Meters (m)', color='white')
        elif "Velocity" in self.title:
            time_seconds = [0, 1, 2, 3]
            values = [85, 92, 78, 96]
            color = '#96ceb4'
            ax.set_ylabel('Velocity (m/s)', color='white')
        else:
            time_seconds = []
            values = []
            color = '#ffffff'
        
        ax.plot(time_seconds, values, marker='o', linewidth=3, markersize=8, color=color)
        ax.set_facecolor('#2d2d2d')
        ax.set_xlabel('Time (s)', color='white')
        ax.set_title(self.title, color='white', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()

