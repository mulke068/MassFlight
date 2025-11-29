
from OpenGL import GL
from OpenGL.GLU import gluPerspective
from PyQt5.QtWidgets import QOpenGLWidget

from config.render_config import DEFAULT_FOV, FAR_CLIP, MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH, NEAR_CLIP
from gui.engine.camera import Camera
from gui.engine.overlay import Overlay
from gui.engine.sphere import Sphere
from gui.engine.texture_manager import TextureManager


class SphereWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        self.camera = Camera()
        self.texture_manager = TextureManager()
        
        self.sphere = Sphere()
        self.overlay = Overlay()

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

    # ----- input handlers (mouse + wheel) -----
    def mousePressEvent(self, event):
        # store start position and button
        try:
            self._last_mouse_pos = event.pos()
            self._mouse_button = event.button()
        except Exception:
            self._last_mouse_pos = None
            self._mouse_button = None
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._last_mouse_pos = None
        self._mouse_button = None
        return super().mouseReleaseEvent(event)

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