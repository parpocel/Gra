import bpy
import math
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
glb_path = argv[0]
out_path = argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

import mathutils

bpy.ops.object.light_add(type="SUN", location=(3, -4, 6))
bpy.context.object.data.energy = 3.0
bpy.ops.object.light_add(type="SUN", location=(-3, 3, 4))
bpy.context.object.data.energy = 1.2

target = mathutils.Vector((0, 0, 0.9))
cam_loc = mathutils.Vector((3.4, -3.4, 1.6))
bpy.ops.object.camera_add(location=cam_loc)
cam = bpy.context.object
direction = target - cam_loc
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 50
bpy.context.scene.camera = cam

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 640
scene.render.film_transparent = False
scene.view_settings.view_transform = "Standard"
scene.world = bpy.data.worlds.new("World")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.9, 0.95, 1)
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("RENDERED", out_path)
