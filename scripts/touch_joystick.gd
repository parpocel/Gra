extends Control

@export var knob_range: float = 80.0

@onready var base: Control = $Base
@onready var knob: Control = $Base/Knob

var _touch_index: int = -1
var _center: Vector2 = Vector2.ZERO


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed and _touch_index == -1:
			_touch_index = event.index
			_center = event.position
			base.position = _center - base.size / 2.0
			knob.position = base.size / 2.0 - knob.size / 2.0
			base.visible = true
			MobileInput.debug_move_touches += 1
			MobileInput.debug_last_move_touch_pos = event.position
		elif not event.pressed and event.index == _touch_index:
			_touch_index = -1
			base.visible = false
			MobileInput.set_move_vector(Vector2.ZERO)
	elif event is InputEventScreenDrag and event.index == _touch_index:
		_update_knob(event.position)


func _update_knob(touch_pos: Vector2) -> void:
	var offset: Vector2 = touch_pos - _center
	if offset.length() > knob_range:
		offset = offset.normalized() * knob_range
	knob.position = base.size / 2.0 + offset - knob.size / 2.0
	MobileInput.set_move_vector(offset / knob_range)
