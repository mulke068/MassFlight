import customtkinter
import tkintermapview

def addPositionCords(coords, map_widget):
    lat, lon = coords
    print(f"Latetute: {lat} Longetute: {lon} Cords")
    map_widget.delete_all_marker()
    map_widget.set_marker(lat,lon, "Position")

def mainFrame():
    app = customtkinter.CTk()
    app.title("MassFlight")
    app.geometry("800x800")
    
    
    map_widget = tkintermapview.TkinterMapView(app, width=800 , height=800)
    map_widget.pack(fill="both", expand=True)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga")
    # map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
    map_widget.place(relx= 0.5, rely= 0.5 , anchor=customtkinter.CENTER)
    map_widget.set_position(49.6117, 6.1319)
    map_widget.set_zoom(10)
    
    map_widget.add_left_click_map_command(lambda coords : addPositionCords(coords, map_widget=map_widget))
    
    app.mainloop()

if __name__ == "__main__":
    
    mainFrame()

