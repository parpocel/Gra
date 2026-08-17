extends Control

@export var knob_range: float = 80.0

@onready var base: Control = $Base
@onready var knob: Control = $Base/Knob

var _touches: Dictionary = {}


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed:
			_on_touch_start(event.index, event.position)
		else:
			_on_touch_end(event.index)
	elif event is InputEventScreenDrag:
		_on_touch_drag(event.index, event.position)
	elif event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		MobileInput.add_look_delta(event.relative)
	elif event is InputEventMouseButton and event.pressed:
		if not DisplayServer.is_touchscreen_available() and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _on_touch_start(index: int, pos: Vector2) -> void:
	var is_move: bool = pos.x < size.x / 2.0
	_touches[index] = {"mode": "move" if is_move else "look", "center": pos, "last_pos": pos}
	if is_move:
		base.position = pos - base.size / 2.0
		knob.position = base.size / 2.0 - knob.size / 2.0
		base.visible = true
		MobileInput.debug_move_touches += 1
		MobileInput.debug_last_move_touch_pos = pos
	else:
		MobileInput.debug_look_touches += 1
		MobileInput.debug_last_look_touch_pos = pos


func _on_touch_drag(index: int, pos: Vector2) -> void:
	if not _touches.has(index):
		return
	var t: Dictionary = _touches[index]
	if t["mode"] == "move":
		MobileInput.debug_move_drags += 1
		var offset: Vector2 = pos - t["center"]
		if offset.length() > knob_range:
			offset = offset.normalized() * knob_range
		MobileInput.debug_max_move_offset = max(MobileInput.debug_max_move_offset, offset.length())
		knob.position = base.size / 2.0 + offset - knob.size / 2.0
		MobileInput.set_move_vector(offset / knob_range)
	else:
		MobileInput.debug_look_drags += 1
		var delta: Vector2 = pos - t["last_pos"]
		t["last_pos"] = pos
		_touches[index] = t
		MobileInput.add_look_delta(delta)


func _on_touch_end(index: int) -> void:
	if not _touches.has(index):
		return
	var t: Dictionary = _touches[index]
	if t["mode"] == "move":
		base.visible = false
		MobileInput.set_move_vector(Vector2.ZERO)
	_touches.erase(index)
