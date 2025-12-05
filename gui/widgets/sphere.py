""""
 SphereWidget module
 Sphere widget for rendering a textured sphere with OpenGL,
 camera controls, and overlay features.
 """

import OpenGL.GL as GL
from OpenGL.GLU import *
from OpenGL.GLU import gluPerspective, gluUnProject
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from gui.engine.camera import Camera
from gui.engine.overlay import Overlay
from gui.engine.sphere import Sphere
from gui.engine.texture_manager import TextureManager
from gui.engine.trajectory import Trajectory
from gui.engine.coordinates import ray_sphere_intersection, xyz_to_lonlat
from config.render_config import (DEFAULT_FOV, FAR_CLIP,
                                  MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH,
                                  NEAR_CLIP, SPHERE_RADIUS)
import logging
LOG = logging.getLogger(__name__)

class SphereWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.setFocusPolicy(Qt.StrongFocus)
        
        self.camera = Camera()
        self.texture_manager = TextureManager()
        self.trajectory = Trajectory()
        self.sphere = Sphere()
        self.overlay = Overlay()

        self.texture = None
        self.bg_texture = None
        self._last_mouse_pos = None
        self._mouse_button = None
        self.setMouseTracking(True)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_trajectory_animation)

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glClearColor(0,0,0,1)

        self.texture_manager.set_textures('earth.jpg', 'stars.jpg')
        self.texture = self.texture_manager.load_texture()
        # background sprite should be loaded using the dedicated loader
        self.bg_texture = self.texture_manager.load_bg_sprite()

        if self.texture is not None:
            try:
                self.sphere.texture = int(self.texture)
            except Exception:
                self.sphere.texture = self.texture

        self.sphere._create_mesh()
        return super().initializeGL()

    def resizeGL(self, w, h):
        GL.glViewport(0,0,w,h)
        return super().resizeGL(w, h)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        self._draw_background()
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        aspect_ration = self.width() / self.height()
        gluPerspective(DEFAULT_FOV, aspect_ration, NEAR_CLIP, FAR_CLIP)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
        cam_paras = self.camera.get_params()
        GL.glTranslatef(0,0, cam_paras['zoom'])
        GL.glTranslatef(cam_paras['tilting_x'], cam_paras['tilting_y'], 0)
        GL.glRotatef(cam_paras['rotation_y'], 1,0,0)
        GL.glRotatef(cam_paras['rotation_x'], 0,1,0)

        self.sphere.draw()
        try:
            self.overlay.draw()
        except Exception:
            pass

        GL.glDisable(GL.GL_TEXTURE_2D)
        self.overlay.draw()
        
        return super().paintGL()

    def _draw_background(self):       
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, self.width(), 0, self.height(), -1, 1)
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
        GL.glEnable(GL.GL_TEXTURE_2D)
        # bg_texture may be a numpy scalar; coerce to int if possible
        if self.bg_texture is not None:
            try:
                bg_id = int(self.bg_texture)
            except Exception:
                bg_id = self.bg_texture
            GL.glBindTexture(GL.GL_TEXTURE_2D, bg_id)
        else:
            GL.glDisable(GL.GL_TEXTURE_2D)
            GL.glEnable(GL.GL_DEPTH_TEST)
            return
        
        GL.glBegin(GL.GL_QUADS)
        # draw quad covering full viewport using 0..width and 0..height
        w = float(self.width())
        h = float(self.height())
        GL.glTexCoord2f(0.0, 0.0); GL.glVertex2f(0.0, 0.0)
        GL.glTexCoord2f(1.0, 0.0); GL.glVertex2f(w, 0.0)
        GL.glTexCoord2f(1.0, 1.0); GL.glVertex2f(w, h)
        GL.glTexCoord2f(0.0, 1.0); GL.glVertex2f(0.0, h)
        GL.glEnd()

        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def mousePressEvent(self, event):
        self.setFocus()
        try:
            self._last_mouse_pos = event.pos()
            self._mouse_button = event.button()
        except Exception:
            self._last_mouse_pos = None
            self._mouse_button = None

        if event.button() == Qt.MouseButton.RightButton:
            self._add_pin_at_cursor(event.x(), event.y())

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._last_mouse_pos = None
        self._mouse_button = None
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._last_mouse_pos is None:
            self._last_mouse_pos = event.pos()
            return super().mouseMoveEvent(event)

        dx = event.x() - self._last_mouse_pos.x()
        dy = event.y() - self._last_mouse_pos.y()

        if self._mouse_button == Qt.MouseButton.LeftButton:
            self.camera.rotate(dx, dy)
        elif self._mouse_button == Qt.MouseButton.MiddleButton:
            self.camera.tilt(dx, dy)

        self._last_mouse_pos = event.pos()
        self.update()
        return super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        # Qt angleDelta().y() returns 120 per notch typically — convert to notches
        try:
            notches = event.angleDelta().y() / 120.0
        except Exception:
            notches = event.delta() / 120.0 if hasattr(event, 'delta') else 0

        if notches:
            self.camera.zoom(notches)
            self.update()

        return super().wheelEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            # reset camera on spacebar
            self.camera.reset()
            self.update()  
        elif event.key() == Qt.Key.Key_C:
            self.overlay.clear()
            self.update()
        elif event.key() == Qt.Key.Key_X:
            self.overlay.remove_last_pin()
            self.update()
        elif event.key() == Qt.Key.Key_T:
            if self.overlay.trajectory.is_animating:
                self.overlay.trajectory.stop_animation()
                self.animation_timer.stop()
                LOG.info("Trajectory animation stopped")
            else:
                self.overlay.start_trajectory_animation()
                self.animation_timer.start(16)  # ~60 FPS
                LOG.info("Trajectory animation started ")
    
    def _update_trajectory_animation(self):
        if self.overlay.trajectory.update():
            self.update()
        else:
            self.animation_timer.stop()
            LOG.info("Trajectory animation complete")
    
    def _get_ray_from_cursor(self, x, y):
        """Calculates a ray origin and direction from the cursor position.

        This involves reconstructing the projection and modelview matrices to un-project
        the 2D screen coordinates back into the 3D world space.

        Args:
            x: The x-coordinate of the cursor.
            y: The y-coordinate of the cursor.

        Returns:
            A tuple containing the ray origin (list) and ray direction (list).
        """
        dpr = self.devicePixelRatioF()
        width_px = int(self.width() * dpr)
        height_px = int(self.height() * dpr)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        gluPerspective(DEFAULT_FOV, width_px / height_px, NEAR_CLIP, FAR_CLIP)
        proj_matrix = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)
        GL.glPopMatrix()

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        cam_params = self.camera.get_params()
        GL.glTranslatef(0, 0, cam_params['zoom'])
        GL.glTranslatef(cam_params['tilting_x'], cam_params['tilting_y'], 0)
        GL.glRotatef(cam_params['rotation_y'], 1, 0, 0)
        GL.glRotatef(cam_params['rotation_x'], 0, 1, 0)
        model_matrix = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
        GL.glPopMatrix()

        viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)

        x_fb = float(x) * dpr
        y_fb = viewport[3] - (float(y) * dpr)

        # Un-project the 2D point at the near and far clipping planes.
        near_point = gluUnProject(x_fb, y_fb, 0.0, model_matrix, proj_matrix, viewport)
        far_point = gluUnProject(x_fb, y_fb, 1.0, model_matrix, proj_matrix, viewport)

        if near_point is None or far_point is None:
            raise RuntimeError('gluUnProject failed to convert screen to world coordinates')

        ray_origin = list(near_point)
        ray_dir = [f - n for f, n in zip(far_point, near_point)]

        # Normalize the direction vector.
        from math import sqrt
        length = sqrt(sum(c * c for c in ray_dir))
        if length > 0:
            ray_dir = [c / length for c in ray_dir]

        return ray_origin, ray_dir

    def _add_pin_at_cursor(self, x, y):
        threshold = 0.25  # degrees
        try:
            self.makeCurrent()
            ray_origin, ray_dir = self._get_ray_from_cursor(x, y)
            intersection = ray_sphere_intersection(ray_origin, ray_dir, [0, 0, 0], SPHERE_RADIUS)
            if intersection:
                self.overlay.add_pin(*intersection)
                lon, lat = xyz_to_lonlat(*intersection)
                LOG.info(f"Pin at Lat,Lon: {lat},{lon}")
                self.update()

        except Exception as e:
            LOG.error(f"Error adding pin: {e}")
        finally:
            self.doneCurrent()
    
