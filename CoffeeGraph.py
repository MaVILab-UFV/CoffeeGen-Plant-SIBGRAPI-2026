from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List, Optional
import json

import open3d as o3d
import numpy as np
import math
import os
import random 

from utils import *



class NodeType(Enum):
    TRONCO = "tronco"
    FOLHA = "folha"
    MICRO_FOLHA = "micro_folha"
    REPRODUTIVO = "reprodutivo"


class TroncoTipo(Enum):
    TIPO1 = "tipo001"
    TIPO2 = "tipo002"
    TIPO3 = "tipo003"
    TIPO4 = "tipo004"
    TIPO5 = "tipo005"
    TIPO6 = "tipo006"
    TIPO7 = "tipo007"
    TIPO8 = "tipo008"
    TIPO9 = "tipo009"


class FolhaTipo(Enum):
    TIPO1 = "tipo001"
    TIPO2 = "tipo002"
    TIPO3 = "tipo003"
    TIPO4 = "tipo004"
    TIPO5 = "tipo005"
    TIPO6 = "tipo006"
    TIPO7 = "tipo007"
    TIPO8 = "tipo008"
    TIPO9 = "tipo009"
    TIPO10 = "tipo010"
    TIPO11 = "tipo011"
    TIPO12 = "tipo012"
    TIPO13 = "tipo013"
    TIPO14 = "tipo014"
    TIPO15 = "tipo015"
    TIPO16 = "tipo016"
    TIPO17 = "tipo017"
    TIPO18 = "tipo018"
    TIPO19 = "tipo019"
    TIPO20 = "tipo020"
    TIPO21 = "tipo021"
    TIPO22 = "tipo022"
    TIPO23 = "tipo023"
    TIPO24 = "tipo024"
    TIPO25 = "tipo025"
    TIPO26 = "tipo026"
    TIPO27 = "tipo027"
    TIPO28 = "tipo028"
    TIPO29 = "tipo029"
    TIPO30 = "tipo030"
    TIPO31 = "tipo031"
    TIPO32 = "tipo032"
    TIPO33 = "tipo033"
    TIPO34 = "tipo034"
    TIPO35 = "tipo035"
    TIPO36 = "tipo036"
    TIPO37 = "tipo037"
    TIPO38 = "tipo038"
    TIPO39 = "tipo039"
    TIPO40 = "tipo040"
    TIPO41 = "tipo041"
    TIPO42 = "tipo042"
    TIPO43 = "tipo043"
    TIPO44 = "tipo044"
    TIPO45 = "tipo045"
    TIPO46 = "tipo046"



# =========================================================
# TRANSFORMAÇÃO ESPACIAL
# =========================================================

@dataclass
class Transform:
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]


# =========================================================
# NÓ BASE DO GRAFO
# =========================================================

class Node:
    def __init__(self, node_type: NodeType, transform: Transform, depth_max:int = 0, ramificacao_nivel: int = 0):
        self.node_type: NodeType = node_type
        self.transform: Transform = transform
        self.parent: Optional["Node"] = None
        self.children: List["Node"] = []
        self.depth_max = depth_max
        self.ramificacao_nivel = ramificacao_nivel
        self.mesh = None          # ← referência direta
        self.mesh_id = id(self)   # ← identificador estável

    def add_child(self, child: "Node"):
        child.parent = self
        self.children.append(child)

    def is_root(self) -> bool:
        return self.parent is None


# =========================================================
# TIPOS DE NÓS
# =========================================================

class Tronco(Node):
    def __init__(
        self,
        tronco_tipo: TroncoTipo,
        position: Vector3,
        rotation: Vector3,
        scale_vertical: float,
        scale_horizontal: float,
        principal: bool = True,
        ramificacao: bool = False,
        ramificacao_nivel: int = 0
    ):
        transform = Transform(position, rotation)
        super().__init__(NodeType.TRONCO, transform, ramificacao_nivel = ramificacao_nivel)

        self.tronco_tipo = tronco_tipo
        self.scale_vertical = scale_vertical
        self.scale_horizontal = scale_horizontal
        self.principal = principal
        self.ramificacao = ramificacao
        


class Folha(Node):
    def __init__(
        self,
        folha_tipo: FolhaTipo,
        position: Vector3,
        rotation: Vector3,
        scale: float
    ):
        transform = Transform(position, rotation)
        super().__init__(NodeType.FOLHA, transform)

        self.folha_tipo = folha_tipo
        self.scale = scale


class MicroFolha(Node):
    def __init__(
        self,
        position: Vector3,
        rotation: Vector3
    ):
        transform = Transform(position, rotation)
        super().__init__(NodeType.MICRO_FOLHA, transform)


class NoReprodutivo(Node):
    """
    Nó puramente lógico/topológico.
    Pode conectar qualquer tipo de nó.
    """
    def __init__(
        self,
        position: Vector3 = (0.0, 0.0, 0.0),
        rotation: Vector3 = (0.0, 0.0, 0.0),        
        ramificacao_nivel: int = 0
    ):
        transform = Transform(position, rotation)
        super().__init__(NodeType.REPRODUTIVO, transform,
        ramificacao_nivel = ramificacao_nivel)

def node_to_dict(node: Node) -> dict:
    data = {
        "node_type": node.node_type.value,
        "transform": {
            "position": node.transform.position,
            "rotation": node.transform.rotation
        },
        "children": []
    }

    # Campos específicos por tipo
    if isinstance(node, Tronco):
        data["tronco_tipo"] = node.tronco_tipo.value
        data["scale_vertical"] = node.scale_vertical
        data["scale_horizontal"] = node.scale_horizontal

    elif isinstance(node, Folha):
        data["folha_tipo"] = node.folha_tipo.value
        data["scale"] = node.scale

    elif isinstance(node, NoReprodutivo):
        data["logical"] = True

    # MicroFolha não tem atributos extras

    for child in node.children:
        data["children"].append(node_to_dict(child))

    return data

    
# =========================================================
# GRAFO DO PÉ DE CAFÉ
# =========================================================

class CafePlantGraph:
    def __init__(self,tronco_size = 0.05):
        self.root: Optional[Node] = None
        self.nodes: List[Node] = []
        self.tronco_size = tronco_size

    def get_total_leaf_area(self) -> float:
        """
        Calcula a área foliar total somando a área da superfície (triângulos)
        de todas as malhas do tipo Folha.
        """
        total_area = 0.0
        
        # Garante que as malhas foram construídas antes de calcular
        if not any(node.mesh for node in self.nodes if isinstance(node, Folha)):
            self.build_meshes()
            
        for node in self.nodes:
            # Verifica se é uma folha (ou microfolha, se quiser incluir) e se tem malha gerada
            if isinstance(node, Folha) and node.mesh is not None:
                # O Open3D tem uma função nativa perfeita para somar a área dos triângulos
                total_area += node.mesh.get_surface_area()
                
        return total_area

    def get_biomass(self) -> float:
        """
        Calcula a biomassa estimada usando a equação Y = 0.507 * d^1.923
        onde d é o diâmetro médio entre a base, o meio (50%) e o topo (10cm do ápice).
        """
        if self.root is None or not isinstance(self.root, Tronco):
            return 0.0

        # Largura original do arquivo Tronco.obj
        LARGURA_BASE_OBJ_CM = 0.5 
        
        altura_max = self.get_max_height()
        
        # 1. Coletar todos os nós do tronco principal em uma lista
        tronco_principal_nodes = []
        current = self.root
        
        # Percorre o grafo seguindo apenas o caminho do tronco principal
        while current is not None:
            if isinstance(current, Tronco) and current.principal:
                tronco_principal_nodes.append(current)
                
                # Procura o próximo segmento do tronco principal entre os filhos
                next_node = None
                for child in current.children:
                    if isinstance(child, Tronco) and child.principal:
                        next_node = child
                        break
                current = next_node
            else:
                break
                
        if not tronco_principal_nodes:
            return 0.0

        # 2. Db: Diâmetro da base (o primeiro nó da lista)
        db_node = tronco_principal_nodes[0]
        db = db_node.scale_horizontal * LARGURA_BASE_OBJ_CM

        # Definindo as alturas alvo para o meio e o topo
        h_mid = altura_max * 0.5
        h_top = max(0.0, altura_max - 10.0) # Evita erro se a planta for menor que 10cm

        # Função auxiliar para encontrar o diâmetro do nó mais próximo de uma altura alvo
        def get_closest_diameter(target_h):
            # Encontra o nó cuja posição Y é mais próxima do alvo
            closest_node = min(
                tronco_principal_nodes, 
                key=lambda n: abs(n.transform.position[1] - target_h)
            )
            return closest_node.scale_horizontal * LARGURA_BASE_OBJ_CM

        # 3. Dm e Dt: Pegando os diâmetros calculados
        dm = get_closest_diameter(h_mid)
        dt = get_closest_diameter(h_top)

        # 4. Cálculo do diâmetro médio (d)
        d_medio = (db + dm + dt) / 3.0

        # 5. Aplicação da Equação Alométrica: Y = 0.507 * (d^1.923)
        a = 0.507
        b = 1.923
        biomassa = a * (d_medio ** b)

        return biomassa

    def set_root(self, node: Node):
        self.root = node
        self.nodes.append(node)

    def add_node(self, parent: Node, child: Node):
        parent.add_child(child)
        self.nodes.append(child)

    def traverse_depth_first(self, node: Optional[Node] = None, depth: int = 0):
        if node is None:
            node = self.root
            if node is None:
                return

        info = node.node_type.value

        if isinstance(node, Tronco):
            info += f" ({node.tronco_tipo.value})"
        elif isinstance(node, Folha):
            info += f" ({node.folha_tipo.value})"

        print("  " * depth + f"- {info}")

        for child in node.children:
            self.traverse_depth_first(child, depth + 1)
            
    def max_trunk_depth_from(self, node: Node) -> int:
        """
        Calcula a profundidade máxima em número de troncos
        a partir de um nó (inclusive), considerando o maior caminho.
        """

        # Conta 1 se o nó atual for um tronco
        current = 1 if node.node_type == NodeType.TRONCO else 0

        # Se não tem filhos, retorna o valor atual
        if not node.children:
            return current

        # Calcula o máximo entre os filhos
        max_child_depth = 0
        for child in node.children:
            depth = self.max_trunk_depth_from(child)
            max_child_depth = max(max_child_depth, depth)

        return current + max_child_depth
    

    def update_all_trunk_depths(self):
        """
        Atualiza o atributo node.depth_max para todos os nós do grafo,
        onde depth_max é a profundidade máxima em troncos a partir do nó.
        """

        def dfs(node: Node) -> int:
            # Conta 1 se o nó atual for um tronco
            current = 1 if node.node_type == NodeType.TRONCO else 0

            if not node.children:
                node.depth_max = current
                return node.depth_max

            max_child_depth = 0
            for child in node.children:
                child_depth = dfs(child)
                max_child_depth = max(max_child_depth, child_depth)

            node.depth_max = current + max_child_depth
            return node.depth_max

        if self.root is not None:
            dfs(self.root)

    def remove_subtree(self, node: Node):
        """
        Remove um nó e todos os seus descendentes do grafo.
        """

        if node is None:
            return

        # 1. Coletar todos os nós da subárvore (DFS)
        nodes_to_remove = []

        def dfs(n: Node):
            nodes_to_remove.append(n)
            for child in n.children:
                dfs(child)

        dfs(node)

        # 2. Desconectar do pai (se não for raiz)
        if node.parent is not None:
            node.parent.children = [
                child for child in node.parent.children if child is not node
            ]
        else:
            # Nó é a raiz
            self.root = None

        # 3. Limpar referências internas
        for n in nodes_to_remove:
            n.children.clear()
            n.parent = None

        # 4. Remover da lista global de nós
        self.nodes = [n for n in self.nodes if n not in nodes_to_remove]
        
    def get_node_world_last_position(self, node: Node) -> Vector3:
        """
        Regra:
        - Se NÃO for tronco: retorna posição do próprio nó
        - Se FOR tronco: posição + deslocamento vertical local
        """

        # --- não tronco ---
        if node.node_type != NodeType.TRONCO:
            return node.transform.position

        # --- tronco ---
        px, py, pz = node.transform.position
        rx, ry, rz = node.transform.rotation

        # vetor Y local
        local_y = (0.0, 1.0, 0.0)

        # rotaciona vetor
        dir_x, dir_y, dir_z = rotate_vector_xyz(local_y, (rx, ry, rz))

        length = self.tronco_size * node.scale_vertical

        return (
            px + dir_x * length,
            py + dir_y * length,
            pz + dir_z * length
        )
      
    
    def save_to_json(self, filepath: str, leaf_area: float = 0.0, biomass: float = 0.0):
        if self.root is None:
            raise RuntimeError("Grafo não possui nó raiz")

        graph_dict = {
            "metadata": {
                "tronco_size": self.tronco_size,
                "total_leaf_area": leaf_area,
                "biomass": biomass
            },
            "root": node_to_dict(self.root)
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(graph_dict, f, indent=4)
            
    def clone(self) -> "CafePlantGraph":
        """
        Cria uma cópia profunda (deep copy) da planta,
        recriando todos os nós e relações.
        """

        if self.root is None:
            return CafePlantGraph(self.tronco_size)

        new_graph = CafePlantGraph(self.tronco_size)

        def clone_node(node: Node) -> Node:
            # Clonar nó de acordo com o tipo
            if isinstance(node, Tronco):
                new_node = Tronco(
                    tronco_tipo=node.tronco_tipo,
                    position=node.transform.position,
                    rotation=node.transform.rotation,
                    scale_vertical=node.scale_vertical,
                    scale_horizontal=node.scale_horizontal,
                    principal=node.principal
                )

            elif isinstance(node, Folha):
                new_node = Folha(
                    folha_tipo=node.folha_tipo,
                    position=node.transform.position,
                    rotation=node.transform.rotation,
                    scale=node.scale
                )

            elif isinstance(node, MicroFolha):
                new_node = MicroFolha(
                    position=node.transform.position,
                    rotation=node.transform.rotation
                )

            elif isinstance(node, NoReprodutivo):
                new_node = NoReprodutivo(
                    position=node.transform.position,
                    rotation=node.transform.rotation
                )

            else:
                raise TypeError(f"Tipo de nó não suportado: {type(node)}")

            # Copiar atributos derivados
            new_node.depth_max = node.depth_max

            return new_node

        def dfs(old_node: Node, new_parent: Optional[Node]):
            new_node = clone_node(old_node)

            if new_parent is None:
                new_graph.set_root(new_node)
            else:
                new_graph.add_node(new_parent, new_node)

            for child in old_node.children:
                dfs(child, new_node)

        dfs(self.root, None)

        return new_graph
        
    def count_leaves(self) -> int:
        """
        Conta quantos nós do tipo Folha existem na planta.
        """
        return sum(
            1 for node in self.nodes
            if node.node_type == NodeType.FOLHA
        )
    def count_all_leaves(self) -> int:
        """
        Conta folhas normais + microfolhas.
        """
        return sum(
            1 for node in self.nodes
            if node.node_type in (NodeType.FOLHA, NodeType.MICRO_FOLHA)
        )
    
    def get_max_height(self) -> float:
        """Encontra a coordenada Y mais alta de toda a planta."""
        if not self.nodes:
            return 1.0 # Evita divisão por zero se o grafo estiver vazio
        return max(node.transform.position[1] for node in self.nodes)

    def get_branch_metrics(self, leaf_node: Node) -> Tuple[int, int]:
        """
        Retorna (distancia_ate_o_tronco_principal, tamanho_total_do_galho)
        em quantidade de nós do tipo Tronco.
        """
        dist_to_main = 0
        branch_base = None
        current = leaf_node.parent

        # Sobe na árvore até achar o tronco principal
        while current is not None:
            if isinstance(current, Tronco):
                if current.principal:
                    break # tronco principal
                
                dist_to_main += 1
                if current.ramificacao:
                    branch_base = current # origem do galho lateral

            current = current.parent

        # O tamanho do galho é a profundidade máxima registrada na sua base
        tamanho_galho = branch_base.depth_max if branch_base else 1
        
        return dist_to_main, max(tamanho_galho, 1)

    def apply_leaf_drop(self, epsilon1: float, epsilon2: float):
        """
        Percorre todas as folhas e as remove com base na probabilidade calculada.
        """
        altura_max = self.get_max_height()
        if altura_max <= 0:
            altura_max = 1.0 

        total_folhas_antes = self.count_all_leaves()
        leaves_to_remove = []

        # Coleta os nós para não modificar a lista enquanto itera
        for node in self.nodes:
            if isinstance(node, Folha) or isinstance(node, MicroFolha):
                altura_atual = node.transform.position[1]
                
                dist_tronco_principal, tamanho_galho = self.get_branch_metrics(node)

                # fórmula matemática de probabilidade
                termo_altura = (1.0 - (altura_atual / altura_max) - epsilon1)
                termo_distancia = (1.0 - (dist_tronco_principal / tamanho_galho))
                
                p = (termo_altura * termo_distancia) - epsilon2
                
                # Garante que p seja um percentual válido entre 0.0 e 1.0
                p = max(0.0, min(1.0, p))

                if random.random() < p:
                    leaves_to_remove.append(node)

        # Remove todas as folhas sorteadas para cair
        removed_count = len(leaves_to_remove)
        for leaf in leaves_to_remove:
            self.remove_subtree(leaf)
            
        porcentagem = (removed_count / total_folhas_antes) * 100 if total_folhas_antes > 0 else 0    
        print(f"Queda de folhas: {removed_count} caíram de um total de {total_folhas_antes} ({porcentagem:.1f}%).")

        
    def count_ramos_by_level(self, nivel: int) -> int:
        """
        Conta troncos que são ramos (ramificacao=True)
        em um determinado nível de ramificação.
        """
        return sum(
            1 for node in self.nodes
            if isinstance(node, Tronco)
            and node.ramificacao
            and node.ramificacao_nivel == nivel
        )
    def get_depth_max_up_to_ramification(self, node: Node) -> int:
        """
        Sobe na árvore a partir de um nó e retorna o depth_max do
        pai do primeiro Tronco com ramificacao=True encontrado.
        Se não encontrar, retorna o depth_max da raiz.
        """

        current = node

        while current.parent is not None:
            if isinstance(current, Tronco) and current.ramificacao:
                # testa se o pai existe (por segurança)
                if current.parent is not None:
                    return current.parent.depth_max

            current = current.parent

        # Chegou na raiz
        return current.depth_max
        
    def build_meshes(self):
        """
        Gera meshes Open3D para todos os nós geométricos da planta.
        Mantém associação node.mesh ↔ node.
        Retorna lista de TriangleMesh.
        """

        meshes = []

        for node in self.nodes:

            if isinstance(node, Tronco):
                mesh = create_trunk_mesh(node, self.tronco_size)

            elif isinstance(node, Folha):
                mesh = create_leaf_mesh(node)

            elif isinstance(node, MicroFolha):
                mesh = create_micro_leaf_mesh(node)

            else:
                node.mesh = None  # nó lógico
                continue

            
            node.mesh = mesh      # ← vínculo explícito
            meshes.append(mesh)

        return meshes



# =========================================================
# EXEMPLO DE USO
# =========================================================

if __name__ == "__main__":

    planta = CafePlantGraph()

    tronco1 = Tronco(
        tronco_tipo=TroncoTipo.TIPO1,
        position=(0, 0, 0),
        rotation=(0, 0, 0),
        scale_vertical=1.5,
        scale_horizontal=2.0
    )
    planta.set_root(tronco1)

    no_reprodutivo1 = NoReprodutivo(position= planta.get_node_world_last_position(tronco1),rotation=(0, 0, 0))
    planta.add_node(tronco1, no_reprodutivo1)

    folha1 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position=planta.get_node_world_last_position(no_reprodutivo1),
        rotation=(0, 0, 0),
        scale=1.0
    )
    planta.add_node(no_reprodutivo1, folha1)
    
    folha2 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position=planta.get_node_world_last_position(no_reprodutivo1),
        rotation=(0, 3.14, 3.14/4), # X, Y, Z 
        scale=1.0
    )
    planta.add_node(no_reprodutivo1, folha2)
    
    
    tronco2 = Tronco(
        tronco_tipo=TroncoTipo.TIPO1,
        position=planta.get_node_world_last_position(no_reprodutivo1),
        rotation=(0, 0, 0),
        scale_vertical=1.0,
        scale_horizontal=1.0
    )
    planta.add_node(no_reprodutivo1, tronco2)

    no_reprodutivo2 = NoReprodutivo(position= planta.get_node_world_last_position(tronco2),rotation=(0, 0, 0))
    planta.add_node(tronco2, no_reprodutivo2)

    folha1 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position=planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(0, 0, 0),
        scale=1.0
    )
    planta.add_node(no_reprodutivo2, folha1)
    
    folha2 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position=planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(0, 3.14, 0),
        scale=1.0
    )
    planta.add_node(no_reprodutivo2, folha2)
    
    micro = MicroFolha(
        position= planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(0, 3.14/2, 0)
    )
    planta.add_node(no_reprodutivo2, micro)
    
    
    ##------------------------------------------------------
    
    tronco2 = Tronco(
        tronco_tipo=TroncoTipo.TIPO1,
        position= planta.get_node_world_last_position(no_reprodutivo1),
        rotation=(3.14/2, 0, 0),
        scale_vertical=1.0,
        scale_horizontal=1.0
    )
    planta.add_node(no_reprodutivo1, tronco2)

    no_reprodutivo2 = NoReprodutivo(position=planta.get_node_world_last_position(tronco2),rotation=(0, 0, 0))
    planta.add_node(tronco2, no_reprodutivo2)

    folha1 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position=planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(0, 0, 0),
        scale=1.0
    )
    planta.add_node(no_reprodutivo2, folha1)
    
    folha2 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position= planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(0, 3.14, 0),
        scale=1.0
    )
    planta.add_node(no_reprodutivo2, folha2)
    
    micro = MicroFolha(
        position=planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(3.14/2, 0, 0)
    )
    planta.add_node(no_reprodutivo2, micro)
    
    
    ##------------------------------------------------------
    
    tronco2 = Tronco(
        tronco_tipo=TroncoTipo.TIPO1,
        position= planta.get_node_world_last_position(no_reprodutivo1),
        rotation=(3.14/2, 3.14, 0),
        scale_vertical=1.0,
        scale_horizontal=1.0
    )
    planta.add_node(no_reprodutivo1, tronco2)

    no_reprodutivo2 = NoReprodutivo(position=planta.get_node_world_last_position(tronco2),rotation=(0, 0, 0))
    planta.add_node(tronco2, no_reprodutivo2)

    folha1 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position=planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(0, 3.14, 0),
        scale=1.0
    )
    planta.add_node(no_reprodutivo2, folha1)
    
    folha2 = Folha(
        folha_tipo=FolhaTipo.TIPO2,
        position= planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(0, 3.14+3.14, 0),
        scale=1.0
    )
    planta.add_node(no_reprodutivo2, folha2)
    
    micro = MicroFolha(
        position=planta.get_node_world_last_position(no_reprodutivo2),
        rotation=(3.14/2, 3.14, 0)
    )
    planta.add_node(no_reprodutivo2, micro)

    planta.traverse_depth_first()
    
    planta.save_to_json("pe_de_cafe_teste_angulo_folha2.json")
    
    # salvar planta 
    # def merge_meshes(meshes):
    #     merged = o3d.geometry.TriangleMesh()
    #     v_offset = 0

    #     for m in meshes:
    #         v = np.asarray(m.vertices)
    #         t = np.asarray(m.triangles)

    #         merged.vertices.extend(o3d.utility.Vector3dVector(v))
    #         merged.triangles.extend(
    #             o3d.utility.Vector3iVector(t + v_offset)
    #         )

    #         v_offset += len(v)

    #     merged.compute_vertex_normals()
    #     return merged
    
    # meshes = planta.build_meshes()
    # merged = merge_meshes(meshes)

    # o3d.io.write_triangle_mesh(
    #     "pe_de_cafe_teste_angulo_folha2.obj",
    #     merged,
    #     write_triangle_uvs=True,
    #     write_vertex_normals=True
    # )
    


