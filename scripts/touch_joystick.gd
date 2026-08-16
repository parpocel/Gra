extends Control

@export var knob_range: float = 60.0

@onready var knob: Control = $Knob

var _touch_index: int = -1


func _ready() -> void:
	knob.position = size / 2.0 - knob.size / 2.0


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		if event.pressed and _touch_index == -1:
			_touch_index = event.index
			_update_knob(event.position)
		elif not event.pressed and event.index == _touch_index:
			_touch_index = -1
			knob.position = size / 2.0 - knob.size / 2.0
			MobileInput.set_move_vector(Vector2.ZERO)
	elif event is InputEventScreenDrag and event.index == _touch_index:
		_update_knob(event.position)


func _update_knob(local_pos: Vector2) -> void:
	var center: Vector2 = size / 2.0
	var offset: Vector2 = local_pos - center
	if offset.length() > knob_range:
		offset = offset.normalized() * knob_range
	knob.position = center + offset - knob.size / 2.0
	MobileInput.set_move_vector(offset / knob_range)
