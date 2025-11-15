import customtkinter as ctk
import tkinter as tk
import pyvista as pv
import threading

class SimpleCTkPyVista(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simple 3D Sphere")
        self.geometry("600x400")
        
        # Simple layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="3D Sphere Viewer", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        # Show sphere button
        show_btn = ctk.CTkButton(main_frame, text="Show 3D Sphere", 
                               command=self.show_sphere, height=40)
        show_btn.pack(pady=20)
        
        self.plotter = None
        
    def show_sphere(self):
        def create_sphere():
            try:
                self.plotter = pv.Plotter()
                sphere = pv.Sphere()
                self.plotter.add_mesh(sphere, color='lightblue')
                self.plotter.show()
            except Exception as e:
                print(f"Error displaying sphere: {e}")
        
        thread = threading.Thread(target=create_sphere, daemon=True)
        thread.start()
        thread.get_tk_widget.grid(row=1, column=0, sticky="nsew")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = SimpleCTkPyVista()
    app.mainloop()