from math import asin, atan2, cos, pi, sin, sqrt
import os
import pyglet
from pyglet import gl
import logging
from PIL import Image

from config import RenderConfig as cfg

LOG = logging.getLogger(__name__)

# class OffscreenPygletRenderer:
#     """
#     Renders a 3D textured sphere offscreen using Pyglet.
#     This is refactored from your window.py and sphere.py.
#     """

#     def __init__(self, width, height, radius=2, resolution=50):
#         self.width = width
#         self.height = height
#         self.radius = radius
#         self.resolution = resolution

#         # --- Camera / Transform State ---
#         self.rotation_x = -100  # Initial view from sphere.py
#         self.rotation_y = 40     # Initial view from sphere.py
#         self.panning_x = 0.0
#         self.panning_y = 0.0
#         self.zoom_distance = -6.0

#         # --- Pyglet Resources ---
#         self.window = None
#         self.batch = None
#         self.vertex_list = None
#         self.texture = None

#         self._create_offscreen()
#         self._load_texture()
#         self._create_sphere_mesh()

#     def _create_offscreen(self):
#         """Create a hidden pyglet window for offscreen rendering."""
#         LOG.debug("Creating offscreen Pyglet window...")
#         try:
#             # Try to get the best GL config
#             display = pyglet.canvas.get_display()
#             screen = display.get_default_screen()
#             config_template = gl.Config(double_buffer=True, depth_size=24, sample_buffers=1, samples=4)
#             try:
#                 config = screen.get_best_config(config_template)
#             except pyglet.canvas.exceptions.NoSuchConfigException:
#                 LOG.warning("Could not find multisample config, falling back.")
#                 config_template = gl.Config(double_buffer=True, depth_size=24)
#                 config = screen.get_best_config(config_template)

#             self.window = pyglet.window.Window(width=self.width, height=self.height, visible=False, config=config)
            
#             # Make context current
#             self.window.switch_to()
            
#             self._setup_gl_once()
#             LOG.debug("Offscreen Pyglet window created.")
#         except Exception as e:
#             LOG.exception("Failed to create offscreen Pyglet window.")
#             raise

#     def _setup_gl_once(self):
#         """Set up OpenGL state that only needs to be set once."""
#         gl.glEnable(gl.GL_DEPTH_TEST)
#         gl.glEnable(gl.GL_CULL_FACE)
#         gl.glClearColor(0.1, 0.1, 0.15, 1.0) # Dark space background
        
#         # Lighting (simple)
#         gl.glEnable(gl.GL_LIGHTING)
#         gl.glEnable(gl.GL_LIGHT0)
#         gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, (gl.GLfloat * 4)(-1, 0.5, 1, 0))
#         gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, (gl.GLfloat * 4)(0.5, 0.5, 0.5, 1))
#         gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, (gl.GLfloat * 4)(1, 1, 1, 1))
        
#         # Material
#         gl.glEnable(gl.GL_COLOR_MATERIAL)
#         gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
#         gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, (gl.GLfloat * 4)(1, 1, 1, 1))
#         gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 50.0)

#     def _load_texture(self):
#         """Loads the sphere texture."""
#         self.window.switch_to()
#         try:
#             # Look for texture in assets/
#             texture_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets/textures', 'earth.jpg'))
#             if not os.path.exists(texture_path):
#                  LOG.warning(f"Texture not found at {texture_path}. Using fallback.")
#                  return # Will render a white sphere
                 
#             image = pyglet.image.load(texture_path)
#             self.texture = image.get_texture()
#             gl.glEnable(self.texture.target)
#             gl.glBindTexture(self.texture.target, self.texture.id)
#             gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
#             gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
#             LOG.info("Earth texture loaded successfully.")
#         except Exception as e:
#             LOG.error(f"Failed to load texture: {e}")

#     def _create_sphere_mesh(self):
#         """Generates vertex/index/texture data for a UV sphere."""
#         self.window.switch_to()
        
#         vertices, tex_coords, indices, normals = [], [], [], []
#         r, res = self.radius, self.resolution

#         for i in range(res + 1):
#             lat_t = i / res  # 0 to 1
#             lat = lat_t * pi - (pi / 2) # -pi/2 to pi/2

#             for j in range(res + 1):
#                 lon_t = j / res # 0 to 1
#                 lon = lon_t * 2 * pi # 0 to 2pi
                
#                 x = r * cos(lat) * cos(lon)
#                 y = r * cos(lat) * sin(lon)
#                 z = r * sin(lat)
                
#                 # Normalize for normal vector
#                 nx, ny, nz = x / r, y / r, z / r

#                 u = 1.0 - lon_t # Flipped for earth.jpg
#                 v = 1.0 - lat_t # Flipped for earth.jpg

#                 vertices.extend((x, y, z))
#                 tex_coords.extend((u, v))
#                 normals.extend((nx, ny, nz))

#         for i in range(res):
#             for j in range(res):
#                 p1 = i * (res + 1) + j
#                 p2 = p1 + 1
#                 p3 = (i + 1) * (res + 1) + j
#                 p4 = p3 + 1
#                 indices.extend((p1, p2, p3, p2, p4, p3))

#         self.batch = pyglet.graphics.Batch()
#         self.vertex_list = self.batch.add_indexed(
#             len(vertices) // 3,
#             gl.GL_TRIANGLES,
#             None,
#             indices,
#             ('v3f', vertices),
#             ('t2f', tex_coords),
#             ('n3f', normals),
#             ('c3B', (255, 255, 255) * (len(vertices) // 3)) # Base color (white)
#         )
#         LOG.debug("Sphere mesh created.")

#     def _setup_frame_camera(self):
#         """Sets up viewport and camera transforms for each frame."""
#         self.window.switch_to()
        
#         # Projection
#         gl.glMatrixMode(gl.GL_PROJECTION)
#         gl.glLoadIdentity()
#         gl.gluPerspective(60.0, self.width / float(self.height), 0.1, 100.0)

#         # ModelView
#         gl.glMatrixMode(gl.GL_MODELVIEW)
#         gl.glLoadIdentity()
        
#         # Apply camera transforms
#         gl.glTranslatef(self.panning_x, self.panning_y, self.zoom_distance)
#         gl.glRotatef(self.rotation_y, 1.0, 0.0, 0.0) # Pitch
#         gl.glRotatef(self.rotation_x, 0.0, 0.0, 1.0) # Z-axis roll (heading)

#     def draw_frame(self):
#         """Render one frame and return it as a PIL Image."""
#         if self.window is None:
#             return None
            
#         try:
#             self.window.switch_to()
#             gl.glViewport(0, 0, self.width, self.height)
#             gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

#             self._setup_frame_camera()
            
#             if self.texture:
#                 gl.glEnable(self.texture.target)
#                 gl.glBindTexture(self.texture.target, self.texture.id)
#             else:
#                 gl.glDisable(gl.GL_TEXTURE_2D)

#             self.batch.draw()

#             # Read pixels
#             buffer = pyglet.image.get_buffer_manager().get_color_buffer()
#             image_data = buffer.get_image_data()
#             raw = image_data.get_data('RGBA', self.width * 4)
#             img = Image.frombytes('RGBA', (self.width, self.height), raw)
            
#             # Pyglet buffer is bottom-up, PIL is top-down
#             img = img.transpose(Image.FLIP_TOP_BOTTOM)
#             return img
            
#         except Exception as e:
#             LOG.exception("draw_frame failed.")
#             return None

#     def resize(self, width, height):
#         """Handle window/frame resize."""
#         self.width = width
#         self.height = height
#         if self.window:
#             self.window.set_size(width, height)
#             gl.glViewport(0, 0, width, height)

#     def cleanup(self):
#         """Clean up Pyglet resources."""
#         if self.window:
#             self.window.close()
#             self.window = None
#             LOG.debug("Pyglet window closed.")

#     # --- Public Control Methods ---

#     def drag(self, dx, dy, button=1):
#         """Handle mouse drag for rotation or panning."""
#         if button == 1: # Left-click (Rotate)
#             self.rotation_x += dx * 0.5
#             self.rotation_y -= dy * .05
#             # Clamp vertical rotation
#             self.rotation_y = max(-90, min(90, self.rotation_y))
#         elif button == 2: # Middle-click (Pan)
#             self.panning_x += dx * 0.5
#             self.panning_y -= dy * 0.5 # Y is inverted

#     def zoom(self, delta):
#         """Handle mouse wheel zoom."""
#         # Clamp zoom to prevent flipping inside sphere
#         new_zoom = self.zoom_distance + delta * 0.5
#         self.zoom_distance = min(new_zoom, -self.radius - 0.5)

#     def set_camera_view(self, rotation_x=None, rotation_y=None, zoom=None, pan_x=None, pan_y=None):
#         """
#         *** YOUR REQUESTED FUNCTION ***
#         Programmatically sets the camera position.
#         Any parameter set to 'None' will not be changed.
#         """
#         LOG.info(f"Setting camera: rot_x={rotation_x}, rot_y={rotation_y}, zoom={zoom}")
#         if rotation_x is not None:
#             self.rotation_x = rotation_x
#         if rotation_y is not None:
#             self.rotation_y = rotation_y
#         if zoom is not None:
#             self.zoom_distance = min(zoom, -self.radius - 0.5) # Clamp
#         if pan_x is not None:
#             self.panning_x = pan_x
#         if pan_y is not None:
#             self.panning_y = pan_y


class OffscreenPygletRenderer:
    """Render a pyglet 3D textured sphere offscreen and expose controls for interaction."""

    def __init__(self,radius=10, resolution=100):
        self.width = 600
        self.height = 400
        self.radius = radius
        self.resolution = resolution

        # Camera / transform state - based on sphere_bkp.py
        self.zoom_distance = -20.0
        self.rotation_x = -100.0  # Yaw (around Y-axis)
        self.rotation_y = 40.0    # Pitch (around X-axis)
        self.panning_x = 0.0
        self.panning_y = 0.0

        # Sphere, texture, and pin state
        self.texture = None
        self.bg_sprite = None
        self.batch = None
        self.pins = [] # Stores [x, y, z] for pins
        self.add_pin = None # Temporary pin holder

        # pyglet resources
        self.window = None
        self.vertex_list = None
        
        # create offscreen window and GL objects
        self._create_offscreen()

    def map_value(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def sphere(self):
        """
        Create a UV sphere mesh with proper lat/lon mapping (from sphere_bkp.py)
        """
        verticals = []
        texture_coords = []
        indices = []
        res = self.resolution
        r = self.radius
        
        for i in range(res + 1):
            lon = self.map_value(i, 0, res, -pi, pi)
            u = -(i / res)
            
            for j in range(res + 1):
                lat = self.map_value(j, 0, res, -pi/2, pi/2)
                v = j / res

                # Sphere coordinates (from sphere_bkp.py)
                x = r * cos(lat) * cos(lon)
                y = r * sin(lat)
                z = r * cos(lat) * sin(lon)
                
                verticals.extend((x, y, z))
                texture_coords.extend((u, v))
                
        for i in range(res):
            for j in range(res):
                p1 = i * (res + 1) + j
                p2 = p1 + 1 
                p3 = (i + 1) * (res + 1) + j
                p4 = p3 + 1

                # Two triangles for each quad
                indices.extend((p1, p2, p3))
                indices.extend((p2, p4, p3))
                
        return verticals, texture_coords, indices

    def _load_texture(self):
        """Loads earth texture and star background."""
        # Note: The path logic here relies on the structure you previously used (up two dirs to find 'assets')
        try:
            image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..', 'assets/textures', 'earth.jpg'))
            image = pyglet.image.load(image_path)
            self.texture = image.get_texture()
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
            LOG.info("Texture 'earth.jpg' loaded successfully.")
        except Exception as e:
            LOG.error(f"Error loading 'earth.jpg' as texture: {e}")
            self.texture = None
            
        try:
            bg_img_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..', 'assets/textures', 'stars.jpg'))
            bg_img = pyglet.image.load(bg_img_path)
            self.bg_sprite = pyglet.sprite.Sprite(bg_img, x=0, y=0, batch=None)
        except Exception as e:
            LOG.error(f"Error loading 'stars.jpg' for background: {e}")
            self.bg_sprite = None

    def _create_offscreen(self):
        # Create a hidden pyglet window (offscreen rendering)
        try:
            config = pyglet.gl.Config(double_buffer=True, depth_size=24)
            self.window = pyglet.window.Window(
                width=self.width, 
                height=self.height, 
                visible=False, 
                config=config
            )
            # self.width = self.window.width
            # self.height = self.window.height
            
            # make context current
            try:
                self.window.context.set_current()
            except Exception:
                self.window.switch_to()

            # prepare geometry (textured mesh from sphere_bkp.py)
            vertices, texture_coords, indices = self.sphere()
            num_vertices = len(vertices) // 3

            # Load textures
            self._load_texture()

            self.batch = pyglet.graphics.Batch()
            
            self.vertex_list = self.batch.add_indexed(
                num_vertices,
                gl.GL_TRIANGLES,
                None,
                indices,
                ('v3f', vertices),
                ('t2f', texture_coords)
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
        
    def _draw_background(self):
        if not self.bg_sprite:
            return
            
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        # Ensure background scales with the current viewport size
        if self.bg_sprite.image.width > 0 and self.bg_sprite.image.height > 0:
            self.bg_sprite.scale_x = self.width / self.bg_sprite.image.width
            self.bg_sprite.scale_y = self.height / self.bg_sprite.image.height
            
        gl.gluOrtho2D(0, self.width, 0, self.height)

        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_CULL_FACE)

        self.bg_sprite.draw()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

    def _setup_frame_3d(self):
        """Set up 3D rendering pipeline (projection/modelview matrices)"""
        gl.glViewport(0, 0, self.width, self.height)
        
        # texturing
        if self.texture:
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(self.texture.target, self.texture.id)
        else:
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glColor3f(1.0, 0.5, 0.5) # Fallback color

        gl.glEnable(gl.GL_CULL_FACE)

        # projection matrix
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # camera settings
        aspect = self.width / self.height
        gl.gluPerspective(60, aspect, 0.1, 100) 
            
        # model view Matrix
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        gl.glTranslatef(0, 0, self.zoom_distance)
        gl.glTranslatef(self.panning_x, self.panning_y, 0)
        
        gl.glRotatef(self.rotation_y, 1, 0, 0)
        gl.glRotatef(self.rotation_x, 0, 1, 0)

    def _draw_pin(self):
        """Draws accumulated pins and adds a new pin if one was clicked."""
        if self.add_pin:
            self.pins.append(self.add_pin)
            self.add_pin = None
        
        if not self.pins:
            return
            
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glPointSize(10)
        
        gl.glColor3f(1, 0, 0) # Red color for pins
        gl.glBegin(gl.GL_POINTS)

        for pin in self.pins:
            gl.glVertex3f(pin[0], pin[1], pin[2])

        gl.glEnd()
        gl.glColor3f(1, 1, 1) # Reset color
        gl.glEnable(gl.GL_TEXTURE_2D)

    # --- RAY CASTING LOGIC (from sphere_bkp.py, with Z-component fix) ---

    def ray_sphere_intersection(self, ray_origin, ray_dir, sphere_center, sphere_radius):
        """Calculate ray-sphere intersection"""
        oc = [ray_origin[i] - sphere_center[i] for i in range(3)]
        
        a = sum(ray_dir[i] * ray_dir[i] for i in range(3))
        b = 2.0 * sum(oc[i] * ray_dir[i] for i in range(3))
        c = sum(oc[i] * oc[i] for i in range(3)) - sphere_radius * sphere_radius
        
        delta = b * b - 4 * a * c
        
        if delta < 0:
            return None
        
        x1 = (-b - sqrt(delta)) / (2.0 * a)
        x2 = (-b + sqrt(delta)) / (2.0 * a)

        # Find the intersection point that is closest and in front of the ray origin
        x = None
        if x1 > 0 and (x1 < x2 or x2 <= 0):
            x = x1
        elif x2 > 0:
            x = x2
        
        if x is None:
            return None

        intersection = [ray_origin[i] + x * ray_dir[i] for i in range(3)]
        return intersection

    def xyz_to_lonlat(self, x, y, z):
        """Convert 3D point on sphere to lon/lat in degrees"""
        radius = sqrt(x*x + y*y + z*z)
        if radius == 0:
            return 0 , 0

        # Latitude (theta)
        lat_radio = max(-1.0, min(1.0, y / radius))
        lat = asin(lat_radio) * 180 / pi
        
        # Longitude (phi)
        lon = -(atan2(z, x) * 180 / pi)
        return lon, lat

    def get_lat_lon_from_screen_click(self, x, y):
        """Perform raycasting to find the lat/lon of a screen click (x, y)."""
        if self.window is None:
            return None
            
        try:
            self.window.switch_to()

            model_matrix = (gl.GLdouble * 16)()
            proj_matrix = (gl.GLdouble * 16)()
            viewport = (gl.GLint * 4)()
            gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX, model_matrix)
            gl.glGetDoublev(gl.GL_PROJECTION_MATRIX, proj_matrix)
            gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)

            near_x, near_y, near_z = gl.GLdouble(), gl.GLdouble(), gl.GLdouble()
            far_x, far_y, far_z = gl.GLdouble(), gl.GLdouble(), gl.GLdouble()

            gl.gluUnProject(x, y, 0.0, model_matrix, proj_matrix, viewport, near_x, near_y, near_z)
            gl.gluUnProject(x, y, 1.0, model_matrix, proj_matrix, viewport, far_x, far_y, far_z)

            ray_origin = [near_x.value, near_y.value, near_z.value]
            
            # Calculate normalized ray direction
            ray_dir = [
                far_x.value - near_x.value,
                far_y.value - near_y.value,
                far_z.value - near_z.value # <-- CORRECTED Z-component
            ]
            length = sqrt(sum(d*d for d in ray_dir))
            if length == 0:
                return None
            ray_dir = [d/length for d in ray_dir]
            
            intersection = self.ray_sphere_intersection(ray_origin, ray_dir, [0, 0, 0], self.radius)
            
            if intersection:
                self.add_pin = intersection # Mark pin to be drawn next frame
                lon, lat = self.xyz_to_lonlat(*intersection)
                LOG.info(f"Clicked at Latitude, Longitude: {lat}, {lon}")
                return lon, lat
            return None
            
        except Exception as e:
            LOG.error(f"Error calculating coordinates: {e}")
            return None


    # --- PUBLIC CONTROL AND DRAWING METHODS ---
    
    def drag(self, dx, dy, button=1):
        """Handle mouse drag for rotation and panning."""
        if button == 1: # Left button (rotation)
            self.rotation_x += dx * 0.5
            self.rotation_y += dy * 0.5
            self.rotation_y = max(-90, min(90, self.rotation_y)) # Clamp pitch
        elif button == 2: # Middle button (panning)
            self.panning_x += dx * 0.05
            self.panning_y -= dy * 0.05

    def zoom(self, delta):
        """Zoom in/out with mouse wheel delta."""
        new_zoom = self.zoom_distance + delta * 1.5
        # Ensure sphere remains visible/is not clipped (using radius 10)
        if new_zoom < -(self.radius + 0.5):
            self.zoom_distance = new_zoom

    def resize(self, new_width, new_height):
        """Manually update the renderer's size and GL context (Fixes scaling)."""
        if self.window and (new_width != self.width or new_height != self.height):
            self.window.set_size(new_width, new_height)
            self.width = new_width
            self.height = new_height
            
            try:
                self.window.context.set_current()
            except Exception:
                self.window.switch_to()
            
            # glViewport is called in _setup_frame_3d, but setting window size is key
            LOG.debug(f'Renderer resized to {new_width}x{new_height}')

    def draw_frame(self):
        """Render one frame and return a PIL Image (RGBA)."""
        if self.window is None:
            return None

        try:
            self.window.switch_to()

            # Clear buffer
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # 1. Draw Background (2D)
            self._draw_background()

            # 2. Setup 3D View
            self._setup_frame_3d()

            # 3. Draw Sphere
            self.batch.draw()
            
            # 4. Draw overlays (Pins)
            self._draw_pin()
            
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

# Example usage (for testing the class structure):
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     
#     # Instantiate the renderer
#     renderer = OffscreenPygletRenderer(
#         width=cfg.configurations.MIN_WINDOW_WIDTH, 
#         height=cfg.configurations.MIN_WINDOW_HEIGHT, 
#         radius=10, 
#         resolution=100
#     )
#     
#     print(f"Renderer initialized with resolution: {renderer.width}x{renderer.height}")
#     
#     # You would normally integrate this into a GUI's main loop/timer
#     pyglet.clock.schedule_interval(renderer.update, 1/10.0) 
#     
#     # Simulating a camera interaction
#     renderer.drag(dx=50, dy=20, button=1)
#     renderer.zoom(-1.0)
#     
#     # Simulating a click (400, 300 is the center of an 800x600 window)
#     renderer.get_lat_lon_from_screen_click(400, 300)
#     
#     # Simulate drawing a frame
#     # frame_image = renderer.draw_frame()
#     # if frame_image:
#     #     frame_image.save("rendered_frame.png")
#     #     print("Frame rendered and saved to rendered_frame.png")
#     
#     # Note: If running this as a script, pyglet.app.run() is needed
#     # for the clock and GL context to persist, but for offscreen use
#     # within a larger app, you just call draw_frame() on demand.