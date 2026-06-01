from OpenGL.GL import *
import glm

from .object import Object
from experience import Light, Node
from projections import Projection
from cameras import Camera


class Diamond(Object):
    """class for single diamond object"""

    def __init__(
        self,
        material_color: glm.vec3,
        camera: Camera,
        projection: Projection,
        light: Light,
        node: Node,
        half_extent: float,
    ):
        super().__init__(
            material_color,
            camera,
            projection,
            light,
            node,
            True
        )

        self._half_extent = half_extent

        h = self._half_extent
        top = glm.vec3(0, h * 2, 0)
        bottom = glm.vec3(0, -h * 2, 0)

        v0 = glm.vec3(-h, 0, h)
        v1 = glm.vec3(h, 0, h)
        v2 = glm.vec3(h, 0, -h)
        v3 = glm.vec3(-h, 0, -h)

        data = []

        # upper pyramid
        data += self._tri(v0, v1, top)
        data += self._tri(v1, v2, top)
        data += self._tri(v2, v3, top)
        data += self._tri(v3, v0, top)

        # lower pyramid
        data += self._tri(v1, v0, bottom)
        data += self._tri(v2, v1, bottom)
        data += self._tri(v3, v2, bottom)
        data += self._tri(v0, v3, bottom)

        self._vertices = glm.array(glm.float32, *data)

        self._VAO = self._prepare_vao()

    def _normal(self, a: glm.vec3, b: glm.vec3, c: glm.vec3) -> glm.vec3:
        return glm.normalize(glm.cross(b - a, c - a))

    def _tri(self, a: glm.vec3, b: glm.vec3, c: glm.vec3):
        n = self._normal(a, b, c)
        return [
            a.x, a.y, a.z, n.x, n.y, n.z,
            b.x, b.y, b.z, n.x, n.y, n.z,
            c.x, c.y, c.z, n.x, n.y, n.z,
        ]

    def draw(self):
        super().draw()
        glDrawArrays(GL_TRIANGLES, 0, 24)