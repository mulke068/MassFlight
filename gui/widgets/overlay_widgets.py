from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from config.app_config import THEME

class FloatingButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['button_active']};
                color: {THEME['text']};
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #555;
            }}
            QPushButton:hover {{
                background-color: {THEME['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {THEME['sidebar']};
            }}
        """)
        self.adjustSize()

class ResultsPanel(QFrame):
    close_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 30, 30, 220);
                border: 1px solid #555;
                border-radius: 8px;
                color: {THEME['text']};
            }}
            QLabel {{
                background-color: transparent;
                border: none;
            }}
            QLabel#Header {{
                font-weight: bold;
                font-size: 14px;
                border-bottom: 1px solid #555;
                padding-bottom: 5px;
            }}
        """)
        self.initUI()
        self.hide()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Header with Close Button
        header_layout = QHBoxLayout()
        title = QLabel("Flight Results")
        title.setObjectName("Header")
        header_layout.addWidget(title)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #aaa;
                border: none;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover { color: #fff; }
        """)
        close_btn.clicked.connect(self.close_panel)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Content
        self.content_label = QLabel()
        self.content_label.setTextFormat(Qt.RichText)
        layout.addWidget(self.content_label)
        
        self.setLayout(layout)
    
    def update_results(self, summary, inputs):
        """Updates the panel with simulation results."""
        text = (
            f"<b>Max Altitude:</b> {summary.get('max_altitude', 0):.1f} m<br>"
            f"<b>Total Distance:</b> {summary.get('total_distance', 0):.1f} m<br>"
            f"<b>Flight Time:</b> {summary.get('flight_time', 0):.1f} s<br>"
            f"<b>Impact Velocity:</b> {summary.get('impact_velocity', 0):.1f} m/s<br>"
            f"<hr>"
            f"<small><b>Inputs:</b><br>"
            f"Heading: {inputs.get('heading', 0):.1f}°, Angle: {inputs.get('climb_angle', 0):.1f}°<br>"
            f"Vel: {inputs.get('velocity', 0):.1f} m/s<br>"
            f"Mass: {inputs.get('projectile', {}).get('mass', 0)} kg</small>"
        )
        self.content_label.setText(text)
        self.adjustSize()
        self.show()

    def close_panel(self):
        self.hide()
        self.close_signal.emit()
