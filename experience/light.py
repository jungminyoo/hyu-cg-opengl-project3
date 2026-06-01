import glm

from .uniform import Uniform

class Light:
    def __init__(self, init_light_pos: glm.vec3, init_light_color: glm.vec3):
        self._light_pos = Uniform[glm.vec3]("light_pos", init_light_pos)
        self._light_color = Uniform[glm.vec3]("light_color", init_light_color)
        
    @property
    def light_pos(self): return self._light_pos
    @property
    def light_color(self): return self._light_color