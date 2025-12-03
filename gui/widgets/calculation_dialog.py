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
