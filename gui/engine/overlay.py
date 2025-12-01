
from OpenGL import GL
import logging

from gui.engine import trajectory
from gui.engine.trajectory import Trajectory

LOG = logging.getLogger(__name__)

class Overlay:
    def __init__(self):
        self.pins = []
        self.max_pins = 2
        self.pin_threshold = 0.25

        self.trajectory = Trajectory()
    
    ###################### PINS #############################
    def add_pin(self, x,y,z):
        if len(self.pins) + 1 <= self.max_pins:
            self.pins.append((x,y,z))
        LOG.debug(f'Pin added at {x}, {y}, {z}', exc_info=1)

    def clear_pins(self):
        self.pins = []
        LOG.debug('Pins cleared', exc_info=1)
    
    def remove_last_pin(self):
        if self.pins:
            self.pins.pop()
    
    def start_trajectory_animation(self):
        """Start trajectory animation from first pin to last pin"""
        if len(self.pins) >= 2:
            point1 = self.pins[0]
            point2 = self.pins[-1]
            self.trajectory.generate_trajectory_between_points(point1, point2, num_steps=100)
            self.trajectory.start_animation()
            return True
        return False
    
    
    def draw(self):
        # GL.glEnable(GL.GL_BLEND)
        # GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
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

        trajectories = self.trajectory.get_points()
        if trajectories:
            GL.glLineWidth(4)
            GL.glColor3f(1,1,1) # White color
            GL.glBegin(GL.GL_LINE_STRIP)
            for point in trajectories:
                GL.glVertex3f(
                    point[0],
                    point[1],
                    point[2]
                )
            GL.glEnd()
        
        # reset
        GL.glColor3f(1,1,1)
        GL.glDisable(GL.GL_BLEND)
        GL.glEnable(GL.GL_TEXTURE_2D)

    def clear(self):
        self.pins = []
        self.trajectories = []
        LOG.debug('Overlay cleared', exc_info=1)