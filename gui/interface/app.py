import logging
import os
import sys
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image, ImageTk
from customtkinter import CTkImage

# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..'))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)

from config.app_config import AppConfig as cfg
from gui.rendering.offscreen import OffscreenPygletRenderer

LOG = logging.getLogger(__name__)

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('MassFlight - 3D Sphere')
        self.geometry('900x700')
        self.minsize(cfg.MIN_WINDOW_WIDTH, cfg.MIN_WINDOW_HEIGHT)
        self._set_appearance_mode('System')
        
        try:
            icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..', 'assets/favicon', 'icon.ico'))
            self.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Icon load failed: {e}")

        # Configure grid: left sidebar + right display
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Left sidebar frame (unchanged)
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.sidebar.grid_rowconfigure(4, weight=1)

        # Buttons (unchanged)
        self.button0 = ctk.CTkButton(
            self.sidebar, 
            fg_color=(cfg.LIGHTMODE_BUTTON_COLOR, cfg.DARKMODE_BUTTON_COLOR), 
            text_color=(cfg.LIGHTMODE_TEXT_COLOR, cfg.DARKMODE_TEXT_COLOR), 
            text="3D View", 
            command=self.show_3d_view
        )
        self.button1 = ctk.CTkButton(
            self.sidebar,
            fg_color=(cfg.LIGHTMODE_BUTTON_COLOR, cfg.DARKMODE_BUTTON_COLOR), 
            text_color=(cfg.LIGHTMODE_TEXT_COLOR, cfg.DARKMODE_TEXT_COLOR),  
            text="Velocity", 
            command=self.plot_graph1
        )
        self.button2 = ctk.CTkButton(
            self.sidebar,
            fg_color=(cfg.LIGHTMODE_BUTTON_COLOR, cfg.DARKMODE_BUTTON_COLOR), 
            text_color=(cfg.LIGHTMODE_TEXT_COLOR, cfg.DARKMODE_TEXT_COLOR), 
            text="Acceleration", 
            command=self.plot_graph2
        )
        self.button3 = ctk.CTkButton(
            self.sidebar,
            fg_color=(cfg.LIGHTMODE_BUTTON_COLOR, cfg.DARKMODE_BUTTON_COLOR), 
            text_color=(cfg.LIGHTMODE_TEXT_COLOR, cfg.DARKMODE_TEXT_COLOR),  
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
        
        # Bind <Configure> for automatic resizing
        self.display_area.bind('<Configure>', self._on_resize) 
        
        # Create renderer (initial size may be small, but it will be corrected below)
        self.renderer = OffscreenPygletRenderer(radius=10, resolution=100)
        
        # Create label to show frames inside display area
        self.img_label = ctk.CTkLabel(self.display_area, text='')
        self.img_label.grid(row=0, column=0, sticky='')

        # Bind mouse events
        self.img_label.bind('<ButtonPress-1>', self._on_press)
        self.img_label.bind('<B1-Motion>', self._on_drag)
        self.img_label.bind('<ButtonPress-2>', self._on_press_pan)
        self.img_label.bind('<B2-Motion>', self._on_pan)
        self.img_label.bind('<MouseWheel>', self._on_wheel)
        self.img_label.bind('<ButtonPress-3>', self._on_pin_drop) # Right-click for raycasting

        # mouse tracking for drag
        self._last_x = None
        self._last_y = None
        self.photo = None
        self.current_display = None

        # Start animation loop
        self.after(16, self._update_frame)

        # 🟢 FIX: Schedule initial setup after the main window has stabilized (100ms)
        self.after(100, self._initial_setup)


### ---- Initial Setup Fix
    def _initial_setup(self):
        """Called once after the main window has rendered to ensure proper sizing."""
        # 1. Set the initial view to 3D
        self.show_3d_view()
        
        # 2. Force the resize handler to run with the now-correct size of the display_area.
        # This immediately corrects the Pyglet viewport and fixes the gray screen/delayed loading.
        self._on_resize(event=type('ConfigureEvent', (object,), {'widget': self.display_area})())


### ---- Mouse Inputs
    # (Methods _on_press, _on_press_pan, _on_drag, _on_pan, _on_wheel are unchanged)
    def _on_press(self, event):
        self._last_x = event.x
        self._last_y = event.y

    def _on_press_pan(self, event):
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
            self.renderer.drag(dx, dy, button=2)

    def _on_wheel(self, event):
        if self.renderer:
            self.renderer.zoom(event.delta/150)

    # _on_pin_drop (Raycasting Y-Inversion fix - crucial for pin drop accuracy)
    def _on_pin_drop(self, event):
        """Handle right-click (Button 3) to drop a pin on the sphere."""
        if self.renderer:
            # Tkinter y=0 (top) needs to be inverted to Pyglet y=0 (bottom)
            opengl_y = self.renderer.height - event.y
            self.renderer.get_lat_lon_from_screen_click(event.x, opengl_y)

    # _on_resize (Automatic Resizing fix)
    def _on_resize(self, event):
        """Handle resizing of the display area and propagate it to the renderer."""
        if event.widget == self.display_area:
            new_width = self.display_area.winfo_width()
            new_height = self.display_area.winfo_height()

            if self.renderer and new_width > 0 and new_height > 0 and (new_width != self.renderer.width or new_height != self.renderer.height):
                self.renderer.resize(new_width, new_height)
                

## -- Views
    def _update_frame(self):
        # Schedule the next update first
        self.after(16, self._update_frame) 

        if self.renderer is None:
            return
        
        img = self.renderer.draw_frame()
        if img is not None:
            # 🟢 FIX: Use CTkImage for proper scaling in CustomTkinter
            # The size parameter ensures the CTkLabel respects the image dimensions.
            # We use the PIL Image size directly from the renderer output.
            
            # Note: If CTkImage is not available or causes issues, 
            # fall back to the old method but be aware of the stretching risk.
            try:
                # Preferred method for CustomTkinter
                self.photo = CTkImage(
                    light_image=img, 
                    dark_image=img, 
                    size=(img.width, img.height) # 👈 CRITICAL: Set size explicitly
                )
                self.img_label.configure(image=self.photo)
                # Note: CTkImage objects often don't need the self.img_label.image reference.
                
            except NameError:
                # Fallback to ImageTk.PhotoImage if CTkImage import fails (less reliable for scaling)
                self.photo = ImageTk.PhotoImage(img)
                self.img_label.configure(image=self.photo)
                self.img_label.image = self.photo # Keep reference
        
    def clear_display(self):
        """Clear the current display widget."""
        if self.current_display:
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
        self.img_label.grid(row=0, column=0, sticky='nsew')
        self.current_display = self.img_label
        
        # Manually trigger a resize update when switching views
        # We wrap it in a try-except because winfo_width/height can be 0 or 1 
        # when the widget is first being initialized.
        try:
            self._on_resize(event=type('ConfigureEvent', (object,), {'widget': self.display_area})())
        except Exception:
            pass


    def plot_graph1(self):
        # ... (unchanged graph plotting code)
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
        # ... (unchanged graph plotting code)
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
        # ... (unchanged graph plotting code)
        self.clear_display()
        fig = Figure(figsize=(6, 5), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, t**3)
        fig.suptitle("Altitude")

        canvas = FigureCanvasTkAgg(fig, master=self.display_area)
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        canvas.draw()
        self.current_display = canvas.get_tk_widget()