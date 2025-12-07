from enum import Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config.app_config import THEME

class GraphType(Enum): # TODO: create new graph types
    Altitude = "Altitude"
    Latitude = "Latitude"
    Velocity = "Velocity"

class GraphWidget(QWidget):
    def __init__(self, graph_values=[(0,0)], graph_type=GraphType.Altitude, parent=None):
        super().__init__(parent)
        self.background_color = '#1e1e1e'
        self.graph_type = graph_type
        self.values = graph_values 
        self.x_axis, self.y_axis = zip(*self.values)
        self.period = len(self.values)
        self._pan_start = None
        
        self.draw()

    def initUI(self): 
        ax = self.figure.add_subplot(111)
        
        if GraphType.Altitude == self.graph_type:
            color = THEME['content']
            ax.set_ylabel('Meters (m)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        elif GraphType.Latitude == self.graph_type:
            color = THEME['content']
            ax.set_ylabel('Latitude (deg)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        elif GraphType.Velocity == self.graph_type:
            color = THEME['content']
            ax.set_ylabel('Velocity (m/s)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        else:
            color = THEME['content']
            ax.set_xlabel('Time (s)', color='white')
            ax.set_xlabel('Time (s)', color='white')
        
        ax.plot(self.x_axis, self.y_axis, marker='o', linewidth=3, markersize=8, color='white')
        ax.set_title(self.graph_type.value, color='white', fontsize=14, fontweight='bold')
        ax.set_facecolor(THEME['background_accent'])
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()


        self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.canvas.mpl_connect('button_press_event', self._on_button_press)
        self.canvas.mpl_connect('button_release_event', self._on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)

    def _on_button_press(self, event):
        if event.inaxes is None:
            return
            
        if event.button == 1:  # Left mouse button
            self._pan_start = (event.xdata, event.ydata, event.inaxes)
            self.canvas.setCursor(1)  # Closed hand cursor
    
    def _on_button_release(self, event):
        if event.button == 1 and self._pan_start is not None:  # Left mouse button
            self._pan_start = None
            self.canvas.setCursor(0)  # Arrow cursor


    def _on_mouse_move(self, event):
        if self._pan_start is None or event.inaxes is None:
            return
            
        if event.button != 1:  # Only pan when left button is pressed
            return
            
        start_x, start_y, ax = self._pan_start
        dx = start_x - event.xdata
        dy = start_y - event.ydata
        
        # Get current limits
        x_left, x_right = ax.get_xlim()
        y_bottom, y_top = ax.get_ylim()
        
        # Apply the pan
        ax.set_xlim(x_left + dx, x_right + dx)
        ax.set_ylim(y_bottom + dy, y_top + dy)
        
        self.canvas.draw_idle()

    def _on_scroll(self, event):
        # protect against scrolls outside axes
        if event.inaxes is None:
            return

        ax = event.inaxes
        base_scale = 1.2
        if hasattr(event, 'button') and event.button in ('up', 'down'):
            scale = 1.0 / base_scale if event.button == 'up' else base_scale
        else:
            # fallback using step direction
            step = getattr(event, 'step', None)
            if step is None:
                step = 1 if getattr(event, 'step', 1) > 0 else -1
            scale = 1.0 / base_scale if step > 0 else base_scale

        # get current limits
        x_left, x_right = ax.get_xlim()
        y_bottom, y_top = ax.get_ylim()

        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

        # compute new limits so zoom is centered on mouse
        new_width = (x_right - x_left) * scale
        new_height = (y_top - y_bottom) * scale

        relx = (xdata - x_left) / (x_right - x_left)
        rely = (ydata - y_bottom) / (y_top - y_bottom)

        new_left = xdata - relx * new_width
        new_right = new_left + new_width
        new_bottom = ydata - rely * new_height
        new_top = new_bottom + new_height

        ax.set_xlim(new_left, new_right)
        ax.set_ylim(new_bottom, new_top)
        self.canvas.draw_idle()

    def update_data(self, new_values):
        """Updates the graph with new data points."""
        if not new_values:
            self.values = []
            self.x_axis = []
            self.y_axis = []
        else:
            self.values = new_values
            self.x_axis, self.y_axis = zip(*self.values)
        
        self.figure.clear()
        self.initUI()
        self.canvas.draw()

    def draw(self):
        layout = QVBoxLayout()
        self.figure = Figure(facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background-color: ;")
        self.initUI()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
