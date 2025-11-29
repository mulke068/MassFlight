import logging
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *

from config.app_config import (SPHERE_RADIUS, SPHERE_RESOLUTION, 
                               EARTH_TEXTURE, STARS_TEXTURE,
                               PIN_COLOR, TRAJECTORY_COLOR, ANIMATION_INTERVAL)
from src.engine.camera import Camera
from src.engine.sphere import create_sphere_display_list
from src.engine.texture_manager import TextureManager
from src.models.coordinates import ray_sphere_intersection, xyz_to_lonlat
from src.models.trajectory import Trajectory, SAMPLE_TRAJECTORY
from src.utils.math_helpers import normalize_vector

logger = logging.getLogger(__name__)


class SphereWidget(QOpenGLWidget):
    """OpenGL widget for rendering 3D Earth sphere with trajectory"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        
        # Components
        self.camera = Camera()
        self.texture_manager = TextureManager()
        self.trajectory = Trajectory()
        
        # Sphere
        self.sphere_list = None
        
        # Data
        self.pins = []
        
        # Mouse tracking
        self.last_mouse_pos = None
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        
        # Load sample trajectory
        self.trajectory.set_full_trajectory(SAMPLE_TRAJECTORY)
    
    def initializeGL(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        # Load textures
        self.texture_manager.load_texture('earth', EARTH_TEXTURE)
        self.texture_manager.load_texture('stars', STARS_TEXTURE)
        
        # Create sphere display list
        self.sphere_list = create_sphere_display_list(SPHERE_RADIUS, SPHERE_RESOLUTION)
        
        logger.info("OpenGL initialized successfully")
    
    def resizeGL(self, w, h):
        """Handle window resize"""
        glViewport(0, 0, w, h)
    
    def paintGL(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Draw background
        self._draw_background()
        
        # Setup 3D projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width() / self.height() if self.height() != 0 else 1
        gluPerspective(60, aspect, 0.1, 100)
        
        # Setup model view with camera transforms
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        params = self.camera.get_view_params()
        glTranslatef(0, 0, params['zoom'])
        glTranslatef(params['pan_x'], params['pan_y'], 0)
        glRotatef(params['rotation_y'], 1, 0, 0)
        glRotatef(params['rotation_x'], 0, 1, 0)
        
        # Draw sphere
        if self.texture_manager.has_texture('earth'):
            glEnable(GL_TEXTURE_2D)
            self.texture_manager.bind_texture('earth')
        
        glColor3f(1, 1, 1)
        if self.sphere_list:
            glCallList(self.sphere_list)
        
        glDisable(GL_TEXTURE_2D)
        
        # Draw overlays
        self._draw_pins()
        self._draw_trajectory()
    
    def _draw_background(self):
        """Draw background texture in 2D"""
        if not self.texture_manager.has_texture('stars'):
            return
        
        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width(), 0, self.height(), -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        self.texture_manager.bind_texture('stars')
        
        # Draw fullscreen quad
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
    
    def _draw_pins(self):
        """Draw location pins as points"""
        if not self.pins:
            return
        
        glPointSize(10)
        glColor3f(*PIN_COLOR)
        glBegin(GL_POINTS)
        for pin in self.pins:
            glVertex3f(pin[0], pin[1], pin[2])
        glEnd()
    
    def _draw_trajectory(self):
        """Draw trajectory path as line strip"""
        points = self.trajectory.get_points()
        if not points:
            return
        
        glLineWidth(5)
        glColor3f(*TRAJECTORY_COLOR)
        glBegin(GL_LINE_STRIP)
        for point in points:
            glVertex3f(point[0], point[1], point[2])
        glEnd()
    
    def _update_animation(self):
        """Update trajectory animation"""
        if self.trajectory.update():
            self.update()  # Trigger repaint
        else:
            self.animation_timer.stop()
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        self.last_mouse_pos = event.pos()
        
        # Middle mouse button - add pin
        if event.button() == Qt.MiddleButton:
            self._add_pin_at_cursor(event.x(), event.y())
    
    def mouseMoveEvent(self, event):
        """Handle mouse drag"""
        if self.last_mouse_pos is None:
            self.last_mouse_pos = event.pos()
            return
        
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        
        if event.buttons() & Qt.LeftButton:
            self.camera.rotate(dx, dy)
        elif event.buttons() & Qt.RightButton:
            self.camera.pan(dx, dy)
        
        self.last_mouse_pos = event.pos()
        self.update()
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zoom"""
        delta = event.angleDelta().y()
        self.camera.handle_scroll(delta / 120)
        self.update()
    
    def keyPressEvent(self, event):
        """Handle keyboard input"""
        if event.key() == Qt.Key_Space:
            self.reset_view()
        elif event.key() == Qt.Key_T:
            self.toggle_trajectory_animation()
        elif event.key() == Qt.Key_C:
            self.clear_pins()
    
    def _add_pin_at_cursor(self, x, y):
        """Add a pin at cursor position by raycasting"""
        try:
            # Get current matrices
            model_matrix = (GLdouble * 16)()
            proj_matrix = (GLdouble * 16)()
            viewport = (GLint * 4)()
            glGetDoublev(GL_MODELVIEW_MATRIX, model_matrix)
            glGetDoublev(GL_PROJECTION_MATRIX, proj_matrix)
            glGetIntegerv(GL_VIEWPORT, viewport)
            
            # Unproject near and far points
            near = [GLdouble(), GLdouble(), GLdouble()]
            far = [GLdouble(), GLdouble(), GLdouble()]
            
            gluUnProject(x, y, 0.0, model_matrix, proj_matrix, viewport, *near)
            gluUnProject(x, y, 1.0, model_matrix, proj_matrix, viewport, *far)
            
            # Create ray
            ray_origin = [near[i].value for i in range(3)]
            ray_dir = [far[i].value - near[i].value for i in range(3)]
            ray_dir = normalize_vector(ray_dir)
            
            # Check intersection with sphere
            intersection = ray_sphere_intersection(
                ray_origin, ray_dir, [0, 0, 0], SPHERE_RADIUS
            )
            
            if intersection:
                self.pins.append(tuple(intersection))
                lon, lat = xyz_to_lonlat(*intersection)
                logger.info(f"Pin added at Lat: {lat:.2f}°, Lon: {lon:.2f}°")
                self.update()
        
        except Exception as e:
            logger.error(f"Error adding pin: {e}")
    
    def reset_view(self):
        """Reset camera and clear data"""
        self.camera.reset()
        self.pins = []
        self.trajectory.reset()
        self.animation_timer.stop()
        self.update()
        logger.info("View reset")
    
    def toggle_trajectory_animation(self):
        """Start/stop trajectory animation"""
        if self.trajectory.is_animating:
            self.trajectory.stop_animation()
            self.animation_timer.stop()
            logger.info("Trajectory animation stopped")
        else:
            if self.trajectory.is_complete():
                self.trajectory.reset()
            self.trajectory.start_animation()
            self.animation_timer.start(int(ANIMATION_INTERVAL * 1000))
            logger.info("Trajectory animation started")
    
    def clear_pins(self):
        """Clear all pins"""
        self.pins = []
        self.update()
        logger.info("Pins cleared")
    
    def cleanup(self):
        """Cleanup resources"""
        self.texture_manager.cleanup()
        if self.sphere_list:
            glDeleteLists(self.sphere_list, 1)