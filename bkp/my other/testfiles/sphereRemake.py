from vispy import app, gloo
from vispy.util.transforms import perspective, translate, rotate
import numpy as np

vertex_shader = """
attribute vec3 a_position;
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
void main() {
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
}
"""

fragment_shader = """
void main() {
    gl_FragColor = vec4(0.3, 0.5, 1.0, 1.0);
}
"""

def create_sphere(radius=1.0, slices=32, stacks=32):
    vertices = []
    for stack in range(stacks + 1):
        phi = np.pi * stack / stacks
        for slice in range(slices + 1):
            theta = 2 * np.pi * slice / slices
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            vertices.append([x, y, z])
    return np.array(vertices, dtype=np.float32)

class Canvas(app.Canvas):
    """
    Canvas class for rendering a 3D sphere using VisPy.

    This class sets up the OpenGL program, creates the sphere geometry,
    and handles drawing, resizing, and animation updates.
    """
    def __init__(self):
        app.Canvas.__init__(self, size=(800, 600), title='VisPy Sphere')
        self.vertices = create_sphere()
        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.program['a_position'] = self.vertices
        
        self.view = translate((0, 0, -5))
        self.model = np.eye(4, dtype=np.float32)
        
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        
    def on_draw(self, event):
        gloo.clear(color='white')
        self.program.draw('points')
        
    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.size)
        self.projection = perspective(45.0, event.size[0] / event.size[1], 1.0, 100.0)
        self.program['u_projection'] = self.projection
        self.program['u_view'] = self.view
        self.program['u_model'] = self.model
        
    def on_timer(self, event):
        self.model = np.dot(rotate(1, (0, 1, 0)), self.model)
        self.program['u_model'] = self.model
        self.update()

if __name__ == '__main__':
    c = Canvas()
    c.show()
    app.run()