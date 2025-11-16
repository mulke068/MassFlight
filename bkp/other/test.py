import pyglet
from pyglet.gl import *
import math

window = pyglet.window.Window(800, 600, "Sphere from Points")

# Generate sphere points using spherical coordinates
def generate_sphere_points(radius=200, num_points=2000):
    points = []
    colors = []
    
    for i in range(num_points):
        # Golden angle for even distribution
        theta = math.pi * (3 - math.sqrt(5)) * i
        phi = math.acos(1 - 2 * (i + 0.5) / num_points)
        
        x = radius * math.sin(phi) * math.cos(theta) + 400
        y = radius * math.sin(phi) * math.sin(theta) + 300
        z = radius * math.cos(phi)
        
        points.extend([x, y])
        # Color based on z-depth for 3D effect
        depth_color = int(128 + 127 * (z / radius))
        colors.extend([depth_color, int(128 + 127 * math.sin(phi)), 200, 255])
    
    return points, colors

# Generate the sphere
sphere_points, sphere_colors = generate_sphere_points(radius=200, num_points=3000)

# Create a batch for efficient rendering
batch = pyglet.graphics.Batch()

# Add vertex list to batch
vertex_list = batch.add(
    len(sphere_points) // 2,  # number of vertices
    GL_POINTS,
    None,
    ('v2f', sphere_points),
    ('c4B', sphere_colors)
)

@window.event
def on_draw():
    window.clear()
    
    # Set point size
    glPointSize(3)
    
    # Enable point smoothing for nicer circles
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw the batch
    batch.draw()

# Run the application
pyglet.app.run()