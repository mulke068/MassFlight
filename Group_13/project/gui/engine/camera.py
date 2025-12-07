"""
Camera module to handle 3D camera transformations.
provides functionality for zooming, rotating, tilting, and resetting the camera view.
"""

from OpenGL import GL
from config.render_config import INITIAL_ROT_X, INITIAL_ROT_Y, INITIAL_TILT_X, INITIAL_TILT_Y, INITIAL_ZOOM, MAX_ZOOM_IN, ROTATE_SENSITIVITY, TILTING_SENSITIVITY, ZOOM_SENSITIVITY
import logging

LOG = logging.getLogger(__name__)

class Camera:
    def __init__(self):
        self.zoom_distance = INITIAL_ZOOM
        self.rotation_x = INITIAL_ROT_X
        self.rotation_y = INITIAL_ROT_Y
        self.tilting_x = INITIAL_TILT_X
        self.tilting_y = INITIAL_TILT_Y
    
    def set(self):
        GL.glLoadIdentity()
        GL.glTranslatef(0,0, self.zoom_distance)
        GL.glTranslatef(self.tilting_x, self.tilting_y, 0)

        GL.glRotatef(self.rotation_y, 1,0,0)
        GL.glRotatef(self.rotation_x, 0,1,0)

    def zoom(self, scroll_y):
        new_zoom = self.zoom_distance + scroll_y * ZOOM_SENSITIVITY
        if new_zoom < MAX_ZOOM_IN:
            self.zoom_distance = new_zoom

    def rotate(self, dx, dy):
        self.rotation_x += dx * ROTATE_SENSITIVITY
        self.rotation_y += dy * ROTATE_SENSITIVITY
        # Not more then to north or south pole
        self.rotation_y = max(-90, min(90, self.rotation_y))
    
    def tilt(self, dx, dy):
        self.tilting_x += dx * TILTING_SENSITIVITY 
        self.tilting_y -= dy * TILTING_SENSITIVITY

    def reset(self):
        self.zoom_distance = INITIAL_ZOOM
        self.rotation_x = INITIAL_ROT_X
        self.rotation_y = INITIAL_ROT_Y
        self.tilting_x = INITIAL_TILT_X
        self.tilting_y = INITIAL_TILT_Y

    def get_params(self):
        return {
            'zoom': self.zoom_distance,
            'rotation_x': self.rotation_x,
            'rotation_y': self.rotation_y,
            'tilting_x': self.tilting_x,
            'tilting_y': self.tilting_y
        }