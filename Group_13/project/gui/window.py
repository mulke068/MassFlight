from gui.widgets.graph import GraphType
from PyQt6 import QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QFrame, QWidget, QMessageBox, QPushButton
from config.app_config import APP_NAME, ICON_FILE, WINDOW_HEIGHT, WINDOW_WIDTH, THEME
from .widgets import sphere as sphere
from .widgets import graph as graph
from .widgets import sidebar as sidebar
from .widgets.calculation_dialog import CalculationDialog
from .widgets.world_view import WorldViewContainer
from services.ballistic_manager import BallisticManager
from utils.coordinates import xyz_to_lonlat, calculate_bearing
import logging

LOG = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100,100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowIcon(QtGui.QIcon(ICON_FILE))
        self.pages = []
        self.setStyleSheet(f"QMainWindow {{ background-color: {THEME['background']}; }} QLabel {{ color: {THEME['text']}; }}")

        self.ballistic_manager = BallisticManager()

        self.initUI()

        LOG.info("Main window initialized")
    
    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.sidebar_area())
        main_layout.addWidget(self.content_area())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_widget.setLayout(main_layout)
        
        self.page_switch(0)
    
    def sidebar_area(self):
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(400)
        sidebar_frame.setStyleSheet(f"""QFrame {{ background-color: {THEME['sidebar']};border-right: 2px solid #333; }}""")
        
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 40, 20, 40)
        sidebar_layout.setSpacing(15)
        
        title = QLabel("MAIN MENU")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 0px;
                border-bottom: 2px solid #333;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(30)

        buttons_data = [
            ("World View", 0),
            ("Altitude", 1),
            ("Latitude", 2),
            ("Longitude", 3),
            ("Velocity", 4),
            ("Distance", 5),
            ("Gravity", 6)
        ]
        
        self.button_group = []
        for text, index in buttons_data:
            button = sidebar.SidebarButton(text)
            button.clicked.connect(lambda checked, idx=index: self.page_switch(idx))
            self.button_group.append(button)
            sidebar_layout.addWidget(button)

        sidebar_layout.addSpacing(20)
        
        # Instructions
        instructions = QLabel(
            "Controls:\n"
            "• Left drag: Rotate\n"
            "• Middle drag: Pan\n"
            "• Scroll: Zoom\n"
            "• Right click: Add pin\n"
            "• Space: Reset view\n"
            "• T: Toggle trajectory\n"
            "• C: Clear all pins\n"
            "• X: Clear latest pin"
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text_secondary']};
                font-size: 11px;
                padding: 15px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
            }}
        """)
        sidebar_layout.addWidget(instructions)
        sidebar_layout.addStretch()
        
        footer = QLabel("MassFlight © 2025")
        footer.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text_secondary']};
                font-size: 12px;
                padding: 10px;
                border-top: 1px solid #333;
            }}
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(footer)

        sidebar_frame.setLayout(sidebar_layout)
        return sidebar_frame

    def content_area(self):
        content_frame = QFrame()
        content_frame.setStyleSheet(f"QFrame {{ background-color: {THEME['background']}; }}")
        
        self.stacked_widget = QStackedWidget()
        
        # --- Page 0: World View with Overlay UI ---
        self.sphere_widget = sphere.SphereWidget()
        self.world_view_container = WorldViewContainer(self.sphere_widget)
        
        # Connect buttons from container
        self.world_view_container.calc_btn.clicked.connect(self.open_calculation_dialog)
        self.world_view_container.animate_btn.clicked.connect(self.run_animation)
        self.world_view_container.reset_btn.clicked.connect(self.reset_simulation)
        
        # --- Pages List ---
        self.pages = [
            self.world_view_container,
            graph.GraphWidget(graph_type=GraphType.Altitude),
            graph.GraphWidget(graph_type=GraphType.Latitude),
            graph.GraphWidget(graph_type=GraphType.Longitude),
            graph.GraphWidget(graph_type=GraphType.Velocity),
            graph.GraphWidget(graph_type=GraphType.Distance),
            graph.GraphWidget(graph_type=GraphType.Gravity)
        ]
        
        for page in self.pages:
            self.stacked_widget.addWidget(page)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.addWidget(self.stacked_widget)
        
        content_frame.setLayout(content_layout)
        
        return content_frame

    def run_animation(self):
        """Starts the trajectory animation on the sphere."""
        self.sphere_widget.start_animation()
        LOG.info("Animation started")

    def reset_simulation(self):
        """Clears the simulation results and resets the view."""
        self.sphere_widget.overlay.clear()
        self.sphere_widget.update()
        
        # Hide UI via container
        self.world_view_container.results_panel.hide()
        self.world_view_container.animate_btn.hide()
        self.world_view_container.reset_btn.hide()
        self.world_view_container.speed_label.hide()
        self.world_view_container.speed_slider.hide()
        
        # Clear graphs
        for i in range(1, 7):
            self.pages[i].update_data([])

    def page_switch(self, index):
        self.stacked_widget.setCurrentIndex(index)
        # mark buttons active/disabled appropriately instead of attempting
        # to construct a new SidebarButton (which requires a text arg)
        for idx, button in enumerate(self.button_group):
            try:
                button.set_active(idx == index)
            except Exception:
                # fallback: ignore if widget doesn't implement set_active
                pass

        LOG.info(f"Switched to page {index}")
    
    def open_calculation_dialog(self):
        """Opens the calculation dialog and handles the result."""
        dialog = CalculationDialog(self)
        
        # Pre-fill with Pin Data
        start_lat, start_lon, heading, target_lat, target_lon = self._get_values_from_pins()
        
        dialog.set_initial_values(lat=start_lat, lon=start_lon, heading=heading, 
                                  target_lat=target_lat, target_lon=target_lon)

        if dialog.exec():
            data = dialog.get_data()
            LOG.info(f"Starting calculation with: {data}")
            
            try:
                result = self.ballistic_manager.calculate_trajectory(
                    lat=data['lat'],
                    lon=data['lon'],
                    altitude=data['altitude'],
                    velocity=data['velocity'],
                    heading=data['heading'],
                    climb_angle=data['climb_angle'],
                    projectile_params=data['projectile']
                )
                
                self._update_visualization(result, data)

            except Exception as e:
                LOG.error(f"Calculation failed: {e}")
                QMessageBox.critical(self, "Error", f"Calculation failed: {str(e)}")

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Q:
            self.close()
        elif a0.key() == Qt.Key.Key_P:
            popup = QMessageBox(self)
            popup.setWindowTitle("Test")
            popup.setText("This is a test popup.")
            popup.exec()
        
        return super().keyPressEvent(a0)

    def closeEvent(self, a0):
        LOG.info("Application closing")
        a0.accept()
        return super().closeEvent(a0)

    def _get_values_from_pins(self):
        """Extracts initial values from map pins."""
        sphere_widget = self.sphere_widget
        pins = sphere_widget.overlay.pins
        LOG.info(f"Found {len(pins)} pins: {pins}")
        
        start_lat, start_lon, heading = None, None, None
        target_lat, target_lon = None, None
        
        if len(pins) >= 1:
            p1 = pins[0]
            start_lon, start_lat = xyz_to_lonlat(p1[0], p1[1], p1[2])
            LOG.info(f"Pin 1 (Start): Lat={start_lat}, Lon={start_lon}")
            
            if len(pins) >= 2:
                p2 = pins[1]
                target_lon, target_lat = xyz_to_lonlat(p2[0], p2[1], p2[2])
                LOG.info(f"Pin 2 (Target): Lat={target_lat}, Lon={target_lon}")
                
                heading = calculate_bearing(start_lat, start_lon, target_lat, target_lon)
                LOG.info(f"Calculated Heading: {heading}")
                
        return start_lat, start_lon, heading, target_lat, target_lon

    def _update_visualization(self, result, data):
        """Updates the visualization with simulation results."""
        # Update Sphere View
        viz_points = result['visualization_points']
        if viz_points:
            self.sphere_widget.overlay.set_trajectory_data(viz_points)
            
            # Show Results Panel & Buttons
            self.world_view_container.results_panel.update_results(result['summary'], data)
            self.world_view_container.animate_btn.show()
            self.world_view_container.reset_btn.show()
            self.world_view_container.speed_label.show()
            self.world_view_container.speed_slider.show()
            
            # Force layout update
            self.world_view_container.update_layout()
            
            # Update Graphs
            telemetry = result['telemetry']
            times = telemetry.get('time', [])
            altitudes = telemetry.get('altitude', [])
            
            self.pages[1].update_data(list(zip(times, altitudes)))
            self.pages[2].update_data(list(zip(times, telemetry.get('latitude', []))))
            self.pages[3].update_data(list(zip(times, telemetry.get('longitude', []))))
            self.pages[4].update_data(list(zip(times, telemetry.get('velocity', []))))
            self.pages[5].update_data(list(zip(times, telemetry.get('distance', []))))
            self.pages[6].update_data(list(zip(telemetry.get('latitude', []), telemetry.get('gravity', []))))