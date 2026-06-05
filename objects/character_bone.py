from OpenGL.GL import *
import glm

from .object import ObjectWithoutLight
from projections import Projection
from cameras import Camera
from experience import JointLinkNode


class CharacterBone(ObjectWithoutLight):
    """class for bone line between parent joint and child joint"""

    def __init__(
        self,
        camera: Camera,
        projection: Projection,
        node: JointLinkNode,
        parent_node: JointLinkNode,
        color: glm.vec3
    ):
        self._parent_node = parent_node
        super().__init__(camera, projection, node, True)

        self._vertices = glm.array(glm.float32,
            # position      color
            0.0, 0.0, 0.0,  color.x, color.y, color.z,
            1.0, 0.0, 0.0,  color.x, color.y, color.z,
        )

        self._VAO = self._prepare_vao()

    def _get_position(self, node: JointLinkNode) -> glm.vec3:
        '''extract joint's position from raw global transform matrix'''
        M = node.global_transform
        return glm.vec3(M[3].x, M[3].y, M[3].z)

    # Override
    def _update_MVP(self):
        end = self._get_position(self._parent_node)
        start = self._get_position(self._node)

        direction = end - start

        M_line = glm.mat4(1.0)

        # in affine matrix, first column means frame's x-axis vector
        # so set x-axis vector to direction vector (joint -> parent joint)
        M_line[0] = glm.vec4(direction.x, direction.y, direction.z, 0.0)

        # in affine matrix, last column means frame's origin point
        # so set origin point as joint's position
        M_line[3] = glm.vec4(start.x, start.y, start.z, 1.0)

        self._MVP.data = (
            self._projection.P.matrix *
            self._camera.V.matrix *
            M_line
        )

    def draw(self):
        super().draw()
        glDrawArrays(GL_LINES, 0, 2)