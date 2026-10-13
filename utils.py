import random
import math
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Optional
import json
import open3d as o3d
import numpy as np
import math
import os


def random_angle(min_deg, max_deg):
    return math.radians(random.uniform(min_deg, max_deg))

def wrap_angle(theta):
    return theta % (2 * math.pi)
    

# ================= CONFIGURAÇÕES =================
base_path = "./"
texture_dir = os.path.join("textures")

# ---- FOLHAS ----
leaf_obj_path = os.path.join(texture_dir, "Leaf.obj")

# ---- TRONCOS ----
trunk_obj_path = os.path.join(texture_dir, "Tronco.obj")

# =================================================

leaf_source = o3d.io.read_triangle_mesh(leaf_obj_path)
trunk_source = o3d.io.read_triangle_mesh(trunk_obj_path)

# =========================================================
# TIPOS BÁSICOS
# =========================================================


Vector3 = Tuple[float, float, float]

def euler_xyz_to_matrix(rot):
    rx, ry, rz = rot

    Rx = np.array([
        [1, 0, 0],
        [0, math.cos(rx), -math.sin(rx)],
        [0, math.sin(rx),  math.cos(rx)]
    ])

    Ry = np.array([
        [ math.cos(ry), 0, math.sin(ry)],
        [0, 1, 0],
        [-math.sin(ry), 0, math.cos(ry)]
    ])

    Rz = np.array([
        [math.cos(rz), -math.sin(rz), 0],
        [math.sin(rz),  math.cos(rz), 0],
        [0, 0, 1]
    ])

    return Rz @ Ry @ Rx

def apply_full_transform(mesh, position, rotation, scale):

    R = euler_xyz_to_matrix(rotation)

   
    # escala NÃO uniforme (como Blender)
    S = np.diag([scale[0], scale[1], scale[2]])

    vertices = np.asarray(mesh.vertices)
    vertices = vertices @ S.T
    mesh.vertices = o3d.utility.Vector3dVector(vertices)

    mesh.rotate(R, center=(0, 0, 0))
    mesh.translate(position)

    mesh.compute_vertex_normals()

    return mesh


def rotate_vector_xyz(v, rot):
    """
    Rotaciona um vetor v=(x,y,z) usando Euler XYZ
    """
    x, y, z = v
    rx, ry, rz = rot

    # Rotação X
    cy = math.cos(rx)
    sy = math.sin(rx)
    y, z = y * cy - z * sy, y * sy + z * cy

    # Rotação Y
    cx = math.cos(ry)
    sx = math.sin(ry)
    x, z = x * cx + z * sx, -x * sx + z * cx

    # Rotação Z
    cz = math.cos(rz)
    sz = math.sin(rz)
    x, y = x * cz - y * sz, x * sz + y * cz

    return (x, y, z)
    
def create_trunk_mesh(node, tronco_size):

    
    mesh = o3d.geometry.TriangleMesh(trunk_source)
    
    scale = (
        node.scale_horizontal,
        node.scale_vertical,
        node.scale_horizontal
    )

    return apply_full_transform(
        mesh,
        node.transform.position,
        node.transform.rotation,
        scale
    )
    
def create_leaf_mesh(node):

    mesh = o3d.geometry.TriangleMesh(leaf_source)

    scale = (node.scale, node.scale, node.scale)

    return apply_full_transform(
        mesh,
        node.transform.position,
        node.transform.rotation,
        scale
    )
 
def create_micro_leaf_mesh(node):

    combined = o3d.geometry.TriangleMesh()
    v_offset = 0

    def append_mesh(target, source):
        nonlocal v_offset

        v = np.asarray(source.vertices)
        t = np.asarray(source.triangles)

        target.vertices.extend(o3d.utility.Vector3dVector(v))
        target.triangles.extend(o3d.utility.Vector3iVector(t + v_offset))

        v_offset += len(v)

    # ---------------------------------------------------
    # TRONCO LOCAL (SEM TRANSFORM GLOBAL)
    # ---------------------------------------------------
    trunk = o3d.geometry.TriangleMesh(trunk_source)

    trunk = apply_full_transform(
        trunk,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale=(0.8, 0.3, 0.8)
    )

    append_mesh(combined, trunk)

    # ---------------------------------------------------
    # FOLHA 1 LOCAL
    # ---------------------------------------------------
    leaf1 = o3d.geometry.TriangleMesh(leaf_source)

    leaf1 = apply_full_transform(
        leaf1,
        position=(0.0, 0.05*0.3, 0.0),
        rotation=(0, 0, 0),
        scale=(0.8*0.4, 0.3*0.4, 0.8*0.4)
    )

    append_mesh(combined, leaf1)

    # ---------------------------------------------------
    # FOLHA 2 LOCAL
    # ---------------------------------------------------
    leaf2 = o3d.geometry.TriangleMesh(leaf_source)

    leaf2 = apply_full_transform(
        leaf2,
        position=(0.0, 0.05*0.3, 0.0),
        rotation=(0, math.pi, 0),
        scale=(0.8*0.4, 0.3*0.4, 0.8*0.4)
    )

    append_mesh(combined, leaf2)

    combined.compute_vertex_normals()

    # ---------------------------------------------------
    # TRANSFORM GLOBAL DO NODE (UMA ÚNICA VEZ)
    # ---------------------------------------------------
    R = euler_xyz_to_matrix(node.transform.rotation)
    combined.rotate(R, center=(0, 0, 0))
    combined.translate(node.transform.position)

    combined.compute_vertex_normals()

    return combined
