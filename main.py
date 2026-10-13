from CoffeeGraph import CafePlantGraph, Tronco, Folha, MicroFolha, NoReprodutivo, TroncoTipo, FolhaTipo
from lsystem import LSystem
from config import generate_iterations, FOLHAS_POSSIVEIS, FOLHAS_ESCALA, EPSILON_1, EPSILON_2
import random

# random.seed(42)

file_name = f"pe_de_cafe"

planta = CafePlantGraph()

tronco = Tronco(
    tronco_tipo=TroncoTipo.TIPO1,
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    scale_vertical=1.0,
    scale_horizontal=1.0,
)
planta.set_root(tronco)

no = NoReprodutivo(
    position=planta.get_node_world_last_position(tronco),
    rotation=(0, 0, 0)
)
planta.add_node(tronco, no)
scale_folha = random.uniform(FOLHAS_ESCALA[0], FOLHAS_ESCALA[1])
for theta in [0, 3.14]:
    folha = Folha(
        folha_tipo=random.choice(FOLHAS_POSSIVEIS),
        position=planta.get_node_world_last_position(no),
        rotation=(0, theta, 0),
        scale=scale_folha,
    )
    planta.add_node(no, folha)

micro = MicroFolha(
    position=planta.get_node_world_last_position(no),
    rotation=(0, 3.14 / 2, 0),
)
planta.add_node(no, micro)

lsys = LSystem(planta)
lsys.generate(generate_iterations)
#lsys.print()

# aplica a queda das folhas 
planta.apply_leaf_drop(EPSILON_1, EPSILON_2)

planta.build_meshes()

area_foliar = planta.get_total_leaf_area()
biomassa = planta.get_biomass()

print(f"🌱 Geração concluída!")
print(f"Área Foliar Total: {area_foliar:.4f} m²")
print(f"Biomassa Estimada: {biomassa:.4f} Kg")



planta.save_to_json(f"{file_name}.json",leaf_area=area_foliar, biomass=biomassa)
# obj sem material
# lsys.save_obj(f"{file_name}.obj")


