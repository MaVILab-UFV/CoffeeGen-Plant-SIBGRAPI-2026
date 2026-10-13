# Café 1 (~20 meses)
#Altura:               46.4 cm
#Diâmetro da Copa:    53.5 cm

from CoffeeGraph import FolhaTipo
import math

tree_size = 10
generate_iterations = 30

max_depth_ramos = [
    12,  # principal
    7,   # laterais nível 1
    4,   # laterais nível 2
]

min_depth_ramos = [2, 3, 6]
max_depth_folhas = 3

fator_reducao_ramo = 0.82

DELTA_Y_MIN_NIVEL0 = 95
DELTA_Y_MAX_NIVEL0 = 125

ANG_X_MIN_NIVEL0 = 66
ANG_X_MAX_NIVEL0 = 78

DELTA_Y_MIN_RAMO = 36
DELTA_Y_MAX_RAMO = 50

FOLHAS_ESCALA = [0.75, 0.90]
TRONCO_ESCALA_VERTICAL = [0.7, 1.2]

TRONCO_UP_EH = 0.08
MAX_TRONCO_UP_EH_R = 1.5

FOLHAS_POSSIVEIS = [
    FolhaTipo.TIPO1,
    FolhaTipo.TIPO2,
    FolhaTipo.TIPO3,
    FolhaTipo.TIPO4,
    FolhaTipo.TIPO5,
    FolhaTipo.TIPO6,
    FolhaTipo.TIPO7,
    FolhaTipo.TIPO8,
    FolhaTipo.TIPO9,
    FolhaTipo.TIPO10,
    FolhaTipo.TIPO11,
    FolhaTipo.TIPO12,
    FolhaTipo.TIPO13,
    FolhaTipo.TIPO14,
    FolhaTipo.TIPO15,
    FolhaTipo.TIPO16,
    FolhaTipo.TIPO17,
    FolhaTipo.TIPO18,
    FolhaTipo.TIPO19,
    FolhaTipo.TIPO20,
    FolhaTipo.TIPO21,
    FolhaTipo.TIPO22,
    FolhaTipo.TIPO23,
    FolhaTipo.TIPO24,
    FolhaTipo.TIPO25,
    FolhaTipo.TIPO26,
    FolhaTipo.TIPO27,
    FolhaTipo.TIPO28,
    FolhaTipo.TIPO29,
    FolhaTipo.TIPO30,
    FolhaTipo.TIPO31,
    FolhaTipo.TIPO32,
    FolhaTipo.TIPO33,
    FolhaTipo.TIPO34,
    FolhaTipo.TIPO35,
    FolhaTipo.TIPO36,
    FolhaTipo.TIPO37,
    FolhaTipo.TIPO38,
    FolhaTipo.TIPO39,
    FolhaTipo.TIPO40,
    FolhaTipo.TIPO41,
    FolhaTipo.TIPO42,
    FolhaTipo.TIPO43,
    FolhaTipo.TIPO44,
    FolhaTipo.TIPO45,
    FolhaTipo.TIPO46,
]

# parametros do drop das folhas
EPSILON_1 = 0.1 
EPSILON_2 = -0.05

