from abc import ABC, abstractmethod
import glm

from experience import AffineMatrix, Uniform

class Camera(ABC):
    '''abstract class for various cameras'''
    
    def __init__(self):
        super().__init__()
        
        self._view_pos = Uniform[glm.vec3]("view_pos", glm.vec3())

    @abstractmethod
    def update(self, delta: int): pass
    
    # event callbacks
    @abstractmethod
    def key_callback(self, window: int, key: int, scancode: int, action: int, mods: int): pass
    @abstractmethod
    def mouse_button_callback(self, window: int, button: int, action: int, mods: int): pass
    @abstractmethod
    def cursor_pos_callback(self, window: int, xpos: int, ypos: int): pass
    @abstractmethod
    def scroll_callback(self, window: int, xoffset: int, yoffset: int): pass

    @property
    def view_pos(self): return self._view_pos
    @property
    @abstractmethod
    def V(self) -> AffineMatrix: pass