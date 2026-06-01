from abc import ABC, abstractmethod

from experience import AffineMatrix

class Projection(ABC):
    '''abstract class for various projections'''
    
    def __init__(self):
        super().__init__()

    @abstractmethod
    def update_by_viewport(self, width: int, height: int): pass

    @property
    @abstractmethod
    def P(self) -> AffineMatrix: pass