from OpenGL import GL
from OpenGL.GLU import gluPerspective, gluUnProject
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QTimer

from config.render_config import DEFAULT_FOV, FAR_CLIP, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, NEAR_CLIP, SPHERE_RADIUS
from gui.engine.camera import Camera
from gui.engine.overlay import Overlay
from gui.engine.sphere import Sphere
from gui.engine.texture_manager import TextureManager
from utils.coordinates import ray_sphere_intersection, xyz_to_lonlat, lonlat_to_xyz
from utils.coordinates import ray_sphere_intersection, xyz_to_lonlat, lonlat_to_xyz
from gui.engine.trajectory import Trajectory


import logging
LOG = logging.getLogger(__name__)

class SphereWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.camera = Camera()
        self.texture_manager = TextureManager()
        self.trajectory = Trajectory()
        
        self.sphere = Sphere()
        self.overlay = Overlay()

        self.texture = None
        self.bg_texture = None

        # simple interaction state
        self._last_mouse_pos = None
        self._mouse_button = None
        # track mouse movement even without button presses (optional)
        self.setMouseTracking(True)
        
        # Animation timer for trajectory
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_trajectory_animation)

    def start_animation(self):
        self.overlay.start_trajectory_animation()
        self.animation_timer.start(16)

    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glClearColor(0,0,0,1)

        # Debug OpenGL Context
        version = GL.glGetString(GL.GL_VERSION)
        vendor = GL.glGetString(GL.GL_VENDOR)
        renderer = GL.glGetString(GL.GL_RENDERER)

        LOG.info(f"OpenGL Context: {version.decode('utf-8')}")
        LOG.info(f"OpenGL Vendor: {vendor.decode('utf-8')}")
        LOG.info(f"OpenGL Renderer: {renderer.decode('utf-8')}")

        try:
            profile_mask = GL.glGetIntegerv(GL.GL_CONTEXT_PROFILE_MASK)
            LOG.info(f"Context Profile Mask: {profile_mask} (Compat=2, Core=1)")
        except Exception as e:
            LOG.info(f"Could not get profile mask (likely legacy context): {e}")

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
        else:
             LOG.warning("Failed to load sphere texture, using fallback color.")

        # create the sphere mesh/display list now that a GL context exists
        self.sphere._create_mesh()
        return super().initializeGL()

    def resizeGL(self, w, h):
        GL.glViewport(0,0,w,h)
        return super().resizeGL(w, h)

    def paintGL(self):
        # Reset pixel storage modes that might interfere with QPainter or internal blits
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 4)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)

        err = GL.glGetError()
        if err != GL.GL_NO_ERROR:
             LOG.error(f"OpenGL Error Pre-Paint: {err}")

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
        GL.glEnable(GL.GL_TEXTURE_2D)
        # Reset color to white for texturing
        GL.glColor3f(1, 1, 1)
        self.sphere.draw()

        # ensure overlay renders after the sphere
        try:
            self.overlay.draw()
        except Exception:
            pass

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

    
    # ----- input handlers (mouse + wheel) -----
    def mousePressEvent(self, event):
        # store start position and button
        self.setFocus()
        try:
            self._last_mouse_pos = event.position()
            self._mouse_button = event.button()
        except Exception:
            self._last_mouse_pos = None
            self._mouse_button = None

        if event.button() == Qt.MouseButton.RightButton:#& self.point2 == 0:
            self._add_pin_at_cursor(event.position().x(), event.position().y())

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._last_mouse_pos = None
        self._mouse_button = None
        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        # do nothing if no last position recorded
        if self._last_mouse_pos is None:
            self._last_mouse_pos = event.position()
            return super().mouseMoveEvent(event)

        dx = event.position().x() - self._last_mouse_pos.x()
        dy = event.position().y() - self._last_mouse_pos.y()

        if self._mouse_button == Qt.MouseButton.LeftButton:
            # rotate camera on left-drag
            self.camera.rotate(dx, dy)
        elif self._mouse_button == Qt.MouseButton.MiddleButton:
            # tilt/pan on right-drag
            self.camera.tilt(dx, dy)

        self._last_mouse_pos = event.position()
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            # reset camera on spacebar
            self.camera.reset()
            self.update()  
        elif event.key() == Qt.Key.Key_C:
            self.overlay.clear()
            self.update()
        # else if x is pressed clear only one pin starting with pin2
        elif event.key() == Qt.Key.Key_X:
            self.overlay.remove_last_pin()
            self.update()
        elif event.key() == Qt.Key.Key_T:
            # Toggle animation using existing points (pins or sample)
            if self.overlay.trajectory.is_animating:
                self.overlay.trajectory.stop_animation()
                self.animation_timer.stop()
                LOG.info("Trajectory animation stopped")
            else:
                self.overlay.start_trajectory_animation()
                self.animation_timer.start(16)  # ~60 FPS
                LOG.info("Trajectory animation started ")
    


    def _update_trajectory_animation(self):
        """Update trajectory animation and redraw"""
        if not self.overlay.trajectory.update():
            self.animation_timer.stop()
            LOG.info("Trajectory animation complete")
            return
        
        self.update()

    def set_animation_speed(self, speed):
        """Sets the number of steps processed per frame."""
        self.overlay.trajectory.set_animation_speed(speed)
        LOG.debug(f"Animation speed set to {speed}x")

    # def fit_view_to_trajectory(self, points):
    #     """Adjusts camera to fit all points in view with a true side profile."""
    #     if not points:
    #         return

    #     # 1. Calculate Centroid (Midpoint)
    #     sum_x = sum(p[0] for p in points)
    #     sum_y = sum(p[1] for p in points)
    #     sum_z = sum(p[2] for p in points)
    #     count = len(points)
        
    #     center_x = sum_x / count
    #     center_y = sum_y / count
    #     center_z = sum_z / count
        
    #     # 2. Calculate Side Vector for Camera Position
    #     # Start and End points
    #     start = points[0]
    #     end = points[-1]
        
    #     # Flight Vector (Start -> End)
    #     fx = end[0] - start[0]
    #     fy = end[1] - start[1]
    #     fz = end[2] - start[2]
        
    #     # Up Vector (Normal at Midpoint)
    #     # Just use the center vector itself (from origin to center)
    #     ux, uy, uz = center_x, center_y, center_z
        
    #     # Cross Product: Side = Flight x Up
    #     sx = fy * uz - fz * uy
    #     sy = fz * ux - fx * uz
    #     sz = fx * uy - fy * ux
        
    #     # Normalize Side Vector
    #     import math
    #     s_len = math.sqrt(sx*sx + sy*sy + sz*sz)
    #     if s_len > 0:
    #         sx /= s_len
    #         sy /= s_len
    #         sz /= s_len
        
    #     # Convert Side Vector to Lat/Lon for Camera Rotation
    #     # We want the camera to look FROM this side vector TOWARDS the center.
    #     # So we calculate the lat/lon of this vector.
    #     from gui.engine.coordinates import xyz_to_lonlat
    #     cam_lon, cam_lat = xyz_to_lonlat(sx, sy, sz)
        
    #     # Set Camera Rotation
    #     # rotation_y (Pitch) = Latitude
    #     # rotation_x (Yaw) = -Longitude - 90
    #     self.camera.rotation_y = cam_lat
    #     self.camera.rotation_x = -cam_lon - 90
    #     self.camera.tilting_x = 0
    #     self.camera.tilting_y = 0
        
    #     # 3. Calculate Zoom (Bounding Sphere Radius)
    #     max_dist = 0
    #     for p in points:
    #         dist = math.sqrt((p[0]-center_x)**2 + (p[1]-center_y)**2 + (p[2]-center_z)**2)
    #         if dist > max_dist:
    #             max_dist = dist
        
    #     fov_rad = math.radians(DEFAULT_FOV)
    #     required_dist = max_dist / math.tan(fov_rad / 2)
    #     required_dist *= 2.0 # Generous padding
        
    #     # Clamp zoom
    #     if required_dist < 15: required_dist = 15
    #     if required_dist > 150: required_dist = 150
        
    #     self.camera.zoom_distance = -required_dist
        
    #     self.update()

    
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
                LOG.debug(f"Pin at Lat,Lon: {lat},{lon}")
                self.update()

        except Exception as e:
            LOG.error(f"Error adding pin: {e}")
        finally:
            self.doneCurrent()
    
