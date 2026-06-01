from OpenGL.GL import *
import glm

from experience import Uniform, Shader, Light, Node
from projections import Projection
from cameras import Camera

global_vertex_shader_src_no_lighting = '''
#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec3 vin_color; 

out vec4 vout_color;

uniform mat4 MVP;

void main()
{
    // 3D points in homogeneous coordinates
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);

    gl_Position = MVP * p3D_in_hcoord;

    vout_color = vec4(vin_color, 1.);
}
'''

global_fragment_shader_src_no_lighting = '''
#version 330 core

in vec4 vout_color;

out vec4 FragColor;

void main()
{
    FragColor = vout_color;
}
'''

global_vertex_shader_src = '''
#version 330 core

layout (location = 0) in vec3 vin_pos; 
layout (location = 1) in vec3 vin_normal; 

out vec3 vout_surface_pos;
out vec3 vout_normal;

uniform mat4 MVP;
uniform mat4 M;

void main()
{
    vec4 p3D_in_hcoord = vec4(vin_pos.xyz, 1.0);
    gl_Position = MVP * p3D_in_hcoord;

    vout_surface_pos = vec3(M * vec4(vin_pos, 1));
    vout_normal = normalize( mat3(inverse(transpose(M)) ) * vin_normal);
}
'''

global_fragment_shader_src = '''
#version 330 core

in vec3 vout_surface_pos;
in vec3 vout_normal;  // interpolated normal

out vec4 FragColor;

uniform vec3 view_pos;
uniform vec3 light_pos;
uniform vec3 light_color;
uniform vec3 material_color;

void main()
{
    // light and material properties
    float material_shininess = 32.0;

    // light components
    vec3 light_ambient = 0.3*light_color;
    vec3 light_diffuse = light_color;
    vec3 light_specular = light_color;

    // material components
    vec3 material_ambient = material_color;
    vec3 material_diffuse = material_color;
    vec3 material_specular = vec3(1,1,1);  // for non-metal material

    // ambient
    vec3 ambient = light_ambient * material_ambient;

    // for diffiuse and specular
    vec3 normal = normalize(vout_normal);
    vec3 surface_pos = vout_surface_pos;
    vec3 light_dir = normalize(light_pos - surface_pos);

    // diffuse
    float diff = max(dot(normal, light_dir), 0);
    vec3 diffuse = diff * light_diffuse * material_diffuse;

    // specular
    vec3 view_dir = normalize(view_pos - surface_pos);
    vec3 reflect_dir = reflect(-light_dir, normal);
    float spec = pow( max(dot(view_dir, reflect_dir), 0.0), material_shininess);
    vec3 specular = spec * light_specular * material_specular;

    vec3 color = ambient + diffuse + specular;
    FragColor = vec4(color, 1.);
}
'''

class Object:
    """
    parent class for various objects using phong illumination and phone shading\n
    """ 
    
    def __init__(
        self, 
        material_color: glm.vec3, 
        camera: Camera, 
        projection: Projection, 
        light: Light, 
        node: Node,
        is_seperate: bool
    ):
        super().__init__()
        
        # set environments
        self._camera = camera
        self._projection = projection
        self._light = light
        self._node = node
        
        # set Uniforms and Shader
        self._M = Uniform[glm.mat4x4]("M", glm.mat4x4())
        self._MVP = Uniform[glm.mat4x4]("MVP", glm.mat4x4())
        self._update_MVP()
        self._material_color = Uniform[glm.vec3]("material_color", material_color)
        
        self._shader = Shader(
            global_vertex_shader_src, 
            global_fragment_shader_src,
            [
                self._M,
                self._MVP,
                self._material_color,
                self._camera.view_pos,
                self._light.light_pos,
                self._light.light_color,
            ]
        )
        
        # set attributes
        self._is_seperate = is_seperate
        self._vertices = glm.array(glm.float32)
        self._indices = glm.array(glm.uint32)
        self._VAO: int | list[int] = None
    
    def _prepare_vao(self) -> int | list[int]:
        # create and activate VAO (vertex array object)
        VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
        glBindVertexArray(VAO)      # activate VAO

        # create and activate VBO (vertex buffer object)
        VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
        glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

        # copy vertex data to VBO
        glBufferData(GL_ARRAY_BUFFER, self._vertices.nbytes, self._vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer
        
        if not self._is_seperate:
            # create and activate EBO (element buffer object)
            EBO = glGenBuffers(1)   # create a buffer object ID and store it to EBO variable
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)  # activate EBO as an element buffer object

            # copy index data to EBO
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self._indices.nbytes, self._indices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy index data to the currently bound element buffer

        # configure vertex positions
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(0)

        # configure vertex colors
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(1)
        
        return VAO
    
    def _update_MVP(self):
        self._M.data = self._node.global_transform * self._node.shape_transform
        self._MVP.data = (
            self._projection.P.matrix * 
            self._camera.V.matrix * 
            self._M.data
        )

    def draw(self): 
        self._update_MVP()
        
        # bind VAO
        glBindVertexArray(self.VAO)
        
        # update uniforms
        self._shader.use_program()
        glUniformMatrix4fv(self._MVP.location, 1, GL_FALSE, glm.value_ptr(self._MVP.data))
        glUniformMatrix4fv(self._M.location, 1, GL_FALSE, glm.value_ptr(self._M.data))
        glUniform3f(self._camera.view_pos.location, self._camera.view_pos.data.x, self._camera.view_pos.data.y, self._camera.view_pos.data.z)
        glUniform3f(self._light.light_pos.location, self._light.light_pos.data.x, self._light.light_pos.data.y, self._light.light_pos.data.z)
        glUniform3f(self._light.light_color.location, self._light.light_color.data.x, self._light.light_color.data.y, self._light.light_color.data.z)
        glUniform3f(self._material_color.location, self._material_color.data.x, self._material_color.data.y, self._material_color.data.z)
    
    @property
    def VAO(self): return self._VAO
    @property
    def shader(self): return self._shader

class ObjectWithoutLight:
    """
    parent class for various objects which not uses lighting\n
    """ 
    
    def __init__(
        self, 
        camera: Camera, 
        projection: Projection, 
        node: Node,
        is_seperate: bool
    ):
        super().__init__()
        
        # set environments
        self._camera = camera
        self._projection = projection
        self._node = node
        
        # set Uniforms and Shader
        self._MVP = Uniform[glm.mat4x4]("MVP", glm.mat4x4())
        self._update_MVP()
        
        self._shader = Shader(
            global_vertex_shader_src_no_lighting, 
            global_fragment_shader_src_no_lighting,
            [ self._MVP, ]
        )
        
        # set attributes
        self._is_seperate = is_seperate
        self._vertices = glm.array(glm.float32)
        self._indices = glm.array(glm.uint32)
        self._VAO: int | list[int] = None
    
    def _prepare_vao(self) -> int | list[int]:
        # create and activate VAO (vertex array object)
        VAO = glGenVertexArrays(1)  # create a vertex array object ID and store it to VAO variable
        glBindVertexArray(VAO)      # activate VAO

        # create and activate VBO (vertex buffer object)
        VBO = glGenBuffers(1)   # create a buffer object ID and store it to VBO variable
        glBindBuffer(GL_ARRAY_BUFFER, VBO)  # activate VBO as a vertex buffer object

        # copy vertex data to VBO
        glBufferData(GL_ARRAY_BUFFER, self._vertices.nbytes, self._vertices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy vertex data to the currently bound vertex buffer
        
        if not self._is_seperate:
            # create and activate EBO (element buffer object)
            EBO = glGenBuffers(1)   # create a buffer object ID and store it to EBO variable
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)  # activate EBO as an element buffer object

            # copy index data to EBO
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self._indices.nbytes, self._indices.ptr, GL_STATIC_DRAW) # allocate GPU memory for and copy index data to the currently bound element buffer

        # configure vertex positions
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), None)
        glEnableVertexAttribArray(0)

        # configure vertex colors
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * glm.sizeof(glm.float32), ctypes.c_void_p(3*glm.sizeof(glm.float32)))
        glEnableVertexAttribArray(1)
        
        return VAO
    
    def _update_MVP(self):
        self._MVP.data = (
            self._projection.P.matrix * 
            self._camera.V.matrix * 
            self._node.global_transform * self._node.shape_transform
        )

    def draw(self): 
        self._update_MVP()
        
        # bind VAO
        glBindVertexArray(self.VAO)
        
        # update uniforms
        self._shader.use_program()
        glUniformMatrix4fv(self._MVP.location, 1, GL_FALSE, glm.value_ptr(self._MVP.data))
    
    @property
    def VAO(self): return self._VAO
    @property
    def shader(self): return self._shader
