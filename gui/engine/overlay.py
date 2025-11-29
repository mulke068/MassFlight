
from OpenGL import GL
import logging

LOG = logging.getLogger(__name__)

class Overlay:
    def __init__(self):
        self.pins = []
        self.trajectories = []
        self.trajectories_queue = []
        self.is_animating = False
    
    def add_pin(self, pin):
        self.pins.append(pin)
        LOG.debug(f'Pin added at {pin.position}', exc_info=1)

    def add_trajectory(self, points):
        self.trajectories = points
        LOG.debug(f'Trajectory added with {len(points)} points', exc_info=1)
    
    def clear(self):
        self.pins = []
        self.trajectories = []
        LOG.debug('Overlay cleared', exc_info=1)
    
    def draw(self):
        GL.glDisable(GL.GL_TEXTURE_2D)
        
        if self.pins:
            GL.glPointSize(10)
            GL.glColor3f(1,0,0)  # Red color 
            GL.glBegin(GL.GL_POINTS)
            for pin in self.pins:
                GL.glVertex3f(
                    pin[0],
                    pin[1],
                    pin[2]
                )
            GL.glEnd()

        if self.trajectories:
            GL.glLineWidth(5)
            GL.glColor3f(1,1,1) # White color
            GL.glBegin(GL.GL_LINE_STRIP)
            for point in self.trajectories:
                GL.glVertex3f(
                    point[0],
                    point[1],
                    point[2]
                )
            GL.glEnd()
        
        # reset
        GL.glColor3f(1,1,1)
        GL.glEnable(GL.GL_TEXTURE_2D)