import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure


class App(ctk.CTk):
    #Farbpalette
    lightomodeButtonColor = "#D3D3D3"
    lightmodeTextColor  = "#000000"
    darkmodeButtonColor = "#2B2B2B"
    darkmodeTextColor  = "#FFFFFF"

    def __init__(self):
        super().__init__()  # Elternkonstruktor aufrufen
        self.geometry("800x700")
        self.title("MassFlight V0.1")
        self.minsize(600, 500)
        self.iconbitmap("favicon.ico")

        # grid fur das Hauptfenster konfigurieren   
        self.grid_rowconfigure(0, weight=0)
        self.grid_columnconfigure((0, 1), weight=1)

        #self.rightSidebar = ctk.CTkScrollableFrame(self, width=600, height=600)
        #self.rightSidebar.grid(row=0, column=1, rowspan=14, padx=20, pady=20, sticky="ns")$
        self.widgets()
    
    def widgets(self):
        self.button0 = ctk.CTkButton(self, fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), text_color=(self.lightmodeTextColor, self.darkmodeTextColor), text="Map View" )#, command=self.map)
        self.button1 = ctk.CTkButton(self, fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), text_color=(self.lightmodeTextColor, self.darkmodeTextColor), text="Velovity", command=self.plot_graph1)
        self.button2 = ctk.CTkButton(self, fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), text_color=(self.lightmodeTextColor, self.darkmodeTextColor), text="Acceleration", command=self.plot_graph2)
        self.button3 = ctk.CTkButton(self, fg_color=(self.lightomodeButtonColor, self.darkmodeButtonColor), text_color=(self.lightmodeTextColor, self.darkmodeTextColor), text="Altitude", command=self.plot_graph3)
        self.button0.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.button1.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.button2.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.button3.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

    def plot_graph1(self):
        # clear previous plots
        for w in self.grid_slaves(row=None, column=1):
            w.grid_forget()

        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, t**2)

        # grid
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, columnspan=3, rowspan=20)
        self.canvas.draw()
        # grid nav
        self.toolbarFrame = ctk.CTkFrame(master=self)
        self.toolbarFrame.grid(row=21, column=1, padx= 30, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)

    def plot_graph2(self):
        for w in self.grid_slaves(row=None, column=1):
            w.grid_forget()
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, columnspan=3, rowspan=20)
        self.canvas.draw()

        self.toolbarFrame = ctk.CTkFrame(master=self)
        self.toolbarFrame.grid(row=21, column=1, padx= 30, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)

    def plot_graph3(self):
        for w in self.grid_slaves(row=None, column=1):
            w.grid_forget()
        fig = Figure(figsize=(5, 5), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t,t**3)

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, columnspan=3, rowspan=20)
        self.canvas.draw()

        self.toolbarFrame = ctk.CTkFrame(master=self)
        self.toolbarFrame.grid(row=21, column=1, padx= 30, sticky="ew")
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)

if __name__ == "__main__":
    app = App()
    app.mainloop()
