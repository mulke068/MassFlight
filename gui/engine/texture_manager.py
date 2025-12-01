from typing import Any
import numpy as np
#import pyglet
from OpenGL import GL
from PIL import Image
import os
import logging

LOG = logging.getLogger(__name__)

# texture
# image from solarsystemscope
class TextureManager:
    def __init__(self, assets_path='assets/textures'):
        self.texture_name = None
        self.bg_sprite_name = None
        self.assets_path = assets_path

    def set_textures(self, texture_name, bg_sprite_name):
        self.texture_name = texture_name
        self.bg_sprite_name = bg_sprite_name

    def load_texture(self):
        if not self.texture_name:
            LOG.warning("No texture name provided.")
            return None
        return self._create_OpenGL_texture(self.texture_name)
    
    def load_bg_sprite(self):
        if not self.bg_sprite_name:
            LOG.warning("No background sprite name provided.")
            return None
        return self._create_OpenGL_texture(self.bg_sprite_name)
    
    def _create_OpenGL_texture(self, file_name) -> Any:
        try:
            
            base_dir = os.path.dirname(__file__)
            project_root = os.path.dirname(os.path.dirname(base_dir))
            image_path = os.path.join(project_root, self.assets_path, file_name)
            
            if not os.path.exists(image_path):
                LOG.error(f"Texture file '{file_name}' not found at path: {image_path}")
                return None
            
            image = Image.open(image_path)
            # convert to rgb and byte array
            # image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            image_data = np.array(image.convert("RGB"), dtype=np.uint8)
            # ensure contiguous bytes layout and set upload alignment
            image_data = np.ascontiguousarray(image_data)
            
            # Generate OpenGL texture
            # generate and bind texture id
            texture_id = GL.glGenTextures(1)
            # glGenTextures sometimes returns a numpy scalar/array; coerce to int
            try:
                texture_id = int(texture_id)
            except Exception:
                # if it's a sequence, grab first
                try:
                    texture_id = int(texture_id[0])
                except Exception:
                    pass

            GL.glBindTexture(GL.GL_TEXTURE_2D, texture_id)

            # ensure proper unpack alignment for byte arrays
            GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
            
            # Set sane texture parameters so NPOT textures and sampling behave
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
            # GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_REPEAT)
            GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

            # upload texture data to GPU
            GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGB, image.width, image.height, 0, GL.GL_RGB, GL.GL_UNSIGNED_BYTE, image_data.tobytes())
            
            return texture_id
            
        except Exception as e:
            LOG.error(f"Error creating OpenGL texture from '{file_name}': {e}")
            return None

#    def _get_image_from_file(self, file_name):
        #try:
            ## image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\..', 'assets/textures', file_name))
            #base_dir = os.path.dirname(__file__)
            #print(base_dir)
            #dir = os.path.join(base_dir, '..', '..', self.assets_path, file_name)
            #print(dir)
            #image_path = os.path.abspath(dir)
            #print(image_path)
            
            #if not os.path.exists(image_path):
                #raise FileNotFoundError(f"Texture file '{file_name}' not found at path: {image_path}")
            #image = pyglet.image.load(image_path)
            #LOG.info(f"Texture '{file_name}' loaded successfully.")
            #return image
        #except Exception as e:
            #LOG.error(f"Error loading '{file_name}' as texture: {e}")
            #return None