from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cameras import Camera
    from projections import PerspectiveProjection
    
from typing import Callable
from OpenGL.GL import *
from glfw.GLFW import *

class Window:
    '''class for managing single window'''
    
    def __init__(self, width: int, height: int, title: str, perspective: PerspectiveProjection, camera: Camera):
        # initialize glfw
        if not glfwInit():
            return
        glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)   # OpenGL 3.3
        glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)
        glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)  # Do not allow legacy OpenGl API calls
        glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE) # for macOS

        # create a window and OpenGL context
        self._width = width
        self._height = height
        self._title = title
        self._window = glfwCreateWindow(self.width, self.height, self.title, None, None)
        if not self.window:
            glfwTerminate()
            return
        glfwMakeContextCurrent(self.window)
        
        # register event callbacks
        glfwSetKeyCallback(self.window, self._generate_key_callback(camera))
        glfwSetMouseButtonCallback(self.window, camera.mouse_button_callback)
        glfwSetCursorPosCallback(self.window, camera.cursor_pos_callback)
        glfwSetFramebufferSizeCallback(self.window, self._generate_framebuffer_size_callback(perspective))
        glfwSetScrollCallback(self.window, camera.scroll_callback)
        
        # initialize flags
        self._current_polygon_mode = GL_FILL
        self._grid_enabled = True
        
    def _generate_key_callback(self, camera: Camera):
        def key_callback(window: int, key: int, scancode: int, action: int, mods: int):
            camera.key_callback(window, key, scancode, action, mods)
            
            # additional key handling operations
            if key==GLFW_KEY_ESCAPE and action==GLFW_PRESS:
                glfwSetWindowShouldClose(window, GLFW_TRUE)
            if key==GLFW_KEY_L and action==GLFW_PRESS:
                if self._current_polygon_mode == GL_FILL: self._current_polygon_mode = GL_LINE
                else: self._current_polygon_mode = GL_FILL
            if key==GLFW_KEY_G and action==GLFW_PRESS:
                self._grid_enabled = not self._grid_enabled
        
        return key_callback
        
    def _generate_framebuffer_size_callback(self, perspective: PerspectiveProjection) -> Callable:
        def framebuffer_size_callback(window: int, width: int, height: int):
            glViewport(0, 0, width, height)
            perspective.update_by_viewport(width, height)
            self._width = width
            self._height = height
        
        return framebuffer_size_callback
    
    def update(self):
        # swap front and back buffers
        glfwSwapBuffers(self.window)
        # poll events
        glfwPollEvents()
        
    def terminate(self):
        glfwTerminate()
        
    @property
    def window(self): return self._window
    @property
    def width(self): return self._width
    @property
    def height(self): return self._height
    @property
    def title(self): return self._title
    @property
    def current_polygon_mode(self): return self._current_polygon_mode
    @property
    def grid_enabled(self): return self._grid_enabled
    @property
    def should_close(self): return glfwWindowShouldClose(self.window)