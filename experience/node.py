from __future__ import annotations
import glm

class Node:
    """class for nodes in hierarchical mesh"""
    
    def __init__(self, parent: Node | None, shape_transform: glm.mat4x4):
        # hierarchy
        self._parent = parent
        self._children: list[Node] = []
        if parent is not None:
            parent.add_child(self)

        # transform
        self._transform = glm.mat4()
        self._global_transform = glm.mat4()

        # shape
        self._shape_transform = shape_transform
        
    def add_child(self, child: Node):
        self._children.append(child)

    def set_transform(self, transform: glm.mat4x4):
        self._transform = transform

    def update_tree_global_transform(self):
        if self._parent is not None:
            self._global_transform = self._parent.global_transform * self._transform
        else:
            self._global_transform = self._transform

        for child in self._children:
            child.update_tree_global_transform()

    @property
    def global_transform(self): return self._global_transform
    @property
    def shape_transform(self): return self._shape_transform

class JointLinkNode:
    """class for nodes in character"""
    
    def __init__(self, parent: JointLinkNode | None, link_transform: glm.mat4x4, shape_transform: glm.mat4x4):
        # hierarchy
        self._parent = parent
        self._children: list[JointLinkNode] = []
        if parent is not None:
            parent.add_child(self)

        # transform
        self._link_transform = link_transform
        self._joint_transform = glm.mat4()
        self._global_transform = glm.mat4()

        # shape
        self._shape_transform = shape_transform
        
    def add_child(self, child: JointLinkNode):
        self._children.append(child)

    def set_joint_transform(self, joint_transform: glm.mat4x4):
        self._joint_transform = joint_transform

    def update_tree_global_transform(self):
        if self._parent is not None:
            # Parent * La * Ja
            self._global_transform = self._parent.global_transform \
                                        * self._link_transform \
                                        * self._joint_transform
        else:
            # L0(=I) * J0
            self._global_transform = self._link_transform \
                                    * self._joint_transform

        for child in self._children:
            child.update_tree_global_transform()

    @property
    def global_transform(self): return self._global_transform
    @property
    def shape_transform(self): return self._shape_transform