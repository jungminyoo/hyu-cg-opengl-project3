from OpenGL.GL import *
import glm
import numpy as np

from .object import ObjectWithoutLight
from projections import Projection
from cameras import Camera
from experience import Node

class Grid(ObjectWithoutLight):
    '''class for grid on xz plane'''
    
    def __init__(self, camera: Camera, projection: Projection, node: Node, grid_half_width: int, grid_half_depth: int):
        super().__init__(camera, projection, node, True)
        
        self._vertices = glm.array(glm.float32,
            # position        # color
            0.0, 0.0, -0.5,  0.5, 0.5, 0.5, # line start
            0.0, 0.0, 0.5,   0.5, 0.5, 0.5, # line end
        )
        
        self._VAO = self._prepare_vao()
        self._grid_half_width = grid_half_width
        self._grid_half_depth = grid_half_depth

    def draw(self):
        super().draw()
        
        for i in range(-self._grid_half_width, self._grid_half_width + 1):
            MVP_line = self._MVP.data \
                        * glm.translate(glm.vec3(i, 0, 0)) \
                        * glm.scale(glm.vec3(self._grid_half_depth * 2))
            glUniformMatrix4fv(self._MVP.location, 1, GL_FALSE, glm.value_ptr(MVP_line))
            glDrawArrays(GL_LINES, 0, 2)
        
        for i in range(-self._grid_half_depth, self._grid_half_depth + 1):
            MVP_line = self._MVP.data \
                        * glm.translate(glm.vec3(0, 0, i)) \
                        * glm.scale(glm.vec3(self._grid_half_width * 2)) \
                        * glm.rotate(np.pi * 0.5, glm.vec3(0, 1, 0))
            glUniformMatrix4fv(self._MVP.location, 1, GL_FALSE, glm.value_ptr(MVP_line))
            glDrawArrays(GL_LINES, 0, 2)