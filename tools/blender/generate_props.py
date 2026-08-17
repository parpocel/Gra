import bpy
import colorsys
import math
import random
import sys

import bmesh

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
kind = argv[0] if len(argv) > 0 else "tree"
seed = int(argv[1]) if len(argv) > 1 else random.randint(0, 999999)
out_path = argv[2] if len(argv) > 2 else "/tmp/%s.glb" % kind

random.seed(seed)


def make_material(name, color, roughness=0.9):
	mat = bpy.data.materials.new(name=name)
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes.get("Principled BSDF")
	bsdf.inputs["Base Color"].default_value = (*color, 1.0)
	bsdf.inputs["Roughness"].default_value = roughness
	return mat


def finish(obj, name, color, roughness=0.9):
	obj.name = name
	bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
	obj.data.materials.append(make_material(name + "_mat", color, roughness))
	bpy.ops.object.shade_flat()


def build_tree():
	trunk_h = random.uniform(2.2, 3.4)
	trunk_r_base = random.uniform(0.14, 0.22)
	trunk_r_top = trunk_r_base * random.uniform(0.45, 0.65)
	bark_color = (
		random.uniform(0.28, 0.4),
		random.uniform(0.18, 0.27),
		random.uniform(0.1, 0.16),
	)
	bpy.ops.mesh.primitive_cone_add(
		vertices=7, radius1=trunk_r_base, radius2=trunk_r_top, depth=trunk_h,
		location=(0, 0, trunk_h / 2.0),
	)
	trunk = bpy.context.active_object
	finish(trunk, "TreeTrunk", bark_color, roughness=0.95)

	leaf_base = (
		random.uniform(0.12, 0.22),
		random.uniform(0.35, 0.55),
		random.uniform(0.12, 0.22),
	)
	canopy_z = trunk_h * 0.8
	cluster_count = random.randint(3, 5)
	for i in range(cluster_count):
		r = random.uniform(0.9, 1.4)
		ox = random.uniform(-0.5, 0.5)
		oy = random.uniform(-0.5, 0.5)
		oz = canopy_z + random.uniform(-0.1, 0.45)
		bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=r, location=(ox, oy, oz))
		leaf = bpy.context.active_object
		bm = bmesh.new()
		bm.from_mesh(leaf.data)
		for v in bm.verts:
			v.co += v.normal * random.uniform(-0.12, 0.12)
		bm.to_mesh(leaf.data)
		bm.free()
		leaf.data.update()
		jitter = 0.06
		shade = (
			max(0.0, min(1.0, leaf_base[0] + random.uniform(-jitter, jitter))),
			max(0.0, min(1.0, leaf_base[1] + random.uniform(-jitter, jitter))),
			max(0.0, min(1.0, leaf_base[2] + random.uniform(-jitter, jitter))),
		)
		finish(leaf, "TreeLeaves_%d" % i, shade, roughness=0.85)
		leaf.parent = trunk


def build_rock():
	radius = random.uniform(1.8, 2.6)
	bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=(0, 0, 0))
	rock = bpy.context.active_object
	bm = bmesh.new()
	bm.from_mesh(rock.data)
	for v in bm.verts:
		disp = random.uniform(-0.22, 0.28) * radius
		v.co += v.normal * disp
	bm.to_mesh(rock.data)
	bm.free()
	rock.data.update()

	sx = random.uniform(1.1, 1.5)
	sy = random.uniform(1.0, 1.4)
	sz = random.uniform(0.55, 0.72)
	rock.scale = (sx, sy, sz)
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

	min_z = min((rock.matrix_world @ v.co).z for v in rock.data.vertices)
	rock.location.z -= min_z
	bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)

	stone_color = (
		random.uniform(0.82, 0.92),
		random.uniform(0.8, 0.89),
		random.uniform(0.74, 0.84),
	)
	finish(rock, "Rock", stone_color, roughness=0.95)


bpy.ops.wm.read_factory_settings(use_empty=True)

if kind == "tree":
	build_tree()
else:
	build_rock()

bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=out_path, export_format="GLB")
print("EXPORTED kind=%s seed=%d path=%s" % (kind, seed, out_path))
