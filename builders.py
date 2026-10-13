import math
import random
from CoffeeGraph import Tronco, Folha, MicroFolha, NoReprodutivo, TroncoTipo, FolhaTipo
from config import FOLHAS_POSSIVEIS, FOLHAS_ESCALA, TRONCO_ESCALA_VERTICAL

def add_folhas_e_micro(planta, parent, theta):
    folha_tipo =random.choice(FOLHAS_POSSIVEIS)
    scale_folha = random.uniform(FOLHAS_ESCALA[0], FOLHAS_ESCALA[1])
    folha1 = Folha(
        folha_tipo=folha_tipo,
        position=planta.get_node_world_last_position(parent),
        rotation=(0, theta, 0),
        scale=scale_folha ,
    )
    planta.add_node(parent, folha1)

    folha2 = Folha(
        folha_tipo=folha_tipo,
        position=planta.get_node_world_last_position(parent),
        rotation=(0, theta + math.pi, 0),
        scale=scale_folha ,
    )
    planta.add_node(parent, folha2)

    micro = MicroFolha(
        position=planta.get_node_world_last_position(parent),
        rotation=parent.transform.rotation,
    )
    planta.add_node(parent, micro)

def create_tronco(planta, parent, rotation, nivel, principal=False, ramificacao=False):
    tronco = Tronco(
        tronco_tipo=TroncoTipo.TIPO4,
        position=planta.get_node_world_last_position(parent),
        rotation=rotation,
        scale_vertical=random.uniform(TRONCO_ESCALA_VERTICAL[0], TRONCO_ESCALA_VERTICAL[1]),
        scale_horizontal=1.0,
        principal=principal,
        ramificacao=ramificacao,
        ramificacao_nivel=nivel,
    )
    planta.add_node(parent, tronco)
    return tronco

def create_no_reprodutivo(planta, tronco, nivel):
    no = NoReprodutivo(
        position=planta.get_node_world_last_position(tronco),
        rotation=tronco.transform.rotation,
        ramificacao_nivel=nivel,
    )
    planta.add_node(tronco, no)
    return no
