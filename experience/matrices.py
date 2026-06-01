from abc import ABC, abstractmethod
import glm

class AffineMatrix(ABC):
    '''wrapper class for affine 4x4 matrix'''
    
    def __init__(self, matrix: glm.mat4x4):
        super().__init__()
        
        self._matrix = matrix
    
    @property
    def matrix(self): return self._matrix
    @matrix.setter
    def matrix(self, matrix: glm.mat4x4): self._matrix = matrix