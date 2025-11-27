import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore
from vispy import scene
from vispy.geometry import create_sphere


class SphereWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.init_ui()
        
    def init_ui(self):
        """  Initialize the user interface  """
        self.setWindowTitle('VisPy Sphere in PyQt')
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Create VisPy canvas
        self.canvas = scene.SceneCanvas(keys='interactive', size=(800, 600))
        layout.addWidget(self.canvas.native)
        
        # Create 3D view
        self.view = self.canvas.central_widget.add_view()
        self.view.camera = 'turntable'
        self.view.camera.fov = 50
        
        # Create sphere
        self.create_sphere()
        
        # Add controls
        self.add_controls()
        
    def create_sphere(self):
        """Create and display a 3D sphere"""
        # Create sphere geometry - returns MeshData object
        sphere_mesh = create_sphere(radius=1.0, rows=20, cols=20)
        
        # Create mesh visual using the MeshData object
        mesh = scene.visuals.Mesh(meshdata=sphere_mesh, 
                                 color=(0.7, 0.7, 1.0, 1.0),
                                 shading='smooth')
        
        self.view.add(mesh)
        
        # Add coordinate axes for reference
        axes = scene.visuals.XYZAxis(parent=self.view.scene)
        
    def add_controls(self):
        """Add some basic controls"""
        control_widget = QtWidgets.QWidget()
        control_layout = QtWidgets.QHBoxLayout(control_widget)
        
        # Rotation speed slider
        rotation_label = QtWidgets.QLabel("Auto Rotation Speed:")
        control_layout.addWidget(rotation_label)
        
        self.rotation_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.rotation_slider.setRange(0, 100)
        self.rotation_slider.setValue(0)
        self.rotation_slider.valueChanged.connect(self.update_rotation)
        control_layout.addWidget(self.rotation_slider)
        
        # Reset view button
        reset_btn = QtWidgets.QPushButton("Reset View")
        reset_btn.clicked.connect(self.reset_view)
        control_layout.addWidget(reset_btn)
        
        # Add controls to main layout
        self.centralWidget().layout().addWidget(control_widget)
        
        # Timer for auto-rotation
        from PyQt5.QtCore import QTimer
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_camera)
        self.rotation_speed = 0
        
    def update_rotation(self, value):
        """Update rotation speed based on slider value"""
        self.rotation_speed = value / 1000.0  # Scale down for smoother rotation
        if value == 0:
            self.timer.stop()
        else:
            self.timer.start(16)  # ~60 FPS
            
    def rotate_camera(self):
        """Rotate camera automatically"""
        if hasattr(self.view.camera, '_transform'):
            self.view.camera._transform.rotate(1, (0, 1, 0))
            self.canvas.update()
            
    def reset_view(self):
        """Reset camera to initial position"""
        self.view.camera.set_range()
        self.canvas.update()


    def show_sphere():
        # Create Qt application
        app = QtWidgets.QApplication(sys.argv)
        
        # Create and show main window
        window = SphereWindow()
        window.show()
        
        # Start the event loop
        sys.exit(app.exec_())
