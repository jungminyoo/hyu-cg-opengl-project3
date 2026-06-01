import os

from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

from cameras import OrbitCamera
from projections import PerspectiveProjection
from experience import Window, Light, Node
from objects import Cube, Diamond, Frame, Grid, OBJModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    
    # initialize environments
    camera = OrbitCamera(45, 60, 10)
    perspective = PerspectiveProjection(1080, 1080, 45, .1, 50)
    window = Window(1080, 1080, "Project 2", perspective, camera)
    light = Light(glm.vec3(20, 20, 20), glm.vec3(1, 1, 1))

    # initialize nodes
    I = glm.mat4()              # identity matrix
    
    # center diamond node
    node_camera_center_diamond = Node(None, I)
    node_camera_center_diamond.set_transform(glm.translate(camera.current_center))
    node_camera_center_diamond.update_tree_global_transform()
    
    # base and city node
    base = Node(None, I)
    node_city = Node(base, 
                     glm.translate(glm.vec3(2, -0.2, 4)) *
                     glm.scale(glm.vec3(.005,.005,.005))
                    )
    
    # drone nodes
    drone_scale = glm.scale(glm.vec3(0.05, 0.05, 0.05))
    node_drone1 = Node(node_city, drone_scale)
    node_drone2 = Node(node_city, drone_scale)
    node_drone3 = Node(node_city, drone_scale)
    node_drone4 = Node(node_city, drone_scale)
    node_drone5 = Node(node_city, drone_scale)

    drone_nodes = [
        node_drone1,
        node_drone2,
        node_drone3,
        node_drone4,
        node_drone5,
    ]

    drone_params = [
        # radius, speed, height, floating_amp, floating_speed, phase
        (1.0, 0.9, 1.2, 0.15, 1.3, 0.0),
        (1.4, 0.6, 1.5, 0.18, 1.0, 1.2),
        (1.8, 1.1, 1.8, 0.12, 1.6, 2.4),
        (2.2, 0.45, 2.1, 0.20, 0.8, 3.1),
        (2.6, 0.75, 2.4, 0.16, 1.4, 4.0),
    ]
    
    # motorcycle node
    node_motorcycle = Node(node_city, glm.rotate(glm.radians(180), glm.vec3(0,1,0)))
    
    # aircraft node
    node_aircraft = Node(node_motorcycle, 
                         glm.rotate(glm.radians(180), glm.vec3(0,1,0)) *
                         glm.scale(glm.vec3(0.1, 0.1, 0.1))
                        )
    
    base.update_tree_global_transform()
    
    # initialize objects
    grid = Grid(camera, perspective, base, 10, 10)
    frame_world = Frame(camera, perspective, base, 10)
    camera_center_diamond = Diamond(glm.vec3(0.45, 0.70, 0.45), camera, perspective, light, node_camera_center_diamond, .1)
    
    # city object
    city = OBJModel(
        glm.vec3(0.8, 0.8, 0.75), camera, perspective, light, node_city, 
        os.path.join(BASE_DIR, "models", "city.obj")
    )
    
    # drone objects
    drone1 = OBJModel(
        glm.vec3(0.95, 0.35, 0.35), camera, perspective, light, node_drone1, 
        os.path.join(BASE_DIR, "models", "drone.obj")
    )
    drone2 = OBJModel(
        glm.vec3(0.35, 0.65, 0.95), camera, perspective, light, node_drone2, 
        os.path.join(BASE_DIR, "models", "drone.obj")
    )
    drone3 = OBJModel(
        glm.vec3(0.45, 0.85, 0.55), camera, perspective, light, node_drone3, 
        os.path.join(BASE_DIR, "models", "drone.obj")
    )
    drone4 = OBJModel(
        glm.vec3(0.95, 0.75, 0.35), camera, perspective, light, node_drone4, 
        os.path.join(BASE_DIR, "models", "drone.obj")
    )
    drone5 = OBJModel(
        glm.vec3(0.75, 0.45, 0.95), camera, perspective, light, node_drone5, 
        os.path.join(BASE_DIR, "models", "drone.obj")
    )
    
    # motorcycle object
    motorcycle = OBJModel(
        glm.vec3(0.6, 0.7, 0.8), camera, perspective, light, node_motorcycle, 
        os.path.join(BASE_DIR, "models", "motorcycle.obj")
    )
    
    # aircraft object
    aircraft = OBJModel(
        glm.vec3(0.8, 0.7, 0.5), camera, perspective, light, node_aircraft, 
        os.path.join(BASE_DIR, "models", "aircraft.obj")
    )
    
    prev_t = glfwGetTime()
    motor_history = []

    # loop until the user closes the window
    while not window.should_close:
        # enable depth test
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        # update polygon mode (GL_FILL or GL_LINE)
        glPolygonMode(GL_FRONT_AND_BACK, window.current_polygon_mode)
        
        t = glfwGetTime()
        delta = t - prev_t
        prev_t = t
        
        # update V matrix
        camera.update(delta)


        # update M matrices
        # center diamond
        T_float = glm.translate(glm.vec3(0, .1 * np.sin(t), 0))
        M_camera_center_diamond = glm.translate(camera.current_center) * T_float
        node_camera_center_diamond.set_transform(M_camera_center_diamond)
        node_camera_center_diamond.update_tree_global_transform()
        
        # city
        city_angle = t * 0.15

        city_x = 3.0 * np.cos(city_angle)
        city_z = 3.0 * np.sin(city_angle)
        city_y = 0.3 * np.sin(t * 0.7)

        T_city = glm.translate(glm.vec3(city_x, city_y, city_z))
        R_tilt = (
            glm.rotate(np.radians(20), glm.vec3(1, 0, 0)) *
            glm.rotate(np.radians(15), glm.vec3(0, 0, 1))
        )
        R_spin = glm.rotate(t * 0.2, glm.vec3(0, 1, 0))

        node_city.set_transform(
            T_city *
            R_spin *
            R_tilt
        )
        
        # drones
        for node_drone, (radius, speed, height, float_amp, float_speed, phase) in zip(drone_nodes, drone_params):
            angle = t * speed + phase

            x = radius * np.cos(angle)
            z = radius * np.sin(angle)
            y = height + float_amp * np.sin(t * float_speed + phase)

            T_orbit = glm.translate(glm.vec3(x, y, z))
            R_heading = glm.rotate(-angle + np.radians(90), glm.vec3(0, 1, 0))

            node_drone.set_transform(T_orbit * R_heading)
            
        # motorcycle
        motor_t = t * 0.6

        motor_x = (
            2.8 * np.sin(motor_t)
            + 0.8 * np.sin(motor_t * 2.3)
        )
        motor_z = (
            2.0 * np.cos(motor_t * 0.8)
            + 0.6 * np.sin(motor_t * 1.7)
        )
        motor_y = (
            0.2
            + 0.08 * np.sin(t * 3.0)
        )

        # 진행 방향 계산
        future_x = (
            2.8 * np.sin(motor_t + 0.01)
            + 0.8 * np.sin((motor_t + 0.01) * 2.3)
        )
        future_z = (
            2.0 * np.cos((motor_t + 0.01) * 0.8)
            + 0.6 * np.sin((motor_t + 0.01) * 1.7)
        )

        dir_x = future_x - motor_x
        dir_z = future_z - motor_z

        heading = np.arctan2(dir_x, dir_z)

        T_motor = glm.translate(glm.vec3(
            motor_x,
            motor_y,
            motor_z
        ))
        R_motor_heading = glm.rotate(
            heading,
            glm.vec3(0, 1, 0)
        )
        R_motor_tilt = (
            glm.rotate(np.radians(10) * np.sin(t * 4), glm.vec3(0, 0, 1)) *
            glm.rotate(np.radians(-6), glm.vec3(1, 0, 0))
        )

        node_motorcycle.set_transform(
            T_motor *
            R_motor_heading *
            R_motor_tilt
        )

        # motorcycle history backup
        motor_history.append(glm.vec3(motor_x, motor_y, motor_z))
        if len(motor_history) > 200:
            motor_history.pop(0)
        
        # aircraft
        if len(motor_history) > 40:
            target_pos = motor_history[0]

            air_x = target_pos.x + 0.5
            air_y = target_pos.y + 0.8 + 0.15 * np.sin(t * 2.5)
            air_z = target_pos.z

            T_air = glm.translate(glm.vec3(
                air_x,
                air_y,
                air_z
            ))
            R_air = (
                glm.rotate(heading, glm.vec3(0, 1, 0)) *
                glm.rotate(np.radians(8) * np.sin(t * 3), glm.vec3(0, 0, 1))
            )

            node_aircraft.set_transform(
                T_air *
                R_air
            )
            
        base.update_tree_global_transform()


        # draw
        frame_world.draw()
        if window.grid_enabled: grid.draw()
        if camera.center_enabled: camera_center_diamond.draw()
        
        city.draw()
        drone1.draw()
        drone2.draw()
        drone3.draw()
        drone4.draw()
        drone5.draw()
        motorcycle.draw()
        aircraft.draw()
        
        window.update()         # update window

    # terminate glfw
    window.terminate()

if __name__ == "__main__":
    main()
