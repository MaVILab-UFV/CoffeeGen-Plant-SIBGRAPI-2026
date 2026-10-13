import bpy
import os
import json
import mathutils
# from CoffeeGraph import TroncoTipo, FolhaTipo

# ================= CONFIGURAÇÕES =================
base_path = "C:\\Users\\ezequ\\Desktop\\Teste 2\\CoffeeGen-Plant-main"
texture_dir = os.path.join(base_path, "textures")
json_path = os.path.join(base_path, "pe_de_cafe.json")


leaf_obj_path = os.path.join(texture_dir, "Leaf.obj")
leaf_name = "Leaves"
# leaf_count = len(vars(FolhaTipo)) - 1 # 46
leaf_count = 46
leaf_diffuse_pattern = os.path.join("Folhas", "Textura {:d}", "Diffuse.png")
leaf_opacity_img = os.path.join("Folhas", "Textura {:d}", "Opacity.jpg")
leaf_normal_img = os.path.join("Folhas", "Textura {:d}", "Normal.jpg")


trunk_obj_path = os.path.join(texture_dir, "Tronco.obj")
trunk_name = "Trunk"
# trunk_count = len(vars(TroncoTipo)) - 1 # 6
trunk_count = 13
trunk_diffuse_pattern = "Troncos\\Textura {:d}\\tronco_diffuse.jpg"
trunk_normal_img = "Troncos\\Textura {:d}\\tronco_Normal.jpg"
# =================================================


# =================================================
# UTILIDADES
# =================================================

def import_obj(path, name):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.obj_import(filepath=path)
    obj = bpy.context.selected_objects[0]
    obj.name = name
    return obj


def apply_transform(obj, transform):
    obj.location = transform["position"]
    obj.rotation_euler = transform["rotation"]
    
    
import mathutils

def make_transform_matrix(transform, scale=None):
    """
    Cria matriz 4x4 a partir de:
      - position
      - rotation (Euler)
      - scale (opcional)
    """
    loc = mathutils.Vector(transform["position"])
    rot = mathutils.Euler(transform["rotation"], 'XYZ')

    m_loc = mathutils.Matrix.Translation(loc)
    m_rot = rot.to_matrix().to_4x4()

    if scale is not None:
        m_scale = mathutils.Matrix.Diagonal(
            (scale[0], scale[1], scale[2], 1.0)
        )
    else:
        m_scale = mathutils.Matrix.Identity(4)

    return m_loc @ m_rot @ m_scale


# =================================================
# IMPORTA FONTES
# =================================================

leaf_source  = import_obj(leaf_obj_path,  f"{leaf_name}_source")
trunk_source = import_obj(trunk_obj_path, f"{trunk_name}_source")




# =================================================
# CRIA MATERIAIS (RESUMIDO: REAPROVEITA O SEU)
# =================================================

def load_image(path, colorspace='sRGB'):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    return img


leaf_materials = []
for i in range(1, leaf_count + 1):
    mat = bpy.data.materials.new(name=f"{leaf_name}_MAT_{i:02d}")
    mat.use_nodes = True
    mat.blend_method = 'CLIP'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    tex_diff = nodes.new("ShaderNodeTexImage")
    tex_diff.image = load_image(
        os.path.join(texture_dir, leaf_diffuse_pattern.format(i))
    )

    tex_op = nodes.new("ShaderNodeTexImage")
    tex_op.image = load_image(
        os.path.join(texture_dir, leaf_opacity_img.format(i)), 'Non-Color'
    )

    tex_norm = nodes.new("ShaderNodeTexImage")
    tex_norm.image = load_image(
        os.path.join(texture_dir, leaf_normal_img.format(i)), 'Non-Color'
    )

    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.inputs["Strength"].default_value = 0.4

    links.new(tex_diff.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex_op.outputs["Color"], bsdf.inputs["Alpha"])
    links.new(tex_norm.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    leaf_materials.append(mat)


trunk_materials = []
for i in range(1, trunk_count + 1):
    mat = bpy.data.materials.new(name=f"{trunk_name}_MAT_{i:02d}")
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")

    tex_diff = nodes.new("ShaderNodeTexImage")
    tex_diff.image = load_image(
        os.path.join(texture_dir, trunk_diffuse_pattern.format(i, i))
    )

    tex_norm = nodes.new("ShaderNodeTexImage")
    tex_norm.image = load_image(
        os.path.join(texture_dir, trunk_normal_img.format(i)), 'Non-Color'
    )

    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.inputs["Strength"].default_value = 0.5

    links.new(tex_diff.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tex_norm.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    trunk_materials.append(mat)


# =================================================
# INSTANCIAÇÃO A PARTIR DO JSON
# =================================================

def apply_transform_to_mesh(obj,matrix_world):
    """
    Aplica (congela) a transformação do objeto na mesh.
    Depois disso:
      - location = (0,0,0)
      - rotation = (0,0,0)
      - scale    = (1,1,1)
    Filhos criados depois NÃO herdarão transformações passadas.
    """
    if obj.type != 'MESH':
        return

    mesh = obj.data

    # Aplica a matriz world nos vértices
    mesh.transform(matrix_world)

    # Zera a transformação do objeto
    obj.matrix_world = mathutils.Matrix.Identity(4)

def create_object_from_node(tronco_size,node, parent_obj=None):

    node_type = node["node_type"]
    obj = None

    # ================= TRONCO =================
    if node_type == "tronco":
        obj = trunk_source.copy()
        obj.data = trunk_source.data.copy()
        obj.data.materials.clear()

        # mat_idx = int(node["tronco_tipo"][-1]) - 1
        mat_idx = int(node["tronco_tipo"].replace("tipo", "")) - 1
        print(
            "TRONCO:",
            node["tronco_tipo"],
            "mat_idx:",
            mat_idx,
            "materiais disponíveis:",
            len(trunk_materials)
        )
        
        obj.data.materials.append(trunk_materials[mat_idx])

        scale = (
            node["scale_horizontal"],
            node["scale_vertical"],
            node["scale_horizontal"]
        )

        # congela na geometria
        apply_transform_to_mesh(obj,make_transform_matrix(node["transform"],scale))
        
        bpy.context.collection.objects.link(obj)

    # ================= FOLHA =================
    elif node_type == "folha":
        obj = leaf_source.copy()
        obj.data = leaf_source.data.copy()
        obj.data.materials.clear()

        # mat_idx = int(node["folha_tipo"][-1]) - 1
        mat_idx = int(node["folha_tipo"].replace("tipo", "")) - 1
        print(
            "FOLHA:",
            node["folha_tipo"],
            "mat_idx:",
            mat_idx,
            "materiais disponíveis:",
            len(leaf_materials)
        )
        obj.data.materials.append(leaf_materials[mat_idx])

        scale = (node.get("scale", 1.0),node.get("scale", 1.0),node.get("scale", 1.0))
        

        
        
        # congela na geometria
        apply_transform_to_mesh(obj,make_transform_matrix(node["transform"],scale))
        
        bpy.context.collection.objects.link(obj)

    # ================= MICRO FOLHA (COMPOSTA) =================
    elif node_type == "micro_folha":
        

        # --- tronco da microfolha ---
        trunk = trunk_source.copy()
        trunk.data = trunk_source.data.copy()
        trunk.data.materials.clear()
        trunk.data.materials.append(trunk_materials[3])  # TIPO4

        trunk.scale = (0.8, 0.3, 0.8)
        apply_transform(trunk, node["transform"])
        bpy.context.collection.objects.link(trunk)

        if parent_obj:
            trunk.parent = parent_obj

        # --- folha 1 ---
        leaf1 = leaf_source.copy()
        leaf1.data = leaf_source.data.copy()
        leaf1.data.materials.clear()
        leaf1.data.materials.append(leaf_materials[3])  # TIPO4
        leaf1.scale = (0.4, 0.4, 0.4)
        bpy.context.collection.objects.link(leaf1)
        leaf1.parent = trunk
        leaf1.location = (0.0, 0.05, 0.0)
        leaf1.rotation_euler = (0.0, 0.0, 0.0)        
        

        # --- folha 2 (180° em Y local) ---
        leaf2 = leaf_source.copy()
        leaf2.data = leaf_source.data.copy()
        leaf2.data.materials.clear()
        leaf2.data.materials.append(leaf_materials[3])  # TIPO4
        leaf2.scale = (0.4, 0.4, 0.4)
        bpy.context.collection.objects.link(leaf2)
        leaf2.parent = trunk
        leaf2.rotation_euler = (0.0, 3.14159265, 0.0)
        leaf2.location = (0.0, 0.05, 0.0)
        

        obj = trunk  # para hierarquia do grafo

    # ================= NÓ REPRODUTIVO =================
    elif node_type == "reprodutivo":
        obj = bpy.data.objects.new("Reprodutivo", None)
        # congela na geometria
        apply_transform_to_mesh(obj,make_transform_matrix(node["transform"],None))
        obj.empty_display_size = 0.0
        bpy.context.collection.objects.link(obj)

    # ================= PARENT =================
    if parent_obj and obj and obj.parent is None:
        obj.parent = parent_obj

    # ================= RECURSÃO =================
    for child in node.get("children", []):
        create_object_from_node(tronco_size,child, obj)



# =================================================
# EXECUÇÃO
# =================================================

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

create_object_from_node(data["metadata"]["tronco_size"], data["root"])

bpy.data.objects.remove(leaf_source, do_unlink=True)
bpy.data.objects.remove(trunk_source, do_unlink=True)

## adicionado 
output_path = os.path.join(base_path, "pe_de_cafe_7.blend")
bpy.ops.wm.save_as_mainfile(filepath=output_path)
## adicionado

print("Pé de café gerado com sucesso 🌱")

