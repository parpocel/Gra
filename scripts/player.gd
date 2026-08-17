extends CharacterBody3D

const WALK_SPEED := 2.5
const RUN_SPEED := 6.0
const RUN_INTENSITY_THRESHOLD := 0.6
const IDLE_INTENSITY_THRESHOLD := 0.05
const GRAVITY := 9.8
const ROTATION_SPEED := 10.0
const LOOK_SENSITIVITY := 0.2

@onready var camera_pivot: Node3D = $CameraPivot
@onready var model_root: Node3D = $ModelRoot

var camera_yaw: float = 0.0
var camera_pitch: float = -20.0

var _anim_player: AnimationPlayer = null
var _anim_state: String = ""


func _ready() -> void:
	MobileInput.interact_pressed.connect(_on_interact)
	_anim_player = model_root.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if _anim_player != null:
		for anim_name in ["Idle", "Walk", "Run"]:
			if _anim_player.has_animation(anim_name):
				_anim_player.get_animation(anim_name).loop_mode = Animation.LOOP_LINEAR


func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y -= GRAVITY * delta

	var input_dir: Vector2 = MobileInput.move_vector
	if input_dir == Vector2.ZERO:
		input_dir = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var intensity: float = clampf(input_dir.length(), 0.0, 1.0)

	var cam_basis: Basis = camera_pivot.global_transform.basis
	var forward: Vector3 = -cam_basis.z
	forward.y = 0.0
	forward = forward.normalized()
	var right: Vector3 = cam_basis.x
	right.y = 0.0
	right = right.normalized()

	var direction: Vector3 = right * input_dir.x + forward * -input_dir.y
	if direction.length() > 0.001:
		direction = direction.normalized()
		var speed: float = lerpf(WALK_SPEED, RUN_SPEED, intensity)
		velocity.x = direction.x * speed
		velocity.z = direction.z * speed
		var target_angle: float = atan2(direction.x, direction.z)
		model_root.rotation.y = lerp_angle(model_root.rotation.y, target_angle, ROTATION_SPEED * delta)
	else:
		velocity.x = move_toward(velocity.x, 0.0, RUN_SPEED)
		velocity.z = move_toward(velocity.z, 0.0, RUN_SPEED)

	move_and_slide()
	_update_animation(intensity)

	var look_delta: Vector2 = MobileInput.consume_look_delta()
	if look_delta != Vector2.ZERO:
		_apply_look(look_delta * LOOK_SENSITIVITY)

	if Input.is_action_just_pressed("interact"):
		_on_interact()


func _update_animation(intensity: float) -> void:
	if _anim_player == null:
		return
	var state: String
	if intensity < IDLE_INTENSITY_THRESHOLD:
		state = "Idle"
	elif intensity < RUN_INTENSITY_THRESHOLD:
		state = "Walk"
	else:
		state = "Run"
	if state != _anim_state and _anim_player.has_animation(state):
		_anim_player.play(state)
		_anim_state = state


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _apply_look(delta: Vector2) -> void:
	camera_yaw -= delta.x
	camera_pitch = clamp(camera_pitch - delta.y, -60.0, 10.0)
	camera_pivot.rotation_degrees = Vector3(camera_pitch, camera_yaw, 0.0)


func _on_interact() -> void:
	print("Interact!")
