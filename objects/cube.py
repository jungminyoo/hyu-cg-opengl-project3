from OpenGL.GL import *
import glm

from .object import Object
from experience import Light, Node
from projections import Projection
from cameras import Camera

class Cube(Object):
    '''class for single cube object'''
    
    def __init__(
        self,
        material_color: glm.vec3, 
        camera: Camera, 
        projection: Projection, 
        light: Light,
        node: Node, 
        half_extent: float
    ):
        super().__init__(material_color, camera, projection, light, node, True)
        
        self._half_extent = half_extent
        
        # 8 vertices for 12 triangles
        self._vertices = glm.array(glm.float32,
            # position      normal
            -self._half_extent,  self._half_extent,  self._half_extent,  0, 0, 1, # v0
            self._half_extent, -self._half_extent,  self._half_extent,  0, 0, 1, # v2
            self._half_extent,  self._half_extent,  self._half_extent,  0, 0, 1, # v1

            -self._half_extent,  self._half_extent,  self._half_extent,  0, 0, 1, # v0
            -self._half_extent, -self._half_extent,  self._half_extent,  0, 0, 1, # v3
            self._half_extent, -self._half_extent,  self._half_extent,  0, 0, 1, # v2

            -self._half_extent,  self._half_extent, -self._half_extent,  0, 0,-1, # v4
            self._half_extent,  self._half_extent, -self._half_extent,  0, 0,-1, # v5
            self._half_extent, -self._half_extent, -self._half_extent,  0, 0,-1, # v6

            -self._half_extent,  self._half_extent, -self._half_extent,  0, 0,-1, # v4
            self._half_extent, -self._half_extent, -self._half_extent,  0, 0,-1, # v6
            -self._half_extent, -self._half_extent, -self._half_extent,  0, 0,-1, # v7

            -self._half_extent,  self._half_extent,  self._half_extent,  0, 1, 0, # v0
            self._half_extent,  self._half_extent,  self._half_extent,  0, 1, 0, # v1
            self._half_extent,  self._half_extent, -self._half_extent,  0, 1, 0, # v5

            -self._half_extent,  self._half_extent,  self._half_extent,  0, 1, 0, # v0
            self._half_extent,  self._half_extent, -self._half_extent,  0, 1, 0, # v5
            -self._half_extent,  self._half_extent, -self._half_extent,  0, 1, 0, # v4
    
            -self._half_extent, -self._half_extent,  self._half_extent,  0,-1, 0, # v3
            self._half_extent, -self._half_extent, -self._half_extent,  0,-1, 0, # v6
            self._half_extent, -self._half_extent,  self._half_extent,  0,-1, 0, # v2

            -self._half_extent, -self._half_extent,  self._half_extent,  0,-1, 0, # v3
            -self._half_extent, -self._half_extent, -self._half_extent,  0,-1, 0, # v7
            self._half_extent, -self._half_extent, -self._half_extent,  0,-1, 0, # v6

            self._half_extent,  self._half_extent,  self._half_extent,  1, 0, 0, # v1
            self._half_extent, -self._half_extent,  self._half_extent,  1, 0, 0, # v2
            self._half_extent, -self._half_extent, -self._half_extent,  1, 0, 0, # v6

            self._half_extent,  self._half_extent,  self._half_extent,  1, 0, 0, # v1
            self._half_extent, -self._half_extent, -self._half_extent,  1, 0, 0, # v6
            self._half_extent,  self._half_extent, -self._half_extent,  1, 0, 0, # v5

            -self._half_extent,  self._half_extent,  self._half_extent, -1, 0, 0, # v0
            -self._half_extent, -self._half_extent, -self._half_extent, -1, 0, 0, # v7
            -self._half_extent, -self._half_extent,  self._half_extent, -1, 0, 0, # v3

            -self._half_extent,  self._half_extent,  self._half_extent, -1, 0, 0, # v0
            -self._half_extent,  self._half_extent, -self._half_extent, -1, 0, 0, # v4
            -self._half_extent, -self._half_extent, -self._half_extent, -1, 0, 0, # v7
        )
        
        self._VAO = self._prepare_vao()
    
    def draw(self):
        super().draw()
        glDrawArrays(GL_TRIANGLES, 0, 36)