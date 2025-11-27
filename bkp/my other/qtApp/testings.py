import math
from math import sqrt, sin, cos, atan2, asin, pi
import numpy as np
from typing import Tuple, List, Optional
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QMessageBox, QOpenGLWidget
import SphereWidget

class OrbitalCalculator:
    """
    Calculate orbital trajectories and velocities between positions on a sphere
    """
    
    def __init__(self, sphere_radius: float = 10.0, gravitational_parameter: float = 398600.4418):
        """
        Initialize the orbital calculator
        
        Args:
            sphere_radius: Radius of the sphere (default 10 for visualization)
            gravitational_parameter: GM for Earth in km³/s² (default) or scaled value
        """
        self.sphere_radius = sphere_radius
        self.GM = gravitational_parameter
        self.scale_factor = 0.001  # Adjusted for visualization scale
        
    def lonlat_to_xyz(self, lon: float, lat: float, altitude: float = 0.0) -> Tuple[float, float, float]:
        """
        Convert longitude/latitude to 3D Cartesian coordinates
        
        Args:
            lon: Longitude in degrees (-180 to 180)
            lat: Latitude in degrees (-90 to 90)
            altitude: Altitude above sphere surface
            
        Returns:
            (x, y, z) coordinates
        """
        # Convert to radians
        lon_rad = math.radians(lon)
        lat_rad = math.radians(lat)
        
        # Calculate coordinates
        r = self.sphere_radius + altitude
        x = r * cos(lat_rad) * cos(lon_rad)
        y = r * sin(lat_rad)
        z = r * cos(lat_rad) * sin(lon_rad)
        
        return (x, y, z)
    
    def xyz_to_lonlat(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """
        Convert 3D Cartesian coordinates to longitude/latitude/altitude
        
        Args:
            x, y, z: Cartesian coordinates
            
        Returns:
            (lon, lat, altitude) in degrees and units
        """
        radius = sqrt(x*x + y*y + z*z)
        
        if radius == 0:
            return 0, 0, -self.sphere_radius
        
        lat_rad = asin(y / radius)
        lon_rad = atan2(z, x)
        
        lon = math.degrees(lon_rad)
        lat = math.degrees(lat_rad)
        altitude = radius - self.sphere_radius
        
        return lon, lat, altitude
    
    def calculate_great_circle_distance(self, pos1: Tuple[float, float, float], 
                                     pos2: Tuple[float, float, float]) -> float:
        """
        Calculate great circle distance between two points on sphere
        
        Args:
            pos1: (lon1, lat1) or (x1, y1, z1)
            pos2: (lon2, lat2) or (x2, y2, z2)
            
        Returns:
            Distance in same units as sphere radius
        """
        if len(pos1) == 2:
            lon1, lat1 = pos1
            lon2, lat2 = pos2
            x1, y1, z1 = self.lonlat_to_xyz(lon1, lat1)
            x2, y2, z2 = self.lonlat_to_xyz(lon2, lat2)
        else:
            x1, y1, z1 = pos1
            x2, y2, z2 = pos2
        
        # Normalize vectors
        r1 = sqrt(x1*x1 + y1*y1 + z1*z1)
        r2 = sqrt(x2*x2 + y2*y2 + z2*z2)
        
        if r1 == 0 or r2 == 0:
            return 0
        
        # Dot product of normalized vectors
        dot_product = (x1*x2 + y1*y2 + z1*z2) / (r1 * r2)
        
        # Clamp to avoid floating point errors
        dot_product = max(-1.0, min(1.0, dot_product))
        
        # Central angle
        central_angle = math.acos(dot_product)
        
        # Arc length
        distance = self.sphere_radius * central_angle
        
        return distance
    
    def calculate_orbital_velocity(self, position: Tuple[float, float, float], 
                                 altitude: float = 0.0) -> float:
        """
        Calculate circular orbital velocity at given position
        
        Args:
            position: (x, y, z) or (lon, lat)
            altitude: Altitude above surface
            
        Returns:
            Orbital velocity magnitude
        """
        if len(position) == 2:
            lon, lat = position
            x, y, z = self.lonlat_to_xyz(lon, lat, altitude)
        else:
            x, y, z = position
            
        r = sqrt(x*x + y*y + z*z)
        
        if r == 0:
            return 0
            
        # Circular orbital velocity: v = sqrt(GM / r)
        velocity = sqrt(self.GM / r) * self.scale_factor
        
        return velocity
    
    def calculate_transfer_trajectory(self, start_pos: Tuple[float, float, float],
                                    target_pos: Tuple[float, float, float],
                                    altitude: float = 0.0) -> dict:
        """
        Calculate trajectory parameters for transferring between positions
        
        Args:
            start_pos: Starting position (lon, lat) or (x, y, z)
            target_pos: Target position (lon, lat) or (x, y, z)
            altitude: Orbital altitude
            
        Returns:
            Dictionary with trajectory parameters
        """
        # Convert to Cartesian if needed
        if len(start_pos) == 2:
            start_xyz = self.lonlat_to_xyz(start_pos[0], start_pos[1], altitude)
        else:
            start_xyz = start_pos
            
        if len(target_pos) == 2:
            target_xyz = self.lonlat_to_xyz(target_pos[0], target_pos[1], altitude)
        else:
            target_xyz = target_pos
        
        # Calculate distances
        r1 = sqrt(sum(x*x for x in start_xyz))
        r2 = sqrt(sum(x*x for x in target_xyz))
        
        if r1 == 0 or r2 == 0:
            return {"error": "Invalid positions"}
        
        # Angle between position vectors
        dot_product = sum(start_xyz[i] * target_xyz[i] for i in range(3))
        theta = math.acos(max(-1.0, min(1.0, dot_product / (r1 * r2))))
        
        # For visualization, use a simple elliptical transfer
        a_transfer = (r1 + r2) / 2
        
        # Velocity calculations
        v1_circular = sqrt(self.GM / r1) * self.scale_factor
        v1_transfer = sqrt(self.GM * (2/r1 - 1/a_transfer)) * self.scale_factor
        delta_v = abs(v1_transfer - v1_circular)
        
        # Transfer time (simplified)
        distance = self.calculate_great_circle_distance(start_xyz, target_xyz)
        transfer_time = distance / (v1_transfer * 0.5)  # Simplified time calculation
        
        # Calculate direction vector
        direction_vector = self.calculate_direction_vector(start_xyz, target_xyz)
        
        return {
            "start_position": start_xyz,
            "target_position": target_xyz,
            "required_velocity": delta_v,
            "transfer_time": transfer_time,
            "direction_vector": direction_vector,
            "distance": distance,
            "start_velocity": v1_circular,
            "transfer_velocity": v1_transfer
        }
    
    def calculate_direction_vector(self, start_pos: Tuple[float, float, float],
                                 target_pos: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """
        Calculate normalized direction vector from start to target
        
        Args:
            start_pos: Starting (x, y, z)
            target_pos: Target (x, y, z)
            
        Returns:
            Normalized direction vector (dx, dy, dz)
        """
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dz = target_pos[2] - start_pos[2]
        
        magnitude = sqrt(dx*dx + dy*dy + dz*dz)
        
        if magnitude == 0:
            return (0, 0, 0)
            
        return (dx/magnitude, dy/magnitude, dz/magnitude)
    
    def generate_trajectory_points(self, start_pos: Tuple[float, float, float],
                                 target_pos: Tuple[float, float, float],
                                 num_points: int = 50,
                                 altitude: float = 0.0) -> List[Tuple[float, float, float]]:
        """
        Generate points along the trajectory for visualization
        
        Args:
            start_pos: Starting position
            target_pos: Target position
            num_points: Number of points to generate
            altitude: Orbital altitude
            
        Returns:
            List of (x, y, z) points along trajectory
        """
        if len(start_pos) == 2:
            start_xyz = self.lonlat_to_xyz(start_pos[0], start_pos[1], altitude)
        else:
            start_xyz = start_pos
            
        if len(target_pos) == 2:
            target_xyz = self.lonlat_to_xyz(target_pos[0], target_pos[1], altitude)
        else:
            target_xyz = target_pos
        
        points = []
        
        # Generate points along a great circle arc
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Spherical interpolation (slerp)
            omega = math.acos(max(-1.0, min(1.0, 
                (start_xyz[0]*target_xyz[0] + start_xyz[1]*target_xyz[1] + start_xyz[2]*target_xyz[2]) / 
                (self.sphere_radius * self.sphere_radius))))
            
            if abs(omega) < 1e-10:
                points.append(start_xyz)
                continue
                
            a = math.sin((1 - t) * omega) / math.sin(omega)
            b = math.sin(t * omega) / math.sin(omega)
            
            x = a * start_xyz[0] + b * target_xyz[0]
            y = a * start_xyz[1] + b * target_xyz[1]
            z = a * start_xyz[2] + b * target_xyz[2]
            
            # Normalize to sphere surface
            length = sqrt(x*x + y*y + z*z)
            if length > 0:
                scale = self.sphere_radius / length
                x *= scale
                y *= scale
                z *= scale
            
            points.append((x, y, z))
        
        return points


class EnhancedSphereWidget(QWidget):
    """
    Enhanced version of SphereWidget with orbital calculation capabilities
    """
    
    trajectoryCalculated = pyqtSignal(dict)  # Signal when trajectory is calculated
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.orbital_calculator = OrbitalCalculator()
        
        # Position data
        self.start_position = None
        self.target_position = None
        self.current_trajectory = None
        
        # Create UI
        self.setup_ui()
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_trajectory)
        self.animation_index = 0
        
    def setup_ui(self):
        """Setup the user interface"""
        main_layout = QVBoxLayout()
        
        # Create sphere widget
        self.sphere_widget = SphereWidget.SphereWidget()
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Start position input
        start_layout = QVBoxLayout()
        start_layout.addWidget(QLabel("Start Position:"))
        self.start_lon_input = QLineEdit()
        self.start_lat_input = QLineEdit()
        start_layout.addWidget(QLabel("Longitude:"))
        start_layout.addWidget(self.start_lon_input)
        start_layout.addWidget(QLabel("Latitude:"))
        start_layout.addWidget(self.start_lat_input)
        
        # Target position input
        target_layout = QVBoxLayout()
        target_layout.addWidget(QLabel("Target Position:"))
        self.target_lon_input = QLineEdit()
        self.target_lat_input = QLineEdit()
        target_layout.addWidget(QLabel("Longitude:"))
        target_layout.addWidget(self.target_lon_input)
        target_layout.addWidget(QLabel("Latitude:"))
        target_layout.addWidget(self.target_lat_input)
        
        # Buttons
        button_layout = QVBoxLayout()
        self.calc_button = QPushButton("Calculate Trajectory")
        self.clear_button = QPushButton("Clear")
        self.animate_button = QPushButton("Animate")
        self.stop_button = QPushButton("Stop Animation")
        
        self.calc_button.clicked.connect(self.calculate_trajectory_from_input)
        self.clear_button.clicked.connect(self.clear_trajectory)
        self.animate_button.clicked.connect(self.start_animation)
        self.stop_button.clicked.connect(self.stop_animation)
        
        button_layout.addWidget(self.calc_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.animate_button)
        button_layout.addWidget(self.stop_button)
        
        # Info display
        self.info_label = QLabel("Set start and target positions to calculate trajectory")
        self.info_label.setWordWrap(True)
        
        # Add to control layout
        control_layout.addLayout(start_layout)
        control_layout.addLayout(target_layout)
        control_layout.addLayout(button_layout)
        
        # Add to main layout
        main_layout.addWidget(self.sphere_widget)
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.info_label)
        
        self.setLayout(main_layout)
        
        # Connect sphere widget signals
        self.sphere_widget.mousePressEvent = self.enhanced_mouse_press
        
    def enhanced_mouse_press(self, event):
        """Enhanced mouse press handler for position selection"""
        # Call original handler first
        super(SphereWidget, self.sphere_widget).mousePressEvent(event)
        
        # Get click position in widget coordinates
        pos = event.pos()
        
        # Convert to sphere coordinates (simplified - you'll need proper ray-sphere intersection)
        # For now, we'll use the input fields
        if event.button() == Qt.LeftButton:
            # Set as start position
            self.start_lon_input.setText("0")  # Placeholder
            self.start_lat_input.setText("0")  # Placeholder
        elif event.button() == Qt.RightButton:
            # Set as target position
            self.target_lon_input.setText("0")  # Placeholder
        
    def calculate_trajectory_from_input(self):
        """Calculate trajectory from user input"""
        try:
            # Get coordinates from input fields
            start_lon = float(self.start_lon_input.text())
            start_lat = float(self.start_lat_input.text())
            target_lon = float(self.target_lon_input.text())
            target_lat = float(self.target_lat_input.text())
            
            # Calculate trajectory
            self.calculate_trajectory((start_lon, start_lat), (target_lon, target_lat))
            
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric coordinates")
    
    def calculate_trajectory(self, start_pos: Tuple[float, float], target_pos: Tuple[float, float]):
        """Calculate trajectory between start and target positions"""
        # Calculate trajectory data
        trajectory_data = self.orbital_calculator.calculate_transfer_trajectory(start_pos, target_pos)
        
        if "error" in trajectory_data:
            QMessageBox.warning(self, "Calculation Error", trajectory_data["error"])
            return
        
        # Generate visualization points
        trajectory_points = self.orbital_calculator.generate_trajectory_points(start_pos, target_pos)
        
        # Update sphere widget
        self.sphere_widget.trajectory_points = trajectory_points
        
        # Add pins for start and target positions
        start_xyz = trajectory_data["start_position"]
        target_xyz = trajectory_data["target_position"]
        self.sphere_widget.pins = [start_xyz, target_xyz]
        
        # Store current trajectory
        self.current_trajectory = trajectory_data
        
        # Update info display
        self.update_trajectory_info(trajectory_data)
        
        # Emit signal
        self.trajectoryCalculated.emit(trajectory_data)
        
        # Refresh display
        self.sphere_widget.update()
    
    def update_trajectory_info(self, trajectory_data: dict):
        """Update the information display with trajectory data"""
        info_text = f"""
        <b>Trajectory Calculation Results:</b><br>
        Distance: {trajectory_data['distance']:.2f} units<br>
        Required Delta-V: {trajectory_data['required_velocity']:.4f} units/s<br>
        Transfer Time: {trajectory_data['transfer_time']:.2f} seconds<br>
        Start Velocity: {trajectory_data['start_velocity']:.4f} units/s<br>
        Transfer Velocity: {trajectory_data['transfer_velocity']:.4f} units/s<br>
        Direction: {trajectory_data['direction_vector']}
        """
        self.info_label.setText(info_text)
    
    def clear_trajectory(self):
        """Clear current trajectory"""
        self.sphere_widget.trajectory_points = []
        self.sphere_widget.pins = []
        self.current_trajectory = None
        self.info_label.setText("Trajectory cleared")
        self.sphere_widget.update()
    
    def start_animation(self):
        """Start trajectory animation"""
        if not self.sphere_widget.trajectory_points:
            QMessageBox.warning(self, "Animation Error", "No trajectory to animate")
            return
        
        self.animation_index = 0
        self.animation_timer.start(100)  # Update every 100ms
    
    def stop_animation(self):
        """Stop trajectory animation"""
        self.animation_timer.stop()
    
    def animate_trajectory(self):
        """Animate the trajectory point by point"""
        if self.animation_index < len(self.sphere_widget.trajectory_points):
            # Show partial trajectory up to current index
            partial_trajectory = self.sphere_widget.trajectory_points[:self.animation_index + 1]
            self.sphere_widget.trajectory_points = partial_trajectory
            self.animation_index += 1
            self.sphere_widget.update()
        else:
            self.stop_animation()


# Example usage and standalone application
class OrbitalVisualizationApp(QWidget):
    """Standalone application for orbital visualization"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Orbital Trajectory Calculator")
        self.setGeometry(100, 100, 1000, 800)
        
        layout = QVBoxLayout()
        
        # Create enhanced sphere widget
        self.enhanced_widget = EnhancedSphereWidget()
        
        # Connect signals
        self.enhanced_widget.trajectoryCalculated.connect(self.on_trajectory_calculated)
        
        layout.addWidget(self.enhanced_widget)
        self.setLayout(layout)
    
    def on_trajectory_calculated(self, trajectory_data):
        """Handle trajectory calculation completion"""
        print("Trajectory calculated:")
        print(f"  Distance: {trajectory_data['distance']:.2f}")
        print(f"  Delta-V: {trajectory_data['required_velocity']:.4f}")
        print(f"  Time: {trajectory_data['transfer_time']:.2f}")


# Example usage function
def example_calculation():
    """Demonstrate orbital calculations"""
    calculator = OrbitalCalculator()
    
    # Example: New York to Tokyo
    new_york = (-74.0060, 40.7128)
    tokyo = (139.6503, 35.6762)
    
    trajectory = calculator.calculate_transfer_trajectory(new_york, tokyo)
    
    print("Orbital Trajectory Calculation Example")
    print("=" * 50)
    print(f"New York to Tokyo:")
    print(f"  Distance: {trajectory['distance']:.2f} units")
    print(f"  Required Delta-V: {trajectory['required_velocity']:.6f} units/s")
    print(f"  Transfer Time: {trajectory['transfer_time']:.2f} seconds")
    print(f"  Start Velocity: {trajectory['start_velocity']:.6f} units/s")
    print(f"  Transfer Velocity: {trajectory['transfer_velocity']:.6f} units/s")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    # Run example calculation
    example_calculation()
    
    # Launch GUI application
    app = QApplication(sys.argv)
    
    # You can choose to run either the enhanced widget alone or the full app
    window = OrbitalVisualizationApp()
    window.show()
    
    # Or use just the enhanced widget:
    # widget = EnhancedSphereWidget()
    # widget.show()
    
    sys.exit(app.exec_())