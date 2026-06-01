import glm

from .projection import Projection
from experience import AffineMatrix

class PerspectiveProjection(Projection):
    '''class for perspective projection'''
    
    def __init__(self, init_width: int, init_height: int, fovy: int, near: int, far: int):
        super().__init__()
        
        self._fovy = fovy
        self._near = near
        self._far = far
        self._P = AffineMatrix(glm.mat4())
        self.update_by_viewport(init_width, init_height)
        
    def update_by_viewport(self, width, height):
        self._P.matrix = glm.perspective(self._fovy, width / height, self._near, self._far)
        
    @property
    def P(self): return self._P