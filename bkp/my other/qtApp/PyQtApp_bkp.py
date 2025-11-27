import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QStackedWidget, QLabel,
                             QFrame, QOpenGLWidget)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QSurfaceFormat
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# OpenGL imports
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np
from math import asin, atan2, cos, pi, sin, sqrt
import logging

LOG = logging.getLogger(__name__)


class SphereWidget(QOpenGLWidget):
    """OpenGL widget for rendering the 3D sphere"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        
        # Camera settings
        self.zoom_distance = -20
        self.rotation_x = -100
        self.rotation_y = 40
        self.panning_x = 0
        self.panning_y = 0
        
        # Sphere settings
        self.SPHERE_RADIUS = 10
        self.SPHERE_RESOLUTION = 100
        
        # Data
        self.pins = []
        self.trajectory_points = []
        
        # Mouse tracking
        self.last_mouse_pos = None
        
        # Textures
        self.earth_texture = None
        self.bg_texture = None
        
    def initializeGL(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Load textures
        self.load_textures()
        
        # Create sphere
        self.create_sphere_display_list()
        
    def load_textures(self):
        """Load Earth and background textures"""
        try:
            # Load Earth texture
            img = Image.open('earth.jpg')
            img_data = np.array(img.convert('RGB'), dtype=np.uint8)
            
            self.earth_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.earth_texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height,
                        0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            LOG.info("Earth texture loaded successfully")
        except Exception as e:
            LOG.error(f"Error loading earth.jpg: {e}")
            self.earth_texture = None
            
        try:
            # Load background texture
            bg_img = Image.open('stars.jpg')
            bg_data = np.array(bg_img.convert('RGB'), dtype=np.uint8)
            
            self.bg_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.bg_texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, bg_img.width, bg_img.height,
                        0, GL_RGB, GL_UNSIGNED_BYTE, bg_data)
            LOG.info("Background texture loaded successfully")
        except Exception as e:
            LOG.error(f"Error loading stars.jpg: {e}")
            self.bg_texture = None
    
    def create_sphere_display_list(self):
        """Create a display list for the sphere"""
        self.sphere_list = glGenLists(1)
        glNewList(self.sphere_list, GL_COMPILE)
        
        resolution = self.SPHERE_RESOLUTION
        radius = self.SPHERE_RADIUS
        
        for i in range(resolution):
            glBegin(GL_TRIANGLE_STRIP)
            for j in range(resolution + 1):
                for k in range(2):
                    lat = pi * (-0.5 + float(i + k) / resolution)
                    lon = 2 * pi * float(j) / resolution
                    
                    x = radius * cos(lat) * cos(lon)
                    y = radius * sin(lat)
                    z = radius * cos(lat) * sin(lon)
                    
                    u = float(j) / resolution
                    v = float(i + k) / resolution
                    
                    glTexCoord2f(-u, v)
                    glVertex3f(x, y, z)
            glEnd()
        
        glEndList()
    
    def resizeGL(self, w, h):
        """Handle window resize"""
        glViewport(0, 0, w, h)
        
    def paintGL(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw background
        self.draw_background()
        
        # Setup 3D projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width() / self.height() if self.height() != 0 else 1
        gluPerspective(60, aspect, 0.1, 100)
        
        # Setup model view
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom_distance)
        glTranslatef(self.panning_x, self.panning_y, 0)
        glRotatef(self.rotation_y, 1, 0, 0)
        glRotatef(self.rotation_x, 0, 1, 0)
        
        # Draw sphere
        if self.earth_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.earth_texture)
        
        glColor3f(1, 1, 1)
        glCallList(self.sphere_list)
        
        glDisable(GL_TEXTURE_2D)
        
        # Draw pins
        self.draw_pins()
        
        # Draw trajectory
        self.draw_trajectory()
    
    def draw_background(self):
        """Draw background texture"""
        if not self.bg_texture:
            return
            
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width(), 0, self.height(), -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.bg_texture)
        
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(0, 0)
        glTexCoord2f(1, 0)
        glVertex2f(self.width(), 0)
        glTexCoord2f(1, 1)
        glVertex2f(self.width(), self.height())
        glTexCoord2f(0, 1)
        glVertex2f(0, self.height())
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
    
    def draw_pins(self):
        """Draw location pins"""
        if not self.pins:
            return
            
        glPointSize(10)
        glColor3f(1, 0, 0)
        glBegin(GL_POINTS)
        for pin in self.pins:
            glVertex3f(pin[0], pin[1], pin[2])
        glEnd()
    
    def draw_trajectory(self):
        """Draw trajectory line"""
        if not self.trajectory_points:
            return
            
        glLineWidth(5)
        glColor3f(1, 1, 1)
        glBegin(GL_LINE_STRIP)
        for point in self.trajectory_points:
            glVertex3f(point[0], point[1], point[2])
        glEnd()
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse drag"""
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
            
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        
        if event.buttons() & Qt.LeftButton:
            self.rotation_x += dx * 0.5
            self.rotation_y -= dy * 0.5
            self.rotation_y = max(-90, min(90, self.rotation_y))
        elif event.buttons() & Qt.RightButton:
            self.panning_x += dx * 0.05
            self.panning_y -= dy * 0.05
        
        self.last_mouse_pos = event.pos()
        self.update()
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y() / 120
        new_zoom = self.zoom_distance + delta * 1.5
        if new_zoom < -(self.SPHERE_RADIUS + 0.5):
            self.zoom_distance = new_zoom
        self.update()


class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.normal_color = "#2d3848"
        self.hover_color = "#3f4e63"
        self.active_color = "#56687e"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.normal_color};
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {self.hover_color};
            }}
            QPushButton:pressed {{
                background-color: {self.active_color};
            }}
        """)


class GraphWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.figure = Figure(facecolor='#1e1e1e')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1e1e1e;")
        self.create_plot()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def create_plot(self):
        ax = self.figure.add_subplot(111)
        
        if "Altitude" in self.title:
            time_seconds = [0, 1, 2, 3]
            values = [150, 220, 180, 300]
            color = '#4ecdc4'
            ax.set_ylabel('Meters (m)', color='white')
        elif "Latitude" in self.title:
            time_seconds = [0, 1, 2, 3, 4, 5, 6]
            values = [1200, 1400, 1300, 1600, 1500, 1700, 1900]
            color = '#45b7d1'
            ax.set_ylabel('Meters (m)', color='white')
        elif "Velocity" in self.title:
            time_seconds = [0, 1, 2, 3]
            values = [85, 92, 78, 96]
            color = '#96ceb4'
            ax.set_ylabel('Velocity (m/s)', color='white')
        else:
            time_seconds = []
            values = []
            color = '#ffffff'
        
        ax.plot(time_seconds, values, marker='o', linewidth=3, markersize=8, color=color)
        ax.set_facecolor('#2d2d2d')
        ax.set_xlabel('Time (s)', color='white')
        ax.set_title(self.title, color='white', fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MassFlight")
        self.setGeometry(100, 100, 1400, 800)
        self.current_active_button = None
        self.set_theme()
        self.initUI()
        
    def set_theme(self):
        self.setStyleSheet("QMainWindow { background-color: #1a1a1a; } QLabel { color: white; }")
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area)
        
        central_widget.setLayout(main_layout)
        
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(400)
        sidebar.setStyleSheet("QFrame { background-color: #252525; border-right: 2px solid #333; }")
        
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
        title.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(title)
        sidebar_layout.addSpacing(30)
        
        buttons_data = [
            ("World View", 0),
            ("Altitude", 1),
            ("Latitude", 2),
            ("Velocity", 3)
        ]
        
        self.buttons = []
        for text, index in buttons_data:
            btn = SidebarButton(text)
            btn.clicked.connect(lambda checked, idx=index: self.switch_page(idx))
            self.buttons.append(btn)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        footer = QLabel("Data Analytics v1.0")
        footer.setStyleSheet("QLabel { color: #666; font-size: 12px; padding: 10px; border-top: 1px solid #333; }")
        footer.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(footer)
        
        sidebar.setLayout(sidebar_layout)
        return sidebar
        
    def create_content_area(self):
        content_frame = QFrame()
        content_frame.setStyleSheet("QFrame { background-color: #1e1e1e; }")
        
        self.stacked_widget = QStackedWidget()
        
        # Create pages - World View now uses SphereWidget
        self.pages = [
            SphereWidget(),  # World View with 3D sphere
            GraphWidget("Altitude Over Time"),
            GraphWidget("Latitude Changes"),
            GraphWidget("Velocity Trends")
        ]
        
        for page in self.pages:
            self.stacked_widget.addWidget(page)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(self.stacked_widget)
        
        content_frame.setLayout(layout)
        return content_frame
        
    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # Reset all buttons to normal state
        for btn in self.buttons:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn.normal_color};
                    color: white;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                    font-weight: bold;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {btn.hover_color};
                }}
                QPushButton:pressed {{
                    background-color: {btn.active_color};
                }}
            """)
        
        # Set active state for clicked button
        active_btn = self.buttons[index]
        active_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {active_btn.active_color};
                color: white;
                border: none;
                padding: 15px;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                border-left: 4px solid #4ecdc4;
            }}
            QPushButton:hover {{
                background-color: {active_btn.active_color};
            }}
        """)


def main():
    # Only show warnings and errors, not debug messages
    logging.basicConfig(
        level=logging.WARNING,  # Changed from DEBUG to WARNING
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    # Optionally, make matplotlib even quieter
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()