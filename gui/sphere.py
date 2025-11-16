# python version 3.9.13
# pyglet version 1.5.27



from copy import Error
from math import asin, atan2, cos, pi, sin, sqrt
import pyglet
from pyglet import gl

import logging

LOG = logging.getLogger(__name__)


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

def sphere(radius, resolution):
    """
    Create a UV sphere mesh with proper lat/lon mapping
    lat (θ): -90° to +90° (south to north pole)
    lon (φ): -180° to +180° (wraps around)
    """
    verticals = []
    texture_coords = []
    indices = []
    for i in range(resolution +1):
        lon = map(i, 0 ,resolution, -pi, pi)
        u = -(i / resolution)
        # u = i / resolution
        
        for j in range(resolution +1):
            lat = map(j, 0 , resolution, -pi/2, pi/2)
            v = j / resolution

            # x = radius * sin(lon) * cos(lat)
            # y = radius * sin(lon) * sin(lat)
            # z = radius * cos(lon)
            x = radius * cos(lat) * cos(lon)
            y = radius * sin(lat)
            z = radius * cos(lat) * sin(lon)
            
            verticals.extend((x,y,z))
            texture_coords.extend((u,v))
            
    for i in range(resolution):
        for j in range(resolution):
            p1 = i * (resolution + 1) + j
            p2 = p1 +1 
            p3 = (i + 1) * (resolution +1) + j
            p4 = p3 + 1

            # Two triangles for each quad
            indices.extend((p1, p2, p3))
            indices.extend((p2, p4, p3))
            
    return verticals, texture_coords, indices

# texture
# image from solarsystemscope
try:
    image = pyglet.image.load('earth.jpg')
    texture = image.get_texture()
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)

    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    # image.build_mipmaps()
    LOG.info("Texture 'world_map.jpg' loaded successfully.")
except Error as e:
    LOG.error(f"Error loading 'World.png' as texture {e}")
    texture = None


# Sphere mesh

SPHERE_RADIUS = 10
SPHERE_RESULUTION = 100
vertices, texture_coords, indices = sphere(SPHERE_RADIUS,SPHERE_RESULUTION)
num_vertices = len(vertices) // 3

batch = pyglet.graphics.Batch()

try:
    vertex_list = batch.add_indexed(
        num_vertices,
        gl.GL_TRIANGLES,
        # gl.GL_LINES,
        None,
        indices,
        ('v3f', vertices),
        ('t2f', texture_coords)
    )
except Error as e:
    LOG.error(f'adding data to batch error {e}')


def setup_3d():
    """Set up 3D rendering pipeline"""
    try:
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        
        #texturing
        if texture:
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(texture.target, texture.id)
        
        gl.glViewport(0,0, window.width, window.height)
        
        #projection matrix
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        # camera settings
        aspect = window.width / window.height
        gl.gluPerspective(60, aspect, 0.1, 100) # 60 fov, z 0.1-100
            
        # model view Matrix
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        gl.glTranslatef(0, 0, zoom_distance)
        gl.glTranslatef(panning_x, panning_y, 0)
        
        # gl.glRotatef(rotation,0,1,0)
        gl.glRotatef(rotation_y, 1,0,0)
        gl.glRotatef(rotation_x, 0,1,0)
        # gl.glRotatef(rotation_z, 0,0,1)
    except Error as e:
        LOG.error(f'3D setup error {e}')


# rotation = 0

# def update(dt):
#     global rotation
#     rotation += 20 * dt

# Camera Control
zoom_distance = -20
rotation_x = -100
rotation_y = 40
# rotation_z = 0
panning_x = 0
panning_y = 0

@window.event
def on_mouse_scroll(x, y , scroll_x, scroll_y):
    """Zoom in/out with mouse wheel"""
    global zoom_distance
    LOG.debug(f'x{x},y{y},scroll_x{scroll_x},scroll_y{scroll_y}',exc_info=40)
    LOG.debug(f'zoom_distance{zoom_distance}',exc_info=1)
    new_zoom = zoom_distance + scroll_y * 1.5
    if new_zoom < -(SPHERE_RADIUS + 0.5):
        zoom_distance = new_zoom

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    """Handle mouse drag for rotation and panning"""
    global rotation_x, rotation_y, panning_x, panning_y 
    LOG.debug(f'x{x},y{y},dx{dx},dy{dy}')
    LOG.debug(f'rotation: x{rotation_x},y{y},padding: x{panning_x},y{panning_y}')
    if buttons == 1:
        rotation_x += dx * 0.5
        rotation_y -= dy * 0.5
        rotation_y = max(-90, min(90, rotation_y))
    elif buttons == 2:
        panning_x += dx * 0.05
        panning_y -= dy * 0.05

@window.event
def on_key_press(symbol, modifiers):
    """Reset view with spacebar"""
    global zoom_distance, rotation_x, rotation_y, panning_x, panning_y, pins, add_pin
    if symbol == pyglet.window.key.SPACE:
        zoom_distance = -20
        rotation_x = -100
        rotation_y = 40
        panning_x = 0
        panning_y = 0
        pins = []
        add_pin = None

def screen_to_world_ray(x, y, model_matrix, proj_matrix, viewport):
    pass

def ray_sphere_intersection(ray_origin, ray_dir, sphere_center, sphere_radius):
    """Calculate ray-sphere intersection"""
    oc = [ray_origin[i] - sphere_center[i] for i in range(3)]
    
    a = sum(ray_dir[i] * ray_dir[i] for i in range(3))
    b = 2.0 * sum(oc[i] * ray_dir[i] for i in range(3))
    c = sum(oc[i] * oc[i] for i in range(3)) - sphere_radius * sphere_radius
    
    delta = b * b - 4 * a * c
    
    if delta < 0:
        return None
    
    x1 = (-b - sqrt(delta)) / (2.0 * a)
    x2 = (-b + sqrt(delta)) / (2.0 * a)
    if x1 > 0:
        x = x1
    elif x2 > 0:
        x = x2
    else:
        return None

    intersection = [ray_origin[i] + x * ray_dir[i] for i in range(3)]
    return intersection

def xyz_to_lonlat(x,y,z):
    """Convert 3D point on sphere to lon/lat in degrees"""
    radius = sqrt(x*x + y*y + z*z)
    if radius == 0:
        return 0 , 0

    lat_radio = max(-1.0, min(1.0, y / radius))
    lat = asin(lat_radio) * 180 / pi
    # [180,-180] to [-180,180]
    # atan2 ned for correct cal [-180, 180]
    lon = -(atan2(z, x) * 180 / pi)
    return lon,lat

pins = []
add_pin = None

def draw_pin():
    global pins , add_pin
    if add_pin:
        pins.append((add_pin[0], add_pin[1], add_pin[2]))
        
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glPointSize(10.0)
        
        gl.glColor3f(1.0,0.0,0.0)
        gl.glBegin(gl.GL_POINTS)
        # gl.glVertex3f(
        #     add_pin[0],
        #     add_pin[1],
        #     add_pin[2]
        # )

        for pin in pins:
            gl.glVertex3f(pin[0],pin[1],pin[2])

        gl.glEnd()
        
        #reset
        gl.glColor3f(1,1,1)
        gl.glEnable(gl.GL_TEXTURE_2D)


@window.event
def on_mouse_press(x,y, button, modifiers):
    """Click on sphere to get lat/lon coordinates"""
    # LOG.info(f'x {x} y {y} button {button} modifiers {modifiers}')
    global add_pin
    if button == 4:
            try:
                
                # Get all current matrices
                model_matrix = (gl.GLdouble * 16)()
                proj_matrix = (gl.GLdouble * 16)()
                viewport = (gl.GLint * 4)()
                gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX, model_matrix)
                gl.glGetDoublev(gl.GL_PROJECTION_MATRIX, proj_matrix)
                gl.glGetIntegerv(gl.GL_VIEWPORT, viewport)

                # Un-project the near clipping plane point
                # near_x, near_y, near_z = (gl.GLdouble * 3)()
                near_x = gl.GLdouble()
                near_y = gl.GLdouble()
                near_z = gl.GLdouble()

                gl.gluUnProject(x, y, 0.0, model_matrix, proj_matrix, viewport, near_x, near_y, near_z)
                
                # Un-project the far clipping plane point
                # far_x, far_y, far_z = (gl.GLdouble * 3)()
                far_x = gl.GLdouble()
                far_y = gl.GLdouble()
                far_z = gl.GLdouble()
                gl.gluUnProject(x, y, 1.0, model_matrix, proj_matrix, viewport, far_x, far_y, far_z)

                # Ray origin is the near point
                ray_origin = [near_x.value, near_y.value, near_z.value]
                
                # Calculate normalized ray direction
                ray_dir = [
                    far_x.value - near_x.value,
                    far_y.value - near_y.value,
                    far_z.value - near_z.value
                ]
                length = sqrt(sum(d*d for d in ray_dir))
                if length == 0:
                    return
                ray_dir = [d/length for d in ray_dir]
                
                # Sphere center is (0,0,0) in world space
                intersection = ray_sphere_intersection(ray_origin, ray_dir, [0,0,0], SPHERE_RADIUS)
                
                if intersection:
                    add_pin = intersection
                    lon, lat = xyz_to_lonlat(*intersection)
                    LOG.info(f"Clicked x{x},y{y} at Latitude , Longtitude: {lat}, {lon}")
            except Exception as e:
                LOG.error(f"Error calculating coordinates: {e}")

## background image
bg_img = pyglet.image.load("stars.jpg")
bg_sprite = pyglet.sprite.Sprite(
    bg_img,
    x=0,
    y=0,
    batch=None
)
bg_sprite.scale_x = window.width / bg_img.width
bg_sprite.scale_y = window.height / bg_img.height

def draw_background():
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.gluOrtho2D(0, window.width, 0, window.height)

    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    gl.glDisable(gl.GL_DEPTH_TEST)       # draw on top
    gl.glDisable(gl.GL_CULL_FACE)

    bg_sprite.draw()

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_CULL_FACE)


@window.event
def on_draw():
    """Render the scene"""
    try:
        window.clear()    
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        draw_background()
        setup_3d()
        batch.draw()
        draw_pin()
    except Error as e:
        LOG.error(f'On Draw error {e}')

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    print("Run ")
    # pyglet.clock.schedule_interval(update, 1/60.0)
    pyglet.app.run()
