import bpy
import colorsys
import random
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
seed = int(argv[0]) if len(argv) > 0 else random.randint(0, 999999)
out_path = argv[1] if len(argv) > 1 else "/tmp/character.glb"

random.seed(seed)


def random_color(s=0.6, v=0.9):
    h = random.random()
    return colorsys.hsv_to_rgb(h, s, v)


def add_box(name, size, location, color):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    mat = bpy.data.materials.new(name=name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    obj.data.materials.append(mat)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_flat()
    return obj


bpy.ops.wm.read_factory_settings(use_empty=True)

skin_tones = [
    (0.94, 0.78, 0.63),
    (0.76, 0.57, 0.42),
    (0.55, 0.38, 0.27),
    (0.36, 0.24, 0.17),
]
skin = random.choice(skin_tones)
shirt_color = random_color()
pants_color = random_color()
has_hat = random.random() < 0.5
hat_color = random_color()

leg_h = random.uniform(0.75, 0.9)
torso_h = random.uniform(0.55, 0.65)
head_s = random.uniform(0.32, 0.4)
torso_w = random.uniform(0.42, 0.52)
torso_d = 0.26
leg_w = 0.16
leg_gap = 0.05

leg_z = leg_h / 2
add_box("Leg_L", (leg_w, torso_d * 0.8, leg_h), (-(leg_gap / 2 + leg_w / 2), 0, leg_z), pants_color)
add_box("Leg_R", (leg_w, torso_d * 0.8, leg_h), (leg_gap / 2 + leg_w / 2, 0, leg_z), pants_color)

torso_z = leg_h + torso_h / 2
add_box("Torso", (torso_w, torso_d, torso_h), (0, 0, torso_z), shirt_color)

arm_w = 0.14
arm_h = torso_h + 0.05
arm_z = leg_h + torso_h - arm_h / 2
arm_x = torso_w / 2 + arm_w / 2
add_box("Arm_L", (arm_w, arm_w, arm_h), (-arm_x, 0, arm_z), skin)
add_box("Arm_R", (arm_w, arm_w, arm_h), (arm_x, 0, arm_z), skin)

head_z = leg_h + torso_h + head_s / 2
add_box("Head", (head_s, head_s, head_s), (0, 0, head_z), skin)

if has_hat:
    hat_h = 0.22
    hat_z = leg_h + torso_h + head_s + hat_h / 2 - 0.02
    add_box("Hat", (head_s * 0.95, head_s * 0.95, hat_h), (0, 0, hat_z), hat_color)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=out_path, export_format="GLB")

print("EXPORTED seed=%d path=%s" % (seed, out_path))
