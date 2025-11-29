from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GraphWidget(QWidget):
    """Widget displaying a matplotlib graph"""
    
    def __init__(self, title, data_type='altitude', parent=None):
        super().__init__(parent)
        self.title = title
        self.data_type = data_type
        self.initUI()
    
    def initUI(self):
        """Initialize the widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create matplotlib figure
        self.figure = Figure(facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1e1e1e;")
        
        # Create initial plot
        self.create_plot()
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def create_plot(self):
        """Create the plot based on data type"""
        ax = self.figure.add_subplot(111)
        
        # Get data and styling based on type
        time_data, values, color, ylabel = self._get_plot_data()
        
        # Plot the data
        ax.plot(time_data, values, marker='o', linewidth=3, 
                markersize=8, color=color)
        
        # Styling
        ax.set_facecolor('#2d2d2d')
        ax.set_xlabel('Time (s)', color='white', fontsize=11)
        ax.set_ylabel(ylabel, color='white', fontsize=11)
        ax.set_title(self.title, color='white', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, alpha=0.3, color='white', linestyle='--')
        
        # Spine colors
        for spine in ax.spines.values():
            spine.set_color('#555')
        
        self.figure.tight_layout()
    
    def _get_plot_data(self):
        """Get sample data based on data type"""
        if self.data_type == 'altitude':
            time_data = [0, 1, 2, 3, 4, 5, 6, 7]
            values = [150, 220, 180, 300, 280, 350, 320, 400]
            color = '#4ecdc4'
            ylabel = 'Altitude (m)'
        
        elif self.data_type == 'latitude':
            time_data = [0, 1, 2, 3, 4, 5, 6, 7]
            values = [1200, 1400, 1300, 1600, 1500, 1700, 1900, 2000]
            color = '#45b7d1'
            ylabel = 'Distance (m)'
        
        elif self.data_type == 'velocity':
            time_data = [0, 1, 2, 3, 4, 5, 6, 7]
            values = [85, 92, 78, 96, 102, 88, 94, 110]
            color = '#96ceb4'
            ylabel = 'Velocity (m/s)'
        
        else:
            time_data = []
            values = []
            color = '#ffffff'
            ylabel = 'Value'
        
        return time_data, values, color, ylabel
    
    def update_data(self, time_data, values):
        """
        Update the plot with new data
        
        Args:
            time_data: List of time values
            values: List of corresponding data values
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        _, _, color, ylabel = self._get_plot_data()
        
        ax.plot(time_data, values, marker='o', linewidth=3, 
                markersize=8, color=color)
        
        ax.set_facecolor('#2d2d2d')
        ax.set_xlabel('Time (s)', color='white', fontsize=11)
        ax.set_ylabel(ylabel, color='white', fontsize=11)
        ax.set_title(self.title, color='white', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, alpha=0.3, color='white', linestyle='--')
        
        for spine in ax.spines.values():
            spine.set_color('#555')
        
        self.figure.tight_layout()
        self.canvas.draw()