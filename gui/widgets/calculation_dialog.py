"""Dialog for ballistic calculation parameters."""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFormLayout, QGroupBox, 
                             QComboBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from config.app_config import THEME

class CalculationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ballistic Calculation Settings")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {THEME['background']}; color: {THEME['text']}; }}
            QLabel {{ color: {THEME['text']}; }}
            QGroupBox {{ color: {THEME['text']}; font-weight: bold; border: 1px solid #555; margin-top: 10px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }}
            QLineEdit, QDoubleSpinBox {{ 
                background-color: {THEME['input_bg'] if 'input_bg' in THEME else '#333'}; 
                color: {THEME['text']}; 
                border: 1px solid #555; 
                padding: 5px; 
            }}
            QPushButton {{
                background-color: {THEME['button_normal']};
                color: {THEME['text']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: {THEME['button_hover']}; }}
        """)
        
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # --- Launch Parameters ---
        launch_group = QGroupBox("Launch Parameters")
        launch_layout = QFormLayout()
        
        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90, 90)
        self.lat_input.setDecimals(6)
        self.lat_input.setValue(49.815) # Default
        
        self.lon_input = QDoubleSpinBox()
        self.lon_input.setRange(-180, 180)
        self.lon_input.setDecimals(6)
        self.lon_input.setValue(6.131) # Default
        
        self.alt_input = QDoubleSpinBox()
        self.alt_input.setRange(0, 100000)
        self.alt_input.setValue(300) # Default
        self.alt_input.setSuffix(" m")
        
        self.vel_input = QDoubleSpinBox()
        self.vel_input.setRange(0, 5000)
        self.vel_input.setValue(800)
        self.vel_input.setSuffix(" m/s")
        
        self.heading_input = QDoubleSpinBox()
        self.heading_input.setRange(0, 360)
        self.heading_input.setValue(0)
        self.heading_input.setSuffix(" °")
        
        self.climb_input = QDoubleSpinBox()
        self.climb_input.setRange(0, 90)
        self.climb_input.setValue(45)
        self.climb_input.setSuffix(" °")
        
        launch_layout.addRow("Latitude:", self.lat_input)
        launch_layout.addRow("Longitude:", self.lon_input)
        launch_layout.addRow("Altitude:", self.alt_input)
        launch_layout.addRow("Velocity:", self.vel_input)
        launch_layout.addRow("Heading:", self.heading_input)
        launch_layout.addRow("Climb Angle:", self.climb_input)
        launch_group.setLayout(launch_layout)
        layout.addWidget(launch_group)

        # --- Target Parameters (Optional) ---
        target_group = QGroupBox("Target Location (Optional)")
        target_layout = QFormLayout()
        
        self.target_lat_input = QDoubleSpinBox()
        self.target_lat_input.setRange(-90, 90)
        self.target_lat_input.setDecimals(6)
        self.target_lat_input.setSpecialValueText("None")
        self.target_lat_input.setValue(0) # Default None-ish
        
        self.target_lon_input = QDoubleSpinBox()
        self.target_lon_input.setRange(-180, 180)
        self.target_lon_input.setDecimals(6)
        self.target_lon_input.setSpecialValueText("None")
        self.target_lon_input.setValue(0)
        
        target_layout.addRow("Target Latitude:", self.target_lat_input)
        target_layout.addRow("Target Longitude:", self.target_lon_input)
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # Connect signals to auto-update heading if target changes
        self.target_lat_input.valueChanged.connect(self.update_heading_from_target)
        self.target_lon_input.valueChanged.connect(self.update_heading_from_target)
        self.lat_input.valueChanged.connect(self.update_heading_from_target)
        self.lon_input.valueChanged.connect(self.update_heading_from_target)
        
        # --- Projectile Parameters ---
        proj_group = QGroupBox("Projectile Parameters")
        proj_layout = QFormLayout()
        
        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(0.1, 10000)
        self.mass_input.setValue(100.0)
        self.mass_input.setSuffix(" kg")
        
        self.cal_input = QDoubleSpinBox()
        self.cal_input.setRange(0.001, 1.0)
        self.cal_input.setDecimals(3)
        self.cal_input.setValue(0.155)
        self.cal_input.setSuffix(" m")
        
        self.bc_input = QDoubleSpinBox()
        self.bc_input.setRange(0.01, 10.0)
        self.bc_input.setValue(0.5)
        
        proj_layout.addRow("Mass:", self.mass_input)
        proj_layout.addRow("Caliber:", self.cal_input)
        proj_layout.addRow("Ballistic Coeff:", self.bc_input)
        proj_group.setLayout(proj_layout)
        layout.addWidget(proj_group)
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.calc_btn = QPushButton("Calculate")
        self.calc_btn.clicked.connect(self.accept)
        self.calc_btn.setStyleSheet(f"background-color: {THEME['button_active']}; font-weight: bold;")
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.calc_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def set_initial_values(self, lat=None, lon=None, heading=None, target_lat=None, target_lon=None):
        """Pre-fills the dialog with provided values."""
        if lat is not None:
            self.lat_input.setValue(lat)
        if lon is not None:
            self.lon_input.setValue(lon)
        if heading is not None:
            self.heading_input.setValue(heading)
        if target_lat is not None:
            self.target_lat_input.setValue(target_lat)
        if target_lon is not None:
            self.target_lon_input.setValue(target_lon)

        # Target Logic
        if target_lat is not None and target_lon is not None:
            # Lock Heading
            self.heading_input.setReadOnly(True)
            self.heading_input.setStyleSheet("background-color: #222; color: #888;")
            self.heading_input.setToolTip("Locked to Target Bearing")
            
            # Calculate Distance for Velocity Estimation
            try:
                from gui.engine.coordinates import calculate_distance
                dist_km = calculate_distance(lat, lon, target_lat, target_lon)
                dist_m = dist_km * 1000.0
                
                # Vacuum approximation for 45 degree launch: Range = v^2 / g
                # v = sqrt(Range * g)
                import math
                g = 9.81
                v_est = math.sqrt(dist_m * g)
                
                # Apply a rough drag factor (e.g. 1.3x) since vacuum is too optimistic
                v_est *= 1.3 
                
                self.vel_input.setValue(v_est)
                self.climb_input.setValue(45.0)
                
                # Add a label or feedback
                self.setWindowTitle("Ballistic Calculation - TARGET MODE")
                
            except Exception as e:
                print(f"Error estimating velocity: {e}")
        else:
             self.heading_input.setReadOnly(False)
             self.heading_input.setStyleSheet("")
             self.setWindowTitle("Ballistic Calculation Settings")

    def update_heading_from_target(self):
        """Calculates heading if target is set."""
        # Simple check: if target is 0,0 (default), ignore
        t_lat = self.target_lat_input.value()
        t_lon = self.target_lon_input.value()
        
        if t_lat == 0 and t_lon == 0:
            return

        s_lat = self.lat_input.value()
        s_lon = self.lon_input.value()
        
        try:
            from gui.engine.coordinates import calculate_bearing
            heading = calculate_bearing(s_lat, s_lon, t_lat, t_lon)
            self.heading_input.setValue(heading)
        except ImportError:
            pass # Should not happen if coordinates.py is fixed

    def get_data(self):
        """Returns a dictionary of all input values."""
        return {
            "lat": self.lat_input.value(),
            "lon": self.lon_input.value(),
            "altitude": self.alt_input.value(),
            "velocity": self.vel_input.value(),
            "heading": self.heading_input.value(),
            "climb_angle": self.climb_input.value(),
            "projectile": {
                "mass": self.mass_input.value(),
                "caliber": self.cal_input.value(),
                "bc": self.bc_input.value()
            }
        }
