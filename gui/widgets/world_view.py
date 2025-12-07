from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import Qt, QTimer
from .overlay_widgets import FloatingButton, ResultsPanel

class WorldViewContainer(QWidget):
    """Container for SphereWidget and floating UI elements."""
    def __init__(self, sphere_widget, parent=None):
        super().__init__(parent)
        self.sphere_widget = sphere_widget
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.sphere_widget)
        
        # Floating UI Elements
        self.calc_btn = FloatingButton("Calculate", self)
        self.animate_btn = FloatingButton("Animate", self)
        self.animate_btn.hide()
        self.reset_btn = FloatingButton("Reset", self)
        self.reset_btn.hide()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.speed_slider.hide()
        self.speed_label = QLabel("Speed: 1x", self)
        self.speed_label.hide()
        
        # Speed Slider
        self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(1)
        self.speed_slider.setFixedWidth(150)
        self.speed_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #333;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #3498db;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
        """)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        
        self.speed_label.setStyleSheet("color: white; font-weight: bold; background-color: rgba(0,0,0,0.5); padding: 4px; border-radius: 4px;")
        
        self.results_panel = ResultsPanel(self)
        
    def on_speed_changed(self, value):
        self.sphere_widget.set_animation_speed(value)
        self.speed_label.setText(f"Speed: {value}x")
        
    def resizeEvent(self, event):
        self.update_layout()
        super().resizeEvent(event)

    def showEvent(self, event):
        QTimer.singleShot(100, self.update_layout)
        super().showEvent(event)

    def update_layout(self):
        """Updates the positions of floating widgets."""
        w = self.width()
        h = self.height()
        padding = 20
        
        # Top Right: Calculate
        self.calc_btn.move(w - self.calc_btn.width() - padding, padding)
        
        # Below Calculate: Animate
        self.animate_btn.move(w - self.animate_btn.width() - padding, 
                              padding + self.calc_btn.height() + 10)
        
        # Below Animate: Reset
        self.reset_btn.move(w - self.reset_btn.width() - padding,
                            padding + self.calc_btn.height() + 10 + self.animate_btn.height() + 10)

        # Speed Slider (Bottom Left)
        self.speed_slider.move(padding, h - 40)
        self.speed_label.move(padding, h - 65)

        # Bottom Right: Results
        panel_w = self.results_panel.width()
        panel_h = self.results_panel.height()
        self.results_panel.move(w - panel_w - padding, h - panel_h - padding)
