from OpenGL import GL
import logging

from gui.engine import trajectory
from gui.engine.trajectory import Trajectory
# from gui.engine.trajectory import SAMPLE_TRAJECTORY

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

    def get_pins(self, index):
        return self.pins[index]

    def clear_pins(self):
        self.pins = []
        LOG.debug('Pins cleared', exc_info=1)
    
    def remove_last_pin(self):
        if self.pins:
            self.pins.pop()

    ###################### TRAJECTORY #############################
    def start_trajectory_animation(self):
        """Starts the trajectory animation."""
        if self.trajectory.full_trajectory:
            self.trajectory.start_animation()
        # Fallback: If no trajectory but we have pins, maybe we should have calculated? 
        # For now, just do nothing or use sample if explicitly requested, but better to rely on calculation.
        elif not self.trajectory.full_trajectory:
            LOG.warning("No trajectory data available to animate.")
        return True
    
    def set_trajectory_data(self, points):
        """Sets the trajectory data from a list of (x, y, z) points."""
        self.trajectory.set_full_trajectory(points)
        LOG.info(f"Trajectory data set with {len(points)} points")
    
    ######################### DRAWING #####################
    def draw(self):
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
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
        self.trajectory.clear()
        LOG.debug('Overlay cleared', exc_info=1)