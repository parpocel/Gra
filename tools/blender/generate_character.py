import bpy
import colorsys
import math
import random
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
seed = int(argv[0]) if len(argv) > 0 else random.randint(0, 999999)
out_path = argv[1] if len(argv) > 1 else "/tmp/character.glb"
preset = argv[2] if len(argv) > 2 else None

random.seed(seed)

FPS = 24
objects = {}


def random_color(s=0.6, v=0.9, h_range=(0.0, 1.0)):
	h = random.uniform(*h_range)
	return colorsys.hsv_to_rgb(h, s, v)


def reparent(child, parent):
	child.parent = parent
	child.matrix_parent_inverse = parent.matrix_world.inverted()
	bpy.context.view_layer.update()


def add_part(name, size, center_pos, pivot_pos, color, parent=None):
	bpy.ops.mesh.primitive_cube_add(size=1, location=center_pos)
	obj = bpy.context.active_object
	obj.name = name
	obj.scale = size
	bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

	bpy.context.scene.cursor.location = pivot_pos
	bpy.context.view_layer.objects.active = obj
	obj.select_set(True)
	bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

	min_dim = min(size)
	bevel_width = min(0.022, max(0.006, min_dim * 0.16))
	bevel_width = min(bevel_width, min_dim * 0.45)
	mod = obj.modifiers.new(name="Bevel", type="BEVEL")
	mod.width = bevel_width
	mod.segments = 2
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


rest_state = []


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

# --- proportions (feet at z=0) ---
foot_h = 0.12
lower_leg_h = 0.43
upper_leg_h = 0.40
torso_h = 0.60
upper_arm_h = 0.27
lower_arm_h = 0.25
hand_h = 0.13
head_s = 0.32

leg_w = 0.16
leg_d = 0.20
torso_w = 0.48
torso_d = 0.26
arm_w = 0.14

z_ankle = foot_h
z_knee = z_ankle + lower_leg_h
z_hip = z_knee + upper_leg_h
z_shoulder = z_hip + torso_h
z_elbow = z_shoulder - upper_arm_h
z_wrist = z_elbow - lower_arm_h
z_hand_bottom = z_wrist - hand_h
z_head_top = z_shoulder + head_s

leg_x = 0.11
arm_x = torso_w / 2.0 + arm_w / 2.0 + 0.01

# --- torso + shirt ---
torso = add_part(
	"Torso", (torso_w, torso_d, torso_h),
	(0.0, 0.0, (z_hip + z_shoulder) / 2.0), (0.0, 0.0, (z_hip + z_shoulder) / 2.0),
	jacket_color,
)
add_part(
	"Shirt", (torso_w * 0.55, torso_d * 1.05, 0.10),
	(0.0, 0.0, z_shoulder - 0.02), (0.0, 0.0, z_shoulder - 0.02),
	shirt_color, parent=torso,
)

if has_backpack:
	add_part(
		"Backpack", (torso_w * 0.7, torso_d * 0.5, torso_h * 0.85),
		(0.0, torso_d * 0.85, (z_hip + z_shoulder) / 2.0), (0.0, torso_d * 0.85, (z_hip + z_shoulder) / 2.0),
		backpack_color, parent=torso,
	)

# --- legs (parented to torso so hip-bob during Walk/Run carries the whole body) ---
for side, sx in (("L", -leg_x), ("R", leg_x)):
	foot = add_part(
		"Foot_%s" % side, (leg_w, leg_d * 1.15, foot_h),
		(sx, leg_d * 0.1, foot_h / 2.0), (sx, 0.0, 0.0),
		shoe_color,
	)
	lower_leg = add_part(
		"LowerLeg_%s" % side, (leg_w * 0.9, leg_d * 0.85, lower_leg_h),
		(sx, 0.0, (z_ankle + z_knee) / 2.0), (sx, 0.0, z_knee),
		pants_color,
	)
	reparent(foot, lower_leg)
	upper_leg = add_part(
		"UpperLeg_%s" % side, (leg_w, leg_d, upper_leg_h),
		(sx, 0.0, (z_knee + z_hip) / 2.0), (sx, 0.0, z_hip),
		pants_color, parent=torso,
	)
	reparent(lower_leg, upper_leg)

# --- head + face details ---
head = add_part(
	"Head", (head_s, head_s, head_s),
	(0.0, 0.0, z_shoulder + head_s / 2.0), (0.0, 0.0, z_shoulder),
	skin, parent=torso,
)
add_part(
	"Glasses", (head_s * 0.92, 0.03, head_s * 0.22),
	(0.0, -head_s / 2.0, z_shoulder + head_s * 0.58), (0.0, -head_s / 2.0, z_shoulder + head_s * 0.58),
	(0.05, 0.05, 0.05), parent=head,
)
if has_beard:
	add_part(
		"Beard", (head_s * 0.8, head_s * 0.5, head_s * 0.4),
		(0.0, -head_s * 0.15, z_shoulder + head_s * 0.18), (0.0, -head_s * 0.15, z_shoulder + head_s * 0.18),
		hair_color, parent=head,
	)
if has_cap:
	add_part(
		"Cap", (head_s * 1.05, head_s * 1.05, head_s * 0.35),
		(0.0, 0.0, z_shoulder + head_s * 0.92), (0.0, 0.0, z_shoulder + head_s * 0.92),
		cap_color, parent=head,
	)
	add_part(
		"CapBrim", (head_s * 0.5, head_s * 0.35, head_s * 0.08),
		(0.0, -head_s * 0.6, z_shoulder + head_s * 0.8), (0.0, -head_s * 0.6, z_shoulder + head_s * 0.8),
		cap_color, parent=head,
	)
	add_part(
		"CapLogo", (head_s * 0.22, 0.02, head_s * 0.18),
		(0.0, -head_s * 0.51, z_shoulder + head_s * 0.95), (0.0, -head_s * 0.51, z_shoulder + head_s * 0.95),
		cap_logo_color, parent=head,
	)
else:
	add_part(
		"Hair", (head_s * 1.02, head_s * 1.02, head_s * 0.3),
		(0.0, 0.0, z_shoulder + head_s * 0.88), (0.0, 0.0, z_shoulder + head_s * 0.88),
		hair_color, parent=head,
	)

# --- arms ---
for side, sx in (("L", -arm_x), ("R", arm_x)):
	upper_arm = add_part(
		"UpperArm_%s" % side, (arm_w, arm_w, upper_arm_h),
		(sx, 0.0, (z_elbow + z_shoulder) / 2.0), (sx, 0.0, z_shoulder),
		jacket_color, parent=torso,
	)
	lower_arm = add_part(
		"LowerArm_%s" % side, (arm_w * 0.85, arm_w * 0.85, lower_arm_h),
		(sx, 0.0, (z_wrist + z_elbow) / 2.0), (sx, 0.0, z_elbow),
		skin,
	)
	reparent(lower_arm, upper_arm)
	hand = add_part(
		"Hand_%s" % side, (arm_w * 0.8, arm_w * 0.8, hand_h),
		(sx, 0.0, (z_hand_bottom + z_wrist) / 2.0), (sx, 0.0, z_wrist),
		skin,
	)
	reparent(hand, lower_arm)
	if has_book and side == "R":
		add_part(
			"Book", (0.14, 0.03, 0.18),
			(sx, -0.09, z_hand_bottom + 0.03), (sx, -0.09, z_hand_bottom + 0.03),
			book_color, parent=hand,
		)

# ================= animations =================
UL = objects["UpperLeg_L"]
UR = objects["UpperLeg_R"]
AL = objects["UpperArm_L"]
AR = objects["UpperArm_R"]

# --- Idle: subtle breathing sway ---
animate_rot_x(AL, "Idle", 1, FPS * 2.0, amplitude_deg=4.0, phase_offset=0.0)
animate_rot_x(AR, "Idle", 1, FPS * 2.0, amplitude_deg=4.0, phase_offset=0.0)
animate_pos_z(torso, "Idle", 1, FPS * 2.0, amplitude=0.012, phase_offset=0.0)

# --- Walk: alternating arm/leg swing ---
animate_rot_x(UL, "Walk", 1, FPS * 1.0, amplitude_deg=28.0, phase_offset=0.0)
animate_rot_x(UR, "Walk", 1, FPS * 1.0, amplitude_deg=28.0, phase_offset=math.pi)
animate_rot_x(AR, "Walk", 1, FPS * 1.0, amplitude_deg=24.0, phase_offset=0.0)
animate_rot_x(AL, "Walk", 1, FPS * 1.0, amplitude_deg=24.0, phase_offset=math.pi)
animate_pos_z(torso, "Walk", 1, FPS * 1.0, amplitude=0.02, phase_offset=math.pi / 2.0, freq_mult=2.0)

# --- Run: bigger/faster swing + more bob ---
animate_rot_x(UL, "Run", 1, FPS * 0.55, amplitude_deg=48.0, phase_offset=0.0, offset_deg=-8.0)
animate_rot_x(UR, "Run", 1, FPS * 0.55, amplitude_deg=48.0, phase_offset=math.pi, offset_deg=-8.0)
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
