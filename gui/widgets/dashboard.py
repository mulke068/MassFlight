from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QScrollArea
from .graph import GraphWidget, GraphType

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Main Layout is a VBox containing the ScrollArea
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Container Widget inside Scroll Area
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        
        # Grid Layout for Graphs
        self.layout = QGridLayout(container)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # --- Create Graphs ---
        # "Graphs that really matter": Altitude, Polar (Trajectory), Velocity, Distance
        
        # Row 0: Primary Visuals
        self.graph_alt = GraphWidget(GraphType.Altitude)
        self.graph_polar = GraphWidget(GraphType.PolarTrajectory)
        
        # Row 1: Key Telemetry
        self.graph_vel = GraphWidget(GraphType.Velocity)
        self.graph_dist = GraphWidget(GraphType.Downrange)
        
        # Row 2: Detailed Analysis (The "Nice to have when scrolling down")
        self.graph_fpa = GraphWidget(GraphType.FlightPathAngle)
        self.graph_hvd = GraphWidget(GraphType.HeightVsDistance)
        
        graphs = [
            (self.graph_alt, 0, 0), (self.graph_polar, 0, 1),
            (self.graph_vel, 1, 0), (self.graph_dist, 1, 1),
            (self.graph_fpa, 2, 0), (self.graph_hvd, 2, 1)
        ]
        
        for graph, r, c in graphs:
            graph.setMinimumHeight(400) # Make them tall and nice
            self.layout.addWidget(graph, r, c)
            
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def update_data(self, telemetry_data):
        """Updates all graphs with new telemetry data."""
        if not telemetry_data:
            self.graph_alt.update_data([])
            self.graph_polar.update_data([])
            self.graph_dist.update_data([])
            self.graph_vel.update_data([])
            self.graph_fpa.update_data([])
            self.graph_hvd.update_data([])
            return

        times = telemetry_data.get('time', [])
        alts = telemetry_data.get('altitude', [])
        dists = telemetry_data.get('distance', [])
        vels = telemetry_data.get('velocity', [])
        fpas = telemetry_data.get('flight_path_angle', [])
        
        # 1. Altitude vs Time
        self.graph_alt.update_data(list(zip(times, alts)))
        
        # 2. Polar Trajectory (Downrange vs Altitude)
        self.graph_polar.update_data(list(zip(dists, alts)))
        
        # 3. Velocity vs Time
        self.graph_vel.update_data(list(zip(times, vels)))
        
        # 4. Downrange vs Time
        self.graph_dist.update_data(list(zip(times, dists)))
        
        # 5. Flight Path Angle vs Time
        self.graph_fpa.update_data(list(zip(times, fpas)))
        
        # 6. Height vs Downrange
        self.graph_hvd.update_data(list(zip(dists, alts)))
