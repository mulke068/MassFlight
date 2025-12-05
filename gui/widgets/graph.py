"""
GraphWidget module
A widget to display graphs using Matplotlib within a PyQt5 application.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config.app_config import THEME
import logging
LOG = logging.getLogger(__name__)

class GraphWidget(QWidget):
    def __init__(self, graph_values=[(0,0)], graph_type='Altitude', parent=None):
        super().__init__(parent)
        self.background_color = '#1e1e1e'
        self.graph_type = graph_type
        self.values = graph_values 
        self.x_axis, self.y_axis = zip(*self.values)
        self.period = len(self.values)
        self._pan_start = None
        self.draw()

    def initUI(self): 
        axis_subplot = self.figure.add_subplot(111)
        
        if "Altitude" in self.graph_type:
            color = THEME['content']
            axis_subplot.set_ylabel('Meters (m)', color='white')
            axis_subplot.set_xlabel('Time (s)', color='white')
        elif "Latitude" in self.graph_type:
            color = THEME['content']
            axis_subplot.set_ylabel('Meters (m)', color='white')
            axis_subplot.set_xlabel('Time (s)', color='white')
        elif "Velocity" in self.graph_type:
            color = THEME['content']
            axis_subplot.set_ylabel('Velocity (m/s)', color='white')
            axis_subplot.set_xlabel('Time (s)', color='white')
        else:
            color = THEME['content']
            axis_subplot.set_xlabel('Time (s)', color='white')
            axis_subplot.set_xlabel('Time (s)', color='white')
        
        axis_subplot.plot(self.x_axis, self.y_axis, marker='o', linewidth=3, markersize=8, color='white')
        axis_subplot.set_title(self.graph_type, color='white', fontsize=14, fontweight='bold')
        axis_subplot.set_facecolor(THEME['background_accent'])
        axis_subplot.tick_params(axis='x', colors='white')
        axis_subplot.tick_params(axis='y', colors='white')
        axis_subplot.grid(True, alpha=0.3)
        self.figure.tight_layout()


        self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.canvas.mpl_connect('button_press_event', self._on_button_press)
        self.canvas.mpl_connect('button_release_event', self._on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)

    def _on_button_press(self, event):
        if event.inaxes is None:
            return
            
        if event.button == 1:
            self._pan_start = (event.xdata, event.ydata, event.inaxes)
            self.canvas.setCursor(1)
    
    def _on_button_release(self, event):
        if event.button == 1 and self._pan_start is not None:
            self._pan_start = None
            self.canvas.setCursor(0)

    def _on_mouse_move(self, event):
        if self._pan_start is None or event.inaxes is None:
            return
            
        if event.button != 1:
            return
            
        start_x, start_y, ax = self._pan_start
        dx = start_x - event.xdata
        dy = start_y - event.ydata

        x_left, x_right = ax.get_xlim()
        y_bottom, y_top = ax.get_ylim()

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
            step = getattr(event, 'step', None)
            if step is None:
                step = 1 if getattr(event, 'step', 1) > 0 else -1
            scale = 1.0 / base_scale if step > 0 else base_scale

        x_left, x_right = ax.get_xlim()
        y_bottom, y_top = ax.get_ylim()

        xdata = event.xdata
        ydata = event.ydata
        if xdata is None or ydata is None:
            return

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

    def draw(self):
        layout = QVBoxLayout()
        self.figure = Figure(facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background-color: ;")
        self.initUI()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
