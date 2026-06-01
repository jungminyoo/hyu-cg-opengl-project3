from OpenGL.GL import *
import glm

from .object import ObjectWithoutLight
from projections import Projection
from cameras import Camera
from experience import Node

class Frame(ObjectWithoutLight):
    '''class for frame'''
    
    def __init__(self, camera: Camera, projection: Projection, node: Node, length: float):
        super().__init__(camera, projection, node, True)
        
        self._vertices = glm.array(glm.float32,
            # position        # color
            0.0, 0.0, 0.0,  1.0, 0.0, 0.0, # x-axis start
            length, 0.0, 0.0,  1.0, 0.0, 0.0, # x-axis end 
            0.0, 0.0, 0.0,  0.0, 1.0, 0.0, # y-axis start
            0.0, length, 0.0,  0.0, 1.0, 0.0, # y-axis end 
            0.0, 0.0, 0.0,  0.0, 0.0, 1.0, # z-axis start
            0.0, 0.0, length,  0.0, 0.0, 1.0, # z-axis end 
        )
        
        self._VAO = self._prepare_vao()

    def draw(self):
        super().draw()
        glDrawArrays(GL_LINES, 0, 6)