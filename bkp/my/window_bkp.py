import customtkinter as ctk
from math import cos, pi, sin
import pyglet
from pyglet import gl
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import logging
from PIL import Image, ImageTk
import os
import sys
# Ensure project root is on sys.path so sibling packages (like `config`) can be imported
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
import config.app_config as cfg

conf = cfg.configurations

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
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


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('MassFlight - 3D Sphere')
        self.geometry('900x700')
        self.minsize(conf.MIN_WINDOW_WIDTH, conf.MIN_WINDOW_HEIGHT)
        self._set_appearance_mode('System')
        try:
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icon', 'icon.ico'))
            self.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Icon load failed: {e}")

        # Configure grid: left sidebar + right display
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Buttons
        self.button0 = ctk.CTkButton(
            self.sidebar, 
            fg_color=(conf.LIGHTMODE_BUTTON_COLOR, conf.DARKMODE_BUTTON_COLOR), 
            text_color=(conf.LIGHTMODE_TEXT_COLOR, conf.DARKMODE_TEXT_COLOR), 
            text="3D View", 
            command=self.show_3d_view
        )
        self.button1 = ctk.CTkButton(
            self.sidebar,
            fg_color=(conf.LIGHTMODE_BUTTON_COLOR, conf.DARKMODE_BUTTON_COLOR), 
            text_color=(conf.LIGHTMODE_TEXT_COLOR, conf.DARKMODE_TEXT_COLOR),  
            text="Velocity", 
            command=self.plot_graph1
        )
        self.button2 = ctk.CTkButton(
            self.sidebar,
            fg_color=(conf.LIGHTMODE_BUTTON_COLOR, conf.DARKMODE_BUTTON_COLOR), 
            text_color=(conf.LIGHTMODE_TEXT_COLOR, conf.DARKMODE_TEXT_COLOR), 
            text="Acceleration", 
            command=self.plot_graph2
        )
        self.button3 = ctk.CTkButton(
            self.sidebar,
            fg_color=(conf.LIGHTMODE_BUTTON_COLOR, conf.DARKMODE_BUTTON_COLOR), 
            text_color=(conf.LIGHTMODE_TEXT_COLOR, conf.DARKMODE_TEXT_COLOR),  
            text="Altitude", 
            command=self.plot_graph3
        )

        self.button0.grid(row=0, column=0, padx=20, pady=10, sticky='ew')
        self.button1.grid(row=1, column=0, padx=20, pady=10, sticky='ew')
        self.button2.grid(row=2, column=0, padx=20, pady=10, sticky='ew')
        self.button3.grid(row=3, column=0, padx=20, pady=10, sticky='ew')

        # Right display area
        self.display_area = ctk.CTkFrame(self)
        self.display_area.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
        self.display_area.grid_rowconfigure(0, weight=1)
        self.display_area.grid_columnconfigure(0, weight=1)

        # Create renderer (deferred heavy resources are created inside renderer)
        self.renderer = OffscreenPygletRenderer(width=conf.MIN_WINDOW_WIDTH, height=conf.MIN_WINDOW_HEIGHT, resolution=50)

        # Create label to show frames inside display area
        self.img_label = ctk.CTkLabel(self.display_area, text='')
        self.img_label.grid(row=0, column=0, sticky='nsew')

        # bind mouse events to label
        self.img_label.bind('<ButtonPress-1>', self._on_press)
        self.img_label.bind('<B1-Motion>', self._on_drag)
        # Right-button for panning
        self.img_label.bind('<ButtonPress-2>', self._on_press_pan)
        self.img_label.bind('<B2-Motion>', self._on_pan)
        # Mouse wheel for zoom
        self.img_label.bind('<MouseWheel>', self._on_wheel)

        # mouse tracking for drag
        self._last_x = None
        self._last_y = None
        self.photo = None
        # currently shown widget (label or canvas)
        self.current_display = None

        # Start animation loop
        self.after(16, self._update_frame)

        # Show 3D view by default
        self.show_3d_view()

    def _on_press(self, event):
        self._last_x = event.x
        self._last_y = event.y

    def _on_press_pan(self, event):
        # start pan
        self._last_x = event.x
        self._last_y = event.y

    def _on_drag(self, event):
        if self._last_x is None:
            self._last_x = event.x
            self._last_y = event.y
            return
        dx = event.x - self._last_x
        dy = event.y - self._last_y
        self._last_x = event.x
        self._last_y = event.y
        if self.renderer:
            # left-drag: rotate
            self.renderer.drag(dx, dy, button=1)

    def _on_pan(self, event):
        if self._last_x is None:
            self._last_x = event.x
            self._last_y = event.y
            return
        dx = event.x - self._last_x
        dy = event.y - self._last_y
        self._last_x = event.x
        self._last_y = event.y
        if self.renderer:
            # right-drag: pan (button==2 semantics)
            self.renderer.drag(dx, dy, button=2)

    def _on_wheel(self, event):
        # event.delta positive for up
        if self.renderer:
            self.renderer.zoom(event.delta/150)

    def _update_frame(self):
        if self.renderer is None:
            return
        img = self.renderer.draw_frame()
        if img is not None:
            # convert to PhotoImage
            self.photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self.photo)
            # keep reference
            self.img_label.image = self.photo
        self.after(16, self._update_frame)

    def clear_display(self):
        """Clear the current display widget."""
        if self.current_display:
            # If the display has a cleanup hook, call it
            if hasattr(self.current_display, 'on_destroy'):
                try:
                    self.current_display.on_destroy()
                except Exception:
                    pass
            try:
                self.current_display.grid_forget()
            except Exception:
                try:
                    self.current_display.destroy()
                except Exception:
                    pass
            self.current_display = None

    def show_3d_view(self):
        """Show the 3D sphere visualization."""
        self.clear_display()
        # ensure img_label is visible in the display area
        self.img_label.grid(row=0, column=0, sticky='nsew')
        self.current_display = self.img_label

    def plot_graph1(self):
        """Plot velocity graph."""
        self.clear_display()
        fig = Figure(figsize=(6, 5), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, t**2)
        fig.suptitle("Velocity")

        canvas = FigureCanvasTkAgg(fig, master=self.display_area)
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        canvas.draw()
        self.current_display = canvas.get_tk_widget()

    def plot_graph2(self):
        """Plot acceleration graph."""
        self.clear_display()
        fig = Figure(figsize=(6, 5), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
        fig.suptitle("Acceleration")

        canvas = FigureCanvasTkAgg(fig, master=self.display_area)
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        canvas.draw()
        self.current_display = canvas.get_tk_widget()

    def plot_graph3(self):
        """Plot altitude graph."""
        self.clear_display()
        fig = Figure(figsize=(6, 5), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, t**3)
        fig.suptitle("Altitude")

        canvas = FigureCanvasTkAgg(fig, master=self.display_area)
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        canvas.draw()
        self.current_display = canvas.get_tk_widget()

def run():
    app = App()
    app.mainloop()

