from enum import Enum
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from config.app_config import THEME
import math

class GraphType(Enum):
    Altitude = "Altitude"
    Latitude = "Latitude"
    Longitude = "Longitude"
    Velocity = "Velocity"
    Distance = "Distance (Horizontal)"
    FlightPathAngle = "Flight Path Angle (deg)" 
    PolarTrajectory = "Polar Trajectory" # R vs Theta
    Downrange = "Downrange Distance (km)"
    HeightVsDistance = "Height vs Downrange"

class GraphWidget(QWidget):
    def __init__(self, graph_type=GraphType.Altitude, graph_values=None, parent=None):
        super().__init__(parent)
        self.background_color = '#1e1e1e'
        self.graph_type = graph_type
        self.values = graph_values if graph_values else []
        
        # Unpack values safely
        if self.values:
            self.x_axis, self.y_axis = zip(*self.values)
        else:
            self.x_axis, self.y_axis = [], []
            
        self.period = len(self.values)
        self._pan_start = None
        
        self.draw()

    def initUI(self): 
        # Handle Polar Projection
        if self.graph_type == GraphType.PolarTrajectory:
             # Add subplot with 'polar' projection
             self.ax = self.figure.add_subplot(111, projection='polar')
        else:
             self.ax = self.figure.add_subplot(111)
        
        ax = self.ax
        
        # Common Styling
        color = THEME['content']
        label_color = 'white'
        grid_alpha = 0.3
        
        # Configure Axes Labels
        if GraphType.Altitude == self.graph_type:
            ax.set_ylabel('Height (km)', color=label_color)
            ax.set_xlabel('Time (s)', color=label_color)
            
        elif GraphType.Latitude == self.graph_type:
            ax.set_ylabel('Latitude (deg)', color=label_color)
            ax.set_xlabel('Time (s)', color=label_color)
            
        elif GraphType.Longitude == self.graph_type:
            ax.set_ylabel('Longitude (deg)', color=label_color)
            ax.set_xlabel('Time (s)', color=label_color)
            
        elif GraphType.Velocity == self.graph_type:
            ax.set_ylabel('Velocity (km/s)', color=label_color)
            ax.set_xlabel('Time (s)', color=label_color)
            
        elif GraphType.FlightPathAngle == self.graph_type:
            ax.set_ylabel('Flight Path Angle (deg)', color=label_color)
            ax.set_xlabel('Time (s)', color=label_color)
            
        elif GraphType.Downrange == self.graph_type:
            ax.set_ylabel('Downrange Distance (km)', color=label_color)
            ax.set_xlabel('Time (s)', color=label_color)

        elif GraphType.HeightVsDistance == self.graph_type:
            ax.set_ylabel('Height (km)', color=label_color)
            ax.set_xlabel('Downrange Distance (km)', color=label_color)
        
        elif GraphType.PolarTrajectory == self.graph_type:
            # Polar Plot: Theta is downrange angle (radians), R is radius from Earth center
            # No specific labels usually, but we can title it
            pass

        else:
            ax.set_ylabel('Value', color=label_color)
            ax.set_xlabel('Time (s)', color=label_color)
        
        # Plot Data
        if self.x_axis and self.y_axis:
            # Convert units for nicer display (e.g. m -> km)
            x_data = list(self.x_axis)
            y_data = list(self.y_axis)

            # --- Data Scaling ---
            if self.graph_type in [GraphType.Altitude, GraphType.HeightVsDistance]:
                # Meters -> km for Y
                y_data = [y / 1000.0 for y in y_data]
                
            if self.graph_type in [GraphType.Velocity]:
                # m/s -> km/s
                y_data = [y / 1000.0 for y in y_data]
                
            if self.graph_type in [GraphType.Downrange, GraphType.HeightVsDistance]:
                 # Meters -> km for X (or Y for Downrange graph)
                 if self.graph_type == GraphType.Downrange:
                     y_data = [y / 1000.0 for y in y_data]
                 else:
                     x_data = [x / 1000.0 for x in x_data]

            if self.graph_type == GraphType.PolarTrajectory:
                # Needs [theta, r]
                # Theta: calculated from downrange / Earth Radius
                # R: Earth Radius + Altitude
                # We expect "x_axis" to be downrange distance (m) and "y_axis" to be altitude (m)
                # This needs special handling in update_data(), here assuming pre-processed or processing on fly
                EARTH_RADIUS = 6371000
                theta = [d / EARTH_RADIUS for d in self.x_axis] # radians
                r = [EARTH_RADIUS + alt for alt in self.y_axis]
                
                # For visualization, we might want to offset theta so launch is at 90 deg (Top) or 0 (Right)
                # Let's start at 90 degrees (pi/2) and rotate counter-clockwise (East)
                start_angle = math.pi / 2
                theta = [start_angle - t for t in theta] # Rotating "right" on the map
                
                # We also want to plot the Earth surface
                # Span the theta range of the flight + some buffer
                min_theta = min(theta)
                max_theta = max(theta)
                buffer = (max_theta - min_theta) * 0.2
                if buffer < math.radians(1): buffer = math.radians(1)
                
                theta_earth = [start_angle - (i * buffer*5 + min_theta - buffer) for i in range(100)] # simplified arc
                # BETTER: Just plot a full circle for earth surface reference but clip the view?
                # Plot full earth surface line
                theta_full = [i * (2*math.pi)/100 for i in range(101)]
                r_full = [EARTH_RADIUS for _ in range(101)]
                ax.plot(theta_full, r_full, color='#e67e22', linewidth=2, label="Earth Surface")
                
                # Plot Trajectory
                ax.plot(theta, r, color='#3498db', linewidth=2)
                
                # ZOOM IN TO THE FLIGHT
                # Set Radial limits to show just the atmosphere layer relevant to flight
                max_alt = max(self.y_axis)
                r_min = EARTH_RADIUS # Surface
                r_max = EARTH_RADIUS + max_alt * 1.2 # 20% headroom
                
                # If flight is very low (e.g. < 1km), ensure we have some minimal thickness
                if r_max - r_min < 1000: r_max = r_min + 1000
                
                ax.set_ylim(r_min, r_max)
                
                # Set Thetamin/max to focus on the sector?
                # Matplotlib polar plots are 360 by default. 
                # Restricting theta view in polar is tricky (set_thetamin/max).
                # Let's try to set the sector.
                # Convert radians to degrees for set_thetamin/max
                deg_min = math.degrees(min_theta)
                deg_max = math.degrees(max_theta)
                
                # Since we rotated: theta = 90 - original_theta
                # Launch is at 90. End is at 90 - flight_angle (e.g. 80).
                # So range is [80, 90].
                # We want thetamin ~ 75, thetamax ~ 95.
                
                margin_deg = (max_theta - min_theta) * 180 / math.pi * 0.5
                if margin_deg < 5: margin_deg = 5
                
                # Note: set_thetamin/max takes standard polar angles.
                # Our theta logic: 90 is top.
                
                start_deg = math.degrees(min(theta))
                end_deg = math.degrees(max(theta))
                
                ax.set_thetamin(start_deg - margin_deg)
                ax.set_thetamax(end_deg + margin_deg)
                
                # We need to set rlabel position to be visible
                ax.set_rlabel_position(start_deg - margin_deg/2)
                
            else:
                 ax.plot(x_data, y_data, linewidth=2, color='#3498db') # Standard Blue
        
        ax.set_title(self.graph_type.value, color='white', fontsize=12, fontweight='bold', pad=10)
        ax.set_facecolor(THEME['background_accent'])
        
        # Axis Colors
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        # Spines
        if self.graph_type != GraphType.PolarTrajectory:
             for spine in ax.spines.values():
                 spine.set_edgecolor('#555')
        else:
             ax.spines['polar'].set_edgecolor('#555')

        ax.grid(True, alpha=grid_alpha, color='#555')
        
        # Adjust layout to prevent label cutoff
        # Use subplots_adjust instead of tight_layout for more control, or use tight_layout with padding
        try:
             self.figure.tight_layout(pad=2.0)
        except:
             pass 
             
        # Connect Events
        self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.canvas.mpl_connect('button_press_event', self._on_button_press)
        self.canvas.mpl_connect('button_release_event', self._on_button_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)

    def _on_button_press(self, event):
        if event.inaxes is None or self.graph_type == GraphType.PolarTrajectory:
            return
        if event.button == 1:
            self._pan_start = (event.xdata, event.ydata, event.inaxes)
            try:
                self.canvas.setCursor(Qt.CursorShape.ClosedHandCursor)
            except: pass
    
    def _on_button_release(self, event):
        if event.button == 1 and self._pan_start is not None:
            self._pan_start = None
            try:
                self.canvas.setCursor(Qt.CursorShape.ArrowCursor)
            except: pass

    def _on_mouse_move(self, event):
        if self._pan_start is None or event.inaxes is None or self.graph_type == GraphType.PolarTrajectory:
            return
        if event.button != 1: return
            
        start_x, start_y, ax = self._pan_start
        dx = start_x - event.xdata
        dy = start_y - event.ydata
        
        x_left, x_right = ax.get_xlim()
        y_bottom, y_top = ax.get_ylim()
        
        ax.set_xlim(x_left + dx, x_right + dx)
        ax.set_ylim(y_bottom + dy, y_top + dy)
        self.canvas.draw_idle()

    def _on_scroll(self, event):
        if event.inaxes is None or self.graph_type == GraphType.PolarTrajectory: return
        ax = event.inaxes
        base_scale = 1.2
        
        # Determine scroll direction
        if hasattr(event, 'button') and event.button in ('up', 'down'):
             scale = 1.0 / base_scale if event.button == 'up' else base_scale
        else:
             step = getattr(event, 'step', 0)
             scale = 1.0 / base_scale if step > 0 else base_scale

        x_left, x_right = ax.get_xlim()
        y_bottom, y_top = ax.get_ylim()
        
        xdata, ydata = event.xdata, event.ydata
        if xdata is None or ydata is None: return

        new_width = (x_right - x_left) * scale
        new_height = (y_top - y_bottom) * scale

        relx = (xdata - x_left) / (x_right - x_left)
        rely = (ydata - y_bottom) / (y_top - y_bottom)

        ax.set_xlim(xdata - relx * new_width, (xdata - relx * new_width) + new_width)
        ax.set_ylim(ydata - rely * new_height, (ydata - rely * new_height) + new_height)
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
        self.canvas.setStyleSheet("background-color: #1e1e1e;")
        self.initUI()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
