import math
from CoffeeGraph import Tronco, Folha, MicroFolha, NoReprodutivo
from config import min_depth_ramos, max_depth_folhas, max_depth_ramos, DELTA_Y_MIN_NIVEL0 ,DELTA_Y_MAX_NIVEL0 ,ANG_X_MIN_NIVEL0, ANG_X_MAX_NIVEL0, DELTA_Y_MIN_RAMO, DELTA_Y_MAX_RAMO,fator_reducao_ramo

from builders import add_folhas_e_micro, create_tronco, create_no_reprodutivo
from utils import random_angle, wrap_angle
def apply_rules(planta, node, depth):
    if isinstance(node, Folha):
        if node.parent.depth_max > max_depth_folhas:
            planta.remove_subtree(node)
        return

    if not isinstance(node, NoReprodutivo):
        return

    
    nivel = getattr(node, "ramificacao_nivel", node.parent.ramificacao_nivel)

    has_tronco = any(isinstance(c, Tronco) for c in node.children)
    has_ramificacao = any(isinstance(c, Tronco) and c.ramificacao for c in node.children)
    microfolhas = [c for c in node.children if isinstance(c, MicroFolha)]

    if not has_tronco and microfolhas:
        if depth < max_depth_ramos[nivel]:
            rotation = node.transform.rotation
            maior_ramo = planta.get_depth_max_up_to_ramification(node)
            if nivel == 0:
                delta = random_angle(DELTA_Y_MIN_NIVEL0, DELTA_Y_MAX_NIVEL0)   # 90° a 120°
                # soma
                rotation = (0,wrap_angle(node.transform.rotation[1] + delta),0)
            elif depth >= maior_ramo*fator_reducao_ramo:
                return
                
            planta.remove_subtree(microfolhas[0])
            tronco = create_tronco(
                planta,
                node,
                rotation,
                nivel,
                principal=node.parent.principal,
            )
            no = create_no_reprodutivo(planta, tronco, nivel)
            add_folhas_e_micro(planta, no, no.transform.rotation[1])
   
                

    elif not has_ramificacao and node.depth_max > min_depth_ramos[nivel] and nivel < 2:
        ang_x = node.transform.rotation[0]
        ang_y = node.transform.rotation[1]
        ang_z = node.transform.rotation[2]
        galhos = [0, math.pi]
        
        if nivel == 0:
            ang_x = random_angle(ANG_X_MIN_NIVEL0, ANG_X_MAX_NIVEL0)        
        else:
            delta_y = random_angle(DELTA_Y_MIN_RAMO, DELTA_Y_MAX_RAMO)
            galhos = [-delta_y,delta_y]            
            
        for delta in galhos:
            tronco = create_tronco(
                planta,
                node,
                (ang_x, ang_y+ delta, ang_z),
                nivel + 1,
                principal=False,
                ramificacao=True,
            )
            no = create_no_reprodutivo(planta, tronco, nivel + 1)
            add_folhas_e_micro(planta, no, no.transform.rotation[1])

