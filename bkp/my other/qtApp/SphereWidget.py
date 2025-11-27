


from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import os
from math import cos, pi, sin
import numpy as np

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
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Load textures
        self.load_textures()
        
        # Create sphere
        self.create_sphere_display_list()
        
    def load_textures(self):
        try:
            # Load Earth texture (path relative to this file)
            earth_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'earth.jpg'))
            img = Image.open(earth_path)
            img_data = np.array(img.convert('RGB'), dtype=np.uint8)
            
            self.earth_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.earth_texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height,
                        0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
            print("Earth texture loaded successfully")
        except Exception as e:
            print(f"Error loading earth.jpg from {earth_path}: {e}")
            self.earth_texture = None
            
        try:
            # Load background texture (path relative to this file)
            stars_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'stars.jpg'))
            bg_img = Image.open(stars_path)
            bg_data = np.array(bg_img.convert('RGB'), dtype=np.uint8)
            
            self.bg_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.bg_texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, bg_img.width, bg_img.height,
                        0, GL_RGB, GL_UNSIGNED_BYTE, bg_data)
            print("Background texture loaded successfully")
        except Exception as e:
            print(f"Error loading stars.jpg from {stars_path}: {e}")
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

