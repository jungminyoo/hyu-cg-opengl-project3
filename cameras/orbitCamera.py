from glfw.GLFW import *
import glm
import numpy as np

from .camera import Camera
from experience import AffineMatrix

class OrbitCamera(Camera):
    '''class for orbit camera'''
    
    def __init__(self, init_hor_angle_deg: float, init_ver_angle_deg: float, init_radius: float):
        super().__init__()
        
        # for rotation
        self._current_spherical_angle = glm.vec2(np.radians(init_hor_angle_deg), np.radians(init_ver_angle_deg))
        self._target_spherical_angle = glm.vec2(np.radians(init_hor_angle_deg), np.radians(init_ver_angle_deg))
        
        # for panning
        self._current_center = glm.vec3(0, 0, 0)
        self._target_center = glm.vec3(0, 0, 0)
        self._pan_speed = 0.01
        
        # for zoom
        self._current_radius = init_radius
        self._target_radius = init_radius
        self._zoom_speed = 0.1
        
        # flags
        self._is_left_dragging = False
        self._is_right_dragging = False
        self._is_middle_dragging = False
        self._last_x = 0
        self._last_y = 0
        self._keys = {
            GLFW_KEY_W: False,
            GLFW_KEY_A: False,
            GLFW_KEY_S: False,
            GLFW_KEY_D: False,
            GLFW_KEY_UP: False,
            GLFW_KEY_LEFT: False,
            GLFW_KEY_DOWN: False,
            GLFW_KEY_RIGHT: False,
        }
        self._center_enabled = True
        
        self._V = AffineMatrix(glm.mat4())
        self.update(0)
        
    def update(self, delta):
        self._update_key_control()
        
        # lerping rotation and panning
        lerping_alpha = delta * 3
        self._current_spherical_angle = glm.mix(self._current_spherical_angle, self._target_spherical_angle, lerping_alpha)
        self._current_center = glm.mix(self._current_center, self._target_center, lerping_alpha)
        self._current_radius = glm.mix(self._current_radius, self._target_radius, lerping_alpha)
        
        self._view_pos.data = (
            self._current_center + # for panning
            glm.vec3(       
                self._current_radius * np.sin(self._current_spherical_angle.y) * np.sin(self._current_spherical_angle.x),
                self._current_radius * np.cos(self._current_spherical_angle.y),
                self._current_radius * np.sin(self._current_spherical_angle.y) * np.cos(self._current_spherical_angle.x)
            ) # for rotation and zoom
        )
        
        self._V.matrix = glm.lookAt(
            self._view_pos.data, 
            self._current_center, 
            glm.vec3(0,1,0)
        )
    
    def key_callback(self, window, key, scancode, action, mods):
        if key in self._keys:
            if action==GLFW_PRESS: self._keys[key] = True
            elif action==GLFW_RELEASE: self._keys[key] = False
        if key==GLFW_KEY_C and action==GLFW_PRESS:
                self._center_enabled = not self._center_enabled
                
    def mouse_button_callback(self, window, button, action, mods):
        if button == GLFW_MOUSE_BUTTON_LEFT:
            if action == GLFW_PRESS:
                self._is_left_dragging = True
                self._last_x, self._last_y = glfwGetCursorPos(window)
            elif action == GLFW_RELEASE:
                self._is_left_dragging = False
        elif button == GLFW_MOUSE_BUTTON_RIGHT:
            if action == GLFW_PRESS:
                self._is_right_dragging = True
                self._last_x, self._last_y = glfwGetCursorPos(window)
            elif action == GLFW_RELEASE:
                self._is_right_dragging = False
        elif button == GLFW_MOUSE_BUTTON_MIDDLE:
            if action == GLFW_PRESS:
                self._is_middle_dragging = True
                self._last_x, self._last_y = glfwGetCursorPos(window)
            elif action == GLFW_RELEASE:
                self._is_middle_dragging = False
                
    def cursor_pos_callback(self, window, xpos, ypos):
        if not (self._is_left_dragging or self._is_right_dragging or self._is_middle_dragging):
            return

        dx = xpos - self._last_x
        dy = ypos - self._last_y
        
        if self._is_left_dragging: self._rotate(-dx, -dy)
        elif self._is_right_dragging: self._pan(-dx, -dy)
        elif self._is_middle_dragging:
            self._zoom(-dy * 0.1 * self._zoom_speed)

        self._last_x = xpos
        self._last_y = ypos
        
    def scroll_callback(self, window, xoffset, yoffset):
        self._zoom(-yoffset * self._zoom_speed)
        
    def _update_key_control(self):
        key_pan_speed = 10
        if self._keys.get(GLFW_KEY_W): self._pan(0, -key_pan_speed)
        if self._keys.get(GLFW_KEY_A): self._pan(-key_pan_speed, 0)
        if self._keys.get(GLFW_KEY_S): self._pan(0, key_pan_speed)
        if self._keys.get(GLFW_KEY_D): self._pan(key_pan_speed, 0)
        
        key_rotate_speed = 0.5
        if self._keys.get(GLFW_KEY_UP): self._rotate(0, -key_rotate_speed)
        if self._keys.get(GLFW_KEY_LEFT): self._rotate(-key_rotate_speed, 0)
        if self._keys.get(GLFW_KEY_DOWN): self._rotate(0, key_rotate_speed)
        if self._keys.get(GLFW_KEY_RIGHT): self._rotate(key_rotate_speed, 0)
        
    def _rotate(self, hor_deg: float, ver_deg: float):
        self._target_spherical_angle.x += np.radians(hor_deg) # phi (horizontal angle)
        self._target_spherical_angle.y += np.radians(ver_deg) # theta (vertical angle)
        self._target_spherical_angle.y = np.clip(self._target_spherical_angle.y, 0, np.pi * 0.5)
        
    def _pan(self, dx: float, dz: float):
        phi = self._current_spherical_angle.x
        sx = dx * self._pan_speed
        sz = dz * self._pan_speed
        
        self._target_center.x += sx * np.cos(phi) + sz * np.sin(phi)
        self._target_center.z += -sx * np.sin(phi) + sz * np.cos(phi)
        
    def _zoom(self, dradius: float):
        self._target_radius += dradius
        self._target_radius = np.clip(self._target_radius, 0.1, 30)

    @property
    def V(self): return self._V
    @property
    def current_center(self): return self._current_center
    @property
    def center_enabled(self): return self._center_enabled