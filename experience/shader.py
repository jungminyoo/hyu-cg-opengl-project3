from OpenGL.GL import *

from .uniform import Uniform

class Shader:
    '''class for managing single shader'''
    
    def __init__(self, vertex_shader_src: str, fragment_shader_src: str, uniforms: list[Uniform]):
        self._vertex_shader = vertex_shader_src
        self._fragment_shader = fragment_shader_src
        self._shader_program = self._load_shaders()
        self._uniforms = uniforms
        for uniform in self._uniforms: 
            uniform.location = self._get_uniform_location(uniform.name)

    def _load_shaders(self):
        # build and compile our shader program
        # ------------------------------------
        
        # vertex shader 
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)    # create an empty shader object
        glShaderSource(vertex_shader, self._vertex_shader) # provide shader source code
        glCompileShader(vertex_shader)                      # compile the shader object
        
        # check for shader compile errors
        success = glGetShaderiv(vertex_shader, GL_COMPILE_STATUS)
        if (not success):
            infoLog = glGetShaderInfoLog(vertex_shader)
            print("ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" + infoLog.decode())
            
        # fragment shader
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)    # create an empty shader object
        glShaderSource(fragment_shader, self._fragment_shader) # provide shader source code
        glCompileShader(fragment_shader)                        # compile the shader object
        
        # check for shader compile errors
        success = glGetShaderiv(fragment_shader, GL_COMPILE_STATUS)
        if (not success):
            infoLog = glGetShaderInfoLog(fragment_shader)
            print("ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" + infoLog.decode())

        # link shaders
        shader_program = glCreateProgram()               # create an empty program object
        glAttachShader(shader_program, vertex_shader)    # attach the shader objects to the program object
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)                    # link the program object

        # check for linking errors
        success = glGetProgramiv(shader_program, GL_LINK_STATUS)
        if (not success):
            infoLog = glGetProgramInfoLog(shader_program)
            print("ERROR::SHADER::PROGRAM::LINKING_FAILED\n" + infoLog.decode())
            
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program    # return the shader program
    
    def _get_uniform_location(self, uniform_name: str) -> int:
        return glGetUniformLocation(self.shader_program, uniform_name)
    
    def use_program(self):
        glUseProgram(self.shader_program)
    
    @property
    def vertex_shader(self) -> str: self._vertex_shader
    @vertex_shader.setter
    def vertex_shader(self, vertex_shader_src: str): 
        self._vertex_shader = vertex_shader_src
        self._shader_program = self._load_shaders()    # reload shaders after updating shader code
    
    @property
    def fragment_shader(self) -> str: self._fragment_shader
    @fragment_shader.setter
    def fragment_shader(self, fragment_shader_src: str): 
        self._fragment_shader = fragment_shader_src
        self._shader_program = self._load_shaders()    # reload shaders after updating shader code
    
    @property
    def shader_program(self) -> int: return self._shader_program