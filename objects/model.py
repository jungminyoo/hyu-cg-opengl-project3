from OpenGL.GL import *
import glm

from .object import Object
from experience import Light, Node
from projections import Projection
from cameras import Camera

class OBJModel(Object):
    '''class for external model object (OBJ)'''
    
    def __init__(
        self,
        material_color: glm.vec3, 
        camera: Camera, 
        projection: Projection, 
        light: Light,
        node: Node, 
        path: str
    ):
        super().__init__(material_color, camera, projection, light, node, True)
        
        self._vertices, self._vertex_count = self._load_obj_and_parse(path)
        
        self._VAO = self._prepare_vao()
        
    def draw(self):
        super().draw()
        glDrawArrays(GL_TRIANGLES, 0, self._vertex_count)

    def _load_obj_and_parse(self, path: str):
        positions: list[glm.vec3] = []
        normals: list[glm.vec3] = []

        vertices_data: list[float] = []
        vertex_count = 0

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split()

                if parts[0] == "v":
                    positions.append(glm.vec3(
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3]),
                    ))

                elif parts[0] == "vn":
                    normals.append(glm.vec3(
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3]),
                    ))

                elif parts[0] == "f":
                    face_vertices: list[tuple[int, int]] = []

                    for token in parts[1:]:
                        values = token.split("/")

                        v_idx = int(values[0]) - 1

                        # texture coordinate index는 무시

                        vn_idx = int(values[2]) - 1

                        face_vertices.append((v_idx, vn_idx))

                    # triangle이면 그대로 사용
                    if len(face_vertices) == 3:
                        triangles = [face_vertices]

                    # quad 이상이면 fan triangulation
                    else:
                        triangles = []
                        for i in range(1, len(face_vertices) - 1):
                            triangles.append([
                                face_vertices[0],
                                face_vertices[i],
                                face_vertices[i + 1],
                            ])

                    # face 순서대로 position + normal 저장
                    for tri in triangles:
                        for v_idx, vn_idx in tri:
                            pos = positions[v_idx]
                            normal = normals[vn_idx]

                            vertices_data.extend([
                                pos.x, pos.y, pos.z,
                                normal.x, normal.y, normal.z,
                            ])

                            vertex_count += 1

        vertices = glm.array(glm.float32, *vertices_data)

        return vertices, vertex_count