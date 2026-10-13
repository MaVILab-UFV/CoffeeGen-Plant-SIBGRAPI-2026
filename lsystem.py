from CoffeeGraph import Tronco,TroncoTipo
from rules import apply_rules
from config import TRONCO_UP_EH, MAX_TRONCO_UP_EH_R
import open3d as o3d
import numpy as np



def merge_meshes(meshes):
    merged = o3d.geometry.TriangleMesh()
    v_offset = 0

    for m in meshes:
        v = np.asarray(m.vertices)
        t = np.asarray(m.triangles)

        merged.vertices.extend(o3d.utility.Vector3dVector(v))
        merged.triangles.extend(
            o3d.utility.Vector3iVector(t + v_offset)
        )

        v_offset += len(v)

    merged.compute_vertex_normals()
    return merged

class LSystem:
    def __init__(self, planta):
        planta.update_all_trunk_depths()
        self.planta = planta
        

    def generate(self, iterations):
        for _ in range(iterations):
            self._grow_up(self.planta.root, 0)
            self.planta.update_all_trunk_depths()
        self._fatter(self.planta.root)

    def _grow_up(self, node, depth):
        depth_child = depth 
        if isinstance(node, Tronco):
            if node.ramificacao:
                depth = 0
                depth_child = 1
            else:
                depth_child += 1

        for child in list(node.children):
            self._grow_up(child, depth_child)

        apply_rules(self.planta, node, depth)
        
    def _fatter(self, node):
        if isinstance(node, Tronco):
            if node.depth_max > 4:
                node.tronco_tipo = TroncoTipo.TIPO1
            elif node.depth_max > 3:
                node.tronco_tipo = TroncoTipo.TIPO2
            elif node.depth_max > 2:
                node.tronco_tipo = TroncoTipo.TIPO3
            else:
                node.tronco_tipo = TroncoTipo.TIPO4
            if node.principal:
                node.scale_horizontal = 1.0 + node.depth_max*TRONCO_UP_EH
            else:
                node.scale_horizontal = min(0.8 + node.depth_max*TRONCO_UP_EH, MAX_TRONCO_UP_EH_R)              
                    
                
        for child in list(node.children):
            self._fatter(child)

 
    def save_obj(self, file):
        meshes = self.planta.build_meshes()
        merged = merge_meshes(meshes)

        o3d.io.write_triangle_mesh(
            file,
            merged,
            write_triangle_uvs=True,
            write_vertex_normals=True
        )
        
    def save(self, file):
        self.planta.save_to_json(file)
    def print (self):
        self.planta.traverse_depth_first()
        
