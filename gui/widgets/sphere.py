
from OpenGL import GL
from OpenGL.GLU import gluPerspective, gluUnProject
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GLU import *


from config.render_config import DEFAULT_FOV, FAR_CLIP, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, NEAR_CLIP, SPHERE_RADIUS
from gui.engine.camera import Camera
from gui.engine.overlay import Overlay
from gui.engine.sphere import Sphere
from gui.engine.texture_manager import TextureManager
from gui.engine.coordinates import ray_sphere_intersection, xyz_to_lonlat, lonlat_to_xyz
from gui.engine.trajectory import Trajectory, SAMPLE_TRAJECTORY

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
        self.pin1 = []
        self.pin2 = []

        self.texture = None
        self.bg_texture = None

        # simple interaction state
        self._last_mouse_pos = None
        self._mouse_button = None
        # track mouse movement even without button presses (optional)
        self.setMouseTracking(True)

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glClearColor(0,0,0,1)

        self.texture_manager.set_textures('earth.jpg', 'stars.jpg')
        self.texture = self.texture_manager.load_texture()
        # background sprite should be loaded using the dedicated loader
        self.bg_texture = self.texture_manager.load_bg_sprite()

        # ensure the sphere gets the numeric texture id (glGenTextures may return numpy types)
        if self.texture is not None:
            try:
                self.sphere.texture = int(self.texture)
            except Exception:
                self.sphere.texture = self.texture

        # create the sphere mesh/display list now that a GL context exists
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

        # Sphere.draw will bind the sphere texture (if set) and call the display list
        self.sphere.draw()

        # ensure overlay renders after the sphere
        try:
            self.overlay.draw()
        except Exception:
            pass

        GL.glDisable(GL.GL_TEXTURE_2D)

        self._draw_pins()
        self._draw_trajectory()
        
        return super().paintGL()

    def _draw_background(self):
        """Draw background with stars texture"""
        
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glPushMatrix()
        GL.glLoadIdentity()
        # GL.glOrtho(-1, 1, -1, 1, -1, 1)
        GL.glOrtho(0, self.width(), 0, self.height(), -1, 1)
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        # GL.glPushMatrix()
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
            # nothing to draw
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
        
        
        # GL.glPopMatrix()
        # GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glPopMatrix()
        # GL.glMatrixMode(GL.GL_MODELVIEW)

        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def _draw_pins(self):
        """Draw pins"""
        if not self.pin1 and not self.pin2:
            return
        
        GL.glPointSize(10)
        # draw pins in red; pins stored as (lon, lat) for sphere-relative placement
        GL.glColor3f(1.0, 0.0, 0.0)
        GL.glBegin(GL.GL_POINTS)
        for pin in self.pin1 + self.pin2:
            # support both legacy (x,y,z) and new (lon,lat) storage
            if isinstance(pin, (tuple, list)) and len(pin) == 2:
                lon, lat = pin
                x, y, z = lonlat_to_xyz(lon, lat, SPHERE_RADIUS)
            elif isinstance(pin, (tuple, list)) and len(pin) == 3:
                x, y, z = pin
            else:
                continue

            GL.glVertex3f(x, y, z)
        GL.glEnd()
    
    def _draw_trajectory(self):
        """Draw trajectory"""
        points = self.trajectory.get_points()
        if not points:
            return
        
        # draw trajectory in white
        GL.glColor3f(1.0, 1.0, 1.0)
        GL.glLineWidth(5)
        GL.glBegin(GL.GL_LINE_STRIP)
        for point in points:
            GL.glVertex3f(point[0], point[1], point[2])
        GL.glEnd()
    
    def _update_animation(self):
        """Update animation"""
        if self.trajectory.update():
            self.update()
        else:
            self.animation_timer.stop()
    
    # ----- input handlers (mouse + wheel) -----
    def mousePressEvent(self, event):
        # store start position and button
        self.setFocus()
        try:
            self._last_mouse_pos = event.pos()
            self._mouse_button = event.button()
        except Exception:
            self._last_mouse_pos = None
            self._mouse_button = None

        if event.button() == Qt.MiddleButton :#& self.point2 == 0:
            self._add_pin_at_cursor(event.x(), event.y())

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._last_mouse_pos = None
        self._mouse_button = None
        return super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            # reset camera on spacebar
            self.camera.reset()
            self.update()  
        elif event.key() == Qt.Key_C:
            # clear pins on 'C' key
            self.pin1.clear()
            self.pin2.clear()
            self.update()
        # else if x is pressed clear only one pin starting with pin2
        elif event.key() == Qt.Key_X:
            if self.pin2:
                self.pin2.clear()
            elif self.pin1:
                self.pin1.clear()
            self.update()
        elif event.key() == Qt.Key_T:
            # toggle trajectory on 'T' key
            if self.trajectory.is_animating():
                self.trajectory.stop_animation()
            else:
                self.trajectory.start_animation(SAMPLE_TRAJECTORY)
                self.update()


    def mouseMoveEvent(self, event):
        # do nothing if no last position recorded
        if self._last_mouse_pos is None:
            self._last_mouse_pos = event.pos()
            return super().mouseMoveEvent(event)

        dx = event.x() - self._last_mouse_pos.x()
        dy = event.y() - self._last_mouse_pos.y()

        # import local so we don't add a top-level dependency in other contexts
        from PyQt5.QtCore import Qt

        if self._mouse_button == Qt.LeftButton:
            # rotate camera on left-drag
            self.camera.rotate(dx, dy)
        elif self._mouse_button == Qt.RightButton:
            # tilt/pan on right-drag
            self.camera.tilt(dx, dy)

        self._last_mouse_pos = event.pos()
        self.update()
        return super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        # Qt angleDelta().y() returns 120 per notch typically — convert to notches
        try:
            notches = event.angleDelta().y() / 120.0
        except Exception:
            # fallback to legacy delta
            notches = event.delta() / 120.0 if hasattr(event, 'delta') else 0

        if notches:
            self.camera.zoom(notches)
            self.update()

        return super().wheelEvent(event)
    
    def _add_pin_at_cursor(self, x, y):
        """Add pin at cursor"""
        try:
            # ensure GL context is current and matrices reflect the scene
            try:
                self.makeCurrent()
            except Exception:
                # QOpenGLWidget.makeCurrent may not be available in some contexts
                pass

            # use device-pixel coordinates (account for High-DPI)
            try:
                dpr = float(self.devicePixelRatioF())
            except Exception:
                try:
                    dpr = float(self.devicePixelRatio())
                except Exception:
                    dpr = 1.0

            # compute projection matrix corresponding to paintGL
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glPushMatrix()
            GL.glLoadIdentity()
            width_px = int(self.width() * dpr)
            height_px = int(self.height() * dpr) if self.height() else 1
            aspect = (width_px / height_px) if height_px else 1.0
            gluPerspective(DEFAULT_FOV, aspect, NEAR_CLIP, FAR_CLIP)

            proj_matrix = (GL.GLdouble * 16)()
            GL.glGetDoublev(GL.GL_PROJECTION_MATRIX, proj_matrix)

            # compute modelview matrix corresponding to paintGL
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glPushMatrix()
            GL.glLoadIdentity()
            cam_paras = self.camera.get_params()
            GL.glTranslatef(0, 0, cam_paras['zoom'])
            GL.glTranslatef(cam_paras['tilting_x'], cam_paras['tilting_y'], 0)
            GL.glRotatef(cam_paras['rotation_y'], 1, 0, 0)
            GL.glRotatef(cam_paras['rotation_x'], 0, 1, 0)

            model_matrix = (GL.GLdouble * 16)()
            GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX, model_matrix)

            viewport = (GL.GLint * 4)()
            GL.glGetIntegerv(GL.GL_VIEWPORT, viewport)

            # convert matrices/viewport to Python-compatible tuples
            model = tuple(model_matrix)
            proj = tuple(proj_matrix)
            view = tuple(viewport)

            # convert mouse coords into framebuffer pixels
            x_fb = float(x) * dpr
            y_fb = float(y) * dpr

            # flip Y for OpenGL window coordinate origin (bottom-left)
            y_flipped = view[3] - y_fb

            near_point = gluUnProject(x_fb, y_flipped, 0.0, model, proj, view)
            far_point = gluUnProject(x_fb, y_flipped, 1.0, model, proj, view)

            # restore matrix stacks
            GL.glPopMatrix()
            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glPopMatrix()
            GL.glMatrixMode(GL.GL_MODELVIEW)

            if near_point is None or far_point is None:
                raise RuntimeError('gluUnProject failed to convert screen to world coordinates')

            ray_origin = [float(near_point[i]) for i in range(3)]
            ray_dir = [float(far_point[i]) - float(near_point[i]) for i in range(3)]

            # normalize the ray direction (robust)
            from math import sqrt
            length = sqrt(sum(c * c for c in ray_dir))
            if length != 0:
                ray_dir = [c / length for c in ray_dir]

            # intersect with sphere
            intersection = ray_sphere_intersection(ray_origin, ray_dir, [0, 0, 0], SPHERE_RADIUS)

            if intersection:
                # convert intersection to lon/lat and store as sphere-relative coordinates
                lon, lat = xyz_to_lonlat(*intersection)

                """# avoid duplicates within a small threshold
                duplicate = any(isinstance(p, (tuple, list)) and len(p) == 2 and abs(p[0]-lon) < 0.25 and abs(p[1]-lat) < 0.25 for p in self.pin1 + self.pin2)
                if not duplicate and len(self.pin1) == 0:
                    self.pin1.append((lon, lat))
                    LOG.info(f"1st Pin at Lat: {lat:.2f}°, Lon: {lon:.2f}°")
                    self.update()
                if not duplicate and len(self.pin2) == 0 and len(self.pin1) != 0:
                    self.pin2.append((lon, lat))
                    LOG.info(f"2nd Pin at Lat: {lat:.2f}°, Lon: {lon:.2f}°")
                    self.update()
"""

                threshold = 0.25  # degrees

                def is_close(lon, lat, pin, threshold=0.25):
                    return abs(pin[0] - lon) < threshold and abs(pin[1] - lat) < threshold

                # Place pin1 first if empty
                if not self.pin1:
                    self.pin1.append((lon, lat))
                    LOG.info(f"1st Pin at Lat: {lat:.2f}°, Lon: {lon:.2f}°")
                    self.update()

                # Only allow pin2 after pin1 exists
                elif not self.pin2:
                    # Avoid pin2 being equal/too close to pin1
                    if not is_close(lon, lat, self.pin1[0], threshold):
                        self.pin2.append((lon, lat))
                        print(self.pin1)
                        LOG.info(f"2nd Pin at Lat: {lat:.2f}°, Lon: {lon:.2f}°")
                        self.update()
                    else:
                        LOG.info("Rejected: Pin2 too close to Pin1")
        except Exception as e:
            LOG.error(f"Error adding pin: {e}")
        finally:
            try:
                # release GL context if necessary
                self.doneCurrent()
            except Exception:
                pass
    
