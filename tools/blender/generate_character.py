import bpy
import colorsys
import math
import random
import sys

import bmesh

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
seed = int(argv[0]) if len(argv) > 0 else random.randint(0, 999999)
out_path = argv[1] if len(argv) > 1 else "/tmp/character.glb"
preset = argv[2] if len(argv) > 2 else None

random.seed(seed)

FPS = 24
objects = {}
rest_state = []


def random_color(s=0.6, v=0.9, h_range=(0.0, 1.0)):
	h = random.uniform(*h_range)
	return colorsys.hsv_to_rgb(h, s, v)


def reparent(child, parent):
	child.parent = parent
	child.matrix_parent_inverse = parent.matrix_world.inverted()
	bpy.context.view_layer.update()


def finish_part(obj, name, pivot_pos, color, parent=None, bevel=True, bevel_segments=4):
	obj.name = name
	bpy.context.scene.cursor.location = pivot_pos
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
	bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

	if bevel:
		dims = [d for d in obj.dimensions if d > 0.001]
		min_dim = min(dims) if dims else 0.05
		bevel_width = min(0.016, max(0.004, min_dim * 0.12))
		mod = obj.modifiers.new(name="Bevel", type="BEVEL")
		mod.width = bevel_width
		mod.segments = bevel_segments
		mod.limit_method = "ANGLE"
		mod.angle_limit = math.radians(35)
		bpy.ops.object.modifier_apply(modifier=mod.name)

	bpy.ops.object.shade_flat()
	bpy.context.view_layer.update()

	mat = bpy.data.materials.new(name=name + "_mat")
	mat.use_nodes = True
	bsdf = mat.node_tree.nodes.get("Principled BSDF")
	bsdf.inputs["Base Color"].default_value = (*color, 1.0)
	bsdf.inputs["Roughness"].default_value = 0.9
	obj.data.materials.append(mat)
	obj.rotation_mode = "XYZ"

	if parent is not None:
		obj.parent = parent
		obj.matrix_parent_inverse = parent.matrix_world.inverted()
		bpy.context.view_layer.update()

	objects[name] = obj
	return obj


def add_box(name, size, center_pos, pivot_pos, color, parent=None, bevel=True):
	bpy.ops.mesh.primitive_cube_add(size=1, location=center_pos)
	obj = bpy.context.active_object
	obj.scale = size
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	return finish_part(obj, name, pivot_pos, color, parent, bevel=bevel)


def add_tapered_box(name, top_wd, bottom_wd, height, center_pos, pivot_pos, color, parent=None):
	bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
	obj = bpy.context.active_object
	bm = bmesh.new()
	bm.from_mesh(obj.data)
	for v in bm.verts:
		w, d = top_wd if v.co.z > 0 else bottom_wd
		v.co.x *= w
		v.co.y *= d
		v.co.z *= height
	bm.to_mesh(obj.data)
	bm.free()
	obj.data.update()
	obj.location = center_pos
	bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
	return finish_part(obj, name, pivot_pos, color, parent, bevel=True)


def add_limb(name, radius_top, radius_bottom, height, center_pos, pivot_pos, color, parent=None, sides=8, bevel_segments=2):
	bpy.ops.mesh.primitive_cone_add(vertices=sides, radius1=radius_bottom, radius2=radius_top, depth=height, location=center_pos)
	obj = bpy.context.active_object
	return finish_part(obj, name, pivot_pos, color, parent, bevel=True, bevel_segments=bevel_segments)


def add_joint(name, radius, center_pos, color, parent=None):
	bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=center_pos)
	obj = bpy.context.active_object
	return finish_part(obj, name, center_pos, color, parent, bevel=False)


def add_sphere(name, radius, center_pos, pivot_pos, color, parent=None, subdivisions=2, z_scale=1.0):
	bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius, location=(0, 0, 0))
	obj = bpy.context.active_object
	obj.scale.z = z_scale
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
	obj.location = center_pos
	bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
	return finish_part(obj, name, pivot_pos, color, parent, bevel=False)


def animate_rot_x(obj, track_name, start_frame, cycle_frames, amplitude_deg, phase_offset=0.0, samples=8, offset_deg=0.0):
	if obj.animation_data is None:
		obj.animation_data_create()
	action = bpy.data.actions.new(name="%s_%s_act" % (obj.name, track_name))
	obj.animation_data.action = action
	base_rot = obj.rotation_euler.copy()
	for i in range(samples + 1):
		t = i / samples
		frame = start_frame + t * cycle_frames
		angle = offset_deg + amplitude_deg * math.sin(2 * math.pi * t + phase_offset)
		obj.rotation_euler = base_rot
		obj.rotation_euler.x = base_rot.x + math.radians(angle)
		obj.keyframe_insert(data_path="rotation_euler", index=0, frame=frame)
	obj.rotation_euler = base_rot
	track = obj.animation_data.nla_tracks.new()
	track.name = track_name
	track.strips.new(track_name, start_frame, action)
	obj.animation_data.action = None
	rest_state.append((obj, "rotation_euler", base_rot))


def animate_knee_bend(obj, track_name, start_frame, cycle_frames, amplitude_deg, phase_offset=0.0, samples=8, sign=1.0):
	if obj.animation_data is None:
		obj.animation_data_create()
	action = bpy.data.actions.new(name="%s_%s_bend" % (obj.name, track_name))
	obj.animation_data.action = action
	base_rot = obj.rotation_euler.copy()
	for i in range(samples + 1):
		t = i / samples
		frame = start_frame + t * cycle_frames
		bend = amplitude_deg * max(0.0, math.cos(2 * math.pi * t + phase_offset))
		obj.rotation_euler = base_rot
		obj.rotation_euler.x = base_rot.x + sign * math.radians(bend)
		obj.keyframe_insert(data_path="rotation_euler", index=0, frame=frame)
	obj.rotation_euler = base_rot
	track = obj.animation_data.nla_tracks.new()
	track.name = track_name
	track.strips.new(track_name, start_frame, action)
	obj.animation_data.action = None
	rest_state.append((obj, "rotation_euler", base_rot))


def animate_pos_z(obj, track_name, start_frame, cycle_frames, amplitude, phase_offset=0.0, samples=8, freq_mult=1.0):
	if obj.animation_data is None:
		obj.animation_data_create()
	action = bpy.data.actions.new(name="%s_%s_posact" % (obj.name, track_name))
	obj.animation_data.action = action
	base_pos = obj.location.copy()
	for i in range(samples + 1):
		t = i / samples
		frame = start_frame + t * cycle_frames
		offset = amplitude * math.sin(2 * math.pi * t * freq_mult + phase_offset)
		obj.location = base_pos
		obj.location.z = base_pos.z + offset
		obj.keyframe_insert(data_path="location", index=2, frame=frame)
	obj.location = base_pos
	track = obj.animation_data.nla_tracks.new()
	track.name = track_name
	track.strips.new(track_name, start_frame, action)
	obj.animation_data.action = None
	rest_state.append((obj, "location", base_pos))


bpy.ops.wm.read_factory_settings(use_empty=True)

skin_tones = [
	(0.94, 0.78, 0.63),
	(0.76, 0.57, 0.42),
	(0.55, 0.38, 0.27),
	(0.36, 0.24, 0.17),
]
shoe_tones = [(0.95, 0.95, 0.92), (0.42, 0.28, 0.18), (0.08, 0.08, 0.09), (0.75, 0.65, 0.45)]
hair_tones = [(0.15, 0.1, 0.08), (0.35, 0.22, 0.12), (0.05, 0.05, 0.05), (0.55, 0.5, 0.48)]
book_tones = [(0.55, 0.08, 0.08), (0.3, 0.18, 0.08), (0.08, 0.3, 0.15), (0.1, 0.15, 0.4)]

skin = random.choice(skin_tones)
jacket_color = random_color(s=0.55, v=0.85)
shirt_color = random_color(s=0.5, v=0.9)
pants_color = random_color(s=0.35, v=0.55)
shoe_color = random.choice(shoe_tones)
cap_color = random_color(s=0.55, v=0.85)
cap_logo_color = random_color(s=0.7, v=0.9)
hair_color = random.choice(hair_tones)
backpack_color = random_color(s=0.5, v=0.7)
book_color = random.choice(book_tones)

has_cap = random.random() < 0.7
has_beard = random.random() < 0.6
has_backpack = random.random() < 0.5
has_book = random.random() < 0.4

if preset == "piotr":
	skin = (0.80, 0.62, 0.47)
	jacket_color = (0.10, 0.10, 0.11)
	shirt_color = (0.92, 0.92, 0.90)
	pants_color = (0.22, 0.22, 0.24)
	shoe_color = (0.10, 0.09, 0.09)
	cap_color = (0.07, 0.07, 0.08)
	cap_logo_color = (0.65, 0.1, 0.1)
	hair_color = (0.16, 0.1, 0.07)
	backpack_color = (0.15, 0.15, 0.16)
	book_color = (0.5, 0.08, 0.08)
	has_cap = True
	has_beard = True
	has_backpack = False
	has_book = False

# --- proportions (feet at z=0), loosely human-skeleton-scaled ---
foot_h = 0.10
lower_leg_h = 0.42
upper_leg_h = 0.42
torso_h = 0.60
neck_h = 0.17
head_r = 0.19
upper_arm_h = 0.30
lower_arm_h = 0.28
hand_h = 0.12

z_ankle = foot_h
z_knee = z_ankle + lower_leg_h
z_hip = z_knee + upper_leg_h
z_shoulder = z_hip + torso_h
z_neck_top = z_shoulder + neck_h
z_head_center = z_neck_top + head_r

z_elbow = z_shoulder - upper_arm_h
z_wrist = z_elbow - lower_arm_h
z_hand_bottom = z_wrist - hand_h

leg_x = 0.13
arm_x = 0.27
shoulder_wd = (0.52, 0.30)
waist_wd = (0.38, 0.24)

# --- torso (tapered: wider at shoulders, narrower at waist) + shirt + spine seam ---
torso = add_tapered_box(
	"Torso", shoulder_wd, waist_wd, torso_h,
	(0.0, 0.0, (z_hip + z_shoulder) / 2.0), (0.0, 0.0, (z_hip + z_shoulder) / 2.0),
	jacket_color,
)
add_box(
	"Shirt", (shoulder_wd[0] * 0.55, shoulder_wd[1] * 1.05, 0.10),
	(0.0, 0.0, z_shoulder - 0.02), (0.0, 0.0, z_shoulder - 0.02),
	shirt_color, parent=torso,
)
add_box(
	"Spine", (0.05, 0.04, torso_h * 0.92),
	(0.0, shoulder_wd[1] * 0.5, (z_hip + z_shoulder) / 2.0), (0.0, shoulder_wd[1] * 0.5, (z_hip + z_shoulder) / 2.0),
	tuple(max(0.0, c - 0.05) for c in jacket_color), parent=torso, bevel=False,
)

if has_backpack:
	add_box(
		"Backpack", (shoulder_wd[0] * 0.7, 0.16, torso_h * 0.85),
		(0.0, shoulder_wd[1] * 0.5 + 0.1, (z_hip + z_shoulder) / 2.0), (0.0, shoulder_wd[1] * 0.5 + 0.1, (z_hip + z_shoulder) / 2.0),
		backpack_color, parent=torso,
	)

# --- neck ---
neck = add_limb(
	"Neck", 0.085, 0.10, neck_h,
	(0.0, 0.0, (z_shoulder + z_neck_top) / 2.0), (0.0, 0.0, z_shoulder),
	skin, parent=torso, sides=8,
)

# --- legs (parented to torso so hip-bob during Walk/Run carries the whole body) ---
for side, sx in (("L", -leg_x), ("R", leg_x)):
	foot = add_box(
		"Foot_%s" % side, (0.15, 0.24, foot_h),
		(sx, 0.09, foot_h / 2.0), (sx, 0.0, 0.0),
		shoe_color,
	)
	lower_leg = add_limb(
		"LowerLeg_%s" % side, 0.075, 0.055, lower_leg_h,
		(sx, 0.0, (z_ankle + z_knee) / 2.0), (sx, 0.0, z_knee),
		pants_color,
	)
	reparent(foot, lower_leg)
	knee = add_joint("Knee_%s" % side, 0.08, (sx, 0.0, z_knee), pants_color)
	reparent(knee, lower_leg)
	upper_leg = add_limb(
		"UpperLeg_%s" % side, 0.105, 0.078, upper_leg_h,
		(sx, 0.0, (z_knee + z_hip) / 2.0), (sx, 0.0, z_hip),
		pants_color, parent=torso,
	)
	reparent(lower_leg, upper_leg)
	hip_joint = add_joint("Hip_%s" % side, 0.1, (sx, 0.0, z_hip), pants_color, parent=torso)

# --- head + face details (round head on a neck) ---
head = add_sphere(
	"Head", head_r, (0.0, 0.0, z_head_center), (0.0, 0.0, z_neck_top),
	skin, parent=torso, subdivisions=2,
)
add_box(
	"Glasses", (head_r * 1.7, 0.05, head_r * 0.4),
	(0.0, -head_r * 1.15, z_head_center), (0.0, -head_r * 1.15, z_head_center),
	(0.05, 0.05, 0.05), parent=head, bevel=False,
)
if has_beard:
	add_box(
		"Beard", (head_r * 1.45, head_r * 0.95, head_r * 0.55),
		(0.0, -head_r * 0.35, z_head_center - head_r * 0.45), (0.0, -head_r * 0.35, z_head_center - head_r * 0.45),
		hair_color, parent=head,
	)
if has_cap:
	add_sphere(
		"Cap", head_r * 1.08, (0.0, 0.0, z_head_center + head_r * 0.62), (0.0, 0.0, z_head_center + head_r * 0.62),
		cap_color, parent=head, subdivisions=2, z_scale=0.62,
	)
	add_box(
		"CapBrim", (head_r * 0.9, head_r * 0.6, head_r * 0.12),
		(0.0, -head_r * 1.02, z_head_center + head_r * 0.5), (0.0, -head_r * 1.02, z_head_center + head_r * 0.5),
		cap_color, parent=head,
	)
	add_box(
		"CapLogo", (head_r * 0.4, 0.02, head_r * 0.28),
		(0.0, -head_r * 0.9, z_head_center + head_r * 0.65), (0.0, -head_r * 0.9, z_head_center + head_r * 0.65),
		cap_logo_color, parent=head, bevel=False,
	)
else:
	add_sphere(
		"Hair", head_r * 1.08, (0.0, 0.0, z_head_center + head_r * 0.3), (0.0, 0.0, z_head_center + head_r * 0.3),
		hair_color, parent=head, subdivisions=2, z_scale=0.75,
	)

# --- arms ---
for side, sx in (("L", -arm_x), ("R", arm_x)):
	upper_arm = add_limb(
		"UpperArm_%s" % side, 0.072, 0.058, upper_arm_h,
		(sx, 0.0, (z_elbow + z_shoulder) / 2.0), (sx, 0.0, z_shoulder),
		jacket_color, parent=torso,
	)
	shoulder_joint = add_joint("Shoulder_%s" % side, 0.078, (sx, 0.0, z_shoulder), jacket_color, parent=torso)
	lower_arm = add_limb(
		"LowerArm_%s" % side, 0.052, 0.042, lower_arm_h,
		(sx, 0.0, (z_wrist + z_elbow) / 2.0), (sx, 0.0, z_elbow),
		skin,
	)
	reparent(lower_arm, upper_arm)
	elbow = add_joint("Elbow_%s" % side, 0.055, (sx, 0.0, z_elbow), skin)
	reparent(elbow, upper_arm)
	hand = add_box(
		"Hand_%s" % side, (0.09, 0.045, hand_h),
		(sx, 0.0, (z_hand_bottom + z_wrist) / 2.0), (sx, 0.0, z_wrist),
		skin,
	)
	reparent(hand, lower_arm)
	if has_book and side == "R":
		add_box(
			"Book", (0.14, 0.03, 0.18),
			(sx, -0.09, z_hand_bottom + 0.03), (sx, -0.09, z_hand_bottom + 0.03),
			book_color, parent=hand,
		)

# ================= animations =================
UL = objects["UpperLeg_L"]
UR = objects["UpperLeg_R"]
LL = objects["LowerLeg_L"]
LR = objects["LowerLeg_R"]
AL = objects["UpperArm_L"]
AR = objects["UpperArm_R"]

# --- Idle: subtle breathing sway ---
animate_rot_x(AL, "Idle", 1, FPS * 2.0, amplitude_deg=4.0, phase_offset=0.0)
animate_rot_x(AR, "Idle", 1, FPS * 2.0, amplitude_deg=4.0, phase_offset=0.0)
animate_pos_z(torso, "Idle", 1, FPS * 2.0, amplitude=0.012, phase_offset=0.0)

# --- Walk: alternating arm/leg swing with knee bend during the forward-swing phase ---
animate_rot_x(UL, "Walk", 1, FPS * 1.0, amplitude_deg=28.0, phase_offset=0.0)
animate_rot_x(UR, "Walk", 1, FPS * 1.0, amplitude_deg=28.0, phase_offset=math.pi)
animate_knee_bend(LL, "Walk", 1, FPS * 1.0, amplitude_deg=45.0, phase_offset=0.0, sign=-1.0)
animate_knee_bend(LR, "Walk", 1, FPS * 1.0, amplitude_deg=45.0, phase_offset=math.pi, sign=-1.0)
animate_rot_x(AR, "Walk", 1, FPS * 1.0, amplitude_deg=24.0, phase_offset=0.0)
animate_rot_x(AL, "Walk", 1, FPS * 1.0, amplitude_deg=24.0, phase_offset=math.pi)
animate_pos_z(torso, "Walk", 1, FPS * 1.0, amplitude=0.02, phase_offset=math.pi / 2.0, freq_mult=2.0)

# --- Run: bigger/faster swing + more bob ---
animate_rot_x(UL, "Run", 1, FPS * 0.55, amplitude_deg=48.0, phase_offset=0.0, offset_deg=-8.0)
animate_rot_x(UR, "Run", 1, FPS * 0.55, amplitude_deg=48.0, phase_offset=math.pi, offset_deg=-8.0)
animate_knee_bend(LL, "Run", 1, FPS * 0.55, amplitude_deg=70.0, phase_offset=0.0, sign=-1.0)
animate_knee_bend(LR, "Run", 1, FPS * 0.55, amplitude_deg=70.0, phase_offset=math.pi, sign=-1.0)
animate_rot_x(AR, "Run", 1, FPS * 0.55, amplitude_deg=40.0, phase_offset=0.0)
animate_rot_x(AL, "Run", 1, FPS * 0.55, amplitude_deg=40.0, phase_offset=math.pi)
animate_pos_z(torso, "Run", 1, FPS * 0.55, amplitude=0.045, phase_offset=math.pi / 2.0, freq_mult=2.0)
animate_rot_x(torso, "Run", 1, FPS * 0.55, amplitude_deg=3.0, phase_offset=0.0, offset_deg=-12.0, samples=4)

bpy.context.scene.render.fps = FPS
for o in bpy.data.objects:
	if o.animation_data:
		for t in o.animation_data.nla_tracks:
			t.mute = True
bpy.context.scene.frame_set(0)
for obj, attr, value in rest_state:
	setattr(obj, attr, value)
bpy.context.view_layer.update()
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
	filepath=out_path,
	export_format="GLB",
	export_animation_mode="ACTIONS",
)

print("EXPORTED seed=%d path=%s objects=%d" % (seed, out_path, len(objects)))
