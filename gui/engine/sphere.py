"""
Sphere rendering engine module.
This module provides a Sphere class that creates and renders a textured sphere mesh using OpenGL.
"""

import OpenGL.GL as GL
from config.render_config import SPHERE_RADIUS, SPHERE_RESULUTION
from utils.utils import map_value
from math import cos,sin,pi
from typing import Tuple, List
import logging
LOG = logging.getLogger(__name__)

class Sphere:
    def __init__(self, texture=None):
        self.texture = texture
        self.radius = SPHERE_RADIUS
        self.resolution = SPHERE_RESULUTION
        self.display_list = None
    
    def _create_mesh(self):
        self.display_list = GL.glGenLists(1)
        GL.glNewList(self.display_list, GL.GL_COMPILE)

        vertices, texture_coords, indices = self._sphere_mesh(self.radius, self.resolution)

        v_num = len(vertices)
        t_num = len(texture_coords)
        i_num = len(indices)

        vertex_array = (GL.GLfloat * v_num)(*vertices)
        texture_array = (GL.GLfloat * t_num)(*texture_coords)
        index_array = (GL.GLuint * i_num)(*indices)

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        
        # point OpenGL to these arrays
        # first: size of a array element
        # second: data type
        # third: stride
        # fourth: pointer to data
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, vertex_array)
        GL.glTexCoordPointer(2, GL.GL_FLOAT, 0, texture_array)
        
        GL.glDrawElements(GL.GL_TRIANGLES, i_num, GL.GL_UNSIGNED_INT, index_array)
        
        # reset
        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY)
        GL.glEndList()
        
        LOG.info(f"Sphere mesh created with {len(indices)//3} triangles.")

    def _sphere_mesh(self, radius, resolution) -> Tuple[List[float], List[float], List[int]]:
        """
        Create a UV sphere mesh with proper lat/lon mapping
        lat (θ): -90° to +90° (south to north pole)
        lon (φ): -180° to +180° (wraps around)
        """
        verticals = []
        texture_coords = []
        indices = []
        for i in range(resolution +1):
            lon = map_value(i, 0 ,resolution, -pi, pi)
            u = 1 - (i / resolution)
        
            for j in range(resolution +1):
                lat = map_value(j, 0 , resolution, -pi/2, pi/2)
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

    def draw(self):
        if self.texture:
            GL.glEnable(GL.GL_TEXTURE_2D)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glColor3f(1,1,1)
            
        if self.display_list:
            GL.glCallList(self.display_list)
        
        if self.texture:
            GL.glDisable(GL.GL_TEXTURE_2D)
