import sys

import bpy
import mathutils

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path = argv[0]
out_path = argv[1]
target_z = float(argv[2]) if len(argv) > 2 else 1.5
dist = float(argv[3]) if len(argv) > 3 else 6.0

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

bpy.ops.object.light_add(type="SUN", location=(3, -4, 6))
bpy.context.object.data.energy = 3.0
bpy.ops.object.light_add(type="SUN", location=(-3, 3, 4))
bpy.context.object.data.energy = 1.2

target = mathutils.Vector((0, 0, target_z))
cam_loc = mathutils.Vector((dist * 0.7, -dist * 0.7, target_z))
bpy.ops.object.camera_add(location=cam_loc)
cam = bpy.context.object
forward = (target - cam_loc).normalized()
world_up = mathutils.Vector((0, 0, 1))
right = forward.cross(world_up).normalized()
true_up = right.cross(forward).normalized()
rot = mathutils.Matrix((right, true_up, -forward)).transposed()
cam.matrix_world = mathutils.Matrix.Translation(cam_loc) @ rot.to_4x4()
cam.data.lens = 40
bpy.context.scene.camera = cam

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.view_settings.view_transform = "Standard"
scene.world = bpy.data.worlds.new("World")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.9, 0.95, 1)
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("RENDERED", out_path)
