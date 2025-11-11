# python version 3.9.13
# pyglet version 1.5.27

from math import cos, pi, sin
import pyglet
from pyglet import gl

window = pyglet.window.Window(width=800, height=600, caption="3D Visual", visible=True)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max- out_min) / (in_max - in_min) + out_min 

# normal sphere coordinates
# φ lon -180 - 0 - 180   = 360 points
# θ lat  -90  - 0 - 90    = 180 points

# x,y,z
# x = r * sin(θ) * cos(φ)
# y = r * sin(θ) * sin(φ)
# z = r * cos(θ)
# lat=theta=θ , lon=phi=φ

def sphere(radius, resolution_points):
    verticals = []
    for i in range(0,resolution_points):
        lon = map(i, 0 ,resolution_points, -pi, pi)
        for j in range(0,resolution_points):
            lat = map(j, 0 , resolution_points, -pi/2, pi/2)

            x = radius * sin(lat) * cos(lon)
            y = radius * sin(lat) * sin(lon)
            z = radius * cos(lat)

            # Use extend because the draw function needs a flat list
            verticals.extend((x,y,z))
            # verticals.append((x,y,z)) 
    return verticals

points = sphere(2,50)
num_points = len(points) // 3

batch = pyglet.graphics.Batch()

vertex_list = batch.add(
    num_points,
    gl.GL_POINTS,
    None,
    ('v3f', points),
    ('c3B', (255,255,255) * num_points)
)

def setup_3d():
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glViewport(0,0, window.width, window.height)
    
    #projection matrix
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()

    # camera settings
    aspect = window.width / window.height
    gl.gluPerspective(60, aspect, 0.1, 100) # 60 fov, z 0.1-100
        
    # model Matrix
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    gl.glTranslatef(0.0,0.0,-7)
    
    # visibiliti of points
    gl.glPointSize(3)
    gl.glEnable(gl.GL_POINT_SMOOTH)


@window.event
def on_draw():
    window.clear()
    
    setup_3d()
    
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    # pyglet.graphics.draw(num_points, gl.GL_POINTS, ('v3f',points))
    # pyglet.graphics.draw(num_points, gl.GL_POINTS, ('v3f',points), ('c3B', (255,255,255) * num_points))
    batch.draw()

if __name__ == "__main__":
    print("Run ")
    pyglet.app.run()
