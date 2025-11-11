from math import cos, pi, sin
import pyglet
from pyglet.gl import *
from pyglet import gl

window = pyglet.window.Window(width=800, height=600, caption="3D Visual", visible=True)

def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max- out_min) / (in_max - in_min) + out_min 

# normal sphere coordinates
# long -180 - 0 - 180   = 360 points
# lat  -90  - 0 - 90    = 180 points

# resolution
total = 100
# radius
r = 200

# x,y,z
# x = r * sin(theta) * cos(phi)
# y = r * sin(theta) * sin(phi)
# z = r * cos(theta)
# lon=theta, lat=phi

def sphere():
    verticals = []
    for i in range(0,total):
        lon = map(i, 0 ,total, -pi, pi)
        for j in range(0,total):
            lat = map(j, 0 , total, -pi/2, pi/2)

            x = r * cos(lon) * sin(lat)
            y = r * sin(lon) * sin(lat)
            z = r * cos(lon)

            # Use extend because the draw function needs a flat list
            verticals.extend((x,y,z))
            # verticals.append((x,y,z)) 
    return verticals


points = sphere()
num_vertices = len(points) // 3 # beacause each vertex has 3 components (x, y, z)

gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
pyglet.gl.glPointSize(100)
pyglet.graphics.draw(0, pyglet.gl.GL_POINTS, position=('i', (400,300)))

# @window.event
# def on_draw():
    # global points
    # window.clear()
    
    # gl.glEnable(gl.GL_DEPTH_TEST)


    # pyglet.gl.glPointSize(100)

    # pyglet.graphics.draw(num_vertices, pyglet.gl.GL_POINTS, position=('f', points))
    # print("Draw Point")
    # pyglet.graphics.draw(0, pyglet.gl.GL_POINTS, position=('i', (400,300)))
    
# def update(dt):
#     pass

if __name__ == "__main__":
    print("sphere test")
    # pyglet.clock.schedule_interval(update, 1.0/60)
    pyglet.app.run()
