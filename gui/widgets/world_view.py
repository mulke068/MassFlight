from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .overlay_widgets import FloatingButton, ResultsPanel

from PyQt5.QtCore import QTimer

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
        
        self.results_panel = ResultsPanel(self)
        
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

        # Bottom Right: Results
        panel_w = self.results_panel.width()
        panel_h = self.results_panel.height()
        self.results_panel.move(w - panel_w - padding, h - panel_h - padding)
