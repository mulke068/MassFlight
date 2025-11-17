from math import cos, pi, sin
import pyglet
from pyglet import gl
import logging
from PIL import Image

import config.app_config as cfg

conf = cfg.configurations

LOG = logging.getLogger(__name__)


class OffscreenPygletRenderer:
    """Render a pyglet 3D sphere offscreen and expose controls for interaction."""

    def __init__(self, width=600, height=400, radius=2, resolution=50):
        self.width = width
        self.height = height
        self.radius = radius
        self.resolution = resolution

        # camera / transform state
        self.rotation = 0.0
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.panning_x = 0.0
        self.panning_y = 0.0
        self.zoom_distance = -6.0

        # pyglet resources
        self.window = None
        self.batch = None
        self.vertex_list = None
        self.points = None
        self.num_points = 0

        # create offscreen window and GL objects
        self._create_offscreen()

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def sphere_points(self):
        verts = []
        r = self.radius
        res = self.resolution
        for i in range(res):
            lon = self.map_value(i, 0, res, -pi, pi)
            for j in range(res):
                lat = self.map_value(j, 0, res, -pi/2, pi/2)
                x = r * sin(lon) * cos(lat)
                y = r * sin(lon) * sin(lat)
                z = r * cos(lon)
                verts.extend((x, y, z))
        return verts

    def _create_offscreen(self):
        # Create a hidden pyglet window (offscreen rendering)
        try:
            config = pyglet.gl.Config(double_buffer=True, depth_size=24)
            self.window = pyglet.window.Window(width=self.width, height=self.height, visible=False, config=config)
            # make context current
            try:
                self.window.context.set_current()
            except Exception:
                # older pyglet versions: switch_to
                self.window.switch_to()

            # prepare geometry
            self.points = self.sphere_points()
            self.num_points = len(self.points) // 3
            self.batch = pyglet.graphics.Batch()
            self.vertex_list = self.batch.add(
                self.num_points,
                gl.GL_POINTS,
                None,
                ('v3f', self.points),
                ('c3B', (255, 255, 255) * self.num_points)
            )

            # initial GL setup
            self._setup_3d_once()
            LOG.debug('Offscreen pyglet window created')
        except Exception as e:
            LOG.exception('Failed to create offscreen pyglet window: %s', e)
            raise

    def _setup_3d_once(self):
        # Assumes context current
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        gl.glPointSize(2)
        gl.glEnable(gl.GL_POINT_SMOOTH)

    def _setup_frame(self):
        # Called each frame before drawing
        # Ensure context current
        try:
            self.window.context.set_current()
        except Exception:
            self.window.switch_to()

        gl.glViewport(0, 0, self.width, self.height)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = self.width / float(self.height)
        gl.gluPerspective(60.0, aspect, 0.1, 100.0)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(self.panning_x, self.panning_y, self.zoom_distance)
        gl.glRotatef(self.rotation_x, 0.0, 1.0, 0.0)
        gl.glRotatef(self.rotation_y, 1.0, 0.0, 0.0)

    def draw_frame(self):
        """Render one frame and return a PIL Image (RGBA)."""
        if self.window is None:
            return None

        try:
            # make context current
            try:
                self.window.context.set_current()
            except Exception:
                self.window.switch_to()

            # Clear and set projection/model
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            self._setup_frame()

            # No automatic rotation animation; rotation is controlled by user drag

            # draw
            self.batch.draw()

            # read pixels from buffer
            buffer = pyglet.image.get_buffer_manager().get_color_buffer()
            image_data = buffer.get_image_data()
            raw = image_data.get_data('RGBA', self.width * 4)
            img = Image.frombytes('RGBA', (self.width, self.height), raw)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            return img
        except Exception as e:
            LOG.exception('draw_frame failed: %s', e)
            return None

    # Control methods used by the GUI
    def drag(self, dx, dy, button=1):
        if button == 1:
            self.rotation_x += dx * 0.5
            self.rotation_y += dy * 0.5
        elif button == 2:
            self.panning_x += dx * 0.01
            self.panning_y -= dy * 0.01

    def zoom(self, delta):
        # delta: positive scroll up, negative scroll down
        self.zoom_distance += delta * 0.5