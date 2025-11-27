
from OpenGL import GL
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


    def initializeGL(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glClearColor(0,0,0,1)

        self.texture_manager.set_textures('earth.jpg', 'stars.jpg')
        self.texture = self.texture_manager.load_texture()
        self.bg_texture = self.texture_manager.load_texture()
        
        self.sphere.draw()
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
        GL.gluPerspective(DEFAULT_FOV, aspect_ration, NEAR_CLIP, FAR_CLIP)
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
        cam_paras = self.camera.get_params()
        GL.glTranslatef(0,0, cam_paras['zoom'])
        GL.glTranslatef(cam_paras['tilting_x'], cam_paras['tilting_y'], 0)
        GL.glRotatef(cam_paras['rotation_y'], 1,0,0)
        GL.glRotatef(cam_paras['rotation_x'], 0,1,0)

        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture.id)

        GL.glColor3f(1,1,1)
        GL.glCallList(self.sphere)

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
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.bg_texture)
        
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0, 0); GL.glVertex2f(-1, -1)
        GL.glTexCoord2f(1, 0); GL.glVertex2f(1, -1)
        GL.glTexCoord2f(1, 1); GL.glVertex2f(1, 1)
        GL.glTexCoord2f(0, 1); GL.glVertex2f(-1, 1)
        GL.glEnd()
        
        
        # GL.glPopMatrix()
        # GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glPopMatrix()
        # GL.glMatrixMode(GL.GL_MODELVIEW)

        GL.glDisable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_DEPTH_TEST)