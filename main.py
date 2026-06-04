import os

from OpenGL.GL import *
from glfw.GLFW import *
import glm
import numpy as np

from cameras import OrbitCamera
from projections import PerspectiveProjection
from experience import Window, Light, Node, DanceBattleSystem
from objects import Diamond, Frame, Grid, OBJModel, Character

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    # initialize console UI
    dances = {
        "HipHop": (os.path.join(BASE_DIR, "motions", "dances", "hiphop.bvh"), 0.15, -1.6),
        "ChaCha": (os.path.join(BASE_DIR, "motions", "dances", "chacha.bvh"), 0.06, 1.4),
        "Zumba": (os.path.join(BASE_DIR, "motions", "dances", "zumba.bvh"), 0.15, -1.6),
        "Salsa": (os.path.join(BASE_DIR, "motions", "dances", "salsa.bvh"), 0.15, -1.7),
        "Reggaeton": (os.path.join(BASE_DIR, "motions", "dances", "reggaeton.bvh"), 0.15, -1.7),
    }

    user_characters: dict[str, Character] = {}
    computer_characters: dict[str, Character] = {}

    system = DanceBattleSystem(list(dances.keys()))
    
    # initialize environments
    camera = OrbitCamera(20, 60, 30)
    perspective = PerspectiveProjection(1080, 1080, 45, .1, 50)
    window = Window(1080, 1080, "Project 3", perspective, camera)
    light = Light(glm.vec3(20, 20, 20), glm.vec3(1, 1, 1))

    # initialize nodes
    I = glm.mat4()              # identity matrix
    
    # center diamond node
    node_camera_center_diamond = Node(None, I)
    node_camera_center_diamond.set_transform(glm.translate(camera.current_center))
    node_camera_center_diamond.update_tree_global_transform()
    
    # nodes
    base = Node(None, I)
    node_stage = Node(base, glm.translate((1.2, -0.2, 0)))
    base.update_tree_global_transform()
    
    # initialize objects
    grid = Grid(camera, perspective, base, 10, 10)
    frame_world = Frame(camera, perspective, base, 10)
    camera_center_diamond = Diamond(glm.vec3(0.45, 0.70, 0.45), camera, perspective, light, node_camera_center_diamond, .1)
    
    stage = OBJModel(
        glm.vec3(0.8,0.8,0.8), 
        camera, 
        perspective, 
        light, 
        node_stage, 
        os.path.join(BASE_DIR, "models", "stage.obj"),
    )
    
    # initialize characters
    for name, item in dances.items():
        path, scale, init_y_position = item
        
        user_characters[name] = Character(
            camera,
            perspective,
            light,
            path,
            scale,
            glm.vec3(0.2, 1.0, 0.2),
            glm.vec3(2, init_y_position, 0),
            0
        )

        computer_characters[name] = Character(
            camera,
            perspective,
            light,
            path,
            scale,
            glm.vec3(1.0, 0.2, 0.2),
            glm.vec3(-2, init_y_position, 0),
            0
        )

    user_characters["win"] = Character(
        camera,
        perspective,
        light,
        os.path.join(BASE_DIR, "motions", "results", "win.bvh"),
        0.03,
        glm.vec3(0.2, 1.0, 0.2),
        glm.vec3(0, 1.15, 2),
        90
    )
    user_characters["lose"] = Character(
        camera,
        perspective,
        light,
        os.path.join(BASE_DIR, "motions", "results", "lose.bvh"),
        0.03,
        glm.vec3(0.2, 1.0, 0.2),
        glm.vec3(0, 1.4, -2),
        90
    )

    computer_characters["win"] = Character(
        camera,
        perspective,
        light,
        os.path.join(BASE_DIR, "motions", "results", "win.bvh"),
        0.03,
        glm.vec3(1.0, 0.2, 0.2),
        glm.vec3(0, 1.15, -2),
        90
    )
    computer_characters["lose"] = Character(
        camera,
        perspective,
        light,
        os.path.join(BASE_DIR, "motions", "results", "lose.bvh"),
        0.03,
        glm.vec3(1.0, 0.2, 0.2),
        glm.vec3(0, 1.4, -6),
        90
    )
    
    # initialize crowds
    crowd1 = Character(
        camera, 
        perspective, 
        light, 
        os.path.join(BASE_DIR, "motions", "crowds", "crowd1.bvh"),
        0.015,
        glm.vec3(0.95, 0.35, 0.35),
        glm.vec3(8, 0, 0),
        -90
    )
    crowd1.play()
    crowd2 = Character(
        camera, 
        perspective, 
        light, 
        os.path.join(BASE_DIR, "motions", "crowds", "crowd2.bvh"),
        0.015,
        glm.vec3(0.30, 0.65, 1.00),
        glm.vec3(8, 0, 3),
        -90
    )
    crowd2.play()
    crowd3 = Character(
        camera, 
        perspective, 
        light, 
        os.path.join(BASE_DIR, "motions", "crowds", "crowd3.bvh"),
        0.015,
        glm.vec3(0.35, 0.85, 0.45),
        glm.vec3(8, 0, 6),
        -90
    )
    crowd3.play()
    crowd4 = Character(
        camera, 
        perspective, 
        light, 
        os.path.join(BASE_DIR, "motions", "crowds", "crowd4.bvh"),
        0.015,
        glm.vec3(1.00, 0.75, 0.25), 
        glm.vec3(8, 0, -3),
        -90
    )
    crowd4.play()
    crowd5 = Character(
        camera, 
        perspective, 
        light, 
        os.path.join(BASE_DIR, "motions", "crowds", "crowd5.bvh"),
        0.015,
        glm.vec3(0.75, 0.45, 1.00), 
        glm.vec3(8, 0, -6),
        -90
    )
    crowd5.play()
    
    prev_t = glfwGetTime()

    # loop until the user closes the window
    while not window.should_close:
        # update console UI
        system.update()

        if system.should_quit:
            glfwSetWindowShouldClose(window.window, GLFW_TRUE)

        if system.state == DanceBattleSystem.STATE_WAIT_RESTART \
            and system.final_winner != None:
            if system.final_winner == "User":
                user_characters["win"].play()
                computer_characters["lose"].play()
            elif system.final_winner == "Computer":
                user_characters["lose"].play()
                computer_characters["win"].play()
            if system.final_winner == "Draw":
                user_characters["win"].play()
                computer_characters["win"].play()
        else:
            if system.current_user_choice is not None:
                user_characters[system.current_user_choice].play()
            if system.current_computer_choice is not None:
                computer_characters[system.current_computer_choice].play()
        
        # enable depth test
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        # update polygon mode (GL_FILL or GL_LINE)
        glPolygonMode(GL_FRONT_AND_BACK, window.current_polygon_mode)
        
        t = glfwGetTime()
        delta = t - prev_t
        prev_t = t
        
        # update V matrix
        camera.update(delta, system.state)
        
        # update light
        if system.state in (DanceBattleSystem.STATE_USER_DANCING,
                            DanceBattleSystem.STATE_COMPUTER_DANCING,
                            DanceBattleSystem.STATE_COMPUTER_REVEAL,
                            DanceBattleSystem.STATE_ROUND_RESULT,
                            DanceBattleSystem.STATE_WAIT_NEXT_ROUND):
            light.light_color.data = glm.vec3(
                glm.abs(glm.sin(t * 2) + 1.234) * 0.4 + 0.4,
                glm.abs(glm.cos(t * 2) + 0.778) * 0.4 + 0.4,
                glm.abs(glm.sin(t * 2) - 0.132) * 0.4 + 0.4,
            )
        else: light.light_color.data = glm.vec3(1, 1, 1)

        # update center diamond node
        T_float = glm.translate(glm.vec3(0, .1 * np.sin(t), 0))
        M_camera_center_diamond = glm.translate(camera.current_center) * T_float
        node_camera_center_diamond.set_transform(M_camera_center_diamond)
        node_camera_center_diamond.update_tree_global_transform()
        
        # update nodes
        base.update_tree_global_transform()

        # draw
        frame_world.draw()
        if window.grid_enabled: grid.draw()
        if camera.center_enabled and \
            not (system.state in 
                    (DanceBattleSystem.STATE_USER_DANCING, 
                    DanceBattleSystem.STATE_COMPUTER_DANCING,
                    DanceBattleSystem.STATE_WAIT_RESTART)
            ): camera_center_diamond.draw()
        
        stage.draw()
        
        if system.state == DanceBattleSystem.STATE_WAIT_RESTART \
            and system.final_winner != None:
            if system.final_winner == "User":
                user_characters["win"].draw()
                computer_characters["lose"].draw()
            elif system.final_winner == "Computer":
                user_characters["lose"].draw()
                computer_characters["win"].draw()
            if system.final_winner == "Draw":
                user_characters["win"].draw()
                computer_characters["win"].draw()
        else:
            if system.current_user_choice is not None:
                user_characters[system.current_user_choice].draw()
            if system.current_computer_choice is not None:
                computer_characters[system.current_computer_choice].draw()
        
        crowd1.draw()
        crowd2.draw()
        crowd3.draw()
        crowd4.draw()
        crowd5.draw()
        
        window.update()         # update window

    # terminate glfw
    window.terminate()

if __name__ == "__main__":
    main()
