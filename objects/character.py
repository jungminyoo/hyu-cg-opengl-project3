from dataclasses import dataclass, field
import glm

from .object import Object, ObjectWithoutLight
from .diamond import Diamond
from .character_bone import CharacterBone
from cameras import Camera
from projections import Projection
from experience import JointLinkNode, Light


@dataclass
class BVHJoint:
    name: str
    node: "JointLinkNode | None" = None
    object: "Object | None" = None
    bone_object: "ObjectWithoutLight | None" = None
    parent: "BVHJoint | None" = None
    offset: glm.vec3 = field(default_factory=lambda: glm.vec3(0, 0, 0))
    channels: list[str] = field(default_factory=list)
    children: list["BVHJoint"] = field(default_factory=list)
    is_end_site: bool = False
    channel_start_index: int = 0
    def add_child(self, child: "BVHJoint"):
        self.children.append(child)

@dataclass
class BVHData:
    root: BVHJoint
    joints: list[BVHJoint]
    frames: int
    frame_time: float
    motion_values: list[list[float]]
    total_channels: int

class Character:
    '''class for character with motion by bvh'''
    
    def __init__(
        self, 
        camera: Camera, 
        projection: Projection, 
        light: Light,
        path: str,
        scale: float,
        color: glm.vec3,
        init_position: glm.vec3,
        init_y_rotation: float
    ):
        # initialize motion datas
        self._scale = scale
        self._init_position = init_position
        self._init_y_rotation = init_y_rotation
        self._is_playing = False
        self._current_frame_idx = 0
        self._frame_elapsed_time = 0
        
        # parse bvh file
        self._bvh_data = self._load_bvh_and_parse(path)
        # self._print_bvh_data()
        
        # initialize nodes recursively
        self._base_node = JointLinkNode(None, glm.rotate(glm.radians(self._init_y_rotation), (0,1,0)), glm.mat4())
        self._initialize_node(self._bvh_data.root, self._base_node)
        self._base_node.update_tree_global_transform()
        
        # initialize objects
        for joint in self._bvh_data.joints:
            cube = Diamond(color, camera, projection, light, joint.node, 0.08)
            joint.object = cube
            
            if (joint.parent is not None) and (joint.parent.node is not None):
                bone = CharacterBone(camera, projection, joint.node, joint.parent.node, color)
                joint.bone_object = bone

    def play(self):
        self._is_playing = True
    def reset(self):
        self._current_frame_idx = 0
        self._frame_elapsed_time = 0
        
    def _apply_frame(self, frame_idx: int):
        current_frame = self._bvh_data.motion_values[frame_idx]

        for joint in self._bvh_data.joints:
            M = glm.mat4()

            for channel_idx in range(len(joint.channels)):
                motion_idx = joint.channel_start_index + channel_idx
                frame_value = current_frame[motion_idx]
                channel = joint.channels[channel_idx]

                if channel == "Xrotation":
                    M *= glm.rotate(glm.radians(frame_value), (1, 0, 0))
                elif channel == "Yrotation":
                    M *= glm.rotate(glm.radians(frame_value), (0, 1, 0))
                elif channel == "Zrotation":
                    M *= glm.rotate(glm.radians(frame_value), (0, 0, 1))
                elif channel == "Xposition":
                    M *= glm.translate(
                        glm.vec3(self._init_position.x, 0, 0) +
                        glm.vec3(frame_value * self._scale, 0, 0)
                    )
                elif channel == "Yposition":
                    M *= glm.translate(
                        glm.vec3(0, self._init_position.y, 0) +
                        glm.vec3(0, frame_value * self._scale, 0)
                    )
                elif channel == "Zposition":
                    M *= glm.translate(
                        glm.vec3(0, 0, self._init_position.z) +
                        glm.vec3(0, 0, frame_value * self._scale)
                    )

            joint.node.set_joint_transform(M)

        self._base_node.update_tree_global_transform()

    def draw(self, delta: float):
        if self._is_playing:
            self._frame_elapsed_time += delta

            while self._frame_elapsed_time >= self._bvh_data.frame_time:
                self._current_frame_idx += 1
                self._current_frame_idx %= self._bvh_data.frames
                self._frame_elapsed_time -= self._bvh_data.frame_time

        self._apply_frame(self._current_frame_idx)

        for joint in self._bvh_data.joints:
            joint.object.draw()
            if joint.bone_object is not None:
                joint.bone_object.draw()
        
    def _initialize_node(self, joint: BVHJoint, parent: JointLinkNode | None):
        node = JointLinkNode(parent, glm.translate(joint.offset * self._scale), glm.mat4())
        joint.node = node
        
        for child in joint.children:
            self._initialize_node(child, node)
            
        return node
    
    def _load_bvh_and_parse(self, path: str) -> BVHData:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        idx = 0
        joints: list[BVHJoint] = []
        total_channels = 0

        def parse_joint(parent: BVHJoint | None) -> BVHJoint:
            nonlocal idx, total_channels

            parts = lines[idx].split()

            if parts[0] == "ROOT" or parts[0] == "JOINT":
                joint_name = parts[1]
                joint = BVHJoint(name=joint_name, parent=parent)

                if parent is not None:
                    parent.add_child(joint)

                joints.append(joint)

                idx += 1  # ROOT/JOINT line
                assert lines[idx] == "{"
                idx += 1

                while idx < len(lines):
                    parts = lines[idx].split()

                    if parts[0] == "OFFSET":
                        joint.offset = glm.vec3(
                            float(parts[1]),
                            float(parts[2]),
                            float(parts[3]),
                        )
                        idx += 1

                    elif parts[0] == "CHANNELS":
                        channel_count = int(parts[1])
                        joint.channels = parts[2:2 + channel_count]
                        joint.channel_start_index = total_channels
                        total_channels += channel_count
                        idx += 1

                    elif parts[0] == "JOINT":
                        parse_joint(joint)

                    elif parts[0] == "End":
                        parse_end_site(joint)

                    elif parts[0] == "}":
                        idx += 1
                        break

                    else:
                        idx += 1

                return joint

            raise ValueError(f"Invalid joint line: {lines[idx]}")

        def parse_end_site(parent: BVHJoint):
            nonlocal idx

            # line: End Site
            end_joint = BVHJoint(
                name=f"{parent.name}_EndSite",
                parent=parent,
                is_end_site=True,
            )
            parent.add_child(end_joint)

            idx += 1  # End Site
            assert lines[idx] == "{"
            idx += 1

            while idx < len(lines):
                parts = lines[idx].split()

                if parts[0] == "OFFSET":
                    end_joint.offset = glm.vec3(
                        float(parts[1]),
                        float(parts[2]),
                        float(parts[3]),
                    )
                    idx += 1

                elif parts[0] == "}":
                    idx += 1
                    break

                else:
                    idx += 1

        # HIERARCHY
        if lines[idx] != "HIERARCHY":
            raise ValueError("BVH file must start with HIERARCHY")
        idx += 1

        root = parse_joint(None)

        # MOTION
        if lines[idx] != "MOTION":
            raise ValueError("Expected MOTION section")
        idx += 1

        # Frames: 834
        frames_parts = lines[idx].replace(":", " ").split()
        frames = int(frames_parts[1])
        idx += 1

        # Frame Time: 0.00833333
        frame_time_parts = lines[idx].replace(":", " ").split()
        frame_time = float(frame_time_parts[2])
        idx += 1

        motion_values: list[list[float]] = []

        for _ in range(frames):
            values = [float(v) for v in lines[idx].split()]

            if len(values) != total_channels:
                raise ValueError(
                    f"Motion channel count mismatch: "
                    f"expected {total_channels}, got {len(values)} at frame {len(motion_values)}"
                )

            motion_values.append(values)
            idx += 1

        return BVHData(
            root=root,
            joints=joints,
            frames=frames,
            frame_time=frame_time,
            motion_values=motion_values,
            total_channels=total_channels,
        )
        
    def _print_bvh_data(self):
        print("root:", self._bvh_data.root.name)
        print("joint count:", len(self._bvh_data.joints))
        print("frames:", self._bvh_data.frames)
        print("frame time:", self._bvh_data.frame_time)
        print("total channels:", self._bvh_data.total_channels)

        for joint in self._bvh_data.joints:
            print(joint.name, joint.offset, joint.channels, joint.channel_start_index)
