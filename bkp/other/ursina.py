from ursina import *

# 1. Initialize the engine
app = Ursina()

# 2. Create the Earth sphere
# Make sure you have an image file named 'earth_map.jpg' in your project folder
earth = Entity(
    model='sphere',
    texture='earth_map', # Maps the image onto the sphere
    scale=20,           # Make it large
    double_sided=True,  # Ensure you can see the inside if you zoom in
    rotation_x=90       # Adjust axis if needed
)

# 3. Add a responsive camera for navigation
# Allows you to click and drag to view the Earth, like in Google Earth
camera.fov = 90
EditorCamera() # Provides easy mouse-based controls

# A simple marker for the starting point
start_marker = Entity(model='sphere', color=color.red, scale=0.5, collider='sphere', parent=earth)
# We will draw the projectile line here
projectile_line = Entity(model=Mesh(), color=color.yellow, thickness=2, parent=earth)

def input(key):
    # Check for a mouse click (e.g., left click)
    if key == 'left mouse down':
        # Perform a raycast from the mouse position
        hit_info = raycast(camera.screen_to_world(mouse.position, camera.clip_plane_far), camera.forward, distance=100)
        
        if hit_info.hit and hit_info.entity == earth:
            # 1. Place the starting marker at the hit point
            start_marker.position = hit_info.point
            
            # 2. Calculate and draw the projectile line
            # This is complex, but involves calculating an arc (a parabola or great circle)
            # based on the launch angle and speed, and updating the projectile_line's mesh.
            
            # Example: Drawing a simple line segment (needs a mesh update)
            # projectile_line.model.vertices = [start_marker.position, start_marker.position + camera.forward * 5]
            # projectile_line.model.generate()
            
# Finally, run the application
app.run()