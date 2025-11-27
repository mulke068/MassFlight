import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from math import cos, pi, sin
import pyglet
from pyglet import gl, image
from PIL import Image
import io
import logging
import threading
import time

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
LOG = logging.getLogger(__name__)


class PygletOffscreenRenderer(ctk.CTkFrame):
    """Render pyglet 3D scene to texture and display in CTK."""
    
    def __init__(self, parent, width=600, height=400):
        super().__init__(parent, fg_color="black")
        self.width = width
        self.height = height
        
        # OpenGL state variables
        self.rotation = 0
        self.rotation_x = 0
        self.rotation_y = 0
        self.panning_x = 0
        self.panning_y = 0
        self.zoom_distance = -6
        
        # Pyglet resources
        self.window = None
        self.batch = None
        self.vertex_list = None
        self.points = None
        self.num_points = 0
        
        # Create offscreen canvas for rendering
        self._create_offscreen_window()
        
        # Create Tkinter label to display rendered frames
        self.canvas_label = ctk.CTkLabel(self, text="Loading 3D View...", fg_color="black")
        self.canvas_label.pack(fill=ctk.BOTH, expand=True)
        
        # Start rendering loop
        self.running = True
        self._animate()
    
    def _create_offscreen_window(self):
        """Create an offscreen pyglet window for rendering."""
        try:
            # Use offscreen rendering (headless)
            self.window = pyglet.window.Window(
                width=self.width,
                height=self.height,
                caption="3D Sphere Offscreen",
                visible=False  # Offscreen rendering
            )
            
            # Generate sphere data
            self.points = self.sphere(2, 50)
            self.num_points = len(self.points) // 3
            
            # Create graphics batch
            self.batch = pyglet.graphics.Batch()
            self.vertex_list = self.batch.add(
                self.num_points,
                gl.GL_POINTS,
                None,
                ('v3f', self.points),
                ('c3B', (255, 255, 255) * self.num_points)
            )
            
            LOG.info("Offscreen pyglet window created successfully")
        except Exception as e:
            LOG.error(f"Error creating offscreen window: {e}")
    
    def map_value(self, x, in_min, in_max, out_min, out_max):
        """Map a value from one range to another."""
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def sphere(self, radius, resolution_points):
        """Generate sphere vertices."""
        verticals = []
        for i in range(0, resolution_points):
            lon = self.map_value(i, 0, resolution_points, -pi, pi)
            for j in range(0, resolution_points):
                lat = self.map_value(j, 0, resolution_points, -pi/2, pi/2)

                x = radius * sin(lon) * cos(lat)
                y = radius * sin(lon) * sin(lat)
                z = radius * cos(lon)

                verticals.extend((x, y, z))
        return verticals
    
    def setup_3d(self):
        """Set up 3D OpenGL projection and model matrices."""
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glViewport(0, 0, self.window.width, self.window.height)
        gl.glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # Projection matrix
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # Camera settings
        aspect = self.window.width / self.window.height
        gl.gluPerspective(60, aspect, 0.1, 100)
            
        # Model matrix
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glTranslatef(self.panning_x, self.panning_y, self.zoom_distance)
        gl.glRotatef(self.rotation_x, 0, 1, 0)
        gl.glRotatef(self.rotation_y, 1, 0, 0)
        
        # Point visibility settings
        gl.glPointSize(2)
        gl.glEnable(gl.GL_POINT_SMOOTH)

    def draw_frame(self):
        """Draw and capture one frame."""
        if self.window is None or self.batch is None:
            return None
        
        try:
            self.window.clear()
            self.setup_3d()
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # Rotate automatically
            self.rotation += 0.5
            if self.rotation > 360:
                self.rotation = 0
            
            # Apply extra rotation
            gl.glRotatef(self.rotation, 0, 0, 1)
            
            self.batch.draw()
            
            # Capture the frame as image data
            image_data = pyglet.image.get_buffer_manager().get_color_buffer()
            data = image_data.get_image_data()
            
            # Convert to PIL Image
            pil_image = Image.frombytes(
                'RGBA',
                (self.width, self.height),
                data.get_data('RGBA', self.width * 4)
            )
            # Flip vertically (OpenGL to PIL coordinate system)
            pil_image = pil_image.transpose(Image.FLIP_TOP_BOTTOM)
            
            return pil_image
        except Exception as e:
            LOG.error(f"Error drawing frame: {e}")
            return None
    
    def _animate(self):
        """Animation loop for rendering."""
        if self.running:
            try:
                frame = self.draw_frame()
                if frame:
                    # Convert PIL image to PhotoImage
                    photo = ctk.CTkImage(light_image=frame, dark_image=frame, size=(self.width, self.height))
                    self.canvas_label.configure(image=photo, text="")
                    self.canvas_label.image = photo  # Keep a reference
            except Exception as e:
                LOG.error(f"Error in animation loop: {e}")
            
            self.after(16, self._animate)  # ~60 FPS

    def on_mouse_scroll(self, delta):
        """Handle mouse scroll for zoom."""
        self.zoom_distance += delta * 0.1
    
    def on_mouse_drag(self, dx, dy, button):
        """Handle mouse drag for rotation."""
        if button == 1:
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
        elif button == 2:
            self.panning_x += dx * 0.1
            self.panning_y += dy * 0.1
    
    def destroy(self):
        """Clean up resources."""
        self.running = False
        if self.window:
            self.window.close()
        super().destroy()


class App(ctk.CTk):
    # Color palette
    lightomodeButtonColor = "#D3D3D3"
    lightmodeTextColor = "#000000"
    darkmodeButtonColor = "#2B2B2B"
    darkmodeTextColor = "#FFFFFF"

    def __init__(self):
        super().__init__()
        self.geometry("1000x700")
        self.title("MassFlight V0.1")
        self.minsize(800, 600)

        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Store current display
        self.current_display = None
        
        self.widgets()
    
    def widgets(self):
        # Left sidebar frame
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # Buttons
        self.button0 = ctk.CTkButton(
            self.sidebar, 
            fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), 
            text_color=(self.lightmodeTextColor, self.darkmodeTextColor), 
            text="3D View", 
            command=self.show_3d_view
        )
        self.button1 = ctk.CTkButton(
            self.sidebar,
            fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), 
            text_color=(self.lightmodeTextColor, self.darkmodeTextColor), 
            text="Velocity", 
            command=self.plot_graph1
        )
        self.button2 = ctk.CTkButton(
            self.sidebar,
            fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), 
            text_color=(self.lightmodeTextColor, self.darkmodeTextColor), 
            text="Acceleration", 
            command=self.plot_graph2
        )
        self.button3 = ctk.CTkButton(
            self.sidebar,
            fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), 
            text_color=(self.lightmodeTextColor, self.darkmodeTextColor), 
            text="Altitude", 
            command=self.plot_graph3
        )
        
        self.button0.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.button1.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.button2.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.button3.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Right display area
        self.display_area = ctk.CTkFrame(self)
        self.display_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.display_area.grid_rowconfigure(0, weight=1)
        self.display_area.grid_columnconfigure(0, weight=1)
        
        # Show 3D view by default
        self.show_3d_view()
    
    def clear_display(self):
        """Clear the current display widget."""
        if self.current_display:
            self.current_display.destroy()
            self.current_display = None
    
    def show_3d_view(self):
        """Show the 3D sphere visualization with pyglet."""
        self.clear_display()
        
        # Create embedded pyglet renderer
        self.pyglet_frame = PygletOffscreenRenderer(self.display_area, width=600, height=400)
        self.pyglet_frame.grid(row=0, column=0, sticky="nsew")
        
        self.current_display = self.pyglet_frame
    
    def plot_graph1(self):
        """Plot velocity graph."""
        self.clear_display()
        
        fig = Figure(figsize=(6, 5), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, t**2)
        fig.suptitle("Velocity")

        canvas = FigureCanvasTkAgg(fig, master=self.display_area)
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
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
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
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
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        canvas.draw()
        
        self.current_display = canvas.get_tk_widget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
